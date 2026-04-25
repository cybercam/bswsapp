"""Sitemap XML (single or split) and robots.txt."""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

from ..config import SITE_URL, TODAY

# Google recommends ≤50,000 URLs per sitemap file.
MAX_URLS_PER_SITEMAP = 50_000

HUB_URL = f"{SITE_URL}/bible/"


def _loc_xml(url: str) -> str:
    safe = xml_escape(url, {"'": "&apos;", '"': "&quot;"})
    return safe


def _urlset_body(urls: list[str], lastmod: str) -> str:
    entries = "\n".join(
        f"  <url><loc>{_loc_xml(u)}</loc><lastmod>{lastmod}</lastmod></url>" for u in urls
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n"
        "</urlset>"
    )


def _sitemap_index_body(part_filenames: list[str], lastmod: str) -> str:
    lines = "\n".join(
        f"  <sitemap><loc>{_loc_xml(f'{SITE_URL}/bible/{fn}')}</loc>"
        f"<lastmod>{lastmod}</lastmod></sitemap>"
        for fn in part_filenames
    )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{lines}\n"
        "</sitemapindex>"
    )


def normalize_sitemap_urls(urls: list[str]) -> list[str]:
    """Stable unique list with hub first, then sorted remaining URLs."""
    hub_norm = HUB_URL.rstrip("/")
    seen: set[str] = set()
    rest: list[str] = []
    for raw in sorted({u.strip() for u in urls if u and u.strip()}):
        if raw.rstrip("/") == hub_norm:
            continue
        if raw not in seen:
            seen.add(raw)
            rest.append(raw)
    return [HUB_URL] + rest


def generate_sitemap_files(all_urls: list[str]) -> list[tuple[str, str]]:
    """
    Return (relative_path_under_bible/, xml_content) for each file to write.
    Single sitemap.xml when under the limit; otherwise sitemap.xml (index) + sitemap-NNN.xml parts.
    """
    urls = normalize_sitemap_urls(all_urls)
    lastmod = TODAY
    n = len(urls)
    if n <= MAX_URLS_PER_SITEMAP:
        return [("sitemap.xml", _urlset_body(urls, lastmod))]

    parts: list[tuple[str, str]] = []
    part_names: list[str] = []
    for i in range(0, n, MAX_URLS_PER_SITEMAP):
        chunk = urls[i : i + MAX_URLS_PER_SITEMAP]
        name = f"sitemap-{i // MAX_URLS_PER_SITEMAP:03d}.xml"
        part_names.append(name)
        parts.append((name, _urlset_body(chunk, lastmod)))
    index_xml = _sitemap_index_body(part_names, lastmod)
    return [("sitemap.xml", index_xml)] + parts


def urls_from_log_file(path: Path) -> list[str]:
    """Read unique non-empty URL lines, stable sorted (for book-wise builds after prune)."""
    if not path.exists():
        return []
    seen: set[str] = set()
    out: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        u = line.strip()
        if not u or u in seen:
            continue
        seen.add(u)
        out.append(u)
    return sorted(out)


# Backwards compatibility: single urlset (used by tests / callers).
def generate_sitemap(all_urls: list[str]) -> str:
    """Return one urlset XML string (first file only). Prefer generate_sitemap_files for production."""
    files = generate_sitemap_files(all_urls)
    return files[0][1]


ROBOTS_TXT = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
Sitemap: {SITE_URL}/bible/sitemap.xml
"""
