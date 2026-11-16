from django.urls import path
from . import views

app_name = 'pcm_web'

urlpatterns = [
    path('cari/', views.cari_berita, name='cari_berita'),
    path('agenda/', views.halaman_agenda, name='agenda'),
    path('kontak/', views.halaman_kontak, name='kontak'),
    path('amal-usaha/', views.halaman_amal_usaha, name='amal_usaha'),
    path('ranting/', views.halaman_ranting, name='ranting'),
    path('berita/', views.daftar_berita, name='daftar_berita'),
    path('berita/<slug:slug>/', views.detail_berita, name='detail_berita'),
    path('unduhan/', views.daftar_unduhan, name='daftar_unduhan'),
]