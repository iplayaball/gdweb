from datetime import datetime
import pytz


def hum_convert(value):
  units = ["B", "KB", "MB", "GB", "TB", "PB"]
  size = 1024.0
  for i in range(len(units)):
    if (value / size) < 1:
      return "%.2f%s" % (value, units[i])
    value = value / size


def printTime(str):
  tz = pytz.timezone('Asia/Shanghai')
  print('--', datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-5], '', str)


if "__main__" == __name__:
	print(hum_convert(1728777876))
	print(1728777876/1024**3)
  # print(hum_convert(10000))
  # print(hum_convert(100000000))
  # print(hum_convert(100000000000))
  # print(hum_convert(1000000000000000))
  # printTime('aaa')
