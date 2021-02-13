from django.contrib import admin
from .models import gdfiles
from .utils import hum_convert


class gdfilesAdmin(admin.ModelAdmin):
	list_display = ('id', 'dsn', 'fsn', 'humanSize', 'Path', 'pdir')
	search_fields = ['Path']
	ordering = ('id',)

	def humanSize(self, obj):
		return hum_convert(obj.Size)
	humanSize.short_description = '大小'


admin.site.register(gdfiles, gdfilesAdmin)
