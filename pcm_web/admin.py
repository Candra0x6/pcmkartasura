from django.contrib import admin
from .models import Agenda, PesanMasuk, ProfilCabang, StrukturPengurus, AUM, PRM, BeritaInformasi, PanitiaKegiatan
from .models import ProfilOrganisasi, Pimpinan

# Register your models here.
admin.site.register(Agenda)
admin.site.register(PesanMasuk)

# Koneksi dengan ProfilOrganisasi dan Pimpinan
admin.site.register(ProfilOrganisasi)
admin.site.register(Pimpinan)
admin.site.register([ProfilCabang, StrukturPengurus, AUM, PRM, BeritaInformasi, PanitiaKegiatan])
