from django import urls
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Berita, Agenda, PesanMasuk
from .models import ProfilOrganisasi, Pimpinan

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

# View untuk menampilkan halaman Beranda (Hero, Sambutan, dan cuplikan Pimpinan)
def beranda(request):
    # Mengambil data profil organisasi pertama dari database
    profil = ProfilOrganisasi.objects.first()
    # Mengambil maksimal 4 data pimpinan teratas untuk ditampilkan sebagai preview di beranda
    pimpinan_inti = Pimpinan.objects.all()[:4]
    # Mengemas data ke dalam dictionary context untuk dikirim ke template HTML
    context = {
        'profil': profil,
        'pimpinan_inti': pimpinan_inti,
    }
    # Merender halaman beranda.html beserta data dari context
    return render(request, 'pcm_web/beranda.html', context)

# View untuk menampilkan halaman Profil PCM dan Struktur Pimpinan lengkap
def profil_pcm(request):
    # Mengambil data profil organisasi (sejarah, visi, misi, dll.) dari database
    profil = ProfilOrganisasi.objects.first()
    # Mengambil seluruh data pengurus/pimpinan yang tersimpan di database
    daftar_pimpinan = Pimpinan.objects.all()
    # Mengemas data ke dalam dictionary context untuk dikirim ke template HTML
    context = {
        'profil': profil,
        'daftar_pimpinan': daftar_pimpinan,
    }
    # Merender halaman profil.html beserta data lengkapnya
    return render(request, 'pcm_web/profil.html', context)