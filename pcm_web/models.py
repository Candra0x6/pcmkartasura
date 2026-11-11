from django.db import models
from django.utils.text import slugify

class ProfilOrganisasi(models.Model):
    nama = models.CharField(max_length=100)
    nama_singkat = models.CharField(max_length=50)
    tagline = models.CharField(max_length=200)
    tentang = models.TextField()
    sejarah = models.TextField()
    visi = models.TextField()
    misi = models.TextField(help_text="Tulis satu misi per baris")
    alamat_sekretariat = models.TextField()
    telepon = models.CharField(max_length=20)
    email = models.EmailField()
    jumlah_anggota_ktam = models.IntegerField(default=0)
    gambar_utama = models.ImageField(upload_to='profil/')

    class Meta:
        verbose_name_plural = "Profil Organisasi"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    def __str__(self):
        return self.nama

class Pimpinan(models.Model):
    nama = models.CharField(max_length=100)
    jabatan = models.CharField(max_length=100)
    periode = models.CharField(max_length=20, help_text="Misal: 2022-2027")
    foto = models.ImageField(upload_to='pimpinan/', blank=True, null=True)
    urutan_tampil = models.IntegerField(default=0)

    class Meta:
        ordering = ['urutan_tampil']
        verbose_name_plural = "Pimpinan"

    def __str__(self):
        return f"{self.nama} - {self.jabatan}"

class Ranting(models.Model):
    nama_ranting = models.CharField(max_length=100)
    ketua = models.CharField(max_length=100)
    alamat = models.TextField()
    telepon = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Ranting"

    def __str__(self):
        return self.nama_ranting

class AmalUsaha(models.Model):
    BIDANG_CHOICES = [
        ('pendidikan', 'Pendidikan'),
        ('kesehatan', 'Kesehatan'),
        ('sosial', 'Sosial'),
        ('ekonomi', 'Ekonomi'),
    ]
    nama = models.CharField(max_length=100)
    bidang = models.CharField(max_length=20, choices=BIDANG_CHOICES)
    deskripsi = models.TextField()
    alamat = models.TextField()
    gambar = models.ImageField(upload_to='aum/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Amal Usaha"

    def __str__(self):
        return f"{self.nama} ({self.get_bidang_display()})"

class Berita(models.Model):
    STATUS_CHOICES = [
        ('draf', 'Draf'),
        ('terbit', 'Terbit'),
    ]
    judul = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    ringkasan = models.TextField()
    isi = models.TextField()
    gambar_sampul = models.ImageField(upload_to='berita/')
    tanggal_terbit = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draf')

    class Meta:
        verbose_name_plural = "Berita"
        ordering = ['-tanggal_terbit']

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.judul)
            slug = base_slug
            counter = 1
            while Berita.objects.filter(slug=slug).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.judul

class Agenda(models.Model):
    nama_kegiatan = models.CharField(max_length=200)
    waktu_mulai = models.DateTimeField()
    tempat = models.CharField(max_length=200)
    keterangan = models.TextField()

    class Meta:
        verbose_name_plural = "Agenda"
        ordering = ['waktu_mulai']

    def __str__(self):
        return self.nama_kegiatan

class Dokumen(models.Model):
    judul = models.CharField(max_length=200)
    keterangan = models.TextField()
    berkas = models.FileField(upload_to='dokumen/')
    tanggal_unggah = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Dokumen"

    def __str__(self):
        return self.judul

class PesanMasuk(models.Model):
    nama = models.CharField(max_length=100)
    email = models.EmailField()
    subjek = models.CharField(max_length=200)
    pesan = models.TextField()
    waktu_kirim = models.DateTimeField(auto_now_add=True)
    sudah_dibaca = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Pesan Masuk"
        ordering = ['-waktu_kirim']

    def __str__(self):
        return f"Dari: {self.nama} - {self.subjek}"

class TautanTerkait(models.Model):
    nama = models.CharField(max_length=100)
    url = models.URLField()
    urutan = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Tautan Terkait"
        ordering = ['urutan']

    def __str__(self):
        return self.nama