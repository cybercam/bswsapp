"""Verse detail pages."""
import html

from .. import config
from ..config import (
    ASSET_INTERLINEAR_CSS_PATH,
    ASSET_READER_JS_PATH,
    ASSET_STRONGS_JS_PATH,
    HREFLANG,
    SITE_URL,
    version_has_verse_detail_features,
)
from ..helpers import verse_detail_rel_url
from ..layout import app_cta_banner, html_head, output_asset_href, theme_sheet, topbar_html


def generate_verse_detail_page(
    version_id,
    vlabel,
    lang_code,
    book_name,
    book_name_source,
    bslug,
    ch_num,
    vnum,
    verse_text,
    prev_verse_url,
    next_verse_url,
    chapter_url,
    active_versions,
    x_default_id,
    verse_lookup,
    crossrefs_data,
    strongs_dict,
    interlinear_chapters,
    english_verse_text: str = "",
    english_source_label: str = "",
):
    has_verse_features = version_has_verse_detail_features(version_id)
    canonical = f"{SITE_URL}/{config.OUT_DIR}/{version_id}/{bslug}/{ch_num}/{vnum}/"
    ref_short = f"{book_name} {ch_num}:{vnum}"
    title = (
        f"{ref_short} — {vlabel} | Bible verse online | Bible Study with Steffi"
    )
    snippet = str(verse_text).replace('"', "'").strip()[:140]
    if snippet:
        description = (
            f"Read {ref_short} in {vlabel}. “{snippet}…” "
            "Open the full chapter, parallel English, and cross references."
        )
    else:
        description = (
            f"Read {ref_short} in {vlabel} — verse detail with chapter link and reader tools."
        )
    keywords = (
        f"{book_name} {ch_num}:{vnum} telugu, {book_name} {ch_num}:{vnum} {vlabel}, "
        f"{book_name_source} {ch_num}:{vnum}, bible verse online, bswsapp"
    )

    hreflang_parts = []
    for vid, vlab, vlng, *_ in active_versions:
        url = f"{SITE_URL}/{config.OUT_DIR}/{vid}/{bslug}/{ch_num}/{vnum}/"
        hreflang_parts.append(f'<link rel="alternate" hreflang="{HREFLANG.get(vid, vlng)}" href="{url}"/>')
    hreflang_parts.append(
        f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/{config.OUT_DIR}/{x_default_id}/{bslug}/{ch_num}/{vnum}/"/>'
    )
    hreflang_str = "\n".join(hreflang_parts)

    safe_verse = html.escape(str(verse_text))
    crumb = f"{book_name} {ch_num}:{vnum} · {vlabel}"
    prev_link = (
        f'<a href="{prev_verse_url}" rel="prev">← Previous Verse</a>'
        if prev_verse_url
        else '<a class="disabled">← Previous Verse</a>'
    )
    next_link = (
        f'<a href="{next_verse_url}" rel="next">Next Verse →</a>'
        if next_verse_url
        else '<a class="disabled">Next Verse →</a>'
    )

    # Cross references use canonical book_chapter_verse keys from the source app.
    # Determine book number from lookup by current verse to avoid depending on display strings.
    current_lookup = None
    for k, info in verse_lookup.items():
        if (
            info.get("book_slug") == bslug
            and int(info.get("chapter_num", -1)) == int(ch_num)
            and int(info.get("verse_num", -1)) == int(vnum)
        ):
            current_lookup = info
            break
    bnum = current_lookup.get("book_num") if current_lookup else None
    xref_key = f"{bnum}_{ch_num}_{vnum}" if bnum is not None else ""
    xrefs = crossrefs_data.get(xref_key, []) if (xref_key and has_verse_features) else []
    xref_items = []
    for ref in xrefs[:16]:
        info = verse_lookup.get(ref)
        if not info:
            continue
        ref_url = verse_detail_rel_url(version_id, info["book_slug"], info["chapter_num"], info["verse_num"])
        xref_items.append(
            f'<div class="xref-item"><a href="{ref_url}">{info["book_name"]} {info["chapter_num"]}:{info["verse_num"]}</a><p class="x-txt">{html.escape(str(info["text"]))}</p></div>'
        )
    xref_html = (
        '<div class="detail-panel"><h3>Cross References</h3><div class="xref-list">' + "".join(xref_items) + "</div></div>"
        if xref_items
        else '<div class="detail-panel"><h3>Cross References</h3><p class="verse-detail-meta">No cross references available for this verse yet.</p></div>'
    )

    inter_tokens = []
    chapter_tokens = interlinear_chapters.get(str(ch_num), {}) if (has_verse_features and isinstance(interlinear_chapters, dict)) else {}
    raw_tokens = chapter_tokens.get(str(vnum), []) if isinstance(chapter_tokens, dict) else []
    if isinstance(raw_tokens, list):
        inter_tokens = raw_tokens
    inter_parts = []
    for tok in inter_tokens[:80]:
        strong = str(tok.get("s", "")).strip()
        btn = (
            f'<button class="inter-token" type="button" data-strong="{html.escape(strong)}" '
            ">"
            f'<span class="w">{html.escape(str(tok.get("w","")))}</span>'
            f'<span class="g">{html.escape(str(tok.get("t","")))}</span>'
            f'<span class="s">{html.escape(strong)}</span>'
            "</button>"
        )
        inter_parts.append(btn)
    interlinear_html = (
        '<div class="detail-panel"><h3>Interlinear</h3><div class="interlinear-verse">' + "".join(inter_parts) + "</div></div>"
        if inter_parts
        else '<div class="detail-panel"><h3>Interlinear</h3><p class="verse-detail-meta">Interlinear data not available for this verse.</p></div>'
    )

    interlinear_head = (
        f'<link rel="stylesheet" href="{output_asset_href(ASSET_INTERLINEAR_CSS_PATH)}"/>'
        if has_verse_features
        else ""
    )

    en_clean = (english_verse_text or "").strip()
    en_block = ""
    if en_clean and english_source_label:
        en_block = (
            f'<section class="english-parallel-block detail-panel" lang="en">'
            f"<h3>{html.escape(english_source_label)}</h3>"
            f'<p class="verse-detail-text verse-detail-text--secondary">{html.escape(en_clean)}</p>'
            "</section>"
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
                        "item": f"{SITE_URL}/{config.OUT_DIR}/{version_id}/{bslug}/{ch_num}/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 5,
                        "name": f"{ref_short}",
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
        title,
        description,
        canonical,
        lang_code,
        hreflang_str,
        keywords,
        extra_head=interlinear_head,
        structured_data=structured_data,
    )
    strongs_script = (
        f'<script src="{output_asset_href(ASSET_STRONGS_JS_PATH)}" defer></script>'
        if has_verse_features
        else ""
    )
    lex_drawer = (
        """<div id="lex-drawer" aria-live="polite">
  <button type="button" id="lex-close-btn" class="icon-btn close" aria-label="Close word study">Close</button>
  <h4 id="lex-strong"></h4>
  <p id="lex-lemma"></p>
  <p id="lex-def"></p>
  <p id="lex-kjv"></p>
  <p id="lex-deriv"></p>
</div>"""
        if has_verse_features
        else ""
    )
    return f"""{head}
<body>
{topbar_html(crumb)}
<div id="wrap">
  <main id="reader">
    <div class="ch-head">
      <h1>{book_name}</h1>
      <h2>Chapter {ch_num} · Verse {vnum}</h2>
      <span class="version-tag">{vlabel}</span>
    </div>
    <article class="verse-detail-card">
      <p class="verse-detail-ref">{ref_short}</p>
      <p class="verse-detail-text">{safe_verse}</p>
      <p class="verse-detail-meta">Book: {book_name_source} · Chapter: {ch_num} · Verse: {vnum}</p>
      <div class="verse-detail-links">
        <a href="{chapter_url}">Open Full Chapter</a>
      </div>
    </article>
    {en_block}
    <section class="detail-grid">
      {xref_html}
      {interlinear_html}
    </section>
    <nav class="ch-nav">{prev_link}{next_link}</nav>
    {app_cta_banner()}
  </main>
</div>
{lex_drawer}
{theme_sheet()}
{strongs_script}
<script src="{output_asset_href(ASSET_READER_JS_PATH)}" defer></script>
</body>
</html>"""
