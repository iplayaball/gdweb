from django.http.response import JsonResponse
from django.shortcuts import render
import json
import re

from .models import gdfiles
from .utils import hum_convert


searchKey = ''
queryIds = set()
queryFIds = set()

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

  # print(queryRest)

  # queryIds = set()
  for f in queryRest:
    queryFIds.add(f.id)
    queryIds.add(f.id)
    getPid(f.id, idMap)

  # print(queryIds)

  rootdir = all[0]
  all = all[1:]

  treeData = []
  tmpNode = {}
  tmpNode['id'] = rootdir.id
  tmpNode['label'] = rootdir.Name
  tmpNode['Size'] = hum_convert(rootdir.Size)
  tmpNode['children'] = getQueryChildren(rootdir, all)

  treeData.append(tmpNode)

  # print(treeData)
  
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
    tmpNode = {}
    tmpNode['name'] = f.Name
    tmpNode['id'] = f.id
    tmpNode['leaf'] = not f.IsDir
    tmpNode['Size'] = hum_convert(f.Size)
    children.append(tmpNode)
  
  return JsonResponse(children, safe=False)


def lazyIndex(request):
  all = gdfiles.objects.all()
  rootdir = all[0]
  all = all[1:]
  # print(rootdir.MimeType)

  # treeData = []
  # tmp = {}
  # tmp['name'] = rootdir.Name
  treeData = getChild(rootdir, all)
  return JsonResponse(treeData, safe=False)


def getChild(pdir, all):
  children = []
  for f in all:
    if f.pdir == pdir:
      tmpNode = {}
      tmpNode['name'] = f.Name
      tmpNode['id'] = f.id
      tmpNode['leaf'] = not f.IsDir
      tmpNode['Size'] = hum_convert(f.Size)
      children.append(tmpNode)
    else:
      if children:
        break
  return children


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
  all = gdfiles.objects.all()
  rootdir = all[0]
  all = all[1:]

  treeData = []
  tmpNode = {}
  tmpNode['id'] = rootdir.id
  tmpNode['label'] = rootdir.Name
  tmpNode['Size'] = hum_convert(rootdir.Size)
  tmpNode['children'] = getChildren(rootdir, all)

  treeData.append(tmpNode)

  return JsonResponse(treeData, safe=False)
