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

    # Pemetaan parameter kategori URL ke (field bidang model AmalUsaha, label judul kategori)
    peta_kategori = {
        'klinik': ('kesehatan', 'Klinik & Balai Pengobatan'),
        'lazismu': ('sosial', 'LazisMu'),
        'panti-asuhan': ('sosial', 'Panti Asuhan'),
        'pondok-pesantren': ('pendidikan', 'Pondok Pesantren'),
        'rumah-sakit': ('kesehatan', 'Rumah Sakit'),
        'sekolah': ('pendidikan', 'Sekolah / Madrasah'),
        'toko': ('ekonomi', 'Toko'),
    }

    if kategori in peta_kategori:
        bidang_filter, nama_kategori = peta_kategori[kategori]
        daftar_aum = AmalUsaha.objects.filter(bidang=bidang_filter).order_by('nama')
        judul_kategori = f"Amal Usaha Muhammadiyah/'Aisyiyah - {nama_kategori}"
    else:
        bidang_filter = ''
        nama_kategori = "Amal Usaha Muhammadiyah/'Aisyiyah"
        daftar_aum = AmalUsaha.objects.all().order_by('nama')
        judul_kategori = "Amal Usaha Muhammadiyah/'Aisyiyah"

    context = {
        'daftar_aum': daftar_aum,
        'kategori': kategori,
        'bidang_filter': bidang_filter,
        'nama_kategori': nama_kategori,
        'judul_kategori': judul_kategori,
    }
    return render(request, 'pcm_web/amal_usaha.html', context)

def halaman_ranting(request):
    # Mengambil semua data ranting diurutkan berdasarkan nama_ranting
    daftar_ranting = Ranting.objects.all().order_by('nama_ranting')
    return render(request, 'pcm_web/ranting.html', {'daftar_ranting': daftar_ranting})

