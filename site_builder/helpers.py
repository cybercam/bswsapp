"""Pure helpers (no layout shell)."""
from typing import Optional

from . import config
from .config import (
    BOOK_SLUGS,
    HREFLANG,
    INDIC_LANG_SCRIPT_FONT,
    PARALLEL_LINK_MODE,
    TELUGU_BOOK_NAMES,
    VERSIONS,
)

def script_font_link_for_lang(lang: str) -> str:
    spec = INDIC_LANG_SCRIPT_FONT.get(lang)
    if not spec:
        return ""
    slug, _fam = spec
    return (
        f'<link href="https://fonts.googleapis.com/css2?family={slug}:wght@400;500;600;700&display=swap" '
        'rel="stylesheet"/>\n'
    )


def indic_script_face_css() -> str:
    """:lang(...) rules so verse text uses a readable Noto stack for each Indian site language."""
    lines = []
    for lang, (_slug, family) in INDIC_LANG_SCRIPT_FONT.items():
        sel = (
            f":lang({lang}) body,:lang({lang}) .v-txt,:lang({lang}) .verse-detail-text,"
            f":lang({lang}) .book-btn,:lang({lang}) #s-search,:lang({lang}) .sr-txt"
        )
        lines.append(f"{sel}{{font-family:'{family}','Lora',Georgia,serif}}")
    return "\n".join(lines)

def book_slug(book_name):
    return BOOK_SLUGS.get(
        book_name,
        book_name.lower().replace(" ", "-").replace("'", ""),
    )


def first_verse_preview(verses, max_len=120):
    """First verse text by numeric order for meta description (handles int/str keys)."""
    if not verses:
        return ""
    try:
        items = sorted(verses.items(), key=lambda x: int(x[0]))
    except (ValueError, TypeError):
        return ""
    if not items:
        return ""
    text = str(items[0][1] or "").strip().replace('"', "'")
    return text[:max_len] if text else ""


def verse_detail_rel_url(version_id, bslug, ch_num, v_num):
    return f"/{config.OUT_DIR}/{version_id}/{bslug}/{ch_num}/{v_num}/"


def version_label(version_id):
    for vid, label, *_ in VERSIONS:
        if vid == version_id:
            return label
    return version_id.upper()


def version_group(version_id: str) -> str:
    for vid, _label, _lng, _script, group in VERSIONS:
        if vid == version_id:
            return group
    return "English"


def version_lang(version_id: str) -> str:
    for vid, _label, lng, *_rest in VERSIONS:
        if vid == version_id:
            return lng
    return "en"


def iter_parallel_version_pairs(active_versions, x_default_id: str):
    """Ordered (primary, secondary) chapter pairs to pre-generate under bible/parallel/."""
    ids = [v[0] for v in active_versions]
    if len(ids) < 2:
        return
    if PARALLEL_LINK_MODE == "all":
        for va in ids:
            for vb in ids:
                if va != vb:
                    yield va, vb
        return
    hub = "web" if "web" in ids else (x_default_id if x_default_id in ids else ids[0])
    for v in ids:
        if v == hub:
            continue
        yield v, hub
        yield hub, v


def default_parallel_secondary(primary_id: str, active_ids: set) -> Optional[str]:
    """Default right-column version for the || link from a single-version chapter page."""
    if len(active_ids) < 2:
        return None
    if primary_id not in active_ids:
        return None
    if version_group(primary_id) == "Indian":
        if "web" in active_ids:
            return "web"
        for vid in active_ids:
            if vid != primary_id:
                return vid
        return None
    for vid, _l, _lc, _s, g in VERSIONS:
        if vid in active_ids and vid != primary_id and g == "Indian":
            return vid
    if "kjv" in active_ids and primary_id != "kjv":
        return "kjv"
    if "web" in active_ids and primary_id != "web":
        return "web"
    for vid in active_ids:
        if vid != primary_id:
            return vid
    return None


def chapter_reading_stats(verses: dict) -> tuple[int, int]:
    """Return (verse_count, estimated_reading_minutes) using a conservative character heuristic."""
    if not verses:
        return 0, 0
    count = len(verses)
    chars = sum(len(str(t or "")) for t in verses.values())
    # ~6 characters per word, ~160 words/min for on-screen devotional reading.
    minutes = max(1, round(chars / (6 * 160)))
    return count, minutes


def verse_get(verses: dict, vnum: int) -> str:
    s = str(vnum)
    if s in verses:
        return str(verses[s] or "")
    if vnum in verses:
        return str(verses[vnum] or "")
    return ""


def display_book_name(book: dict, version_id: str) -> str:
    """Render Telugu names for Telugu version, fallback to source JSON name."""
    if version_id == "telugu":
        return TELUGU_BOOK_NAMES.get(book.get("b"), book.get("n", ""))
    return book.get("n", "")


def nav_section_headers(version_id: str) -> list[tuple[int, str]]:
    """(first_book_number, sidebar_label) in ascending order — Telugu gets finer OT/NT grouping."""
    if version_id == "telugu":
        return [
            (1, "ధర్మశాస్త్రము"),
            (6, "చరిత్ర గ్రంథములు"),
            (18, "కీర్తనా గ్రంథములు"),
            (23, "ప్రధాన ప్రవచన గ్రంథములు"),
            (28, "అల్ప ప్రవచన గ్రంథములు"),
            (40, "సువార్తలు"),
            (44, "సంఘ చరిత్ర"),
            (45, "పౌలు రాసిన పత్రికలు"),
            (58, "సాధారణ పత్రికలు"),
            (66, "ప్రవచన గ్రంథము"),
        ]
    return [(1, "Old Testament"), (40, "New Testament")]


def chapter_verse_action_bar_html() -> str:
    """Fixed bottom bar for verse copy/share/TTS; primary row stays compact, rest in expandable panel."""
    return """
<div id="vbar" role="toolbar" aria-label="Selected verses">
  <div id="vbar-meta" class="vbar-meta">0 verses selected</div>
  <div class="vbar-row vbar-row--primary">
    <button type="button" id="copy-btn">Copy</button>
    <button type="button" id="share-btn">Share</button>
    <button type="button" id="clear-sel-btn">Clear</button>
    <button type="button" id="vbar-more-btn" class="vbar-more" aria-expanded="false" aria-controls="vbar-advanced">More</button>
    <button type="button" id="vbar-close-btn" aria-label="Hide verse toolbar">Hide</button>
  </div>
  <div id="vbar-advanced" class="vbar-advanced">
    <button type="button" id="tts-play-btn">Read selection</button>
    <button type="button" id="tts-chapter-btn">Read chapter</button>
    <button type="button" id="tts-stop-btn">Stop</button>
    <button type="button" id="tts-loop-btn">Loop Off</button>
    <button type="button" id="tts-auto-btn">Auto-Read Off</button>
    <button type="button" id="tts-download-btn">Download text</button>
    <div class="vbar-speed"><label for="tts-rate">Speed</label><input type="range" id="tts-rate" min="0.7" max="1.5" step="0.05" value="1"/></div>
    <button type="button" id="font-dec-vbar-btn" aria-label="Decrease verse font size">A−</button>
    <button type="button" id="font-inc-vbar-btn" aria-label="Increase verse font size">A+</button>
  </div>
</div>"""
