#!/usr/bin/env python3
"""
BSWS Phase 3 — Static Bible Site Generator
============================================
Downloads all 15 Bible JSONs from cybercam/bibles_json on GitHub,
then generates one HTML file per chapter for every version.

Run this from the ROOT of your cybercam/bswsapp repo:
  python3 generate_bible_site.py
  python3 generate_bible_site.py --only telugu   # one (or few) versions; avoids huge disk spikes

Then:
  git add .
  git commit -m "Phase 3: static Bible pages"
  git push

Output:
  bible/index.html              ← landing page with version/language grid
  bible/sitemap.xml             ← chapter + verse detail URLs for Google
  bible/<version>/<book>/<ch>/index.html           ← one page per chapter
  bible/<version>/<book>/<ch>/<verse>/index.html   ← one page per verse
  bible/parallel/<v1>/<v2>/<book>/<ch>/index.html  ← two-column parallel (see PARALLEL_LINK_MODE)
"""

import argparse
import hashlib
import html
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from typing import Optional

# ─── CONFIG ───────────────────────────────────────────────────────────────────

SITE_URL   = "https://bswsapp.com"
OUT_DIR    = Path("bible")           # output folder inside bswsapp repo
CACHE_DIR  = Path(".bible_cache")   # local JSON cache so you don't re-download
TODAY      = date.today().isoformat()

# Must exist in VERSIONS — used for x-default hreflang, hero CTA, and JSON-LD SearchAction.
DEFAULT_VERSION_ID = "kjv"

# Parallel reader: /bible/parallel/{primary}/{secondary}/{book}/{ch}/
# "web_hub" — (v, web) and (web, v) for each non-web v in the active build (manageable file count).
# "all" — every ordered pair primary != secondary among active versions (very large for full 15-version builds).
PARALLEL_LINK_MODE = "web_hub"

DOWNLOAD_ATTEMPTS = 3
RETRY_DELAY_SEC   = 1.0

CDN_BASE       = "https://cdn.jsdelivr.net/gh/cybercam/bibles_json@main"
GITHUB_RAW     = "https://raw.githubusercontent.com/cybercam/bibles_json/main"
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.biblestudywithsteffi.app"
ASSET_STYLE_PATH = "assets/style.css"
ASSET_READER_JS_PATH = "assets/reader.js"
ASSET_INTERLINEAR_CSS_PATH = "assets/interlinear.css"
ASSET_STRONGS_JS_PATH = "assets/strongs.js"
LOCAL_BIBLE_DATA_DIR = Path("/Users/ajaykumarm/Desktop/files/BibleStudyWithSteffi/src/data")
INTERLINEAR_RAW_BASE = "https://raw.githubusercontent.com/cybercam/interlinear/main"
INTERLINEAR_CACHE_DIR = Path(".interlinear_cache")
LOCAL_CROSSREFS_JSON = Path("/Users/ajaykumarm/Desktop/files/BibleStudyWithSteffi/src/data/crossrefs_mobile.json")
LOCAL_STRONGS_JSON = Path("/Users/ajaykumarm/Desktop/files/BibleStudyWithSteffi/src/data/strongs/dictionary.json")
OTHER_LANGUAGE_PAGES = [
    ("telugu-bible.html", "Telugu Bible"),
    ("english-bible.html", "English Bible"),
    ("hindi-bible.html", "Hindi Bible"),
    ("tamil-bible.html", "Tamil Bible"),
    ("kannada-bible.html", "Kannada Bible"),
    ("malayalam-bible.html", "Malayalam Bible"),
    ("bengali-bible.html", "Bengali Bible"),
    ("odia-bible.html", "Odia Bible"),
    ("marathi-bible.html", "Marathi Bible"),
    ("gujarati-bible.html", "Gujarati Bible"),
    ("punjabi-bible.html", "Punjabi Bible"),
    ("urdu-bible.html", "Urdu Bible"),
    ("assamese-bible.html", "Assamese Bible"),
]

# All versions shipped on the site (build incrementally with --only when disk is tight)
VERSIONS = [
    # id,          label,                      lang,  script,   group
    ("bbe",        "Bible in Basic English",   "en",  "latin",  "English"),
    ("kjv",        "King James Version",       "en",  "latin",  "English"),
    ("nkjv",       "New King James Version",   "en",  "latin",  "English"),
    ("web",        "World English Bible",      "en",  "latin",  "English"),
    ("ylt",        "Young's Literal Translation","en","latin",  "English"),
    ("bengali",    "বাংলা বাইবেল",              "bn",  "bengali","Indian"),
    ("gujarati",   "ગુજરાતી બાઇબલ",             "gu",  "latin",  "Indian"),
    ("hindi",      "हिन्दी बाइबिल",              "hi",  "devanagari","Indian"),
    ("kannada",    "ಕನ್ನಡ ಬೈಬಲ್",               "kn",  "latin",  "Indian"),
    ("malayalam",  "മലയാളം ബൈബിൾ",             "ml",  "latin",  "Indian"),
    ("marathi",    "मराठी बायबल",               "mr",  "devanagari","Indian"),
    ("nepali",     "नेपाली बाइबल",              "ne",  "devanagari","Indian"),
    ("odia",       "ଓଡ଼ିଆ ବାଇବେଲ",              "or",  "latin",  "Indian"),
    ("tamil",      "தமிழ் பரிசுத்த வேதாகமம்",  "ta",  "latin",  "Indian"),
    ("telugu",     "తెలుగు బైబిల్",             "te",  "telugu", "Indian"),
]

# Book slug map (English name → URL-safe slug)
BOOK_SLUGS = {
    "Genesis":"genesis","Exodus":"exodus","Leviticus":"leviticus",
    "Numbers":"numbers","Deuteronomy":"deuteronomy","Joshua":"joshua",
    "Judges":"judges","Ruth":"ruth","1 Samuel":"1-samuel","2 Samuel":"2-samuel",
    "1 Kings":"1-kings","2 Kings":"2-kings","1 Chronicles":"1-chronicles",
    "2 Chronicles":"2-chronicles","Ezra":"ezra","Nehemiah":"nehemiah",
    "Esther":"esther","Job":"job","Psalms":"psalms","Psalm":"psalms",
    "Proverbs":"proverbs","Ecclesiastes":"ecclesiastes",
    "Song of Solomon":"song-of-solomon","Song of Songs":"song-of-solomon",
    "Isaiah":"isaiah","Jeremiah":"jeremiah",
    "Lamentations":"lamentations","Ezekiel":"ezekiel","Daniel":"daniel",
    "Hosea":"hosea","Joel":"joel","Amos":"amos","Obadiah":"obadiah",
    "Jonah":"jonah","Micah":"micah","Nahum":"nahum","Habakkuk":"habakkuk",
    "Zephaniah":"zephaniah","Haggai":"haggai","Zechariah":"zechariah",
    "Malachi":"malachi","Matthew":"matthew","Mark":"mark","Luke":"luke",
    "John":"john","Acts":"acts","Romans":"romans",
    "1 Corinthians":"1-corinthians","2 Corinthians":"2-corinthians",
    "Galatians":"galatians","Ephesians":"ephesians","Philippians":"philippians",
    "Colossians":"colossians","1 Thessalonians":"1-thessalonians",
    "2 Thessalonians":"2-thessalonians","1 Timothy":"1-timothy",
    "2 Timothy":"2-timothy","Titus":"titus","Philemon":"philemon",
    "Hebrews":"hebrews","James":"james","1 Peter":"1-peter","2 Peter":"2-peter",
    "1 John":"1-john","2 John":"2-john","3 John":"3-john","Jude":"jude",
    "Revelation":"revelation",
}

# hreflang codes per version
HREFLANG = {
    "bbe":"en","kjv":"en","nkjv":"en","web":"en","ylt":"en",
    "bengali":"bn","gujarati":"gu","hindi":"hi","kannada":"kn",
    "malayalam":"ml","marathi":"mr","nepali":"ne","odia":"or","tamil":"ta",
    "telugu":"te",
}

ALL_MODULES = {"assets", "indexes", "chapters", "verses", "parallel", "sitemap"}

# Indian `VERSIONS` rows get verse-detail extras (crossrefs, Strong's, interlinear) like Telugu.
def version_has_verse_detail_features(version_id: str) -> bool:
    for vid, _label, _lng, _script, group in VERSIONS:
        if vid == version_id:
            return group == "Indian"
    return False


# BCP47 lang → (Google Fonts API family slug, CSS font-family name) for reader + verse-detail body text.
INDIC_LANG_SCRIPT_FONT = {
    "te": ("Noto+Sans+Telugu", "Noto Sans Telugu"),
    "hi": ("Noto+Sans+Devanagari", "Noto Sans Devanagari"),
    "mr": ("Noto+Sans+Devanagari", "Noto Sans Devanagari"),
    "ne": ("Noto+Sans+Devanagari", "Noto Sans Devanagari"),
    "ta": ("Noto+Sans+Tamil", "Noto Sans Tamil"),
    "kn": ("Noto+Sans+Kannada", "Noto Sans Kannada"),
    "ml": ("Noto+Sans+Malayalam", "Noto Sans Malayalam"),
    "bn": ("Noto+Sans+Bengali", "Noto Sans Bengali"),
    "gu": ("Noto+Sans+Gujarati", "Noto Sans Gujarati"),
    "or": ("Noto+Sans+Oriya", "Noto Sans Oriya"),
}


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

# Telugu display names by canonical book order (user-provided app aliases)
TELUGU_BOOK_NAMES = {
    1: "ఆదికాండము", 2: "నిర్గమకాండము", 3: "లేవీయకాండము", 4: "సంఖ్యాకాండము", 5: "ద్వితీయోపదేశకాండము",
    6: "యెహోషువ", 7: "న్యాయాధిపతులు", 8: "రూతు", 9: "1 సమూయేలు", 10: "2 సమూయేలు",
    11: "1 రాజులు", 12: "2 రాజులు", 13: "1 దినవృత్తాంతములు", 14: "2 దినవృత్తాంతములు", 15: "ఎజ్రా",
    16: "నెహెమ్యా", 17: "ఎస్తేరు", 18: "యోబు", 19: "కీర్తనలు", 20: "సామెతలు",
    21: "ప్రసంగి", 22: "పరమగీతము", 23: "యెషయా", 24: "యిర్మియా", 25: "విలాపవాక్యములు",
    26: "యెహెజ్కేలు", 27: "దానియేలు", 28: "హోషేయ", 29: "యోవేలు", 30: "ఆమోసు",
    31: "ఓబద్యా", 32: "యోనా", 33: "మీకా", 34: "నహూము", 35: "హబక్కూకు",
    36: "జెఫన్యా", 37: "హగ్గయి", 38: "జెకర్యా", 39: "మలాకీ", 40: "మత్తయి",
    41: "మార్కు", 42: "లూకా", 43: "యోహాను", 44: "అపొస్తలుల కార్యములు", 45: "రోమీయులకు",
    46: "1 కొరింథీయులకు", 47: "2 కొరింథీయులకు", 48: "గలతీయులకు", 49: "ఎఫెసీయులకు", 50: "ఫిలిప్పీయులకు",
    51: "కొలస్సీయులకు", 52: "1 థెస్సలొనీకయులకు", 53: "2 థెస్సలొనీకయులకు", 54: "1 తిమోతికి", 55: "2 తిమోతికి",
    56: "తీతుకు", 57: "ఫిలేమోనుకు", 58: "హెబ్రీయులకు", 59: "యాకోబు", 60: "1 పేతురు",
    61: "2 పేతురు", 62: "1 యోహాను", 63: "2 యోహాను", 64: "3 యోహాను", 65: "యూదా", 66: "ప్రకటన గ్రంథము",
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────

def download_json(version_id):
    """Download Bible JSON with CDN → raw GitHub fallback. Cache locally.

    Per URL: up to DOWNLOAD_ATTEMPTS tries with RETRY_DELAY_SEC between failures,
    then the next URL is tried. Cache is used only if the file exists and is non-empty.
    """
    CACHE_DIR.mkdir(exist_ok=True)
    cache_file = CACHE_DIR / f"bible_{version_id}.json"

    if cache_file.exists():
        try:
            raw = cache_file.read_text(encoding="utf-8")
            if raw.strip():
                print(f"  [cache] {version_id}")
                return json.loads(raw)
            print(f"  [warn] empty cache file for {version_id} — re-downloading")
        except (json.JSONDecodeError, OSError, UnicodeError) as e:
            print(f"  [warn] corrupt cache for {version_id}: {e} — re-downloading")

    local_file = LOCAL_BIBLE_DATA_DIR / f"bible_{version_id}.json"
    if local_file.exists():
        try:
            raw = local_file.read_text(encoding="utf-8")
            if raw.strip():
                data = json.loads(raw)
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                print(f"  [local] {version_id} from {local_file}")
                return data
        except Exception as e:
            print(f"  [warn] local bible file failed for {version_id}: {e}")

    urls = [
        f"{CDN_BASE}/bible_{version_id}.json",
        f"{GITHUB_RAW}/bible_{version_id}.json",
    ]
    for url in urls:
        host = url.split("/")[2]
        for attempt in range(1, DOWNLOAD_ATTEMPTS + 1):
            try:
                print(f"  [download] {version_id} from {host} (try {attempt}/{DOWNLOAD_ATTEMPTS})...")
                req = urllib.request.Request(url, headers={"User-Agent": "BSWS-Generator/1.0"})
                with urllib.request.urlopen(req, timeout=30) as resp:
                    raw = resp.read().decode("utf-8")
                if not raw.strip():
                    raise ValueError("empty response body")
                data = json.loads(raw)
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
                time.sleep(0.3)  # be polite to CDN / GitHub
                return data
            except Exception as e:
                print(f"  [warn] {host} failed: {e}")
                if attempt < DOWNLOAD_ATTEMPTS:
                    time.sleep(RETRY_DELAY_SEC)
        print(f"  [warn] exhausted retries for {host}, trying fallback URL…")
    print(f"  [ERROR] Could not download {version_id} — skipping")
    return None


def normalise(data):
    """
    Normalise any Bible JSON format into:
    { books: [ { b: int, n: str, ch: [ { c: int, v: {1: str, 2: str...} } ] } ] }

    Handles:
      - Native BSWS format: { books: [{b, n, ch:[{c, v:{}}]}] }
      - Foreign format:     { "Genesis": { "1": { "1": "text" } } }
    """
    if isinstance(data, dict) and "books" in data:
        books = data["books"]
        if books and isinstance(books[0].get("b"), int):
            return data  # already native

    # Foreign format — dict of book names
    BOOK_NUM = {
        "Genesis":1,"Exodus":2,"Leviticus":3,"Numbers":4,"Deuteronomy":5,
        "Joshua":6,"Judges":7,"Ruth":8,"1 Samuel":9,"2 Samuel":10,
        "1 Kings":11,"2 Kings":12,"1 Chronicles":13,"2 Chronicles":14,
        "Ezra":15,"Nehemiah":16,"Esther":17,"Job":18,"Psalm":19,"Psalms":19,
        "Proverbs":20,"Ecclesiastes":21,"Song of Solomon":22,"Song of Songs":22,"Isaiah":23,
        "Jeremiah":24,"Lamentations":25,"Ezekiel":26,"Daniel":27,"Hosea":28,
        "Joel":29,"Amos":30,"Obadiah":31,"Jonah":32,"Micah":33,"Nahum":34,
        "Habakkuk":35,"Zephaniah":36,"Haggai":37,"Zechariah":38,"Malachi":39,
        "Matthew":40,"Mark":41,"Luke":42,"John":43,"Acts":44,"Romans":45,
        "1 Corinthians":46,"2 Corinthians":47,"Galatians":48,"Ephesians":49,
        "Philippians":50,"Colossians":51,"1 Thessalonians":52,"2 Thessalonians":53,
        "1 Timothy":54,"2 Timothy":55,"Titus":56,"Philemon":57,"Hebrews":58,
        "James":59,"1 Peter":60,"2 Peter":61,"1 John":62,"2 John":63,
        "3 John":64,"Jude":65,"Revelation":66,
    }
    books = []
    for book_name, chapters in data.items():
        b_num = BOOK_NUM.get(book_name)
        if not b_num:
            # Try "Book1" format
            m = re.match(r"Book(\d+)", book_name)
            if m:
                b_num = int(m.group(1))
            else:
                print(f"  [warn] unknown book key in foreign JSON: {book_name!r} — skipped")
                continue
        chs = []
        for ch_num_str, verses in chapters.items():
            try:
                c_num = int(ch_num_str)
            except ValueError:
                continue
            v_dict = {}
            for v_num_str, text in verses.items():
                try:
                    s = str(text).strip()
                    if not s:
                        continue
                    v_dict[int(v_num_str)] = s
                except (ValueError, TypeError):
                    pass
            chs.append({"c": c_num, "v": v_dict})
        chs.sort(key=lambda x: x["c"])
        books.append({"b": b_num, "n": book_name, "ch": chs})
    books.sort(key=lambda x: x["b"])
    return {"books": books}


def load_local_json(path: Path, label: str):
    try:
        raw = path.read_text(encoding="utf-8")
        if not raw.strip():
            print(f"  [warn] {label} is empty: {path}")
            return {}
        return json.loads(raw)
    except Exception as e:
        print(f"  [warn] could not load {label} from {path}: {e}")
        return {}


def fetch_remote_json_cached(name: str, url: str):
    INTERLINEAR_CACHE_DIR.mkdir(exist_ok=True)
    cache_file = INTERLINEAR_CACHE_DIR / name
    if cache_file.exists():
        try:
            return json.loads(cache_file.read_text(encoding="utf-8"))
        except Exception:
            pass
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BSWS-Generator/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read().decode("utf-8")
        data = json.loads(raw)
        cache_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        return data
    except Exception as e:
        print(f"  [warn] failed remote json {name}: {e}")
        return {}


def load_interlinear_book_mapping():
    mapping = fetch_remote_json_cached("bookMapping.json", f"{INTERLINEAR_RAW_BASE}/bookMapping.json")
    out = {}
    for key, meta in mapping.items():
        try:
            out[int(key)] = str(meta.get("abbrev", "")).strip()
        except Exception:
            continue
    return out


def load_interlinear_book_tokens(abbrev: str):
    if not abbrev:
        return {}
    data = fetch_remote_json_cached(f"{abbrev}.json", f"{INTERLINEAR_RAW_BASE}/{abbrev}.json")
    chapters = data.get("chapters", {}) if isinstance(data, dict) else {}
    if not isinstance(chapters, dict):
        return {}
    return chapters


def build_verse_lookup(all_books, version_id):
    lookup = {}
    for bk in all_books:
        b_num = bk.get("b")
        b_name_source = bk.get("n", "")
        b_name = display_book_name(bk, version_id)
        bslug = book_slug(b_name_source)
        for ch in bk.get("ch", []):
            c_num = ch.get("c")
            verses = ch.get("v", {})
            for v_num, txt in verses.items():
                key = f"{b_num}_{c_num}_{v_num}"
                lookup[key] = {
                    "book_num": b_num,
                    "chapter_num": c_num,
                    "verse_num": v_num,
                    "book_name": b_name,
                    "book_slug": bslug,
                    "text": txt,
                }
    return lookup


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
    return f"/{OUT_DIR}/{version_id}/{bslug}/{ch_num}/{v_num}/"


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


# ─── HTML TEMPLATES ───────────────────────────────────────────────────────────

SHARED_CSS = (
    """
@import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');
/* Default tokens = "reader" theme (first paint before JS; editorial / spiritual reading) */
:root{
  --bg:#FAFAF8;--bg2:#F2EFE8;--card:#FFFFFF;--border:#DDD8CE;
  --text:#1C1917;--muted:#57534E;--accent:#9A3412;--vnum:#B45309;
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){
  html{scroll-behavior:auto}
  #sidebar,#vbar,#tsheet,.v-row,.icon-btn{transition:none!important}
}
body{background:var(--bg);color:var(--text);font-family:'Lora',Georgia,serif;min-height:100vh;overflow-x:hidden;touch-action:manipulation}
a{color:var(--accent);text-decoration:none}
a:hover{text-decoration:underline}

/* Top bar */
#topbar{position:fixed;top:0;left:0;right:0;height:52px;background:var(--bg2);border-bottom:1px solid var(--border);display:flex;align-items:center;padding:0 16px;gap:10px;z-index:100}
#topbar .logo{font-family:'Cinzel',serif;font-size:14px;color:var(--accent);white-space:nowrap;font-weight:600}
#topbar .crumb{font-size:13px;color:var(--muted);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.icon-btn{background:none;border:1px solid var(--border);color:var(--text);border-radius:6px;padding:6px 10px;cursor:pointer;font-size:13px;font-family:'Cinzel',serif;white-space:nowrap}
.icon-btn:hover{background:var(--card)}
.icon-btn:focus-visible,.book-btn:focus-visible,.ch-btn:focus-visible,.cta-btn:focus-visible,#s-search:focus-visible,.par-ver-select:focus-visible,.t-btn:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
#menu-btn.icon-btn--menu{display:inline-flex;flex-direction:column;justify-content:center;align-items:center;gap:4px;min-width:44px;min-height:44px;padding:10px}
#menu-btn.icon-btn--menu .hb-line{display:block;width:18px;height:2px;background:var(--text);border-radius:1px}

/* Sidebar */
#sidebar{position:fixed;top:52px;left:0;bottom:0;width:280px;background:var(--bg2);border-right:1px solid var(--border);overflow-y:auto;transform:translateX(-100%);transition:transform .25s ease;z-index:90}
#sidebar.open{transform:translateX(0)}
#overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:80}
#overlay.active{display:block}
@media(min-width:900px){
  #sidebar{transform:translateX(0)}
  #wrap{margin-left:280px}
  body.sidebar-collapsed #sidebar{transform:translateX(-100%)}
  body.sidebar-collapsed #wrap{margin-left:0}
}

/* Sidebar internals */
.s-section{font-family:'Cinzel',serif;font-size:10px;letter-spacing:.15em;color:var(--muted);padding:14px 14px 5px;text-transform:uppercase}
.s-ver{width:100%;background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:9px 12px;font-family:'Lora',serif;font-size:13px;margin:0 14px 10px;width:calc(100% - 28px);cursor:pointer}
.book-btn{display:block;width:100%;text-align:left;background:none;border:none;color:var(--text);padding:9px 14px;font-size:13px;font-family:'Lora',serif;cursor:pointer;transition:background .1s}
.book-btn:hover,.book-btn.on{background:var(--card);color:var(--accent)}
#ch-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:5px;padding:8px 14px 14px}
.ch-btn{background:var(--card);border:1px solid var(--border);color:var(--muted);border-radius:5px;padding:7px 3px;font-size:11px;font-family:'Cinzel',serif;cursor:pointer;text-align:center;transition:all .1s}
.ch-btn:hover,.ch-btn.on{background:var(--accent);color:var(--bg);border-color:var(--accent)}
#s-search{width:calc(100% - 28px);margin:10px 14px;background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:9px 12px;font-family:'Lora',serif;font-size:13px}
#s-search::placeholder{color:var(--muted)}
.sr-item{padding:9px 14px;border-bottom:1px solid var(--border);cursor:pointer}
.sr-item:hover{background:var(--card)}
.sr-ref{font-family:'Cinzel',serif;font-size:10px;color:var(--accent);margin-bottom:3px}
.sr-txt{font-size:12px;color:var(--muted);line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}

/* Main content */
#wrap{padding-top:52px}
#reader{max-width:700px;margin:0 auto;padding:40px 20px 120px}
.ch-head{text-align:center;margin-bottom:36px}
.ch-head h1{font-family:'Cinzel',serif;font-size:clamp(20px,5vw,30px);color:var(--accent);margin-bottom:6px}
.ch-head h2{font-family:'Cinzel',serif;font-size:clamp(12px,3vw,16px);color:var(--muted);letter-spacing:.06em;font-weight:400}
.ch-head .version-tag{display:inline-block;margin-top:8px;font-size:11px;font-family:'Cinzel',serif;color:var(--muted);border:1px solid var(--border);border-radius:20px;padding:3px 12px}

/* Verses */
.v-row{display:flex;gap:10px;padding:9px 10px;cursor:pointer;border-radius:7px;transition:background .12s;-webkit-tap-highlight-color:transparent;border-left:3px solid transparent;color:inherit;text-decoration:none}
.v-row:hover{background:var(--card)}
.v-row.sel{background:var(--card);border-left-color:var(--accent);padding-left:7px}
.v-row:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.v-num{font-family:'Cinzel',serif;font-size:11px;color:var(--vnum);min-width:26px;padding-top:5px;flex-shrink:0;text-align:right;font-weight:600}
.v-txt{font-family:'Lora',Georgia,serif;font-size:var(--verse-font-size,clamp(16px,4vw,19px));line-height:1.9;color:var(--text)}

/* Verse detail */
.verse-detail-card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:20px;margin-bottom:20px}
.verse-detail-ref{font-family:'Cinzel',serif;font-size:12px;letter-spacing:.08em;color:var(--accent);margin-bottom:10px}
.verse-detail-text{font-family:'Lora',Georgia,serif;font-size:clamp(20px,4vw,28px);line-height:1.7;color:var(--text)}
.verse-detail-meta{font-size:13px;color:var(--muted);line-height:1.6;margin-top:14px}
.verse-detail-links{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0 0}
.verse-detail-links a{background:var(--bg2);border:1px solid var(--border);border-radius:8px;padding:8px 12px;font-size:12px;font-family:'Cinzel',serif}
.detail-grid{display:grid;grid-template-columns:1fr;gap:14px;margin:18px 0}
.detail-panel{background:var(--bg2);border:1px solid var(--border);border-radius:10px;padding:14px}
.detail-panel h3{font-family:'Cinzel',serif;font-size:12px;letter-spacing:.08em;color:var(--accent);margin:0 0 10px}
.xref-list{display:flex;flex-direction:column;gap:8px}
.xref-item{display:flex;flex-direction:column;gap:3px;padding:9px;border:1px solid var(--border);border-radius:8px;background:var(--card)}
.xref-item a{font-family:'Cinzel',serif;font-size:11px;letter-spacing:.04em}
.xref-item .x-txt{font-size:13px;color:var(--muted);line-height:1.5}
@media(min-width:900px){
  .detail-grid{grid-template-columns:1fr 1fr}
}

/* Chapter nav */
.ch-nav{display:flex;justify-content:space-between;gap:10px;margin-top:48px;padding-top:24px;border-top:1px solid var(--border)}
.ch-nav a{background:var(--card);color:var(--accent);border:1px solid var(--border);padding:12px 20px;border-radius:8px;font-family:'Cinzel',serif;font-size:12px;transition:background .12s;flex:1;text-align:center}
.ch-nav a:hover{background:var(--border);text-decoration:none}
.ch-nav a.disabled{opacity:.35;pointer-events:none}

/* App CTA banner */
.app-cta{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px 20px;margin:36px 0;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.app-cta p{font-size:13px;color:var(--muted);line-height:1.5}
.app-cta strong{color:var(--text);display:block;font-family:'Cinzel',serif;font-size:13px;margin-bottom:3px}
.cta-btn{background:var(--accent);color:var(--bg);border:none;border-radius:8px;padding:11px 20px;font-family:'Cinzel',serif;font-size:12px;font-weight:600;cursor:pointer;white-space:nowrap;text-decoration:none;display:inline-block}
.cta-btn:hover{opacity:.88;text-decoration:none}

/* Verse action bar */
#vbar{position:fixed;bottom:0;left:0;right:0;background:var(--card);border-top:1px solid var(--border);display:flex;gap:8px;padding:10px 14px;z-index:100;flex-wrap:wrap;align-items:center}
#vbar button{background:var(--bg2);color:var(--text);border:1px solid var(--border);border-radius:7px;padding:10px 14px;font-family:'Cinzel',serif;font-size:11px;cursor:pointer;flex:1;min-width:110px}
#vbar button.on{border-color:var(--accent);color:var(--accent)}
#vbar .cta-btn{flex:2}
#vbar .vbar-meta{font-size:11px;color:var(--muted);font-family:'Cinzel',serif;letter-spacing:.04em;min-width:100%;margin-bottom:2px}
#vbar .vbar-speed{display:flex;align-items:center;gap:6px;background:var(--bg2);border:1px solid var(--border);border-radius:7px;padding:6px 10px;min-width:180px}
#vbar .vbar-speed label{font-size:11px;color:var(--muted);font-family:'Cinzel',serif}
#vbar .vbar-speed input{width:90px}
#vbar #vbar-close-btn{flex:0;min-width:auto;padding:10px 12px}
body.vbar-hidden #vbar{transform:translateY(100%)}
@media(max-width:899px){
  #vbar{transition:transform .2s ease}
  #reader{padding-bottom:170px}
  body.vbar-hidden #reader{padding-bottom:40px}
}

/* Theme sheet */
#tsheet{position:fixed;bottom:0;left:0;right:0;background:var(--bg2);border-top:1px solid var(--border);padding:16px 14px 28px;transform:translateY(100%);transition:transform .25s ease;z-index:110}
#tsheet.on{transform:translateY(0)}
#tsheet h3{font-family:'Cinzel',serif;font-size:12px;letter-spacing:.1em;color:var(--muted);margin-bottom:12px}
.t-swatches{display:grid;grid-template-columns:repeat(4,1fr);gap:8px}
.t-btn{border-radius:8px;padding:10px 6px;font-size:11px;font-family:'Cinzel',serif;cursor:pointer;border:2px solid transparent;transition:border-color .15s;text-align:center}
.t-btn.on{border-color:var(--accent)}

/* Parallel panel */
#par-panel{display:none;border-top:1px solid var(--border);background:var(--bg2);padding:20px}
#par-panel.on{display:block}
@media(min-width:1100px){
  #par-panel.on{display:block;position:fixed;top:52px;right:0;bottom:0;width:360px;overflow-y:auto;border-top:none;border-left:1px solid var(--border);padding:20px}
  #wrap.par-open #reader{margin-right:360px}
}
.par-ver-select{width:100%;background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:9px 12px;font-family:'Lora',serif;font-size:13px;margin-bottom:16px;cursor:pointer}
.par-head{font-family:'Cinzel',serif;font-size:11px;letter-spacing:.1em;color:var(--muted);margin-bottom:12px}
.par-jump-select{width:100%;background:var(--card);color:var(--text);border:1px solid var(--border);border-radius:8px;padding:9px 12px;font-family:'Lora',serif;font-size:13px;margin:0 14px 10px;width:calc(100% - 28px);cursor:pointer}

/* Parallel reader (two-column chapter) */
#reader.parallel-reader{max-width:min(1160px,calc(100vw - 40px))}
.par-rows{display:flex;flex-direction:column;gap:0}
.par-row{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:start;padding:10px 0;border-bottom:1px solid var(--border)}
@media(max-width:720px){.par-row{grid-template-columns:1fr}}
.par-cell{min-width:0}
.par-cell .v-row{margin:0}
.par-col-label{font-family:'Cinzel',serif;font-size:10px;letter-spacing:.1em;color:var(--muted);margin-bottom:8px;text-transform:uppercase}

/* Loading */
.loading{text-align:center;padding:60px 20px;color:var(--muted);font-family:'Cinzel',serif;font-size:13px;letter-spacing:.1em}

/* Bible index page */
.ver-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin:24px 0}
.ver-card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px;cursor:pointer;transition:border-color .15s;text-decoration:none;display:block}
.ver-card:hover{border-color:var(--accent);text-decoration:none}
.ver-card .vc-label{font-family:'Cinzel',serif;font-size:13px;color:var(--accent);margin-bottom:4px}
.ver-card .vc-sub{font-size:12px;color:var(--muted)}
.group-title{font-family:'Cinzel',serif;font-size:11px;letter-spacing:.15em;color:var(--muted);margin:28px 0 10px;text-transform:uppercase}
.hero{text-align:center;padding:48px 20px 32px}
.hero h1{font-family:'Cinzel',serif;font-size:clamp(22px,5vw,36px);color:var(--accent);margin-bottom:10px}
.hero p{font-size:15px;color:var(--muted);line-height:1.7;max-width:560px;margin:0 auto 24px}
"""
    + "\n"
    + indic_script_face_css()
    + "\n"
)

SHARED_JS = """
// ── Theme ── (default "reader" = warm editorial light, high contrast for long-form reading)
const THEMES = {
  reader:     { '--bg':'#FAFAF8','--bg2':'#F2EFE8','--card':'#FFFFFF','--border':'#DDD8CE','--text':'#1C1917','--muted':'#57534E','--accent':'#9A3412','--vnum':'#B45309' },
  royal:      { '--bg':'#0D0A1A','--bg2':'#1A1530','--card':'#221D3A','--border':'#3D3560','--text':'#F0EAD6','--muted':'#9B91C1','--accent':'#F5C842','--vnum':'#F5C842' },
  minimalist: { '--bg':'#FFFFFF','--bg2':'#F8F8F6','--card':'#FFFFFF','--border':'#E5E5E0','--text':'#1A1A1A','--muted':'#888880','--accent':'#1A1A1A','--vnum':'#BBBBBB' },
  ocean:      { '--bg':'#0A1628','--bg2':'#0F1F3D','--card':'#132A52','--border':'#1E3F6E','--text':'#E8F4FD','--muted':'#7BAFD4','--accent':'#38BDF8','--vnum':'#38BDF8' },
  nature:     { '--bg':'#0A1A0F','--bg2':'#0F2418','--card':'#143220','--border':'#1E4A2E','--text':'#E8F5EC','--muted':'#7BB88A','--accent':'#4ADE80','--vnum':'#4ADE80' },
  blossom:    { '--bg':'#1A0A14','--bg2':'#2D1020','--card':'#3D1530','--border':'#5C2248','--text':'#FDF0F6','--muted':'#C47EA0','--accent':'#F472B6','--vnum':'#F472B6' },
  ember:      { '--bg':'#1A0E08','--bg2':'#2A1810','--card':'#3A2218','--border':'#5A3828','--text':'#FDF4EE','--muted':'#C49070','--accent':'#FB923C','--vnum':'#FB923C' },
  midnight:   { '--bg':'#080C1A','--bg2':'#0E1428','--card':'#141E3C','--border':'#1E2E58','--text':'#E8EAF6','--muted':'#7B8EC8','--accent':'#818CF8','--vnum':'#818CF8' },
  parchment:  { '--bg':'#F5F0E8','--bg2':'#EDE8DC','--card':'#FBF8F2','--border':'#D4C9A8','--text':'#2C2416','--muted':'#8B7D5A','--accent':'#8B4513','--vnum':'#B8860B' },
};
function applyTheme(id) {
  const t = THEMES[id] || THEMES.reader;
  Object.entries(t).forEach(([k,v]) => document.documentElement.style.setProperty(k,v));
  document.documentElement.setAttribute('data-theme', id);
  localStorage.setItem('bsws_theme', id);
  document.querySelectorAll('.t-btn').forEach(b => b.classList.toggle('on', b.dataset.t === id));
}

const VERSE_LINKS_STORAGE_KEY = 'bsws_enable_verse_links';
function areVerseLinksEnabled() {
  return localStorage.getItem(VERSE_LINKS_STORAGE_KEY) === '1';
}
function setVerseLinksEnabled(enabled) {
  localStorage.setItem(VERSE_LINKS_STORAGE_KEY, enabled ? '1' : '0');
  renderVerseLinksToggle();
}
function renderVerseLinksToggle() {
  const btn = document.getElementById('verse-links-btn');
  if (!btn) return;
  const enabled = areVerseLinksEnabled();
  btn.textContent = enabled ? 'Verse Details On' : 'Verse Details Off';
  btn.classList.toggle('on', enabled);
  btn.setAttribute('aria-pressed', enabled ? 'true' : 'false');
}

// ── Sidebar ──
function openSidebar()  { document.getElementById('sidebar').classList.add('open'); document.getElementById('overlay').classList.add('active'); }
function closeSidebar() { document.getElementById('sidebar').classList.remove('open'); document.getElementById('overlay').classList.remove('active'); }
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('menu-btn')?.addEventListener('click', openSidebar);
  document.getElementById('overlay')?.addEventListener('click', closeSidebar);

  // Theme sheet
  document.getElementById('theme-btn')?.addEventListener('click', () => document.getElementById('tsheet').classList.toggle('on'));
  const swatches = document.querySelector('.t-swatches');
  if (swatches) {
    Object.keys(THEMES).forEach(id => {
      const t = THEMES[id];
      const btn = document.createElement('button');
      btn.className = 't-btn'; btn.dataset.t = id; btn.textContent = id.charAt(0).toUpperCase()+id.slice(1);
      btn.style.background = t['--bg2']; btn.style.color = t['--text']; btn.style.borderColor = t['--border'];
      btn.addEventListener('click', () => applyTheme(id));
      swatches.appendChild(btn);
    });
  }

  // Init theme
  applyTheme(localStorage.getItem('bsws_theme') || 'reader');

  // Parallel toggle
  document.getElementById('par-btn')?.addEventListener('click', () => {
    document.getElementById('par-panel').classList.toggle('on');
    document.getElementById('wrap').classList.toggle('par-open');
  });

  // Font size controls (top bar + action bar)
  initFontScale();
  document.getElementById('font-inc-btn')?.addEventListener('click', () => updateFontScale(0.1));
  document.getElementById('font-dec-btn')?.addEventListener('click', () => updateFontScale(-0.1));
  document.getElementById('font-inc-vbar-btn')?.addEventListener('click', () => updateFontScale(0.1));
  document.getElementById('font-dec-vbar-btn')?.addEventListener('click', () => updateFontScale(-0.1));
  if (localStorage.getItem(VERSE_LINKS_STORAGE_KEY) === null) {
    localStorage.setItem(VERSE_LINKS_STORAGE_KEY, '0');
  }
  renderVerseLinksToggle();
  document.getElementById('verse-links-btn')?.addEventListener('click', () => {
    setVerseLinksEnabled(!areVerseLinksEnabled());
  });

  // Verse detail navigation toggle (Off = plain chapter reading)
  document.addEventListener('click', e => {
    const row = e.target.closest('.v-row');
    if (!row || areVerseLinksEnabled()) return;
    if (e.defaultPrevented || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
    e.preventDefault();
    selectVerse(row);
  });

  // Verse action bar — dismiss on outside click
  document.addEventListener('click', e => {
    if (!e.target.closest('.v-row') && !e.target.closest('#vbar')) {
      clearSelectedVerses();
    }
  });

  // Copy btn (supports multi-select)
  document.getElementById('copy-btn')?.addEventListener('click', () => {
    const selected = getSelectedVerses();
    if (!selected.length) return;
    const payload = selected.map(v => '"' + v.txt + '" — ' + v.ref).join('\\n\\n');
    navigator.clipboard.writeText(payload).then(() => {
      const btn = document.getElementById('copy-btn');
      btn.textContent = 'Copied ✓';
      setTimeout(() => btn.textContent = 'Copy', 1800);
    });
  });

  // Share btn (supports multi-select)
  document.getElementById('share-btn')?.addEventListener('click', () => {
    const selected = getSelectedVerses();
    if (!selected.length) return;
    const url = window.location.href;
    const payload = selected.map(v => '"' + v.txt + '" — ' + v.ref).join('\\n\\n');
    const title = selected.length === 1 ? selected[0].ref : `${selected.length} verses`;
    if (navigator.share) {
      navigator.share({ title, text: payload, url });
    } else {
      navigator.clipboard.writeText(payload + '\\n\\n' + url);
    }
  });

  // TTS controls
  initTtsToggles();
  document.getElementById('tts-play-btn')?.addEventListener('click', speakSelection);
  document.getElementById('tts-chapter-btn')?.addEventListener('click', speakChapter);
  document.getElementById('tts-stop-btn')?.addEventListener('click', () => speechSynthesis?.cancel());
  document.getElementById('tts-loop-btn')?.addEventListener('click', toggleLoopMode);
  document.getElementById('tts-auto-btn')?.addEventListener('click', toggleAutoReadMode);
  document.getElementById('tts-download-btn')?.addEventListener('click', downloadAudioFallback);
  document.getElementById('clear-sel-btn')?.addEventListener('click', clearSelectedVerses);

  // Sidebar search
  const si = document.getElementById('s-search');
  if (si) {
    let st;
    si.addEventListener('input', e => {
      clearTimeout(st);
      const q = e.target.value.trim();
      if (q.length < 3) { document.getElementById('sr').innerHTML=''; return; }
      st = setTimeout(() => sidebarSearch(q), 280);
    });
  }

  // Auto-read chapter on load when enabled
  if (localStorage.getItem('bsws_auto_read_chapter') === '1') {
    setTimeout(() => speakChapter(), 500);
  }
});

function updateVbarState() {
  const rows = document.querySelectorAll('.v-row.sel');
  const vbar = document.getElementById('vbar');
  const meta = document.getElementById('vbar-meta');
  if (!vbar || !meta) return;
  const n = rows.length;
  meta.textContent = `${n} verse${n === 1 ? '' : 's'} selected`;
}

function getSelectedVerses() {
  return [...document.querySelectorAll('.v-row.sel')].map(sel => ({
    ref: sel.dataset.ref || '',
    txt: sel.querySelector('.v-txt')?.textContent || '',
  }));
}

function clearSelectedVerses() {
  document.querySelectorAll('.v-row.sel').forEach(r => r.classList.remove('sel'));
  updateVbarState();
}

function selectVerse(row) {
  row.classList.toggle('sel');
  updateVbarState();
}

function initFontScale() {
  const saved = Number(localStorage.getItem('bsws_font_scale') || '1.0');
  const clamped = Math.min(1.5, Math.max(0.8, saved));
  localStorage.setItem('bsws_font_scale', String(clamped));
  applyFontScale(clamped);
}

function applyFontScale(scale) {
  document.documentElement.style.setProperty('--verse-font-size', `${(18 * scale).toFixed(1)}px`);
}

function updateFontScale(delta) {
  const current = Number(localStorage.getItem('bsws_font_scale') || '1.0');
  const next = Math.min(1.5, Math.max(0.8, Math.round((current + delta) * 10) / 10));
  localStorage.setItem('bsws_font_scale', String(next));
  applyFontScale(next);
}

function bestVoiceForLang(lang) {
  const voices = speechSynthesis?.getVoices?.() || [];
  if (!voices.length) return null;
  const normalized = (lang || 'en').toLowerCase();
  const byLang = voices.filter(v => (v.lang || '').toLowerCase().startsWith(normalized));
  const pool = byLang.length ? byLang : voices;
  const score = v => {
    const n = (v.name || '').toLowerCase();
    let s = 0;
    if (n.includes('neural')) s += 5;
    if (n.includes('google')) s += 4;
    if (n.includes('microsoft')) s += 3;
    if (n.includes('premium') || n.includes('enhanced')) s += 2;
    if (v.default) s += 1;
    return s;
  };
  return [...pool].sort((a, b) => score(b) - score(a))[0] || null;
}

function getTtsRate() {
  const rate = Number(document.getElementById('tts-rate')?.value || '1.0');
  return Math.min(1.5, Math.max(0.7, rate));
}

function getLoopMode() {
  return localStorage.getItem('bsws_tts_loop') === '1';
}

function speakText(text) {
  if (!text || !('speechSynthesis' in window)) return;
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = document.documentElement.lang || 'en';
  const voice = bestVoiceForLang(u.lang);
  if (voice) u.voice = voice;
  u.rate = getTtsRate();
  u.onend = () => {
    if (getLoopMode()) {
      setTimeout(() => speakText(text), 250);
    }
  };
  speechSynthesis.speak(u);
}

function speakSelection() {
  const selected = getSelectedVerses();
  if (!selected.length) return;
  const text = selected.map(v => `${v.ref}. ${v.txt}`).join(' ');
  speakText(text);
}

function speakChapter() {
  const rows = [...document.querySelectorAll('.v-row')];
  if (!rows.length) return;
  const text = rows.map(r => {
    const ref = r.dataset.ref || '';
    const verse = r.querySelector('.v-txt')?.textContent || '';
    return `${ref}. ${verse}`;
  }).join(' ');
  speakText(text);
}

function toggleLoopMode() {
  const next = getLoopMode() ? '0' : '1';
  localStorage.setItem('bsws_tts_loop', next);
  renderTtsToggles();
}

function toggleAutoReadMode() {
  const enabled = localStorage.getItem('bsws_auto_read_chapter') === '1';
  localStorage.setItem('bsws_auto_read_chapter', enabled ? '0' : '1');
  renderTtsToggles();
}

function renderTtsToggles() {
  const loopBtn = document.getElementById('tts-loop-btn');
  const autoBtn = document.getElementById('tts-auto-btn');
  const loopOn = getLoopMode();
  const autoOn = localStorage.getItem('bsws_auto_read_chapter') === '1';
  if (loopBtn) {
    loopBtn.textContent = loopOn ? 'Loop On' : 'Loop Off';
    loopBtn.classList.toggle('on', loopOn);
  }
  if (autoBtn) {
    autoBtn.textContent = autoOn ? 'Auto-Read On' : 'Auto-Read Off';
    autoBtn.classList.toggle('on', autoOn);
  }
}

function initTtsToggles() {
  if (localStorage.getItem('bsws_tts_loop') === null) {
    localStorage.setItem('bsws_tts_loop', '0');
  }
  if (localStorage.getItem('bsws_auto_read_chapter') === null) {
    localStorage.setItem('bsws_auto_read_chapter', '0');
  }
  renderTtsToggles();
}

function downloadAudioFallback() {
  const selected = getSelectedVerses();
  const hasSelection = selected.length > 0;
  const text = hasSelection
    ? selected.map(v => `${v.ref} ${v.txt}`).join('\n\n')
    : [...document.querySelectorAll('.v-row')].map(r => `${r.dataset.ref || ''} ${r.querySelector('.v-txt')?.textContent || ''}`).join('\n');

  // Browser SpeechSynthesis cannot reliably export MP3. Provide downloadable text fallback.
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = hasSelection ? 'selected-verses.txt' : 'chapter-verses.txt';
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1500);
}

function sidebarSearch(q) {
  // Only searches pre-rendered verses on the current page (static site)
  const rows = document.querySelectorAll('.v-row');
  const lq = q.toLowerCase();
  const results = [];
  rows.forEach(r => {
    const txt = r.querySelector('.v-txt')?.textContent || '';
    if (txt.toLowerCase().includes(lq)) {
      results.push({ ref: r.dataset.ref, txt, el: r });
    }
    if (results.length >= 15) return;
  });
  const sr = document.getElementById('sr');
  sr.textContent = '';
  results.forEach(res => {
    const d = document.createElement('div');
    d.className = 'sr-item';
    const refEl = document.createElement('div');
    refEl.className = 'sr-ref';
    refEl.textContent = res.ref || '';
    const txtEl = document.createElement('div');
    txtEl.className = 'sr-txt';
    txtEl.textContent = res.txt || '';
    d.appendChild(refEl);
    d.appendChild(txtEl);
    d.addEventListener('click', () => {
      res.el.scrollIntoView({ behavior:'smooth', block:'center' });
      selectVerse(res.el);
      closeSidebar();
    });
    sr.appendChild(d);
  });
  if (!results.length) {
    const p = document.createElement('p');
    p.style.padding = '10px 14px';
    p.style.fontSize = '12px';
    p.style.color = 'var(--muted)';
    p.textContent = 'No results in this chapter.';
    sr.appendChild(p);
  }
}

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {});
  });
}
"""

INTERLINEAR_CSS = """
.interlinear-verse{display:flex;flex-wrap:wrap;gap:8px}
.inter-token{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:8px;min-width:88px;text-align:left;cursor:pointer}
.inter-token .w{display:block;font-size:13px;color:var(--text);font-weight:600}
.inter-token .g{display:block;font-size:11px;color:var(--muted);margin-top:2px}
.inter-token .s{display:block;font-size:10px;color:var(--accent);margin-top:3px;font-family:'Cinzel',serif}
#lex-drawer{position:fixed;left:0;right:0;bottom:0;z-index:120;background:var(--bg2);border-top:1px solid var(--border);padding:14px;transform:translateY(100%);transition:transform .2s ease}
#lex-drawer.on{transform:translateY(0)}
#lex-drawer .close{float:right}
#lex-drawer h4{font-family:'Cinzel',serif;color:var(--accent);font-size:13px;margin:0 0 8px}
#lex-drawer p{font-size:13px;color:var(--text);line-height:1.5;margin:6px 0}
"""


def output_asset_href(relative_asset_path: str) -> str:
    return f"/{OUT_DIR}/{relative_asset_path}"


def parse_modules(raw_modules: str) -> set[str]:
    raw = (raw_modules or "all").strip().lower()
    if raw == "all":
        return set(ALL_MODULES)
    selected = {m.strip() for m in raw.split(",") if m.strip()}
    unknown = selected - ALL_MODULES
    if unknown:
        raise SystemExit(
            f"Unknown module(s): {sorted(unknown)}. Valid modules: {sorted(ALL_MODULES)}"
        )
    return selected


def should_run(module: str, selected_modules: set[str]) -> bool:
    return module in selected_modules


def write_if_changed(path: Path, content: str, dry_run: bool) -> bool:
    new_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    hash_path = path.with_suffix(path.suffix + ".hash")
    old_hash = hash_path.read_text(encoding="utf-8").strip() if hash_path.exists() else ""
    if old_hash == new_hash and path.exists():
        print(f"    [skip] {path}")
        return False
    if dry_run:
        print(f"    [dry-run] write {path}")
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    hash_path.write_text(new_hash, encoding="utf-8")
    return True


def generate_strongs_js(strongs_dict: dict) -> str:
    payload = json.dumps(strongs_dict or {}, ensure_ascii=False, separators=(",", ":"))
    return f"""
const STRONGS_DICT = {payload};

function bindStrongsDrawer() {{
  const drawer = document.getElementById('lex-drawer');
  if (!drawer) return;
  const closeBtn = document.getElementById('lex-close-btn');
  const setText = (id, text) => {{
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = text || '';
  }};
  document.querySelectorAll('.inter-token').forEach((btn) => {{
    btn.addEventListener('click', () => {{
      const strong = (btn.dataset.strong || '').trim();
      const lex = STRONGS_DICT[strong] || {{}};
      setText('lex-strong', strong || 'Word Study');
      setText('lex-lemma', lex.lemma ? `Lemma: ${{lex.lemma}}` : '');
      setText('lex-def', lex.def ? `Definition: ${{lex.def}}` : '');
      setText('lex-kjv', lex.kjv ? `KJV usage: ${{lex.kjv}}` : '');
      setText('lex-deriv', lex.deriv ? `Derivation: ${{lex.deriv}}` : '');
      drawer.classList.add('on');
    }});
  }});
  closeBtn?.addEventListener('click', () => drawer.classList.remove('on'));
}}

document.addEventListener('DOMContentLoaded', bindStrongsDrawer);
"""


def html_head(
    title,
    description,
    canonical,
    lang,
    hreflang_links,
    keywords="",
    robots_meta="",
    extra_head="",
):
    desc_attr = html.escape(description, quote=True)
    title_attr = html.escape(title, quote=True)
    ld_webpage = json.dumps(
        {
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
        },
        ensure_ascii=False,
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
<meta property="og:type" content="website"/>
<meta property="og:url" content="{canonical}"/>
<meta property="og:title" content="{title_attr}"/>
<meta property="og:description" content="{desc_attr}"/>
<meta property="og:image" content="{SITE_URL}/assets/og-bible.jpg"/>
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
<select class="par-jump-select" aria-label="Open two-column parallel reader" onchange="if(!this.value)return;try{{localStorage.setItem('bsws_parallel_secondary',this.value);}}catch(e){{}}window.location='/{OUT_DIR}/parallel/{version_id}/'+this.value+'/{bslug}/{ch_num}/';">
<option value="" selected disabled>Compare with…</option>
{opts}</select>"""


def sidebar_html(all_books, current_book_num, current_ch, version_id, vlabel, active_versions, parallel_jump_html=""):
    current_book = next((b for b in all_books if b["b"] == current_book_num), None)
    cur_slug = book_slug(current_book["n"]) if current_book else "genesis"

    books_html = ""
    ot_done = False
    for bk in all_books:
        if bk["b"] == 40 and not ot_done:
            books_html += '<div class="s-section">' + ("క్రొత్త నిబంధన" if version_id == "telugu" else "New Testament") + '</div>'
            ot_done = True
        if bk["b"] == 1 and not ot_done:
            books_html += '<div class="s-section">' + ("పాత నిబంధన" if version_id == "telugu" else "Old Testament") + '</div>'
            ot_done = False
        slug = book_slug(bk["n"])
        active = "on" if bk["b"] == current_book_num else ""
        url = f"/{OUT_DIR}/{version_id}/{slug}/1/"
        books_html += f'<a href="{url}" class="book-btn {active}">{display_book_name(bk, version_id)}</a>'

    # Chapter grid for current book
    current_book = next((b for b in all_books if b["b"] == current_book_num), None)
    ch_html = ""
    if current_book:
        slug = book_slug(current_book["n"])
        for c in range(1, len(current_book["ch"]) + 1):
            active = "on" if c == current_ch else ""
            url = f"/{OUT_DIR}/{version_id}/{slug}/{c}/"
            ch_html += f'<a href="{url}" class="ch-btn {active}">{c}</a>'

    # Version selector options (only built / active translations)
    ver_opts = ""
    for vid, vlbl, *_ in active_versions:
        sel = "selected" if vid == version_id else ""
        ver_opts += f'<option value="{vid}" {sel}>{vlbl}</option>'

    return f"""
<aside id="sidebar">
  <div class="s-section">Version</div>
  <select class="s-ver" onchange="window.location='/{OUT_DIR}/'+this.value+'/{cur_slug}/{current_ch}/'">{ver_opts}</select>
  {parallel_jump_html}
  <input id="s-search" type="search" placeholder="Search this chapter…" autocomplete="off"/>
  <div id="sr"></div>
  {'<div class="s-section">Chapters</div><div id="ch-grid">' + ch_html + '</div>' if ch_html else ''}
  <div class="s-section">Books</div>
  {books_html}
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
    canonical   = f"{SITE_URL}/{OUT_DIR}/{version_id}/{bslug}/{ch_num}/"
    verses      = chapter["v"]

    # hreflang — only URLs we actually build (active_versions) + x-default
    hreflang_parts = []
    for vid, vlab, vlng, *_ in active_versions:
        url = f"{SITE_URL}/{OUT_DIR}/{vid}/{bslug}/{ch_num}/"
        hreflang_parts.append(f'<link rel="alternate" hreflang="{HREFLANG.get(vid, vlng)}" href="{url}"/>')
    hreflang_parts.append(
        f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/{OUT_DIR}/{x_default_id}/{bslug}/{ch_num}/"/>'
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
    parallel_href = f"/{OUT_DIR}/parallel/{version_id}/{ds}/{bslug}/{ch_num}/" if ds else ""
    parallel_link_html = (
        f'  <a id="par-link" class="icon-btn" href="{parallel_href}" aria-label="Open parallel two-column view">||</a>\n'
        if parallel_href
        else ""
    )
    parallel_jump = build_parallel_jump_block(version_id, bslug, ch_num, active_versions)

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
{theme_sheet()}
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

    pref = f"/{OUT_DIR}/parallel/{vp}/{vs}"
    books_html = ""
    ot_done = False
    for bk in all_books:
        if bk["b"] == 40 and not ot_done:
            books_html += '<div class="s-section">' + ("క్రొత్త నిబంధన" if vp == "telugu" else "New Testament") + "</div>"
            ot_done = True
        if bk["b"] == 1 and not ot_done:
            books_html += '<div class="s-section">' + ("పాత నిబంధన" if vp == "telugu" else "Old Testament") + "</div>"
            ot_done = False
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
  <select id="par-pri" class="s-ver" aria-label="Primary translation" onchange="var p=this.value;var s=document.getElementById('par-sec').value;if(p===s)return;window.location='/{OUT_DIR}/parallel/'+p+'/'+s+'/{cur_slug}/{current_ch}/';">{pri_opts}</select>
  <label class="s-section" for="par-sec" style="padding-top:8px">Right column</label>
  <select id="par-sec" class="s-ver" aria-label="Secondary translation" onchange="try{{localStorage.setItem('bsws_parallel_secondary',this.value);}}catch(e){{}}var p=document.getElementById('par-pri').value;var s=this.value;if(p===s)return;window.location='/{OUT_DIR}/parallel/'+p+'/'+s+'/{cur_slug}/{current_ch}/';">{sec_opts}</select>
  <input id="s-search" type="search" placeholder="Search this chapter (left column)…" autocomplete="off"/>
  <div id="sr"></div>
  {'<div class="s-section">Chapters</div><div id="ch-grid">' + ch_html + '</div>' if ch_html else ''}
  <div class="s-section">Books</div>
  {books_html}
</aside>
<div id="overlay"></div>"""


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

    canonical_primary = f"{SITE_URL}/{OUT_DIR}/{vp}/{bslug}/{ch_num}/"
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
    single_url = f"/{OUT_DIR}/{vp}/{bslug}/{ch_num}/"
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
):
    has_verse_features = version_has_verse_detail_features(version_id)
    canonical = f"{SITE_URL}/{OUT_DIR}/{version_id}/{bslug}/{ch_num}/{vnum}/"
    title = f"{book_name} {ch_num}:{vnum} — {vlabel} | Bible Study with Steffi"
    description = f"Read {book_name} {ch_num}:{vnum} in {vlabel}. Bible verse detail with chapter navigation and context."
    keywords = f"{book_name} {ch_num}:{vnum}, {book_name} chapter {ch_num} verse {vnum}, {vlabel} bible verse, bswsapp"

    hreflang_parts = []
    for vid, vlab, vlng, *_ in active_versions:
        url = f"{SITE_URL}/{OUT_DIR}/{vid}/{bslug}/{ch_num}/{vnum}/"
        hreflang_parts.append(f'<link rel="alternate" hreflang="{HREFLANG.get(vid, vlng)}" href="{url}"/>')
    hreflang_parts.append(
        f'<link rel="alternate" hreflang="x-default" href="{SITE_URL}/{OUT_DIR}/{x_default_id}/{bslug}/{ch_num}/{vnum}/"/>'
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
            '>'
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
    head = html_head(title, description, canonical, lang_code, hreflang_str, keywords, extra_head=interlinear_head)
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
      <p class="verse-detail-ref">{book_name} {ch_num}:{vnum}</p>
      <p class="verse-detail-text">{safe_verse}</p>
      <p class="verse-detail-meta">Book: {book_name_source} · Chapter: {ch_num} · Verse: {vnum}</p>
      <div class="verse-detail-links">
        <a href="{chapter_url}">Open Full Chapter</a>
      </div>
    </article>
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


# ─── BIBLE INDEX PAGE ─────────────────────────────────────────────────────────

def generate_bible_index(active_versions, x_default_id):
    canonical = f"{SITE_URL}/{OUT_DIR}/"
    n = len(active_versions)
    # Hero + SEO: reflect what this generator run actually built (active_versions).
    # Version cards: always list the full catalog (VERSIONS) so /bible/ stays a directory
    # even when using --only for faster partial builds.
    if n == 1:
        vid0, vlbl0, vlng0, *_ = active_versions[0]
        index_lang = vlng0 if vlng0 != "en" else "en"
        title = f"Read Bible Online — {vlbl0} | Bible Study with Steffi"
        description = f"Read the Holy Bible online in {vlbl0}. Free, no ads. Bible Study with Steffi."
        keywords = (
            "telugu bible online, తెలుగు బైబిల్, bible online free, bswsapp"
            if vid0 == "telugu"
            else f"{vid0} bible online, bible reading free, bswsapp"
        )
        hero_title = "Read the Bible Online"
        hero_p = (
            f"Free Bible reader — {vlbl0}. No ads, no login required. "
            "Browse all available translations below."
        )
        hero_cta_href = f"/{OUT_DIR}/{vid0}/john/1/"
        hero_cta_label = f"Start reading — John 1 ({vlbl0})"
    else:
        index_lang = "en"
        title = "Read Bible Online Free — Telugu, Hindi, Tamil + 16 Versions | Bible Study with Steffi"
        description = (
            "Read the Holy Bible online in Telugu, Hindi, Tamil, Kannada, Malayalam, Bengali, Odia, "
            "Gujarati, Marathi, Nepali and English. Free, no ads. Bible Study with Steffi."
        )
        keywords = (
            "telugu bible online, hindi bible, tamil bible online, bible reading free, kannada bible, "
            "malayalam bible, bengali bible, odia bible, gujarati bible, marathi bible, KJV bible, "
            "NKJV bible, online bible"
        )
        hero_title = "Read the Bible Online"
        hero_p = (
            "Free Bible reader in multiple languages — Indian languages and English. "
            "No ads, no login required."
        )
        hero_cta_href = f"/{OUT_DIR}/{x_default_id}/john/1/"
        hero_cta_label = "Start Reading — John 1"

    english_cards = ""
    indian_cards = ""
    for vid, vlbl, vlng, vscript, vgroup in VERSIONS:
        card = f'<a href="/{OUT_DIR}/{vid}/john/1/" class="ver-card"><div class="vc-label">{vlbl}</div><div class="vc-sub">{vgroup} · {vlng.upper()}</div></a>'
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
        f'<link rel="alternate" hreflang="{HREFLANG.get(vid, "en")}" href="{SITE_URL}/{OUT_DIR}/{vid}/john/1/"/>'
        for vid, *_ in active_versions
    ])

    head = html_head(title, description, canonical, index_lang, hreflang, keywords)

    structured_data = json.dumps({
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Bible Study with Steffi",
        "url": SITE_URL,
        "description": description,
        "potentialAction": {
            "@type": "SearchAction",
            "target": f"{SITE_URL}/{OUT_DIR}/{x_default_id}/{{search_term_string}}/1/",
            "query-input": "required name=search_term_string"
        }
    }, ensure_ascii=False)

    return f"""{head}
<body>
<header id="topbar">
  <span class="logo">Bible Study with Steffi</span>
  <span style="flex:1"></span>
  <button type="button" id="theme-btn" class="icon-btn" aria-label="Reading theme and colors">Aa</button>
</header>
<script type="application/ld+json">{structured_data}</script>
<div id="wrap">
  <div id="reader">
    <div class="hero">
      <h1>{hero_title}</h1>
      <p>{hero_p}</p>
      <a class="cta-btn" href="{hero_cta_href}">{hero_cta_label}</a>
    </div>
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
            f'<a href="/{OUT_DIR}/{version_id}/{bslug}/1/" class="ver-card">'
            f'<div class="vc-label">{html.escape(dname)}</div>'
            f'<div class="vc-sub">{num_ch} chapters</div></a>'
        )
    head = html_head(
        title=f"{vlabel} — Bible Study with Steffi",
        description=f"Read the full {vlabel} Bible online.",
        canonical=f"{SITE_URL}/{OUT_DIR}/{version_id}/",
        lang=lang_code,
        hreflang_links="",
    )
    return f"""{head}
<body>
<header id="topbar">
  <a class="logo" href="/{OUT_DIR}/">Bible Study with Steffi</a>
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
    chapter_links = []
    for ch in book.get("ch", []):
        c = ch.get("c")
        chapter_links.append(
            f'<a class="ch-btn" href="/{OUT_DIR}/{version_id}/{bslug}/{c}/">{c}</a>'
        )
    head = html_head(
        title=f"{dname} — {vlabel}",
        description=f"Read {dname} in {vlabel}.",
        canonical=f"{SITE_URL}/{OUT_DIR}/{version_id}/{bslug}/",
        lang=lang_code,
        hreflang_links="",
    )
    return f"""{head}
<body>
{topbar_html(f"{html.escape(dname)} · {html.escape(vlabel)}", show_verse_links_toggle=False)}
<div id="wrap">
  <main id="reader">
    <div class="ch-head"><h1>{html.escape(dname)}</h1><h2>Select a chapter</h2></div>
    <div id="ch-grid">{"".join(chapter_links)}</div>
  </main>
</div>
{theme_sheet()}
<script src="{output_asset_href(ASSET_READER_JS_PATH)}" defer></script>
</body>
</html>"""


# ─── SITEMAP GENERATOR ────────────────────────────────────────────────────────

def generate_sitemap(all_urls):
    urls_xml = "\n".join([
        f"  <url><loc>{url}</loc><changefreq>monthly</changefreq><priority>0.7</priority><lastmod>{TODAY}</lastmod></url>"
        for url in all_urls
    ])
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url><loc>{SITE_URL}/bible/</loc><changefreq>weekly</changefreq><priority>1.0</priority><lastmod>{TODAY}</lastmod></url>
{urls_xml}
</urlset>"""


# ─── ROBOTS.TXT ───────────────────────────────────────────────────────────────

ROBOTS_TXT = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}/sitemap.xml
Sitemap: {SITE_URL}/bible/sitemap.xml
"""


def generate_manifest_json() -> str:
    return json.dumps(
        {
            "name": "Bible Study with Steffi",
            "short_name": "BSWS Bible",
            "description": "Read the Bible in multiple languages.",
            "start_url": f"/{OUT_DIR}/",
            "display": "standalone",
            "background_color": "#0d0820",
            "theme_color": "#1e1040",
            "lang": "en",
            "icons": [
                {"src": "/assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
                {"src": "/assets/icon-512.png", "sizes": "512x512", "type": "image/png"},
            ],
        },
        indent=2,
        ensure_ascii=False,
    )


def generate_service_worker() -> str:
    return f"""
const CACHE_NAME = 'bsws-bible-v2';
const PRECACHE = [
  '/{OUT_DIR}/',
  '/{OUT_DIR}/{ASSET_STYLE_PATH}',
  '/{OUT_DIR}/{ASSET_READER_JS_PATH}',
  '/{OUT_DIR}/manifest.json',
];

self.addEventListener('install', (e) => {{
  e.waitUntil(caches.open(CACHE_NAME).then((c) => c.addAll(PRECACHE)));
  self.skipWaiting();
}});

self.addEventListener('activate', (e) => {{
  e.waitUntil(caches.keys().then((keys) =>
    Promise.all(keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k)))
  ));
  self.clients.claim();
}});

self.addEventListener('fetch', (e) => {{
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then((cached) => cached || fetch(e.request).then((res) => {{
      if (res.ok && e.request.url.includes('/{OUT_DIR}/')) {{
        const clone = res.clone();
        caches.open(CACHE_NAME).then((c) => c.put(e.request, clone));
      }}
      return res;
    }}))
  );
}});
"""


def write_shared_assets(dry_run: bool, strongs_dict: dict) -> None:
    assets_dir = OUT_DIR / "assets"
    write_if_changed(assets_dir / "style.css", SHARED_CSS, dry_run)
    write_if_changed(assets_dir / "reader.js", SHARED_JS, dry_run)
    write_if_changed(assets_dir / "interlinear.css", INTERLINEAR_CSS, dry_run)
    write_if_changed(assets_dir / "strongs.js", generate_strongs_js(strongs_dict), dry_run)
    write_if_changed(OUT_DIR / "manifest.json", generate_manifest_json(), dry_run)
    write_if_changed(Path("sw.js"), generate_service_worker(), dry_run)


def resolve_active_versions(only_csv: str):
    """Return VERSIONS rows to build. Empty only_csv means all versions."""
    valid_ids = {v[0] for v in VERSIONS}
    if not (only_csv or "").strip():
        return list(VERSIONS)
    wanted = {x.strip() for x in only_csv.split(",") if x.strip()}
    unknown = wanted - valid_ids
    if unknown:
        raise SystemExit(
            f"Unknown version id(s): {sorted(unknown)}. Valid ids: {sorted(valid_ids)}"
        )
    return [v for v in VERSIONS if v[0] in wanted]


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    global OUT_DIR
    parser = argparse.ArgumentParser(
        description="Generate static Bible HTML under ./bible/",
    )
    parser.add_argument(
        "--only",
        metavar="IDS",
        default="",
        help=(
            "Comma-separated version ids to build (e.g. telugu). Default: all versions. "
            "Note: /bible/ index still lists all VERSIONS as reader cards; only chapter/verse "
            "pages are limited by this flag."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count and report outputs without writing files.",
    )
    parser.add_argument(
        "--output",
        default="bible",
        help="Output directory (default: bible).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip chapter/verse generation for versions that already have output.",
    )
    parser.add_argument(
        "--modules",
        default="all",
        help="Comma-separated modules: assets,indexes,chapters,verses,parallel,sitemap (default: all).",
    )
    args = parser.parse_args()
    OUT_DIR = Path(args.output)
    selected_modules = parse_modules(args.modules)

    print("=" * 60)
    print("  BSWS Phase 3 — Static Bible Site Generator")
    print("=" * 60)

    valid_ids = {v[0] for v in VERSIONS}
    if DEFAULT_VERSION_ID not in valid_ids:
        raise SystemExit(
            f"DEFAULT_VERSION_ID {DEFAULT_VERSION_ID!r} must be one of: {sorted(valid_ids)}"
        )

    active_versions = resolve_active_versions(args.only)
    active_ids = {v[0] for v in active_versions}
    x_default_id = (
        DEFAULT_VERSION_ID
        if DEFAULT_VERSION_ID in active_ids
        else active_versions[0][0]
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_sitemap_urls = []
    total_pages = 0
    bible_by_id = {}
    global_strongs_dict = {}

    print(
        f"\n[prep] Loading JSON data for {len(active_versions)} version(s): "
        f"{', '.join(v[0] for v in active_versions)}..."
    )
    for version_id, vlabel, lang_code, script, group in active_versions:
        data_raw = download_json(version_id)
        if not data_raw:
            print(f"  [warn] skipped {version_id} — could not load JSON")
            continue

        bible = normalise(data_raw)
        bible_by_id[version_id] = bible

    if should_run("assets", selected_modules):
        if not global_strongs_dict:
            global_strongs_dict = load_local_json(LOCAL_STRONGS_JSON, "strongs dictionary")
        print("\n[assets] Writing shared assets...")
        write_shared_assets(dry_run=args.dry_run, strongs_dict=global_strongs_dict)

    if should_run("indexes", selected_modules):
        print("\n[indexes] Writing bible and version indexes...")
        write_if_changed(
            OUT_DIR / "index.html",
            generate_bible_index(active_versions, x_default_id),
            args.dry_run,
        )
        for version_id, vlabel, lang_code, script, group in active_versions:
            bible = bible_by_id.get(version_id)
            if not bible:
                continue
            ver_dir = OUT_DIR / version_id
            ver_dir.mkdir(parents=True, exist_ok=True)
            write_if_changed(
                ver_dir / "index.html",
                generate_version_index_page(version_id, vlabel, lang_code, bible["books"]),
                args.dry_run,
            )
            for book in bible["books"]:
                bslug = book_slug(book["n"])
                write_if_changed(
                    ver_dir / bslug / "index.html",
                    generate_book_index_page(version_id, vlabel, lang_code, book),
                    args.dry_run,
                )

    if should_run("chapters", selected_modules) or should_run("verses", selected_modules):
        print(
            f"\n[content] Generating chapters/verses for {len(active_versions)} version(s): "
            f"{', '.join(v[0] for v in active_versions)}..."
        )

    for version_id, vlabel, lang_code, script, group in active_versions:
        if not (should_run("chapters", selected_modules) or should_run("verses", selected_modules)):
            break

        print(f"\n  ▸ {vlabel} ({version_id})")
        bible = bible_by_id.get(version_id)
        if not bible:
            print(f"    Skipped — could not load JSON")
            continue
        all_books = bible["books"]
        verse_lookup = build_verse_lookup(all_books, version_id)

        crossrefs_data = {}
        strongs_dict = {}
        interlinear_map = {}
        interlinear_book_cache = {}
        if version_has_verse_detail_features(version_id):
            crossrefs_data = load_local_json(LOCAL_CROSSREFS_JSON, "crossrefs_mobile.json")
            strongs_dict = global_strongs_dict or load_local_json(LOCAL_STRONGS_JSON, "strongs dictionary")
            interlinear_map = load_interlinear_book_mapping()

        # Flat list of all (book, chapter) for prev/next navigation
        all_chapters = []
        for bk in all_books:
            for ch in bk["ch"]:
                all_chapters.append((bk, ch))

        ver_dir = OUT_DIR / version_id
        ver_dir.mkdir(exist_ok=True)

        if args.resume and ver_dir.exists() and any(ver_dir.iterdir()):
            print(f"    [RESUME] Skipping {version_id} — output already exists.")
            continue

        version_pages = 0
        version_verse_pages = 0
        for idx, (book, chapter) in enumerate(all_chapters):
            bslug  = book_slug(book["n"])
            ch_num = chapter["c"]

            # Prev / next URLs
            prev_url = None
            next_url = None
            if idx > 0:
                pb, pc = all_chapters[idx - 1]
                prev_url = f"/{OUT_DIR}/{version_id}/{book_slug(pb['n'])}/{pc['c']}/"
            if idx < len(all_chapters) - 1:
                nb, nc = all_chapters[idx + 1]
                next_url = f"/{OUT_DIR}/{version_id}/{book_slug(nb['n'])}/{nc['c']}/"

            html = generate_chapter_page(
                bible_data=bible,
                version_id=version_id,
                vlabel=vlabel,
                lang_code=lang_code,
                book=book,
                chapter=chapter,
                all_books=all_books,
                prev_url=prev_url,
                next_url=next_url,
                active_versions=active_versions,
                x_default_id=x_default_id,
            )

            out_path = ver_dir / bslug / str(ch_num)
            out_path.mkdir(parents=True, exist_ok=True)
            if should_run("chapters", selected_modules):
                write_if_changed(out_path / "index.html", html, args.dry_run)

            page_url = f"{SITE_URL}/{OUT_DIR}/{version_id}/{bslug}/{ch_num}/"
            if should_run("chapters", selected_modules):
                all_sitemap_urls.append(page_url)
                total_pages += 1
                version_pages += 1

            interlinear_chapters_for_book = {}
            if version_has_verse_detail_features(version_id):
                abbrev = interlinear_map.get(book.get("b"), "")
                if abbrev:
                    if abbrev not in interlinear_book_cache:
                        interlinear_book_cache[abbrev] = load_interlinear_book_tokens(abbrev)
                    interlinear_chapters_for_book = interlinear_book_cache.get(abbrev, {})

            verse_items = sorted(chapter["v"].items(), key=lambda x: int(x[0]))
            for v_idx, (vnum, vtext) in enumerate(verse_items):
                prev_verse_url = (
                    verse_detail_rel_url(version_id, bslug, ch_num, verse_items[v_idx - 1][0])
                    if v_idx > 0
                    else None
                )
                next_verse_url = (
                    verse_detail_rel_url(version_id, bslug, ch_num, verse_items[v_idx + 1][0])
                    if v_idx < len(verse_items) - 1
                    else None
                )
                chapter_url = f"/{OUT_DIR}/{version_id}/{bslug}/{ch_num}/"
                verse_html = generate_verse_detail_page(
                    version_id=version_id,
                    vlabel=vlabel,
                    lang_code=lang_code,
                    book_name=display_book_name(book, version_id),
                    book_name_source=book["n"],
                    bslug=bslug,
                    ch_num=ch_num,
                    vnum=vnum,
                    verse_text=vtext,
                    prev_verse_url=prev_verse_url,
                    next_verse_url=next_verse_url,
                    chapter_url=chapter_url,
                    active_versions=active_versions,
                    x_default_id=x_default_id,
                    verse_lookup=verse_lookup,
                    crossrefs_data=crossrefs_data,
                    strongs_dict=strongs_dict,
                    interlinear_chapters=interlinear_chapters_for_book,
                )
                verse_out_path = ver_dir / bslug / str(ch_num) / str(vnum)
                verse_out_path.mkdir(parents=True, exist_ok=True)
                if should_run("verses", selected_modules):
                    write_if_changed(verse_out_path / "index.html", verse_html, args.dry_run)
                    all_sitemap_urls.append(f"{SITE_URL}/{OUT_DIR}/{version_id}/{bslug}/{ch_num}/{vnum}/")
                    total_pages += 1
                    version_verse_pages += 1

        print(
            f"    ✓ {version_pages} chapter pages + {version_verse_pages} verse pages "
            f"for {version_id} (running total: {total_pages})"
        )

    # Parallel two-column chapters (same book/chapter, two built translations)
    if should_run("parallel", selected_modules):
        print(
            f"\n[parallel] Generating parallel chapter pages (mode={PARALLEL_LINK_MODE!r})..."
        )
    parallel_pages = 0
    par_root = OUT_DIR / "parallel"
    pairs = list(iter_parallel_version_pairs(active_versions, x_default_id))
    for vp, vs in pairs:
        if not should_run("parallel", selected_modules):
            break
        bible_p = bible_by_id.get(vp)
        bible_s = bible_by_id.get(vs)
        if not bible_p or not bible_s:
            continue
        vlabel_p = version_label(vp)
        vlabel_s = version_label(vs)
        all_books_p = bible_p["books"]
        all_chapters = []
        for bk in all_books_p:
            for ch in bk["ch"]:
                all_chapters.append((bk, ch))

        for idx, (book, chapter) in enumerate(all_chapters):
            bslug = book_slug(book["n"])
            ch_num = chapter["c"]
            pref = f"/{OUT_DIR}/parallel/{vp}/{vs}"
            prev_url = None
            next_url = None
            if idx > 0:
                pb, pc = all_chapters[idx - 1]
                prev_url = f"{pref}/{book_slug(pb['n'])}/{pc['c']}/"
            if idx < len(all_chapters) - 1:
                nb, nc = all_chapters[idx + 1]
                next_url = f"{pref}/{book_slug(nb['n'])}/{nc['c']}/"

            html_par = generate_parallel_chapter_page(
                bible_p=bible_p,
                bible_s=bible_s,
                vp=vp,
                vs=vs,
                vlabel_p=vlabel_p,
                vlabel_s=vlabel_s,
                lang_p=version_lang(vp),
                book_p=book,
                chapter_p=chapter,
                all_books=all_books_p,
                prev_url=prev_url,
                next_url=next_url,
                active_versions=active_versions,
                x_default_id=x_default_id,
            )
            out_path = par_root / vp / vs / bslug / str(ch_num)
            out_path.mkdir(parents=True, exist_ok=True)
            write_if_changed(out_path / "index.html", html_par, args.dry_run)
            parallel_pages += 1
            total_pages += 1

    if should_run("parallel", selected_modules):
        print(f"    ✓ {parallel_pages} parallel chapter pages (not added to sitemap; noindex)")

    if should_run("sitemap", selected_modules):
        print(f"\n[sitemap] Writing sitemap.xml ({len(all_sitemap_urls)} URLs)...")
        write_if_changed(OUT_DIR / "sitemap.xml", generate_sitemap(all_sitemap_urls), args.dry_run)

        # robots.txt in repo root
        write_if_changed(Path("robots.txt"), ROBOTS_TXT, args.dry_run)

    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"  [DRY RUN] Would write/update {total_pages} content pages.")
    else:
        print(f"  ✅ Done! {total_pages} pages generated (chapters + verses + parallel).")
    print(f"  📁 Output: ./{OUT_DIR}/")
    if should_run("sitemap", selected_modules):
        print(f"  🗺  Sitemap: ./{OUT_DIR}/sitemap.xml ({len(all_sitemap_urls)} URLs)")
        print(f"  🤖 robots.txt: ./robots.txt")
    print()
    print("  Next steps: run targeted modules and verify output.")
    print("=" * 60)


if __name__ == "__main__":
    main()
