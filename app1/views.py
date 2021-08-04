from django.http.response import JsonResponse
from django.shortcuts import render

from .models import gdfiles
from .utils import hum_convert



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
  treeData = getChildren(rootdir, all)

  return JsonResponse(treeData, safe=False)
