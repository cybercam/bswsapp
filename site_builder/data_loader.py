"""Bible JSON and aux data loading."""
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

from .config import (
    CACHE_DIR,
    CDN_BASE,
    DOWNLOAD_ATTEMPTS,
    GITHUB_RAW,
    INTERLINEAR_CACHE_DIR,
    INTERLINEAR_RAW_BASE,
    LOCAL_BIBLE_DATA_DIR,
    RETRY_DELAY_SEC,
)
from .helpers import book_slug, display_book_name

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


def build_bcv_text_map(bible: dict) -> dict[str, str]:
    """
    Map \"{book_num}_{chapter}_{verse}\" -> verse text for quick English parallel lookups.
    """
    out: dict[str, str] = {}
    for bk in bible.get("books", []):
        b_num = bk.get("b")
        for ch in bk.get("ch", []):
            c_num = ch.get("c")
            verses = ch.get("v") or {}
            for v_num, txt in verses.items():
                out[f"{b_num}_{c_num}_{v_num}"] = str(txt or "")
    return out


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
