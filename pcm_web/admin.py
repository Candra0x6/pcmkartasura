from django.contrib import admin
from .models import Agenda, PesanMasuk, AmalUsaha, Ranting

# Register your models here.
admin.site.register(Agenda)
admin.site.register(PesanMasuk)

@admin.register(AmalUsaha)
class AmalUsahaAdmin(admin.ModelAdmin):
    list_display = ('nama', 'bidang', 'alamat')
    list_filter = ('bidang',)
    search_fields = ('nama', 'alamat', 'deskripsi')

@admin.register(Ranting)
class RantingAdmin(admin.ModelAdmin):
    list_display = ('nama_ranting', 'ketua', 'telepon', 'alamat')
    search_fields = ('nama_ranting', 'ketua', 'alamat')
