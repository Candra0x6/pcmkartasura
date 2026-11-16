from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta  # Tambahan untuk menghitung jarak hari
from django.db.models import Q
from .models import AmalUsaha, Agenda, Berita, Dokumen, PesanMasuk, Ranting


def daftar_berita(request):
    paginator = Paginator(Berita.objects.terbit(), 6)
    berita_page = paginator.get_page(request.GET.get('page'))
    return render(request, 'pcm_web/berita_list.html', {'berita_page': berita_page})


def detail_berita(request, slug):
    berita = get_object_or_404(Berita.objects.terbit(), slug=slug)
    berita_lainnya = Berita.objects.terbit().exclude(pk=berita.pk)[:3]
    isi_artikel = berita.isi
    sumber_url = ""
    source_marker = "Sumber asli: "
    if source_marker in isi_artikel:
        isi_artikel, sumber_url = isi_artikel.rsplit(source_marker, 1)
        isi_artikel = isi_artikel.rstrip()
        sumber_url = sumber_url.strip()

    return render(
        request,
        'pcm_web/berita_detail.html',
        {
            'berita': berita,
            'berita_lainnya': berita_lainnya,
            'isi_artikel': isi_artikel,
            'sumber_url': sumber_url,
        },
    )


def daftar_unduhan(request):
    dokumen_list = list(Dokumen.objects.order_by('judul'))
    dokumen_cabang = [
        dokumen for dokumen in dokumen_list
        if dokumen.judul.startswith('SK PDM Sukoharjo')
    ]
    dokumen_ranting = [
        dokumen for dokumen in dokumen_list
        if dokumen.judul.startswith('SK PCM Kartasura Susunan PRM')
    ]
    dokumen_lainnya = [
        dokumen for dokumen in dokumen_list
        if dokumen not in dokumen_cabang and dokumen not in dokumen_ranting
    ]
    document_sections = [
        {
            'title': 'SK Tingkat Cabang — PDM Sukoharjo',
            'badge': 'Cabang · 2022–2027',
            'documents': dokumen_cabang,
        },
        {
            'title': 'SK Pimpinan Ranting Muhammadiyah (PRM)',
            'badge': 'PRM · 2022–2027',
            'documents': dokumen_ranting,
        },
        {
            'title': 'Dokumen Resmi Lainnya',
            'badge': 'Dokumen resmi',
            'documents': dokumen_lainnya,
        },
    ]
    return render(
        request,
        'pcm_web/unduhan.html',
        {
            'dokumen_list': dokumen_list,
            'document_sections': document_sections,
        },
    )

def cari_berita(request):
    # Mengambil kata kunci dari URL (misal: ?q=pengajian)
    query = request.GET.get('q')
    hasil = None
    
    if query:
        # Mencari berita yang judul ATAU isinya mengandung kata kunci, dan statusnya sudah 'terbit'
        hasil = Berita.objects.terbit().filter(
            Q(judul__icontains=query) | Q(isi__icontains=query),
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
        return redirect('pcm_web:kontak')

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

