from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Berita, Agenda, PesanMasuk

def cari_berita(request):
    # Mengambil kata kunci dari URL (misal: ?q=pengajian)
    query = request.GET.get('q')
    hasil = None
    
    if query:
        # Mencari berita yang judul ATAU isinya mengandung kata kunci, dan statusnya sudah 'terbit'
        hasil = Berita.objects.filter(
            Q(judul__icontains=query) | Q(isi__icontains=query),
            status='terbit'
        )
        
    return render(request, 'pcm_web/cari.html', {'query': query, 'hasil': hasil})


def halaman_agenda(request):
    # Mengambil waktu saat ini dari zona waktu server
    waktu_sekarang = timezone.now()
    
    # Memisahkan agenda yang belum terjadi (waktu_mulai >= sekarang)
    agenda_mendatang = Agenda.objects.filter(waktu_mulai__gte=waktu_sekarang).order_by('waktu_mulai')
    
    # Memisahkan agenda yang sudah lewat (waktu_mulai < sekarang)
    agenda_selesai = Agenda.objects.filter(waktu_mulai__lt=waktu_sekarang).order_by('-waktu_mulai')
    
    return render(request, 'pcm_web/agenda.html', {
        'agenda_mendatang': agenda_mendatang,
        'agenda_selesai': agenda_selesai
    })


def halaman_kontak(request):
    if request.method == 'POST':
        # Mengambil data dari form HTML
        nama_pengirim = request.POST.get('nama')
        email_pengirim = request.POST.get('email')
        subjek_pesan = request.POST.get('subjek') # Tambahan field subjek
        isi_pesan = request.POST.get('pesan')
        
        # Menyimpan data ke dalam database PesanMasuk
        PesanMasuk.objects.create(
            nama=nama_pengirim, 
            email=email_pengirim, 
            subjek=subjek_pesan, # Tambahan field subjek
            pesan=isi_pesan
        )
        
        # Memunculkan notifikasi sukses
        messages.success(request, 'Terima kasih, pesan Anda berhasil dikirim!')
        return redirect('kontak')

    return render(request, 'pcm_web/kontak.html')