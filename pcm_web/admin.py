from django.contrib import admin
from .models import Agenda, PesanMasuk, AmalUsaha, Ranting

# Register your models here.
admin.site.register(Agenda)
admin.site.register(PesanMasuk)

@admin.register(AmalUsaha)
class AmalUsahaAdmin(admin.ModelAdmin):
    pass

@admin.register(Ranting)
class RantingAdmin(admin.ModelAdmin):
    pass
