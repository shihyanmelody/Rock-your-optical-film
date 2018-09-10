from django.contrib import admin

# Register your models here.
from .models import Pages, Refractiveindex, Extcoeff
admin.site.register(Pages)
admin.site.register(Refractiveindex)
admin.site.register(Extcoeff)