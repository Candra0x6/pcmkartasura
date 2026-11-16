from django.urls import path
from . import views

urlpatterns = [
    path('cari/', views.cari_berita, name='cari_berita'),
    path('agenda/', views.halaman_agenda, name='agenda'),
    path('kontak/', views.halaman_kontak, name='kontak'),
    path('amal-usaha/', views.halaman_amal_usaha, name='amal_usaha'),
    path('ranting/', views.halaman_ranting, name='ranting'),
]