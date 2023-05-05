from django.contrib import admin
from .models import noisedata
from .models import noiseLocation
# Register your models here.
admin.site.register(noisedata)
admin.site.register(noiseLocation)