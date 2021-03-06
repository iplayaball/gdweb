from django.http.response import JsonResponse
from django.shortcuts import render
import json
import re

from .models import gdfiles
from .utils import *


searchKey = ''
queryIds = set()
queryFIds = set()


def convert2dict(f):
	dict = {}
	dict['id'] = f.id
	dict['name'] = f.Name
	dict['IsDir'] = f.IsDir
	dict['Size'] = hum_convert(f.Size)
	# dict['Path'] = f.Path
	dict['MimeType'] = f.MimeType
	# dict['ModTime'] = f.ModTime
	# dict['md5'] = f.md5
	# dict['pdir'] = f.pdir
	dict['fsn'] = f.fsn
	dict['dsn'] = f.dsn
	return dict


def keyFilter(request):
	if queryFIds:
		queryFIds.clear()

	# searchKey = request.POST.get("searchKey", '')
	body_unicode = request.body.decode('utf-8')
	body = json.loads(body_unicode)
	print(json.dumps(body, ensure_ascii=False, sort_keys=True, indent=4, separators=(',', ': ')))
	
	searchKey,isRegex,isFile,isDir,fileType,sizeType,sizeMax,sizeMin = body.values()

	printTime('数据库查询')
	queryCondition = {}
	if isRegex:
		queryCondition['Name__regex'] = searchKey
	else:
		queryCondition['Name__icontains'] = searchKey
	if isFile:
		queryCondition['IsDir'] = False
	if isDir:
		queryCondition['IsDir'] = True
	if fileType:
		queryCondition['MimeType__startswith'] = fileType
	if sizeType == 1:
		queryCondition['Size__lte'] = sizeMax * 1024**3
	elif sizeType == 2:
		queryCondition['Size__gte'] = sizeMin * 1024**3
	elif sizeType == 3:
		queryCondition['Size__range']=(sizeMin * 1024**3,sizeMax * 1024**3)
	
	queryRest = gdfiles.objects.select_related('pdir').filter(**queryCondition)

	""" all = gdfiles.objects.all()
	printTime('遍历查找开始')
	queryRest = []
	for f in all:
		fa = re.findall(searchKey, f.Name)
		if fa:
			queryRest.append(f) """

	printTime('查找完整的父目录')
	restFs = []
	pdirs = {}
	num = {'fn':0, 'dn':0}
	# restCount = queryRest.count()
	for f in queryRest:
		if searchKey:
			res = re.findall(searchKey, f.Name)
			# print(res)
			ll = re.split(searchKey, f.Name)
			#print(ll)
			redName = ''
			for index, item in enumerate(ll):
				if index == len(ll)-1:
					# print(item+'\n')
					redName += item
				else:
					redName += item + '<span style="color:red;">'+res[index]+'</span>'
					# print('red', res[index], 'red')
			# print(redName)
			f.Name = redName
		fs = [f]
		queryFIds.add(f.id)
		if f.IsDir:
			num['dn'] += 1
		else:
			num['fn'] += 1

		getPdir(pdirs, fs, f)
		for i, f in enumerate(fs[:-1]):
			if f.id not in pdirs and f.IsDir:
				pdirs[f.id] = fs[i:]
		fs.reverse()
		restFs.append(fs)
	# print(pdirs)
	printTime('封装每个结果的树')
	treeData = []
	for fs in restFs:
		for i in range (1, len(fs)):
			pf = fs[i-1]
			f = fs[i]
			if hasattr(pf, 'children'):
				# 判断当前 f 是否已经添加过，没添加过才添加
				notIn = True
				for c in pf.children:
					if c == f:
						notIn = False
						break
				if notIn:
					pf.children.append(f)
			else:
				pf.children = [f]

	roots = set()
	for fs in restFs:
		roots.add(fs[0])
	# for root in roots:
	#   print(root.__dict__)
	#   for r in root.children:
	#     print(r.__dict__)
	printTime('树合并')
	for root in roots:
		dict = convert2dict(root)
		if hasattr(root, 'children'):
			dict['children'] = getChildrenDict(root.children)
		treeData.append(dict)

	return JsonResponse(
			{
					'treeData': treeData,
					'expandedKeys': list(queryFIds),
					'num': num
			},
			safe=False
	)

def getChildrenDict(fc):
	children = []
	for f in fc:
		dict = convert2dict(f)
		if hasattr(f, 'children'):
			dict['children'] = getChildrenDict(f.children)
		children.append(dict)
	return children


def getPdir(pdirs, fs, f):
	pdir = f.pdir
	if pdir:
		pdirL = pdirs.get(pdir.id)
		if pdirL:
			fs.extend(pdirL)
		else:
			fs.append(pdir)
			getPdir(pdirs, fs, pdir)


def query(request):
	if queryIds:
		queryIds.clear()
	if queryFIds:
		queryFIds.clear()
	# queryIds = set()
	# queryFIds = set()

	# searchKey = request.POST.get("searchKey", '')
	body_unicode = request.body.decode('utf-8')
	body = json.loads(body_unicode)
	searchKey = body['searchKey']
	print(searchKey)
	# rest = gdfiles.objects.filter(Name__contains=searchKey)
	all = gdfiles.objects.all()

	idMap = {}
	queryRest = []
	for f in all:
		idMap[f.id] = f
		fa = re.findall(searchKey, f.Name)
		if fa:
			queryRest.append(f)

	print(queryRest)

	# queryIds = set()
	for f in queryRest:
		queryFIds.add(f.id)
		queryIds.add(f.id)
		getPid(f.id, idMap)

	print(queryIds)

	rootdir = all[0]
	all = all[1:]

	treeData = []
	tmpNode = {}
	tmpNode['id'] = rootdir.id
	tmpNode['label'] = rootdir.Name
	tmpNode['Size'] = hum_convert(rootdir.Size)
	tmpNode['children'] = getQueryChildren(rootdir, all)

	treeData.append(tmpNode)

	print(treeData)

	return JsonResponse(
		{
			'treeData': treeData,
			'expandedKeys': list(queryFIds)
		},
		safe=False
	)

def getPid(id, idMap):
	f = idMap[id]
	pdir = f.pdir
	if pdir:
		queryIds.add(pdir.id)
		getPid(pdir.id, idMap)

def getQueryChildren(pdir, all):
	children = []
	for f in all:
		if f.pdir == pdir:
			if f.id not in queryIds:
				continue
			tmpNode = {}
			tmpNode['id'] = f.id
			tmpNode['label'] = f.Name
			tmpNode['Size'] = hum_convert(f.Size)
			if f.IsDir:
				tmpNode['children'] = getQueryChildren(f, all)
			children.append(tmpNode)
		else:
			if children:
				break
	return children


def lazyGetChildren(request):
	id = request.GET.get("id")
	# gd = gdfiles.objects.get(id=id)
	childrenData = gdfiles.objects.filter(pdir_id=id)

	# print(childrenData)
	children = []
	for f in childrenData:
		dict = convert2dict(f)
		dict['leaf'] = not f.IsDir
		children.append(dict)

	return JsonResponse(children, safe=False)


def lazyIndex(request):
	gdRoots = gdfiles.objects.filter(MimeType='gdname')

	treeData = []
	for gdRoot in gdRoots:
		dict = convert2dict(gdRoot)
		dict['leaf'] = not gdRoot.IsDir
		# tmpNode['children'] = getChildren(gdRoot, all)
		dict['children'] = []

		treeData.append(dict)

	return JsonResponse(treeData, safe=False)


def getChildren(pdir, all):
	children = []
	for f in all:
		if f.pdir == pdir:
			tmpNode = {}
			tmpNode['id'] = f.id
			tmpNode['label'] = f.Name
			tmpNode['Size'] = hum_convert(f.Size)
			if f.IsDir:
				tmpNode['children'] = getChildren(f, all)
			children.append(tmpNode)
		else:
			if children:
				break
	return children


def index(request):
	gdRoots = gdfiles.objects.filter(MimeType = 'gdname')

	treeData = []
	for gdRoot in gdRoots:
		dict = convert2dict(gdRoot)
		# tmpNode['children'] = getChildren(gdRoot, all)
		# dict['children'] = []
		
		treeData.append(dict)

	return JsonResponse(treeData, safe=False)
