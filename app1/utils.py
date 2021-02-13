def hum_convert(value):
  units = ["B", "KB", "MB", "GB", "TB", "PB"]
  size = 1024.0
  for i in range(len(units)):
    if (value / size) < 1:
      return "%.2f%s" % (value, units[i])
    value = value / size


if "__main__" == __name__:
  print(hum_convert(10))
  print(hum_convert(10000))
  print(hum_convert(100000000))
  print(hum_convert(100000000000))
  print(hum_convert(1000000000000000))
