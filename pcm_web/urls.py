from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from pcm_web import views

# Daftar routing URL utama aplikasi
urlpatterns = [
    path('cari/', views.cari_berita, name='cari_berita'),
    path('agenda/', views.halaman_agenda, name='agenda'),
    path('kontak/', views.halaman_kontak, name='kontak'),
    # Rute menuju panel halaman Admin bawaan Django
    path('admin/', admin.site.urls),
    # Rute halaman utama (Beranda) yang mengarah ke fungsi beranda di views.py
    path('', views.beranda, name='beranda'),
    # Rute halaman Profil PCM & Struktur Pimpinan yang mengarah ke fungsi profil_pcm
    path('profil/', views.profil_pcm, name='profil_pcm'),
]

# Konfigurasi agar file media (seperti foto profil/pimpinan yang di-upload) dapat diakses saat mode development (DEBUG=True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

