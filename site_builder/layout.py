"""HTML shell (head, sidebars, topbar)."""
import html
import json

from . import config
from .config import (
    ASSET_NAV_JS_PATTERN,
    ASSET_STYLE_PATH,
    PLAY_STORE_URL,
    SITE_URL,
)
from .helpers import book_slug, display_book_name, script_font_link_for_lang, version_lang

def output_asset_href(relative_asset_path: str) -> str:
    return f"/{config.OUT_DIR}/{relative_asset_path}"


def output_nav_asset_href(version_id: str) -> str:
    return output_asset_href(ASSET_NAV_JS_PATTERN.format(version_id=version_id))

def html_head(
    title,
    description,
    canonical,
    lang,
    hreflang_links,
    keywords="",
    robots_meta="",
    head_links="",
    og_type="website",
    og_locale="",
    og_title="",
    og_description="",
    og_image=f"{SITE_URL}/assets/og-bible.jpg",
    structured_data=None,
    extra_head="",
):
    desc_attr = html.escape(description, quote=True)
    title_attr = html.escape(title, quote=True)
    og_title_attr = html.escape(og_title or title, quote=True)
    og_desc_attr = html.escape(og_description or description, quote=True)
    ld_obj = structured_data or {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": title,
            "description": description,
            "url": canonical,
            "isPartOf": {
                "@type": "WebSite",
                "name": "Bible Study with Steffi",
                "url": SITE_URL,
            },
            "publisher": {
                "@type": "Organization",
                "name": "Bible Study with Steffi",
                "url": SITE_URL,
            },
    }
    ld_webpage = json.dumps(ld_obj, ensure_ascii=False)
    og_locale_tag = (
        f'<meta property="og:locale" content="{html.escape(og_locale, quote=True)}"/>\n'
        if og_locale
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
{robots_meta}
<title>{title}</title>
<meta name="description" content="{desc_attr}"/>
{"<meta name='keywords' content='" + html.escape(keywords, quote=True) + "'/>" if keywords else ""}
<link rel="canonical" href="{canonical}"/>
{hreflang_links}
{head_links}
{og_locale_tag}<meta property="og:type" content="{html.escape(og_type, quote=True)}"/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:title" content="{og_title_attr}"/>
<meta property="og:description" content="{og_desc_attr}"/>
<meta property="og:image" content="{html.escape(og_image, quote=True)}"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="{title_attr}"/>
<meta name="twitter:description" content="{desc_attr}"/>
<script type="application/ld+json">{ld_webpage}</script>
<link rel="icon" href="/assets/favicon.png"/>
<link rel="manifest" href="{output_asset_href('manifest.json')}"/>
<meta name="theme-color" content="#1e1040"/>
<meta name="mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-capable" content="yes"/>
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>
<meta name="apple-mobile-web-app-title" content="BSWS Bible"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
{script_font_link_for_lang(lang)}<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Lora:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="{output_asset_href(ASSET_STYLE_PATH)}"/>
{extra_head}
</head>"""


def build_parallel_jump_block(version_id: str, bslug: str, ch_num: int, active_versions) -> str:
    if len(active_versions) < 2:
        return ""
    opts = "".join(
        f'<option value="{html.escape(vid)}">{html.escape(vlbl)}</option>'
        for vid, vlbl, *_ in active_versions
        if vid != version_id
    )
    if not opts:
        return ""
    return f"""<div class="s-section">Parallel</div>
<select class="par-jump-select" aria-label="Open two-column parallel reader" onchange="if(!this.value)return;try{{localStorage.setItem('bsws_parallel_secondary',this.value);}}catch(e){{}}window.location='/{config.OUT_DIR}/parallel/{version_id}/'+this.value+'/{bslug}/{ch_num}/';">
<option value="" selected disabled>Compare with…</option>
{opts}</select>"""


def sidebar_html(all_books, current_book_num, current_ch, version_id, vlabel, active_versions, parallel_jump_html=""):
    current_book = next((b for b in all_books if b["b"] == current_book_num), None)
    cur_slug = book_slug(current_book["n"]) if current_book else "genesis"

    # Version selector options (only built / active translations)
    ver_opts = ""
    for vid, vlbl, *_ in active_versions:
        sel = "selected" if vid == version_id else ""
        ver_opts += f'<option value="{vid}" {sel}>{vlbl}</option>'

    return f"""
<aside id="sidebar">
  <div class="s-section">Version</div>
  <select class="s-ver" onchange="window.location='/{config.OUT_DIR}/'+this.value+'/{cur_slug}/{current_ch}/'">{ver_opts}</select>
  {parallel_jump_html}
  <input id="s-search" type="search" placeholder="Search this chapter…" autocomplete="off"/>
  <div id="sr"></div>
  <div class="s-section">Chapters</div>
  <div id="ch-grid"></div>
  <div class="s-section">Books</div>
  <div id="bsws-nav-books"></div>
</aside>
<div id="overlay"></div>"""


def topbar_html(crumb, parallel_link_html="", show_verse_links_toggle=True):
    verse_toggle = ""
    if show_verse_links_toggle:
        verse_toggle = """  <button type="button" id="verse-links-btn" class="icon-btn" aria-label="Toggle verse detail page links" aria-pressed="false">Verse Details Off</button>
"""
    return f"""
<header id="topbar">
  <button type="button" id="menu-btn" class="icon-btn icon-btn--menu" aria-label="Open Bible navigation menu">
    <span class="hb-line" aria-hidden="true"></span><span class="hb-line" aria-hidden="true"></span><span class="hb-line" aria-hidden="true"></span>
  </button>
  <a href="/" class="icon-btn" aria-label="Back to main website">Home</a>
  <a href="/{config.OUT_DIR}/" class="icon-btn" aria-label="Go to Bible index">Bibles</a>
  <span class="logo">Bible Study with Steffi</span>
  <span class="crumb">{crumb}</span>
  <button type="button" id="font-dec-btn" class="icon-btn" aria-label="Decrease verse font size">A-</button>
  <button type="button" id="font-inc-btn" class="icon-btn" aria-label="Increase verse font size">A+</button>
{parallel_link_html}{verse_toggle}  <button type="button" id="theme-btn" class="icon-btn" aria-label="Reading theme and colors">Aa</button>
</header>"""


def theme_sheet():
    return """
<div id="tsheet">
  <h3>Choose Theme</h3>
  <div class="t-swatches"></div>
</div>"""


def app_cta_banner():
    return f"""
<div class="app-cta">
  <div>
    <strong>Bible Study with Steffi App</strong>
    <p>Memorize verses with spaced repetition. Free, no ads, 15+ languages.</p>
  </div>
  <a class="cta-btn" href="{PLAY_STORE_URL}" target="_blank" rel="noopener">Download Free ↗</a>
</div>"""


# ─── CHAPTER PAGE GENERATOR ───────────────────────────────────────────────────

def generate_chapter_page(bible_data, version_id, vlabel, lang_code,
                           book, chapter, all_books,
                           prev_url, next_url,
                           active_versions, x_default_id):
    book_name_source = book["n"]
    book_name = display_book_name(book, version_id)
    book_num    = book["b"]
    ch_num      = chapter["c"]
    bslug       = book_slug(book_name_source)
    canonical   = f"{SITE_URL}/{config.OUT_DIR}/{version_id}/{bslug}/{ch_num}/"
    verses      = chapter["v"]

    # hreflang — only URLs we actually build (active_versions) + x-default
    hreflang_parts = []
    for vid, vlab, vlng, *_ in active_versions:
        url = f"{SITE_URL}/{config.OUT_DIR}/{vid}/{bslug}/{ch_num}/"
        hreflang_parts.append(f'<link rel="alternate" hreflang="{HREFLANG.get(vid, vlng)}" href="{url}"/>')
    hreflang_parts.append(
        f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/{config.OUT_DIR}/{x_default_id}/{bslug}/{ch_num}/"/>'
    )
    hreflang_str = "\n".join(hreflang_parts)

    # SEO title and description
    title       = f"{book_name} {ch_num} — {vlabel} | Bible Study with Steffi"
    # First verse preview for description (lowest verse number with text)
    first_verse = first_verse_preview(verses, 120)
    if first_verse:
        description = f"Read {book_name} chapter {ch_num} in {vlabel}. \"{first_verse}…\" — Bible Study with Steffi."
    else:
        description = f"Read {book_name} chapter {ch_num} in {vlabel} — Bible Study with Steffi."
    keywords    = f"{book_name} {ch_num}, {vlabel}, {book_name} chapter {ch_num} {vlabel}, bible online free, bswsapp"

    # Build verse rows
    verse_rows = ""
    for vnum, text in sorted(verses.items(), key=lambda x: int(x[0])):
        ref = f"{book_name} {ch_num}:{vnum} ({vlabel})"
        safe_ref = ref.replace('"', "&quot;")
        safe_text = str(text).replace("<", "&lt;").replace(">", "&gt;")
        verse_url = verse_detail_rel_url(version_id, bslug, ch_num, vnum)
        verse_rows += f'<a class="v-row" href="{verse_url}" data-ref="{safe_ref}" data-verse-url="{verse_url}"><span class="v-num">{vnum}</span><span class="v-txt">{safe_text}</span></a>\n'

    # Prev / next nav
    prev_link = f'<a href="{prev_url}">← Previous</a>' if prev_url else '<a class="disabled">← Previous</a>'
    next_link = f'<a href="{next_url}">Next →</a>' if next_url else '<a class="disabled">Next →</a>'

    head = html_head(title, description, canonical, lang_code, hreflang_str, keywords)

    active_ids = {v[0] for v in active_versions}
    ds = default_parallel_secondary(version_id, active_ids)
    parallel_href = f"/{config.OUT_DIR}/parallel/{version_id}/{ds}/{bslug}/{ch_num}/" if ds else ""
    parallel_link_html = (
        f'  <a id="par-link" class="icon-btn" href="{parallel_href}" aria-label="Open parallel two-column view">||</a>\n'
        if parallel_href
        else ""
    )
    parallel_jump = build_parallel_jump_block(version_id, bslug, ch_num, active_versions)
    nav_bootstrap = (
        "<script>"
        f"window.__BSWS_OUT_DIR__={json.dumps(str(config.OUT_DIR))};"
        f"window.__BSWS_VERSION_ID__={json.dumps(version_id)};"
        f"window.__BSWS_BOOK_NUM__={book_num};"
        f"window.__BSWS_CH__={ch_num};"
        f"window.__BSWS_SHARE_BOOK__={json.dumps(book_name, ensure_ascii=False)};"
        f"window.__BSWS_VLABEL__={json.dumps(vlabel, ensure_ascii=False)};"
        "</script>"
    )
    nav_script = f'<script src="{output_nav_asset_href(version_id)}" defer></script>'

    return f"""{head}
<body>
{topbar_html(f"{book_name} {ch_num} · {vlabel}", parallel_link_html=parallel_link_html)}
{sidebar_html(all_books, book_num, ch_num, version_id, vlabel, active_versions, parallel_jump_html=parallel_jump)}
<div id="wrap">
  <main id="reader">
    <div class="ch-head">
      <h1>{book_name}</h1>
      <h2>Chapter {ch_num}</h2>
      <span class="version-tag">{vlabel}</span>
    </div>
    {verse_rows}
    {app_cta_banner()}
    <nav class="ch-nav">{prev_link}{next_link}</nav>
  </main>
</div>
{chapter_verse_action_bar_html()}
{theme_sheet()}
{nav_bootstrap}
{nav_script}
<script src="{output_asset_href(ASSET_READER_JS_PATH)}" defer></script>
</body>
</html>"""


def get_chapter_verses(bible: dict, book_num: int, ch_num: int) -> dict:
    for bk in bible.get("books", []):
        if bk.get("b") != book_num:
            continue
        for ch in bk.get("ch", []):
            if ch.get("c") == ch_num:
                return ch.get("v") or {}
    return {}


def sidebar_parallel_html(
    all_books,
    current_book_num,
    current_ch,
    vp,
    vs,
    active_versions,
):
    """Navigation sidebar for parallel reader: URLs stay under /bible/parallel/{vp}/{vs}/…"""
    current_book = next((b for b in all_books if b["b"] == current_book_num), None)
    cur_slug = book_slug(current_book["n"]) if current_book else "genesis"

    pref = f"/{config.OUT_DIR}/parallel/{vp}/{vs}"
    books_html = ""
    par_sections = nav_section_headers(vp)
    section_starts = {s[0] for s in par_sections}
    section_label = dict(par_sections)
    for bk in all_books:
        if bk["b"] in section_starts:
            books_html += f'<div class="s-section">{html.escape(section_label[bk["b"]])}</div>'
        slug = book_slug(bk["n"])
        active = "on" if bk["b"] == current_book_num else ""
        url = f"{pref}/{slug}/1/"
        books_html += f'<a href="{url}" class="book-btn {active}">{display_book_name(bk, vp)}</a>'

    ch_html = ""
    if current_book:
        slug = book_slug(current_book["n"])
        for c in range(1, len(current_book["ch"]) + 1):
            active = "on" if c == current_ch else ""
            url = f"{pref}/{slug}/{c}/"
            ch_html += f'<a href="{url}" class="ch-btn {active}">{c}</a>'

    pri_opts = "".join(
        f'<option value="{html.escape(vid)}"{" selected" if vid == vp else ""}>{html.escape(vlbl)}</option>'
        for vid, vlbl, *_ in active_versions
    )
    sec_opts = "".join(
        f'<option value="{html.escape(vid)}"{" selected" if vid == vs else ""}>{html.escape(vlbl)}</option>'
        for vid, vlbl, *_ in active_versions
    )

    return f"""
<aside id="sidebar">
  <div class="s-section">Parallel columns</div>
  <label class="s-section" for="par-pri" style="padding-top:8px">Left column</label>
  <select id="par-pri" class="s-ver" aria-label="Primary translation" onchange="var p=this.value;var s=document.getElementById('par-sec').value;if(p===s)return;window.location='/{config.OUT_DIR}/parallel/'+p+'/'+s+'/{cur_slug}/{current_ch}/';">{pri_opts}</select>
  <label class="s-section" for="par-sec" style="padding-top:8px">Right column</label>
  <select id="par-sec" class="s-ver" aria-label="Secondary translation" onchange="try{{localStorage.setItem('bsws_parallel_secondary',this.value);}}catch(e){{}}var p=document.getElementById('par-pri').value;var s=this.value;if(p===s)return;window.location='/{config.OUT_DIR}/parallel/'+p+'/'+s+'/{cur_slug}/{current_ch}/';">{sec_opts}</select>
  <input id="s-search" type="search" placeholder="Search this chapter (left column)…" autocomplete="off"/>
  <div id="sr"></div>
  {'<div class="s-section">Chapters</div><div id="ch-grid">' + ch_html + '</div>' if ch_html else ''}
  <div class="s-section">Books</div>
  {books_html}
</aside>
<div id="overlay"></div>"""
