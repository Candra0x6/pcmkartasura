from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Berita, Agenda, PesanMasuk, AmalUsaha, Ranting

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
    # Mengambil semua data agenda dari database
    daftar_agenda = Agenda.objects.all()
    return render(request, 'pcm_web/agenda.html', {'daftar_agenda': daftar_agenda})

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

def halaman_amal_usaha(request):
    kategori = request.GET.get('kategori', '')

    # Pemetaan kode kategori URL ke label judul kategori (sesuai BIDANG_CHOICES)
    peta_kategori = {
        'klinik': 'Klinik & Balai Pengobatan',
        'lazismu': 'LazisMu',
        'masjid': 'Masjid',
        'panti-asuhan': 'Panti Asuhan',
        'pondok-pesantren': 'Pondok Pesantren',
        'rumah-sakit': 'Rumah Sakit',
        'sekolah': 'Sekolah / Madrasah',
        'toko': 'Toko',
    }

    if kategori in peta_kategori:
        nama_kategori = peta_kategori[kategori]
        daftar_aum = AmalUsaha.objects.filter(bidang=kategori).order_by('nama')
        judul_kategori = f"Amal Usaha Muhammadiyah/'Aisyiyah - {nama_kategori}"
    else:
        nama_kategori = "Amal Usaha Muhammadiyah/'Aisyiyah"
        daftar_aum = AmalUsaha.objects.all().order_by('nama')
        judul_kategori = "Amal Usaha Muhammadiyah/'Aisyiyah"

    context = {
        'daftar_aum': daftar_aum,
        'kategori': kategori,
        'nama_kategori': nama_kategori,
        'judul_kategori': judul_kategori,
    }
    return render(request, 'pcm_web/amal_usaha.html', context)

def halaman_ranting(request):
    # Mengambil semua data ranting diurutkan berdasarkan nama_ranting
    daftar_ranting = Ranting.objects.all().order_by('nama_ranting')
    return render(request, 'pcm_web/ranting.html', {'daftar_ranting': daftar_ranting})

