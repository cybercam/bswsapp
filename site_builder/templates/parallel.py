"""Parallel chapter pages."""
import html
from typing import Optional

from .. import config
from ..config import ASSET_READER_JS_PATH, HREFLANG, SITE_URL
from ..helpers import (
    book_slug,
    display_book_name,
    first_verse_preview,
    script_font_link_for_lang,
    verse_detail_rel_url,
    verse_get,
    version_lang,
)
from ..layout import (
    app_cta_banner,
    html_head,
    output_asset_href,
    sidebar_parallel_html,
    theme_sheet,
    topbar_html,
)

def get_chapter_verses(bible: dict, book_num: int, ch_num: int) -> dict:
    for bk in bible.get("books", []):
        if bk.get("b") != book_num:
            continue
        for ch in bk.get("ch", []):
            if ch.get("c") == ch_num:
                return ch.get("v") or {}
    return {}

def generate_parallel_chapter_page(
    bible_p: dict,
    bible_s: dict,
    vp: str,
    vs: str,
    vlabel_p: str,
    vlabel_s: str,
    lang_p: str,
    book_p: dict,
    chapter_p: dict,
    all_books,
    prev_url: Optional[str],
    next_url: Optional[str],
    active_versions,
    x_default_id: str,
):
    book_name_p = display_book_name(book_p, vp)
    book_name_s = display_book_name(book_p, vs)
    book_num = book_p["b"]
    ch_num = chapter_p["c"]
    bslug = book_slug(book_p["n"])
    verses_p = chapter_p.get("v") or {}
    verses_s = get_chapter_verses(bible_s, book_num, ch_num)

    canonical_primary = f"{SITE_URL}/{config.OUT_DIR}/{vp}/{bslug}/{ch_num}/"
    title = f"{book_name_p} {ch_num} — {vlabel_p} / {vlabel_s} (parallel) | Bible Study with Steffi"
    prev1 = first_verse_preview(verses_p, 80)
    prev2 = first_verse_preview(verses_s, 80)
    description = (
        f"Parallel Bible: {book_name_p} chapter {ch_num} — {vlabel_p} and {vlabel_s}. "
        f'"{prev1[:60]}…" / "{prev2[:60]}…" — Bible Study with Steffi.'
        if prev1 and prev2
        else f"Parallel Bible: {book_name_p} chapter {ch_num} in {vlabel_p} and {vlabel_s} — Bible Study with Steffi."
    )
    keywords = f"{book_name_p} {ch_num}, parallel bible, {vlabel_p}, {vlabel_s}, bswsapp"

    robots = '<meta name="robots" content="noindex,follow"/>'
    extra_font = (
        script_font_link_for_lang(version_lang(vs))
        if version_lang(vs) != lang_p
        else ""
    )
    head = html_head(
        title,
        description,
        canonical_primary,
        lang_p,
        "",
        keywords,
        robots_meta=robots,
        extra_head=extra_font,
    )

    def _vkeys(d):
        o = set()
        for x in d.keys():
            try:
                o.add(int(x))
            except (TypeError, ValueError):
                continue
        return o

    nums = sorted(_vkeys(verses_p) | _vkeys(verses_s))
    par_rows = ""
    for vn in nums:
        tp = verse_get(verses_p, vn)
        ts = verse_get(verses_s, vn)
        safe_tp = html.escape(tp, quote=False)
        safe_ts = html.escape(ts, quote=False)
        ref_p = f"{book_name_p} {ch_num}:{vn} ({vlabel_p})".replace('"', "&quot;")
        ref_s = f"{book_name_s} {ch_num}:{vn} ({vlabel_s})".replace('"', "&quot;")
        url_p = verse_detail_rel_url(vp, bslug, ch_num, vn)
        url_s = verse_detail_rel_url(vs, bslug, ch_num, vn)
        par_rows += f"""<div class="par-row">
  <div class="par-cell">
    <a class="v-row v-pr" href="{url_p}" data-ref="{ref_p}" data-verse-url="{url_p}"><span class="v-num">{vn}</span><span class="v-txt">{safe_tp or "—"}</span></a>
  </div>
  <div class="par-cell">
    <a class="v-row v-sc" href="{url_s}" data-ref="{ref_s}" data-verse-url="{url_s}"><span class="v-num">{vn}</span><span class="v-txt">{safe_ts or "—"}</span></a>
  </div>
</div>
"""

    prev_link = f'<a href="{prev_url}">← Previous</a>' if prev_url else '<a class="disabled">← Previous</a>'
    next_link = f'<a href="{next_url}">Next →</a>' if next_url else '<a class="disabled">Next →</a>'
    single_url = f"/{config.OUT_DIR}/{vp}/{bslug}/{ch_num}/"
    exit_parallel = f'  <a class="icon-btn" href="{single_url}" aria-label="Single-column reader (left translation only)">Single</a>\n'

    font_s = script_font_link_for_lang(version_lang(vs)) if version_lang(vs) != lang_p else ""
    # Inject secondary script font if different from primary (extra link before closing head — already closed in html_head)
    # Fonts for secondary are loaded via :lang on body is single; use second link in head by extending html_head — skip for simplicity (Noto stacks in CSS cover many cases)

    crumb = f"{book_name_p} {ch_num} · {vlabel_p} ∥ {vlabel_s}"
    return f"""{head}
<body>
{topbar_html(crumb, parallel_link_html=exit_parallel, show_verse_links_toggle=True)}
{sidebar_parallel_html(all_books, book_num, ch_num, vp, vs, active_versions)}
<div id="wrap">
  <main id="reader" class="parallel-reader">
    <div class="ch-head">
      <h1>{html.escape(book_name_p)}</h1>
      <h2>Chapter {ch_num} · Parallel</h2>
      <span class="version-tag">{html.escape(vlabel_p)} · {html.escape(vlabel_s)}</span>
    </div>
    <div class="par-rows" aria-label="Verse-by-verse parallel columns">
      <div class="par-row par-skip-row" aria-hidden="true">
        <div class="par-cell"><div class="par-col-label">{html.escape(vlabel_p)}</div></div>
        <div class="par-cell"><div class="par-col-label">{html.escape(vlabel_s)}</div></div>
      </div>
{par_rows}
    </div>
    {app_cta_banner()}
    <nav class="ch-nav">{prev_link}{next_link}</nav>
  </main>
</div>
{theme_sheet()}
<script src="{output_asset_href(ASSET_READER_JS_PATH)}" defer></script>
</body>
</html>"""
