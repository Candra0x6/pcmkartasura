from django.urls import path
from . import views

urlpatterns = [
    path('cari/', views.cari_berita, name='cari_berita'),
]