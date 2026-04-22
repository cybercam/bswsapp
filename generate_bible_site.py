#!/usr/bin/env python3
"""
BSWS Phase 3 — Static Bible Site Generator
============================================
Downloads all 15 Bible JSONs from cybercam/bibles_json on GitHub,
then generates one HTML file per chapter for every version.

Run this from the ROOT of your cybercam/bswsapp repo:
  python3 generate_bible_site.py
  python3 generate_bible_site.py --only telugu   # subset build

Then:
  git add .
  git commit -m "Phase 3: static Bible pages"
  git push

Output:
  bible/index.html              ← landing page with version/language grid
  bible/sitemap.xml             ← all chapter URLs for Google
  bible/<version>/<book>/<ch>/index.html   ← one page per chapter
"""

import argparse
import html
import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

# ─── CONFIG ───────────────────────────────────────────────────────────────────

SITE_URL   = "https://bswsapp.com"
OUT_DIR    = Path("bible")           # output folder inside bswsapp repo
CACHE_DIR  = Path(".bible_cache")   # local JSON cache so you don't re-download
TODAY      = date.today().isoformat()

# Must exist in VERSIONS — used for x-default hreflang, hero CTA, and JSON-LD SearchAction.
DEFAULT_VERSION_ID = "kjv"

DOWNLOAD_ATTEMPTS = 3
RETRY_DELAY_SEC   = 1.0

CDN_BASE       = "https://cdn.jsdelivr.net/gh/cybercam/bibles_json@main"
GITHUB_RAW     = "https://raw.githubusercontent.com/cybercam/bibles_json/main"
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.biblestudywithsteffi.app"

# All 15 versions confirmed in the repo
VERSIONS = [
    # id,          label,                      lang,  script,   group
    ("asv",        "American Standard Version","en",  "latin",  "English"),
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
    "asv":"en","bbe":"en","kjv":"en","nkjv":"en","web":"en","ylt":"en",
    "bengali":"bn","gujarati":"gu","hindi":"hi","kannada":"kn",
    "malayalam":"ml","marathi":"mr","nepali":"ne","odia":"or","tamil":"ta",
    "telugu":"te",
}

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


def version_label(version_id):
    for vid, label, *_ in VERSIONS:
        if vid == version_id:
            return label
    return version_id.upper()


def display_book_name(book: dict, version_id: str) -> str:
    """Render Telugu names for Telugu version, fallback to source JSON name."""
    if version_id == "telugu":
        return TELUGU_BOOK_NAMES.get(book.get("b"), book.get("n", ""))
    return book.get("n", "")


# ─── HTML TEMPLATES ───────────────────────────────────────────────────────────

SHARED_CSS = """
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
.v-row{display:flex;gap:10px;padding:9px 10px;cursor:pointer;border-radius:7px;transition:background .12s;-webkit-tap-highlight-color:transparent}
.v-row:hover,.v-row.sel{background:var(--card)}
.v-num{font-family:'Cinzel',serif;font-size:11px;color:var(--vnum);min-width:26px;padding-top:5px;flex-shrink:0;text-align:right;font-weight:600}
.v-txt{font-family:'Lora',Georgia,serif;font-size:var(--verse-font-size,clamp(16px,4vw,19px));line-height:1.9;color:var(--text)}
:lang(te) body,:lang(te) .v-txt,:lang(te) .book-btn,:lang(te) #s-search,:lang(te) .sr-txt{font-family:'Noto Sans Telugu','Lora',Georgia,serif}

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

  // Font size controls
  initFontScale();
  document.getElementById('font-inc-btn')?.addEventListener('click', () => updateFontScale(0.1));
  document.getElementById('font-dec-btn')?.addEventListener('click', () => updateFontScale(-0.1));

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
"""


def html_head(title, description, canonical, lang, hreflang_links, keywords=""):
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
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
{"<link href=\"https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;500;600;700&display=swap\" rel=\"stylesheet\"/>" + chr(10) if lang == "te" else ""}<link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Lora:ital,wght@0,400;0,500;1,400&display=swap" rel="stylesheet"/>
<style>{SHARED_CSS}</style>
</head>"""


def sidebar_html(all_books, current_book_num, current_ch, version_id, vlabel, active_versions):
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
  <input id="s-search" type="search" placeholder="Search this chapter…" autocomplete="off"/>
  <div id="sr"></div>
  {'<div class="s-section">Chapters</div><div id="ch-grid">' + ch_html + '</div>' if ch_html else ''}
  <div class="s-section">Books</div>
  {books_html}
</aside>
<div id="overlay"></div>"""


def topbar_html(crumb):
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
  <button type="button" id="par-btn" class="icon-btn" aria-label="Compare parallel Bible versions">||</button>
  <button type="button" id="theme-btn" class="icon-btn" aria-label="Reading theme and colors">Aa</button>
</header>"""


def verse_action_bar():
    return f"""
<div id="vbar">
  <div id="vbar-meta" class="vbar-meta">0 verses selected</div>
  <button id="tts-chapter-btn">Read Chapter</button>
  <button id="tts-loop-btn">Loop Off</button>
  <button id="tts-auto-btn">Auto-Read Off</button>
  <button id="copy-btn">Copy</button>
  <button id="share-btn">Share</button>
  <button id="tts-play-btn">Speak</button>
  <button id="tts-stop-btn">Stop</button>
  <button id="tts-download-btn">Download</button>
  <button id="clear-sel-btn">Clear</button>
  <div class="vbar-speed">
    <label for="tts-rate">Speed</label>
    <input id="tts-rate" type="range" min="0.7" max="1.5" step="0.1" value="1.0"/>
  </div>
  <a class="cta-btn" href="{PLAY_STORE_URL}" target="_blank" rel="noopener">Memorize in App ↗</a>
</div>"""


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
        verse_rows += f'<div class="v-row" data-ref="{safe_ref}" onclick="selectVerse(this)"><span class="v-num">{vnum}</span><span class="v-txt">{safe_text}</span></div>\n'

    # Prev / next nav
    prev_link = f'<a href="{prev_url}">← Previous</a>' if prev_url else '<a class="disabled">← Previous</a>'
    next_link = f'<a href="{next_url}">Next →</a>' if next_url else '<a class="disabled">Next →</a>'

    head = html_head(title, description, canonical, lang_code, hreflang_str, keywords)

    return f"""{head}
<body>
{topbar_html(f"{book_name} {ch_num} · {vlabel}")}
{sidebar_html(all_books, book_num, ch_num, version_id, vlabel, active_versions)}
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
  <aside id="par-panel">
    <p class="par-head">Parallel Version</p>
    <select class="par-ver-select" onchange="window.location='/{OUT_DIR}/'+this.value+'/{bslug}/{ch_num}/'">
      {''.join(f'<option value="{vid}">{vlab}</option>' for vid,vlab,*_ in active_versions)}
    </select>
    <p style="font-size:13px;color:var(--muted)">Select a version above to compare.</p>
  </aside>
</div>
{verse_action_bar()}
{theme_sheet()}
<script>{SHARED_JS}</script>
</body>
</html>"""


# ─── BIBLE INDEX PAGE ─────────────────────────────────────────────────────────

def generate_bible_index(active_versions, x_default_id):
    canonical = f"{SITE_URL}/{OUT_DIR}/"
    n = len(active_versions)
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
        hero_p = f"Free Bible reader — {vlbl0}. No ads, no login required."
        hero_cta_href = f"/{OUT_DIR}/{vid0}/john/1/"
        hero_cta_label = f"Start reading — John 1 ({vlbl0})"
        english_section = ""
        indian_section = ""
        one_grid = f'<div class="ver-grid"><a href="/{OUT_DIR}/{vid0}/john/1/" class="ver-card"><div class="vc-label">{vlbl0}</div><div class="vc-sub">Open reader</div></a></div>'
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
        for vid, vlbl, vlng, vscript, vgroup in active_versions:
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
    {app_cta_banner()}
  </div>
</div>
{theme_sheet()}
<script>{SHARED_JS}</script>
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
    parser = argparse.ArgumentParser(
        description="Generate static Bible HTML under ./bible/",
    )
    parser.add_argument(
        "--only",
        metavar="IDS",
        default="",
        help="Comma-separated version ids to build (e.g. telugu). Default: all versions.",
    )
    args = parser.parse_args()

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

    # Write Bible index page
    print("\n[1/3] Generating bible/index.html...")
    with open(OUT_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(generate_bible_index(active_versions, x_default_id))
    # bible/ root URL is emitted inside generate_sitemap() (high priority); do not duplicate here.

    # Process each version
    print(
        f"\n[2/3] Generating chapter pages for {len(active_versions)} version(s): "
        f"{', '.join(v[0] for v in active_versions)}..."
    )
    for version_id, vlabel, lang_code, script, group in active_versions:
        print(f"\n  ▸ {vlabel} ({version_id})")

        data_raw = download_json(version_id)
        if not data_raw:
            print(f"    Skipped — could not load JSON")
            continue

        bible = normalise(data_raw)
        all_books = bible["books"]

        # Flat list of all (book, chapter) for prev/next navigation
        all_chapters = []
        for bk in all_books:
            for ch in bk["ch"]:
                all_chapters.append((bk, ch))

        ver_dir = OUT_DIR / version_id
        ver_dir.mkdir(exist_ok=True)

        version_pages = 0
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
            with open(out_path / "index.html", "w", encoding="utf-8") as f:
                f.write(html)

            page_url = f"{SITE_URL}/{OUT_DIR}/{version_id}/{bslug}/{ch_num}/"
            all_sitemap_urls.append(page_url)
            total_pages += 1
            version_pages += 1

        print(f"    ✓ {version_pages} chapter pages for {version_id} (running total: {total_pages})")

    # Sitemap
    print(f"\n[3/3] Writing sitemap.xml ({len(all_sitemap_urls)} URLs)...")
    with open(OUT_DIR / "sitemap.xml", "w", encoding="utf-8") as f:
        f.write(generate_sitemap(all_sitemap_urls))

    # robots.txt in repo root
    with open("robots.txt", "w", encoding="utf-8") as f:
        f.write(ROBOTS_TXT)

    print("\n" + "=" * 60)
    print(f"  ✅ Done! {total_pages} chapter pages generated.")
    print(f"  📁 Output: ./{OUT_DIR}/")
    print(f"  🗺  Sitemap: ./{OUT_DIR}/sitemap.xml ({len(all_sitemap_urls)} URLs)")
    print(f"  🤖 robots.txt: ./robots.txt")
    print()
    print("  Next steps:")
    print("  1. git add .")
    print('  2. git commit -m "Phase 3: static Bible pages"')
    print("  3. git push")
    print("  4. Submit sitemap to Google Search Console:")
    print(f"     {SITE_URL}/bible/sitemap.xml")
    print("=" * 60)


if __name__ == "__main__":
    main()
