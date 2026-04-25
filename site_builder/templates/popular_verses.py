"""Curated popular-verse landing pages (slug URLs under /bible/{version}/{slug}/)."""
from __future__ import annotations

import html
import json

from .. import config
from ..config import ASSET_READER_JS_PATH, OG_LOCALE, SITE_URL
from ..helpers import verse_detail_rel_url
from ..layout import app_cta_banner, html_head, output_asset_href, theme_sheet, topbar_html


def generate_popular_verse_landing_page(
    *,
    version_id: str,
    vlabel: str,
    lang_code: str,
    page_slug: str,
    book_display: str,
    bslug: str,
    ch_num: int,
    vnum: int,
    primary_text: str,
    english_text: str,
    english_label: str,
) -> str:
    canonical = f"{SITE_URL}/{config.OUT_DIR}/{version_id}/{page_slug}/"
    ref_plain = f"{book_display} {ch_num}:{vnum}"
    title = f"{ref_plain} — {vlabel} | Popular verse | Bible Study with Steffi"
    snippet = str(primary_text).replace('"', "'").strip()[:155]
    description = (
        f"Read {ref_plain} in {vlabel}. {snippet}… "
        "Full chapter, verse detail, and English parallel — Bible Study with Steffi."
    )
    keywords = (
        f"{book_display} {ch_num}:{vnum} telugu, {book_display} {ch_num}:{vnum} {vlabel}, "
        f"{ref_plain}, bible verse online, bswsapp"
    )

    # Slug landing pages are generated only for selected versions; omit hreflang cluster
    # to avoid pointing at URLs we did not emit for every language.
    hreflang_str = ""

    chapter_url = f"/{config.OUT_DIR}/{version_id}/{bslug}/{ch_num}/"
    verse_detail_url = verse_detail_rel_url(version_id, bslug, ch_num, vnum)
    safe_primary = html.escape(str(primary_text))
    safe_en = html.escape(str(english_text)) if english_text else ""
    en_block = ""
    if safe_en:
        en_block = (
            f'<section class="english-parallel-block detail-panel" lang="en">'
            f"<h3>{html.escape(english_label)}</h3>"
            f'<p class="verse-detail-text">{safe_en}</p></section>'
        )

    structured_data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": "Bible", "item": f"{SITE_URL}/{config.OUT_DIR}/"},
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": vlabel,
                        "item": f"{SITE_URL}/{config.OUT_DIR}/{version_id}/",
                    },
                    {"@type": "ListItem", "position": 4, "name": ref_plain, "item": canonical},
                ],
            },
            {
                "@type": "WebPage",
                "name": title,
                "url": canonical,
                "description": description,
                "inLanguage": lang_code,
                "isPartOf": {
                    "@type": "WebSite",
                    "name": "Bible Study with Steffi",
                    "url": SITE_URL,
                },
            },
        ],
    }

    head = html_head(
        title,
        description,
        canonical,
        lang_code,
        hreflang_str,
        keywords,
        og_type="article",
        og_locale=OG_LOCALE.get(version_id, ""),
        structured_data=structured_data,
    )

    nav_json = json.dumps(
        {
            "out_dir": str(config.OUT_DIR),
            "version_id": version_id,
            "book_slug": bslug,
            "chapter": ch_num,
            "verse": vnum,
        },
        ensure_ascii=False,
    )

    return f"""{head}
<body>
{topbar_html(f"{html.escape(ref_plain)} · {html.escape(vlabel)}", show_verse_links_toggle=False)}
<div id="wrap">
  <main id="reader">
    <article class="verse-detail-card popular-landing">
      <p class="verse-detail-ref">{html.escape(ref_plain)}</p>
      <p class="verse-detail-text">{safe_primary}</p>
      <div class="verse-detail-links">
        <a href="{chapter_url}">Open full chapter</a>
        <a href="{verse_detail_url}">Verse tools &amp; cross-refs</a>
      </div>
    </article>
    {en_block}
    {app_cta_banner()}
    <p class="verse-detail-meta">Bookmark this page for quick access to {html.escape(ref_plain)} in {html.escape(vlabel)}.</p>
  </main>
</div>
{theme_sheet()}
<script type="application/json" id="popular-ctx">{nav_json}</script>
<script src="{output_asset_href(ASSET_READER_JS_PATH)}" defer></script>
</body>
</html>"""
