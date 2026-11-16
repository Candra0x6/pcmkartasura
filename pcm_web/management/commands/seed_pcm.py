from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.text import slugify

from pcm_web.models import Berita, Dokumen


POSTS_URL = "https://pdmsukoharjo.or.id/wp-json/wp/v2/posts"
GOOGLE_DRIVE_DOWNLOAD_URL = "https://drive.google.com/uc?export=download&id={file_id}"
SK_DOKUMEN = (
    (
        "SK PDM Sukoharjo Susunan PCM Kartasura 2022–2027",
        "1QjrnkfpO9rEN-XJ3BMWvmjcHD-SI1N3_",
        "Pimpinan Cabang Muhammadiyah Kartasura oleh PDM Sukoharjo",
    ),
    (
        "SK PCM Kartasura Susunan PRM Ngemplak 2022–2027",
        "1y7xbeBTXtC-K-FVkucduWEyfWM_oEf_b",
        "Pimpinan Ranting Muhammadiyah Ngemplak oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Makamhaji 2022–2027",
        "11D_fpsdT6YSnE6lLZ6WoKR49C8djEAEj",
        "Pimpinan Ranting Muhammadiyah Makamhaji oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Ngabeyan 2022–2027",
        "1hbtwQw5lb-TORcQQVJsLeyR06CvGhFAK",
        "Pimpinan Ranting Muhammadiyah Ngabeyan oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Pabelan 2022–2027",
        "1BSIbKV9X0S9rUuenXZSW7vhY_v6IYUoC",
        "Pimpinan Ranting Muhammadiyah Pabelan oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Pucangan 2022–2027",
        "1k3RATuDfd_xiPIGD308kBBOpeQOYBMH7",
        "Pimpinan Ranting Muhammadiyah Pucangan oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Gumpang 2022–2027",
        "1hD4YEhyDClb9ZgIpD7QCsAhNBp3EsP8M",
        "Pimpinan Ranting Muhammadiyah Gumpang oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Ngadirejo 2022–2027",
        "1XZYqc7eIyHGNWkOIoKgnOG0BYYVdp3tt",
        "Pimpinan Ranting Muhammadiyah Ngadirejo oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Kertonatan 2022–2027",
        "12jhHDx0oqukvZr61VhsCbEBNdknxo2EL",
        "Pimpinan Ranting Muhammadiyah Kertonatan oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Wirogunan 2022–2027",
        "1a_C8DgnQpuPzEwVA4i6TzdyDlYyf61z2",
        "Pimpinan Ranting Muhammadiyah Wirogunan oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Kartasura 2022–2027",
        "1q5XqVhhDxyqt1xyDlfNXTTSLMsWqwijo",
        "Pimpinan Ranting Muhammadiyah Kartasura oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Gonilan 2022–2027",
        "1BoU70gewqgQrGXH6LMmvUT10Y_4fXNMd",
        "Pimpinan Ranting Muhammadiyah Gonilan oleh PCM Kartasura",
    ),
    (
        "SK PCM Kartasura Susunan PRM Singopuran 2022–2027",
        "1duR7aLQcqgKtuq4gXI46ZQKzbtor0DJN",
        "Pimpinan Ranting Muhammadiyah Singopuran oleh PCM Kartasura",
    ),
)


def fetch_posts():
    params = {"search": "kartasura", "per_page": 20, "_embed": 1}
    response = requests.get(POSTS_URL, params=params, timeout=20)
    response.raise_for_status()
    posts = response.json()
    if not isinstance(posts, list):
        raise ValueError("Respons WordPress bukan daftar artikel.")
    return posts


def format_article_content(value):
    soup = BeautifulSoup(value or "", "html.parser")
    block_tags = ("p", "h2", "h3", "li")
    blocks = []

    for element in soup.find_all(block_tags):
        if element.find_parent(block_tags):
            continue
        text = element.get_text(" ", strip=True)
        if text:
            blocks.append(text)

    if not blocks:
        text = soup.get_text("\n", strip=True)
        blocks = [line.strip() for line in text.splitlines() if line.strip()]

    return "\n\n".join(blocks)


def clean_html(value):
    return BeautifulSoup(value or "", "html.parser").get_text(" ", strip=True)


def publication_date(post):
    value = post.get("date_gmt") or post.get("date")
    parsed = parse_datetime(value) if value else None
    if parsed is None:
        return timezone.now()
    if timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


def featured_image(post):
    media_items = post.get("_embedded", {}).get("wp:featuredmedia", [])
    if not media_items or not isinstance(media_items[0], dict):
        return ""

    image_url = media_items[0].get("source_url")
    if not image_url:
        return ""

    response = requests.get(image_url, timeout=20)
    response.raise_for_status()
    filename = Path(urlparse(image_url).path).name or f"berita-{post.get('id')}.jpg"
    return ContentFile(response.content, name=filename)


def download_sk_pdf(file_id, filename):
    response = requests.get(
        GOOGLE_DRIVE_DOWNLOAD_URL.format(file_id=file_id),
        timeout=60,
    )
    response.raise_for_status()
    if not response.content.lstrip().startswith(b"%PDF-"):
        raise ValueError("Respons Google Drive bukan berkas PDF.")
    return ContentFile(response.content, name=filename)


def sk_pdf_filename(title):
    normalized_title = title.replace("2022–2027", "2022-2027")
    return f"{slugify(normalized_title)}.pdf"


class Command(BaseCommand):
    help = "Impor berita terbaru dari website resmi PDM Sukoharjo."

    def handle(self, *args, **options):
        try:
            posts = fetch_posts()
        except (requests.RequestException, ValueError) as exc:
            self.stderr.write(self.style.WARNING(f"Gagal mengambil berita WordPress: {exc}"))
        else:
            self.import_news(posts)

        self.import_sk_documents()

    def import_news(self, posts):
        posts = [post for post in posts if isinstance(post, dict)]
        source_urls = {post.get("link") for post in posts if post.get("link")}
        old_imports = Berita.objects.filter(
            Q(isi__contains="Sumber asli: https://pdmsukoharjo.or.id/")
            | Q(isi__contains="Sumber: https://pdmsukoharjo.or.id/")
        )
        removed_count = 0
        for berita in old_imports:
            source_marker = (
                "Sumber asli: " if "Sumber asli: " in berita.isi else "Sumber: "
            )
            source_url = berita.isi.rsplit(source_marker, 1)[-1].strip()
            if source_url not in source_urls:
                berita.delete()
                removed_count += 1

        created_count = 0
        existing_count = 0
        for post in posts:
            title = clean_html(post.get("title", {}).get("rendered", ""))[:200]
            if not title:
                self.stderr.write(self.style.WARNING("Artikel tanpa judul dilewati."))
                continue

            summary = clean_html(post.get("excerpt", {}).get("rendered", ""))
            content = format_article_content(post.get("content", {}).get("rendered", ""))
            source_url = post.get("link", "")
            if source_url:
                content = f"{content}\n\nSumber asli: {source_url}" if content else (
                    f"Sumber asli: {source_url}"
                )

            try:
                image = featured_image(post)
            except requests.RequestException as exc:
                image = ""
                self.stderr.write(
                    self.style.WARNING(f"Gagal mengunduh gambar untuk '{title}': {exc}")
                )

            berita, created = Berita.objects.get_or_create(
                judul=title,
                defaults={
                    "ringkasan": summary,
                    "isi": content,
                    "gambar_sampul": image,
                    "tanggal_terbit": publication_date(post),
                    "status_terbit": "terbit",
                },
            )
            if created:
                created_count += 1
            else:
                berita.isi = content
                berita.save(update_fields=["isi"])
                existing_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Impor selesai: {created_count} berita baru, "
                f"{existing_count} sudah ada; {removed_count} berita lama non-Kartasura "
                f"dihapus; {len(posts)} artikel Kartasura diproses."
            )
        )

    def import_sk_documents(self):
        created_count = 0
        existing_count = 0
        failed_count = 0

        for title, file_id, leadership_unit in SK_DOKUMEN:
            filename = sk_pdf_filename(title)
            keterangan = (
                f"Surat keputusan penetapan susunan {leadership_unit} "
                "periode 2022–2027."
            )
            existing = Dokumen.objects.filter(judul=title).first()
            if (
                existing
                and existing.berkas
                and existing.berkas.storage.exists(existing.berkas.name)
                and existing.berkas.name.rsplit("/", 1)[-1] == filename
            ):
                existing_count += 1
                continue

            try:
                pdf_file = download_sk_pdf(file_id, filename)
                dokumen, created = Dokumen.objects.get_or_create(
                    judul=title,
                    defaults={
                        "keterangan": keterangan,
                        "berkas": pdf_file,
                    },
                )
                if created:
                    created_count += 1
                else:
                    old_file_name = dokumen.berkas.name
                    dokumen.keterangan = keterangan
                    dokumen.berkas.save(filename, pdf_file, save=False)
                    new_file_name = dokumen.berkas.name
                    dokumen.save(update_fields=["keterangan", "berkas"])
                    existing_count += 1
                    if (
                        old_file_name
                        and old_file_name != new_file_name
                        and not Dokumen.objects.filter(berkas=old_file_name)
                        .exclude(pk=dokumen.pk)
                        .exists()
                    ):
                        dokumen.berkas.storage.delete(old_file_name)
            except (requests.RequestException, ValueError) as exc:
                failed_count += 1
                self.stderr.write(
                    self.style.WARNING(f"Gagal mengimpor '{title}': {exc}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Impor SK selesai: {created_count} baru, {existing_count} sudah tersedia, "
                f"{failed_count} gagal."
            )
        )
