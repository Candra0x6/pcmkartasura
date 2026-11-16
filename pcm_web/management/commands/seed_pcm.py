from pathlib import Path
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from pcm_web.models import Berita


POSTS_URL = "https://pdmsukoharjo.or.id/wp-json/wp/v2/posts"


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


class Command(BaseCommand):
    help = "Impor berita terbaru dari website resmi PDM Sukoharjo."

    def handle(self, *args, **options):
        try:
            posts = fetch_posts()
        except (requests.RequestException, ValueError) as exc:
            self.stderr.write(self.style.WARNING(f"Gagal mengambil berita WordPress: {exc}"))
            return

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
