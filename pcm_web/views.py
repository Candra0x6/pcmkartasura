from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Berita, Agenda, Dokumen, PesanMasuk


def daftar_berita(request):
    paginator = Paginator(Berita.objects.terbit(), 6)
    berita_page = paginator.get_page(request.GET.get('page'))
    return render(request, 'pcm_web/berita_list.html', {'berita_page': berita_page})


def detail_berita(request, slug):
    berita = get_object_or_404(Berita.objects.terbit(), slug=slug)
    berita_lainnya = Berita.objects.terbit().exclude(pk=berita.pk)[:3]
    return render(
        request,
        'pcm_web/berita_detail.html',
        {'berita': berita, 'berita_lainnya': berita_lainnya},
    )


def daftar_unduhan(request):
    dokumen = Dokumen.objects.order_by('-tanggal_unggah')
    return render(request, 'pcm_web/unduhan.html', {'dokumen_list': dokumen})

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
        return redirect('pcm_web:kontak')

    return render(request, 'pcm_web/kontak.html')