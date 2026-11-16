from django.contrib import admin
from .models import Agenda, AmalUsaha, Berita, Dokumen, PesanMasuk, Ranting

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


@admin.register(Berita)
class BeritaAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tanggal_terbit', 'status_terbit')
    list_filter = ('status_terbit', 'tanggal_terbit')
    search_fields = ('judul', 'ringkasan', 'isi')
    prepopulated_fields = {'slug': ('judul',)}
    date_hierarchy = 'tanggal_terbit'


@admin.register(Dokumen)
class DokumenAdmin(admin.ModelAdmin):
    list_display = ('judul', 'tanggal_unggah')
    list_filter = ('tanggal_unggah',)
    search_fields = ('judul', 'keterangan')
