from django.contrib import admin
from .models import Agenda, PesanMasuk, ProfilCabang, StrukturPengurus, AUM, PRM, BeritaInformasi, PanitiaKegiatan
from .models import ProfilOrganisasi, Pimpinan

# Register your models here.
admin.site.register(Agenda)
admin.site.register(PesanMasuk)

# Koneksi dengan ProfilOrganisasi dan Pimpinan
@admin.register(ProfilOrganisasi)
class ProfilOrganisasiAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return not ProfilOrganisasi.objects.exists()


admin.site.register(Pimpinan)
admin.site.register([ProfilCabang, StrukturPengurus, AUM, PRM, BeritaInformasi, PanitiaKegiatan])
