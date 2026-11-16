from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta  # Tambahan untuk menghitung jarak hari
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
    waktu_sekarang = timezone.now()
    
    # --- LOGIKA AGENDA RUTIN (JALAN 2) ---
    # 1. Cari agenda rutin yang jam/tanggalnya sudah terlewat
    agenda_rutin_lewat = Agenda.objects.filter(rutin=True, waktu_mulai__lt=waktu_sekarang)
    
    for agenda in agenda_rutin_lewat:
        # 2. Bikin jadwal baru persis sama, tapi waktunya ditambah 7 hari (minggu depan)
        Agenda.objects.create(
            nama_kegiatan=agenda.nama_kegiatan,
            waktu_mulai=agenda.waktu_mulai + timedelta(days=7),
            tempat=agenda.tempat,
            keterangan=agenda.keterangan,
            rutin=True # Jadwal minggu depan tetap dicentang rutin
        )
        # 3. Jadwal yang lama centang rutinnya dimatikan biar diam manis di tabel 'Selesai'
        agenda.rutin = False
        agenda.save()
    # ------------------------------------
    
    # Memisahkan agenda yang belum terjadi (waktu_mulai >= sekarang)
    agenda_mendatang = Agenda.objects.filter(waktu_mulai__gte=waktu_sekarang).order_by('waktu_mulai')[:5]
    
    # Memisahkan agenda yang sudah lewat (waktu_mulai < sekarang)
    agenda_selesai = Agenda.objects.filter(waktu_mulai__lt=waktu_sekarang).order_by('-waktu_mulai')[:5]
    
    return render(request, 'pcm_web/agenda.html', {
        'agenda_mendatang': agenda_mendatang,
        'agenda_selesai': agenda_selesai
    })


def halaman_kontak(request):
    if request.method == 'POST':
        # Mengambil data dari form HTML
        nama_pengirim = request.POST.get('nama')
        email_pengirim = request.POST.get('email')
        subjek_pesan = request.POST.get('subjek') 
        isi_pesan = request.POST.get('pesan')
        
        # Menyimpan data ke dalam database PesanMasuk
        PesanMasuk.objects.create(
            nama=nama_pengirim, 
            email=email_pengirim, 
            subjek=subjek_pesan, 
            pesan=isi_pesan
        )
        
        # Memunculkan notifikasi sukses
        messages.success(request, 'Terima kasih, pesan Anda berhasil dikirim!')
        return redirect('kontak')

    return render(request, 'pcm_web/kontak.html')