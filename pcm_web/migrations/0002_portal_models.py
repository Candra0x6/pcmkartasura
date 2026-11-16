from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("pcm_web", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="ProfilCabang",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("nama_pcm", models.CharField(default="Pimpinan Cabang Muhammadiyah Kartasura", max_length=150)), ("sejarah", models.TextField(blank=True)), ("sambutan_ketua", models.TextField(blank=True)), ("foto_ketua", models.ImageField(blank=True, null=True, upload_to="profil/")), ("quote_harian", models.TextField(blank=True)), ("alamat", models.TextField(blank=True)), ("kontak", models.CharField(blank=True, max_length=150))],
            options={"verbose_name": "Profil Cabang", "verbose_name_plural": "Profil Cabang"},
        ),
        migrations.CreateModel(
            name="StrukturPengurus",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("nama", models.CharField(max_length=120)), ("jabatan", models.CharField(max_length=120)), ("tipe", models.CharField(choices=[("PH", "Pimpinan Harian"), ("Majelis", "Majelis"), ("Ortom", "Organisasi Otonom")], default="PH", max_length=10)), ("foto", models.ImageField(blank=True, null=True, upload_to="pengurus/")), ("urutan", models.PositiveIntegerField(default=0))],
            options={"verbose_name_plural": "Struktur Pengurus", "ordering": ["urutan", "nama"]},
        ),
        migrations.CreateModel(
            name="AUM",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("nama", models.CharField(max_length=150)), ("kategori", models.CharField(choices=[("Pendidikan", "Pendidikan"), ("Ekonomi", "Ekonomi"), ("Kesehatan", "Kesehatan"), ("Sosial", "Sosial")], max_length=20)), ("deskripsi", models.TextField(blank=True)), ("alamat", models.TextField(blank=True))],
            options={"verbose_name": "Amal Usaha Muhammadiyah", "verbose_name_plural": "Amal Usaha Muhammadiyah", "ordering": ["kategori", "nama"]},
        ),
        migrations.CreateModel(
            name="PRM",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("nama_desa", models.CharField(max_length=120)), ("ketua_ranting", models.CharField(blank=True, max_length=120)), ("alamat_sekretariat", models.TextField(blank=True))],
            options={"verbose_name": "Pimpinan Ranting Muhammadiyah", "verbose_name_plural": "Pimpinan Ranting Muhammadiyah", "ordering": ["nama_desa"]},
        ),
        migrations.CreateModel(
            name="BeritaInformasi",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("judul", models.CharField(max_length=200)), ("slug", models.SlugField(blank=True, max_length=220, unique=True)), ("isi", models.TextField()), ("gambar", models.ImageField(blank=True, null=True, upload_to="berita/")), ("tanggal_publikasi", models.DateTimeField(auto_now_add=True))],
            options={"verbose_name_plural": "Berita dan Informasi", "ordering": ["-tanggal_publikasi"]},
        ),
        migrations.CreateModel(
            name="PanitiaKegiatan",
            fields=[("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")), ("nama_kegiatan", models.CharField(max_length=180)), ("divisi", models.CharField(max_length=120)), ("nama_anggota", models.CharField(max_length=120)), ("peran", models.CharField(blank=True, max_length=120)), ("tugas_selesai", models.BooleanField(default=False))],
            options={"verbose_name_plural": "Panitia Kegiatan", "ordering": ["nama_kegiatan", "divisi", "nama_anggota"]},
        ),
    ]
