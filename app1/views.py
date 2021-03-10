from django.http.response import JsonResponse
from django.shortcuts import render

from .models import gdfiles
from .utils import hum_convert


def index(request):
    all = gdfiles.objects.all()
    rootdir = all[0]
    all = all[1:]
    treeData = getChildren(rootdir, all)
    
    return JsonResponse(treeData, safe=False)


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