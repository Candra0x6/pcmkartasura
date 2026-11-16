import tempfile
from datetime import timedelta

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .management.commands.seed_pcm import format_article_content, sk_pdf_filename
from .models import Berita, Dokumen


class BeritaDokumenViewTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.media_dir.cleanup)
        media_settings = override_settings(MEDIA_ROOT=self.media_dir.name)
        media_settings.enable()
        self.addCleanup(media_settings.disable)

    def buat_berita(self, judul='Berita uji', **kwargs):
        defaults = {
            'judul': judul,
            'ringkasan': 'Ringkasan berita uji',
            'isi': 'Isi berita uji',
            'gambar_sampul': SimpleUploadedFile('sampul.jpg', b'isi gambar'),
            'tanggal_terbit': timezone.now() - timedelta(days=1),
            'status_terbit': 'terbit',
        }
        defaults.update(kwargs)
        return Berita.objects.create(**defaults)

    def test_daftar_berita_dan_unduhan_berhasil(self):
        self.buat_berita()
        Dokumen.objects.create(
            judul='Dokumen uji',
            keterangan='Keterangan dokumen uji',
            berkas=SimpleUploadedFile('dokumen.pdf', b'isi dokumen'),
        )

        self.assertEqual(self.client.get(reverse('pcm_web:daftar_berita')).status_code, 200)
        self.assertEqual(self.client.get(reverse('pcm_web:daftar_unduhan')).status_code, 200)

    def test_berita_draf_tidak_dapat_dilihat(self):
        berita = self.buat_berita(status_terbit='draf')

        response = self.client.get(reverse('pcm_web:detail_berita', args=[berita.slug]))

        self.assertEqual(response.status_code, 404)

    def test_berita_masa_depan_tidak_dapat_dilihat(self):
        berita = self.buat_berita(tanggal_terbit=timezone.now() + timedelta(days=1))

        response = self.client.get(reverse('pcm_web:detail_berita', args=[berita.slug]))

        self.assertEqual(response.status_code, 404)

    def test_detail_berita_menampilkan_tiga_berita_lain(self):
        berita = self.buat_berita(judul='Berita utama')
        for nomor in range(4):
            self.buat_berita(judul=f'Berita lain {nomor}')

        response = self.client.get(reverse('pcm_web:detail_berita', args=[berita.slug]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['berita_lainnya']), 3)

    def test_detail_berita_memisahkan_ringkasan_isi_dan_sumber(self):
        source_url = 'https://pdmsukoharjo.or.id/berita-uji/'
        berita = self.buat_berita(
            ringkasan='Ringkasan yang tidak ditampilkan di detail',
            isi=f'Paragraf pertama.\n\nParagraf kedua.\n\nSumber asli: {source_url}',
        )

        response = self.client.get(reverse('pcm_web:detail_berita', args=[berita.slug]))

        self.assertNotContains(response, 'Ringkasan yang tidak ditampilkan di detail')
        self.assertEqual(response.context['isi_artikel'], 'Paragraf pertama.\n\nParagraf kedua.')
        self.assertEqual(response.context['sumber_url'], source_url)
        self.assertContains(response, f'href="{source_url}"')
        self.assertContains(response, 'target="_blank"')

    def test_format_isi_artikel_memisahkan_blok_dan_teks_tanpa_tag(self):
        html = '<p>Pertama</p><h2>Judul bagian</h2><ul><li>Daftar</li></ul>'

        self.assertEqual(
            format_article_content(html),
            'Pertama\n\nJudul bagian\n\nDaftar',
        )
        self.assertEqual(
            format_article_content('Baris pertama\nBaris kedua'),
            'Baris pertama\n\nBaris kedua',
        )

    def test_slug_berita_kembar_dibuat_unik(self):
        berita_pertama = self.buat_berita(judul='Berita Kembar')
        berita_kedua = self.buat_berita(judul='Berita Kembar')

        self.assertEqual(berita_pertama.slug, 'berita-kembar')
        self.assertEqual(berita_kedua.slug, 'berita-kembar-1')

    def test_daftar_berita_menggunakan_enam_item_per_halaman(self):
        for nomor in range(7):
            self.buat_berita(judul=f'Berita {nomor}')

        response = self.client.get(reverse('pcm_web:daftar_berita'))

        self.assertEqual(len(response.context['berita_page']), 6)
        self.assertEqual(response.context['berita_page'].paginator.count, 7)
        self.assertEqual(response.context['berita_page'].paginator.num_pages, 2)

    def test_hal_unduhan_mengelompokkan_dan_menautkan_dokumen(self):
        cabang = Dokumen.objects.create(
            judul='SK PDM Sukoharjo Susunan PCM Kartasura 2022–2027',
            keterangan='Penetapan susunan PCM Kartasura periode 2022–2027.',
            berkas=SimpleUploadedFile('sk-cabang.pdf', b'%PDF-cabang'),
        )
        ranting = Dokumen.objects.create(
            judul='SK PCM Kartasura Susunan PRM Ngemplak 2022–2027',
            keterangan='Penetapan susunan PRM Ngemplak periode 2022–2027.',
            berkas=SimpleUploadedFile('sk-ranting.pdf', b'%PDF-ranting'),
        )

        response = self.client.get(reverse('pcm_web:daftar_unduhan'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SK Tingkat Cabang — PDM Sukoharjo')
        self.assertContains(response, 'SK Pimpinan Ranting Muhammadiyah (PRM)')
        self.assertContains(response, 'Pratinjau')
        self.assertContains(response, 'Unduh PDF')
        self.assertContains(response, 'target="_blank"')
        self.assertContains(response, cabang.berkas.url)
        self.assertContains(response, ranting.berkas.url)

    def test_nama_file_sk_mengandung_tanda_hubung_periode(self):
        self.assertEqual(
            sk_pdf_filename('SK PCM Kartasura Susunan PRM Ngemplak 2022–2027'),
            'sk-pcm-kartasura-susunan-prm-ngemplak-2022-2027.pdf',
        )

