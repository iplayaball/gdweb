from django.db import models


class gdfiles(models.Model):
  id = models.CharField(max_length=40,primary_key=True)
  Path = models.CharField(max_length=200, verbose_name='完整路径')
  Name = models.CharField(max_length=100, verbose_name='文件名')
  Size = models.BigIntegerField()
  #hsize = models.CharField(max_length=10, null=True)
  MimeType = models.CharField(max_length=50)
  ModTime = models.CharField(max_length=50, null=True)
  IsDir = models.BooleanField()
  # gdid = models.CharField(max_length=50, null=True)
  md5 = models.CharField(max_length=50, null=True)
  pdir = models.ForeignKey("self", verbose_name=(
      "父目录"), on_delete=models.CASCADE, null=True, db_constraint=False)
  fsn = models.IntegerField(default=0, verbose_name='文件数')
  dsn = models.IntegerField(default=0, verbose_name='目录数')

  def __str__(self):
    return self.Path
