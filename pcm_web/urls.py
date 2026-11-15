from django.urls import path
from . import views

# Daftar routing URL utama aplikasi
urlpatterns = [
    path('dashboard/panitia/', views.dashboard_panitia, name='dashboard_panitia'),
    path('cari/', views.cari_berita, name='cari_berita'),
    path('agenda/', views.halaman_agenda, name='agenda'),
    path('kontak/', views.halaman_kontak, name='kontak'),
    # Rute halaman utama (Beranda) yang mengarah ke fungsi beranda di views.py
    path('', views.beranda, name='beranda'),
    # Rute halaman Profil PCM & Struktur Pimpinan yang mengarah ke fungsi profil_pcm
    path('profil/', views.profil_pcm, name='profil_pcm'),
]

