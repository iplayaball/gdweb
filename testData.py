import os
import sys
import django
import json
import subprocess
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 定位到你的django根目录
# print(os.pardir)
sys.path.append(os.path.abspath(os.path.join(BASE_DIR, os.pardir)))
# 行是必须的
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web_files.settings")
django.setup()

from app1 import models
models.gdfiles.objects.all().delete()

#gdName = 't1:entertainment/chinaMovies'
gdName = 't1:entertainment/综艺'
# gdName = 't1:'

if len(sys.argv) > 1:
  argv = sys.argv[1:]
  if argv[0] == 'jlf':
    with open(f'{BASE_DIR}/testgd.json', 'r') as jsf:
      jsonRes = json.load(jsf)
  else:
    print(f'only jlf ,no {argv}')
    sys.exit()
else:
  # grepv = "|egrep -v '^,|gclone sa file: .*\.json'"
  grepv = "|sed 's/gclone sa file:.*\.json//'"
  lsjCmd = f"rclone lsjson -R --hash {gdName} {grepv}"

  lsjsr = subprocess.run(lsjCmd, stdout=subprocess.PIPE, shell=True)
  jsonRes = json.loads(lsjsr.stdout)
   
dirDict = {}
# 统计目录内的文件数据
for fdict in reversed(jsonRes):
  path = '//'+fdict['Path']
  fdict['Path'] = path
  fdict['id'] = fdict.pop('ID')

  if fdict.get('Hashes'):
    fdict['md5'] = fdict['Hashes']['MD5']
    del fdict['Hashes']

  pdir = re.sub(r'/[^/]*$', '', path)
  # 存在同名同路径的文件
  # if path.startswith('//entertainment/top_film/__小影库-7-8分/M08/(7.9分)-无主之地(2001)'):
  #   print('----'+path)
  #   print('=---'+pdir)
  fdict['pdir'] = pdir

  # print(dirDict)
  # print('-----------')
  if fdict['IsDir']:
    # 测试dirDict 找不到path key 的问题。同一个出问题的目录 2427 个文件时没有问题
    ddata = dirDict.get(path)
    if not ddata:
      # for k in dirDict.keys():
        # print(k)
      # fdict['Path'] = path+'=1' # 同名的文件加上=1标识
      print('no '+path)
      # sys.exit()
      fdict['fsn'] = 0
      fdict['dsn'] = 0
    else:
      ddata = dirDict.pop(path)
      size = ddata['size']
      fsn = ddata['fsn']
      dsn = ddata['dsn']
      fdict['Size'] = size
      fdict['fsn'] = fsn
      fdict['dsn'] = dsn
    print(f'{dsn}={fsn}={size}={path}')
    dsn += 1
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
    dirDict[pdir]['fsn'] = fsn
    dirDict[pdir]['dsn'] = dsn
    
  # print(fdict)
rootdir = dirDict.pop('/')
# print(rootdir)
# sys.exit()
if not dirDict:
  models.gdfiles.objects.create(id='01', Path='/', Name='/',
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
  pobj = models.gdfiles.objects.filter(Path=pdir).exclude(fsn=0)
  if len(pobj) != 1:
    print(pobj)
    sys.exit()
  fdict['pdir'] = pobj[0]
  gdf = models.gdfiles(**fdict)
  gdf.save()

#res = models.gdfiles.objects.all()
# print(res)
