import os
import sys
import django
import json
import subprocess
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 定位到你的django根目录
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))
# 行是必须的
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_files.settings")
django.setup()

from app1 import models
models.gdfiles.objects.all().delete()

#gdName = 't1:entertainment/chinaMovies'
# gdName = 't1:entertainment/综艺'
gdName = 't1:'

grepv = "|egrep -v '^,|gclone sa file: .*\.json'"
lsjCmd = f"rclone lsjson -R --hash {gdName} {grepv}"

lsjsr = subprocess.run(lsjCmd, stdout=subprocess.PIPE, shell=True)
jsonRes = json.loads(lsjsr.stdout)

# with open('testgd.json', 'r') as jsf:
# 	jsonRes = json.load(jsf)

dirDict = {}
# 统计目录内的文件数据
for fdict in reversed(jsonRes):
  path = '//'+fdict['Path']
  fdict['Path'] = path
  fdict['gdid'] = fdict.pop('ID')

  if fdict.get('Hashes'):
    fdict['md5'] = fdict['Hashes']['MD5']
    del fdict['Hashes']

  pdir = re.sub(r'/[^/]*$', '', path)
  fdict['pdir'] = pdir

  if fdict['IsDir']:
    # print(dirDict)
    ddata = dirDict.pop(path)
    size = ddata['size']
    fsn = ddata['fsn']
    dsn = ddata['dsn']
    fdict['Size'] = size
    fdict['fsn'] = fsn
    fdict['dsn'] = dsn
    dsn += 1
    # print(f'{dsn}={fsn}={size}={path}')
  else:
    fsn = 1
    dsn = 0
    size = fdict['Size']
    # print(f'0=0={size}={path}')
  if dirDict.get(pdir):
    dirDict[pdir]['size'] += size
    dirDict[pdir]['fsn'] += fsn
    dirDict[pdir]['dsn'] += dsn
    #tt=dirDict[pdir]['fsn']
    #print(f'{pdir}--{tt}')
  else:
    dirDict[pdir] = {'size': size}
    dirDict[pdir]['fsn'] = 1
    dirDict[pdir]['dsn'] = dsn

  # print(fdict)
rootdir = dirDict.pop('/')
if not dirDict:
  models.gdfiles.objects.create(Path='/', Name='/',
                                Size=rootdir['size'],
                                IsDir=True,
                                fsn=rootdir['fsn'],
                                dsn=rootdir['dsn'],
                                MimeType='gdname',
                                )
else:
  print(dirDict)
  sys.exit()

#print(jsonRes[0])
for fdict in jsonRes:
  pdir = fdict['pdir']
  pobj = models.gdfiles.objects.get(Path=pdir)
  fdict['pdir'] = pobj
  gdf = models.gdfiles(**fdict)
  gdf.save()

#res = models.gdfiles.objects.all()
# print(res)
