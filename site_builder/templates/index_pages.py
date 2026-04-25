"""Landing and book grid indexes."""
import html

from .. import config
from .. import seo_content
from ..config import (
    ASSET_READER_JS_PATH,
    HREFLANG,
    OTHER_LANGUAGE_PAGES,
    SITE_URL,
    VERSIONS,
)
from ..helpers import book_slug, display_book_name, verse_detail_rel_url
from ..layout import app_cta_banner, html_head, output_asset_href, theme_sheet, topbar_html


def generate_bible_index(active_versions, x_default_id):
    canonical = f"{SITE_URL}/{config.OUT_DIR}/"
    # Hero + SEO: keep the /bible/ hub focused on the full regional-language catalog,
    # even when a partial generator run rebuilds only one translation.
    # Version cards: always list the full catalog (VERSIONS) so /bible/ stays a directory
    # even when using --only for faster partial builds.
    index_lang = "en-IN"
    title = "Read Bible Online Free — Telugu, Hindi, Tamil, Kannada & 15 Indian Languages | Bible Study with Steffi"
    description = (
        "Read the Bible online free in Telugu (తెలుగు బైబిల్), Hindi (हिंदी बाइबल), "
        "Tamil, Kannada, Malayalam, Odia, Bengali, Marathi & more. No login, no ads. "
        "Powered by Bible Study with Steffi app."
    )
    keywords = (
        "Telugu Bible online, తెలుగు బైబిల్, Hindi Bible, हिंदी बाइबल, Tamil Bible, "
        "Kannada Bible, Malayalam Bible, Odia Bible, Bengali Bible, read Bible in Indian "
        "languages, free Bible online India"
    )
    hero_title = "Read the Bible Online"
    hero_p = (
        "Free Bible reader in multiple languages — Indian languages and English. "
        "No ads, no login required."
    )
    hero_cta_href = f"/{config.OUT_DIR}/{x_default_id}/john/1/"
    hero_cta_label = "Start Reading — John 1"

    english_cards = ""
    indian_cards = ""
    for vid, vlbl, vlng, vscript, vgroup in VERSIONS:
        card = f'<a href="/{config.OUT_DIR}/{vid}/john/1/" class="ver-card"><div class="vc-label">{vlbl}</div><div class="vc-sub">{vgroup} · {vlng.upper()}</div></a>'
        if vgroup == "English":
            english_cards += card
        else:
            indian_cards += card
    english_section = (
        '<div class="group-title">English Versions</div><div class="ver-grid">'
        + english_cards
        + "</div>"
        if english_cards
        else ""
    )
    indian_section = (
        '<div class="group-title">Indian Languages</div><div class="ver-grid">'
        + indian_cards
        + "</div>"
        if indian_cards
        else ""
    )
    one_grid = english_section + indian_section

    language_cards = "".join(
        f'<a href="/{fname}" class="ver-card"><div class="vc-label">{label}</div><div class="vc-sub">Language landing page</div></a>'
        for fname, label in OTHER_LANGUAGE_PAGES
    )
    language_section = (
        '<div class="group-title">Other Language Bibles</div><div class="ver-grid">'
        + language_cards
        + "</div>"
    )

    hreflang = "\n".join([
        f'<link rel="alternate" hreflang="{HREFLANG.get(vid, "en")}" href="{SITE_URL}/{config.OUT_DIR}/{vid}/john/1/"/>'
        for vid, *_ in active_versions
    ])

    structured_data = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": "Read Bible Online Free in Indian Languages",
        "url": canonical,
        "description": (
            "Free online Bible reader in 15 Indian regional languages including Telugu, "
            "Hindi, Tamil, Kannada, Malayalam."
        ),
        "inLanguage": ["en", "te", "hi", "ta", "kn", "ml", "or", "bn", "mr", "gu", "pa"],
        "isPartOf": {
            "@type": "WebSite",
            "name": "Bible Study with Steffi",
            "url": SITE_URL,
        },
        "breadcrumb": {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": "Read Bible Online", "item": canonical},
            ],
        },
    }
    head = html_head(
        title,
        description,
        canonical,
        index_lang,
        hreflang,
        keywords,
        og_title="Read Bible Online Free in 15 Indian Languages — Bible Study with Steffi",
        og_description=(
            "Free online Bible reader in Telugu, Hindi, Tamil, Kannada, Malayalam, Odia, "
            "Bengali, Marathi and more. No ads, no login."
        ),
        og_image=f"{SITE_URL}/og-bible.png",
        structured_data=structured_data,
    )

    multilingual_intro = """
    <p class="multilingual-intro">
      Read the Bible free online in your language —
      <strong lang="te">తెలుగు బైబిల్</strong> ·
      <strong lang="hi">हिंदी बाइबल</strong> ·
      <strong lang="ta">தமிழ் பைபிள்</strong> ·
      <strong lang="kn">ಕನ್ನಡ ಬೈಬಲ್</strong> ·
      <strong lang="ml">മലയാളം ബൈബിൾ</strong> ·
      <strong lang="or">ଓଡ଼ିଆ ବାଇବେଲ</strong> ·
      <strong lang="bn">বাংলা বাইবেল</strong> ·
      <strong lang="mr">मराठी बायबल</strong>.
      No ads. No login. 15+ languages.
    </p>"""

    return f"""{head}
<body>
<header id="topbar">
  <span class="logo">Bible Study with Steffi</span>
  <span style="flex:1"></span>
  <button type="button" id="theme-btn" class="icon-btn" aria-label="Reading theme and colors">Aa</button>
</header>
<div id="wrap">
  <div id="reader">
    <div class="hero">
      <h1>{hero_title}</h1>
      <p>{hero_p}</p>
      <a class="cta-btn" href="{hero_cta_href}">{hero_cta_label}</a>
    </div>
    {multilingual_intro}
    {one_grid}
    {language_section}
    {app_cta_banner()}
  </div>
</div>
{theme_sheet()}
<script src="{output_asset_href(ASSET_READER_JS_PATH)}" defer></script>
</body>
</html>"""


def generate_version_index_page(version_id, vlabel, lang_code, all_books):
    cards = []
    for bk in all_books:
        bslug = book_slug(bk["n"])
        dname = display_book_name(bk, version_id)
        num_ch = len(bk["ch"])
        cards.append(
            f'<a href="/{config.OUT_DIR}/{version_id}/{bslug}/1/" class="ver-card">'
            f'<div class="vc-label">{html.escape(dname)}</div>'
            f'<div class="vc-sub">{num_ch} chapters</div></a>'
        )
    head = html_head(
        title=f"{vlabel} — Bible Study with Steffi",
        description=f"Read the full {vlabel} Bible online.",
        canonical=f"{SITE_URL}/{config.OUT_DIR}/{version_id}/",
        lang=lang_code,
        hreflang_links="",
    )
    return f"""{head}
<body>
<header id="topbar">
  <a class="logo" href="/{config.OUT_DIR}/">Bible Study with Steffi</a>
  <span class="crumb">{html.escape(vlabel)}</span>
  <button type="button" id="theme-btn" class="icon-btn" aria-label="Reading theme and colors">Aa</button>
</header>
<div id="wrap"><main id="reader"><div class="ver-grid">{"".join(cards)}</div></main></div>
{theme_sheet()}
<script src="{output_asset_href(ASSET_READER_JS_PATH)}" defer></script>
</body>
</html>"""


def generate_book_index_page(version_id, vlabel, lang_code, book):
    bslug = book_slug(book["n"])
    dname = display_book_name(book, version_id)
    en_name = book.get("n", "")
    num_ch = len(book.get("ch", []))
    chapter_links = []
    for ch in book.get("ch", []):
        c = ch.get("c")
        chapter_links.append(
            f'<a class="ch-btn" href="/{config.OUT_DIR}/{version_id}/{bslug}/{c}/">{c}</a>'
        )

    intro_html = seo_content.book_intro_html(version_id, bslug, dname)
    famous_pairs = seo_content.famous_verse_pairs(version_id, bslug)
    famous_parts = []
    for ch_i, v_i in famous_pairs:
        href = verse_detail_rel_url(version_id, bslug, ch_i, v_i)
        famous_parts.append(
            f'<a href="{href}">{html.escape(dname)} {ch_i}:{v_i}</a>'
        )
    famous_section = ""
    if famous_parts:
        famous_section = (
            '<section class="book-famous detail-panel" aria-label="Well-known verses">'
            "<h3>Famous verses</h3>"
            f'<p class="verse-detail-links">{" · ".join(famous_parts)}</p>'
            "</section>"
        )

    rich_seo = (version_id, bslug) in seo_content.BOOK_INTRO_HTML or (
        version_id == "telugu" and bslug in seo_content.TELUGU_SEO_BOOK_SLUGS
    )
    if rich_seo:
        title = (
            f"{dname} ({en_name}) — {vlabel} | Read online | Bible Study with Steffi"
        )
        description = (
            f"Read {dname} ({en_name}) in {vlabel} online — all {num_ch} chapters. "
            f"Free Bible reader: chapter-by-chapter Telugu & Indian language text with "
            f"verse detail pages. Bible Study with Steffi."
        )
        keywords = (
            f"{en_name} {vlabel}, {dname} {vlabel}, {en_name} bible online, "
            f"{dname} bible, read {en_name} online, bswsapp"
        )
    else:
        title = f"{dname} — {vlabel} | Bible Study with Steffi"
        description = (
            f"Read {dname} in {vlabel} online — {num_ch} chapters. "
            "Free Bible reader from Bible Study with Steffi."
        )
        keywords = f"{dname}, {vlabel}, {en_name} bible online, bswsapp"

    canonical = f"{SITE_URL}/{config.OUT_DIR}/{version_id}/{bslug}/"
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
                    {
                        "@type": "ListItem",
                        "position": 4,
                        "name": dname,
                        "item": canonical,
                    },
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
        title=title,
        description=description,
        canonical=canonical,
        lang=lang_code,
        hreflang_links="",
        keywords=keywords,
        structured_data=structured_data,
    )

    sub_h2 = (
        f'<h2><span lang="{lang_code}">{html.escape(dname)}</span> · '
        f'<span lang="en">{html.escape(en_name)}</span></h2>'
        if rich_seo
        else "<h2>Select a chapter</h2>"
    )

    return f"""{head}
<body>
{topbar_html(f"{html.escape(dname)} · {html.escape(vlabel)}", show_verse_links_toggle=False)}
<div id="wrap">
  <main id="reader">
    <div class="ch-head">
      <h1>{html.escape(dname)}</h1>
      {sub_h2}
      <p class="verse-detail-meta">{num_ch} chapters · {html.escape(vlabel)}</p>
    </div>
    <div class="book-intro">{intro_html}</div>
    {famous_section}
    <h3 class="group-title" style="margin-top:24px">Chapters</h3>
    <div id="ch-grid">{"".join(chapter_links)}</div>
    {app_cta_banner()}
  </main>
</div>
{theme_sheet()}
<script src="{output_asset_href(ASSET_READER_JS_PATH)}" defer></script>
</body>
</html>"""
