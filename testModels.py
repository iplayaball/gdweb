import os
import sys
import django
import json
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 定位到你的django根目录
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))
# 行是必须的
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_files.settings")
django.setup()

from app1 import models
models.gdfiles.objects.all().delete()

#gdName = 't1:entertainment/chinaMovies'
#gdName = 't1:entertainment/综艺'
gdName = 't1:'

grepv = "|egrep -v '^,|gclone sa file: .*\.json'"
lsjCmd = f"rclone lsjson -R --hash {gdName} {grepv}"
treeCmd = f"rclone tree -s --human -i --noreport --full-path {gdName} {grepv}"

treesr = subprocess.Popen(treeCmd, stdout=subprocess.PIPE, shell=True)

n=1
pathSizeDict = {}
for l in treesr.stdout.readlines():
  l = bytes.decode(l)
  l = l.lstrip('[').strip().split(']  ')
  pathSizeDict[l[1]] = l[0]

#print(pathSizeDict)
#sys.exit()
lsjsr = subprocess.run(lsjCmd, stdout=subprocess.PIPE, shell=True)
jsonRes = json.loads(lsjsr.stdout)

# with open('testgd.json', 'r') as jsf:
#  jsonRes = json.load(jsf)

nhsizel = []
for fdict in jsonRes:
    Path = '/' + fdict.pop('Path')
    fdict['Path'] = Path
    hsize = pathSizeDict.get(Path)
    if hsize:
      fdict['hsize'] = hsize
      del pathSizeDict[Path]
    else:
      nhsizel.append(fdict)

    fdict['fid'] = fdict.pop('ID')

    if fdict.get('Hashes'):
        fdict['md5'] = fdict['Hashes']['MD5']
        del fdict['Hashes']
    gdf = models.gdfiles(**fdict)
    gdf.save()
    # print(fdict)
print(len(pathSizeDict))
print(pathSizeDict)
print(nhsizel)

#res = models.gdfiles.objects.all()
# print(res)
