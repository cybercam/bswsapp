"""Chapter pages."""
import html
import json

from .. import config
from ..config import ASSET_READER_JS_PATH, HREFLANG, OG_LOCALE, SITE_URL, VERSION_ATTRIBUTION_HTML
from .. import seo_content
from ..helpers import (
    book_slug,
    chapter_reading_stats,
    chapter_verse_action_bar_html,
    default_parallel_secondary,
    display_book_name,
    first_verse_preview,
    verse_detail_rel_url,
)
from ..layout import (
    app_cta_banner,
    build_parallel_jump_block,
    html_head,
    output_asset_href,
    output_nav_asset_href,
    sidebar_html,
    theme_sheet,
    topbar_html,
)

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
    verse_count, read_mins = chapter_reading_stats(verses)
    notable_nums = seo_content.chapter_notable_verses(version_id, bslug, ch_num)
    faq_items = seo_content.chapter_faq_items(version_id, bslug, ch_num)
    attr_html = VERSION_ATTRIBUTION_HTML.get(
        version_id, VERSION_ATTRIBUTION_HTML["_default"]
    )

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
    first_verse = first_verse_preview(verses, 155)
    if first_verse:
        description = (
            f"{book_name} {ch_num} — {vlabel}: {first_verse}… "
            "Read free at Bible Study with Steffi."
        )
    else:
        description = f"Read {book_name} chapter {ch_num} in {vlabel} — Bible Study with Steffi."
    keywords    = f"{book_name} {ch_num}, {vlabel}, {book_name} chapter {ch_num} {vlabel}, bible online free, bswsapp"

    notable_links = ""
    if notable_nums:
        links = []
        verse_key_set = {str(k) for k in verses.keys()}
        for vn in notable_nums:
            if str(vn) not in verse_key_set:
                continue
            vu = verse_detail_rel_url(version_id, bslug, ch_num, vn)
            links.append(f'<a href="{vu}">{book_name} {ch_num}:{vn}</a>')
        if links:
            joined = " · ".join(links)
            notable_links = (
                '<section class="chapter-related detail-panel" aria-label="Notable verses in this chapter">'
                "<h3>Continue studying</h3><p class=\"verse-detail-meta\">Popular verses in this chapter:</p>"
                f'<p class="verse-detail-links">{joined}</p></section>'
            )

    faq_block = ""
    if faq_items:
        rows = []
        for q, a in faq_items:
            rows.append(
                f"<details class=\"faq-item\"><summary>{html.escape(q)}</summary>"
                f"<p>{html.escape(a)}</p></details>"
            )
        faq_block = (
            '<section class="faq-block detail-panel" aria-label="Chapter questions">'
            "<h3>Common questions</h3>" + "".join(rows) + "</section>"
        )

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

    head_links = "\n".join(
        link
        for link in (
            f'<link rel="prev" href="{SITE_URL}{prev_url}"/>' if prev_url else "",
            f'<link rel="next" href="{SITE_URL}{next_url}"/>' if next_url else "",
        )
        if link
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
                        "item": f"{SITE_URL}/{config.OUT_DIR}/{version_id}/{bslug}/1/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 4,
                        "name": f"{book_name} {ch_num}",
                        "item": canonical,
                    },
                ],
            },
            {
                "@type": "Article",
                "headline": f"{book_name} {ch_num} — {vlabel}",
                "url": canonical,
                "inLanguage": lang_code,
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
        head_links=head_links,
        og_type="article",
        og_locale=OG_LOCALE.get(version_id, ""),
        structured_data=structured_data,
    )

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
      <p class="chapter-meta-line verse-detail-meta">{verse_count} verses · about {read_mins} min read</p>
      <span class="version-tag">{vlabel}</span>
    </div>
    {verse_rows}
    {notable_links}
    {faq_block}
    {app_cta_banner()}
    <footer class="chapter-attribution detail-panel" role="note">
      <h3>Source note</h3>
      <p class="verse-detail-meta">{attr_html}</p>
    </footer>
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
