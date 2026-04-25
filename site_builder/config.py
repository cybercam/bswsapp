"""Site generator configuration."""
from datetime import date
from pathlib import Path

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
ASSET_NAV_JS_PATTERN = "assets/nav-{version_id}.js"
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

OG_LOCALE = {
    "bbe":"en_US","kjv":"en_US","nkjv":"en_US","web":"en_US","ylt":"en_US",
    "bengali":"bn_IN","gujarati":"gu_IN","hindi":"hi_IN","kannada":"kn_IN",
    "malayalam":"ml_IN","marathi":"mr_IN","nepali":"ne_NP","odia":"or_IN",
    "tamil":"ta_IN","telugu":"te_IN",
}

ALL_MODULES = {"assets", "indexes", "chapters", "verses", "parallel", "popular", "sitemap"}

# Short attribution lines for generated chapter pages (no unverified publisher/copyright claims).
VERSION_ATTRIBUTION_HTML = {
    "telugu": "ఈ అధ్యాయం <strong>తెలుగు బైబిల్</strong> లేఅవుట్‌లో Bible Study with Steffi రీడర్ ద్వారా చూపబడుతుంది.",
    "hindi": "This chapter is shown in the <strong>हिन्दी बाइबिल</strong> reader in Bible Study with Steffi.",
    "tamil": "This chapter is shown in the <strong>தமிழ் பரிசுத்த வேதாகமம்</strong> reader in Bible Study with Steffi.",
    "kannada": "This chapter is shown in the <strong>ಕನ್ನಡ ಬೈಬಲ್</strong> reader in Bible Study with Steffi.",
    "malayalam": "This chapter is shown in the <strong>മലയാളം ബൈബിൾ</strong> reader in Bible Study with Steffi.",
    "odia": "This chapter is shown in the <strong>ଓଡ଼ିଆ ବାଇବେଲ</strong> reader in Bible Study with Steffi.",
    "bengali": "This chapter is shown in the <strong>বাংলা বাইবেল</strong> reader in Bible Study with Steffi.",
    "marathi": "This chapter is shown in the <strong>मराठी बायबल</strong> reader in Bible Study with Steffi.",
    "gujarati": "This chapter is shown in the <strong>ગુજરાતી બાઇબલ</strong> reader in Bible Study with Steffi.",
    "nepali": "This chapter is shown in the <strong>नेपाली बाइबल</strong> reader in Bible Study with Steffi.",
    "kjv": "This chapter is shown in the <strong>King James Version</strong> reader in Bible Study with Steffi.",
    "nkjv": "This chapter is shown in the <strong>New King James Version</strong> reader in Bible Study with Steffi.",
    "web": "This chapter is shown in the <strong>World English Bible</strong> reader in Bible Study with Steffi.",
    "bbe": "This chapter is shown in the <strong>Bible in Basic English</strong> reader in Bible Study with Steffi.",
    "ylt": "This chapter is shown in <strong>Young's Literal Translation</strong> in Bible Study with Steffi.",
    "_default": "Text is displayed using the reader version named on this page within Bible Study with Steffi.",
}

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

TELUGU_BOOK_NAMES = {
    1: "ఆదికాండము",
    2: "నిర్గమకాండము",
    3: "లేవీయకాండము",
    4: "సంఖ్యాకాండము",
    5: "ద్వితీయోపదేశకాండము",
    6: "యెహోషువ",
    7: "న్యాయాధిపతులు",
    8: "రూతు",
    9: "1 సాముయేలు",
    10: "2 సాముయేలు",
    11: "1 రాజులు",
    12: "2 రాజులు",
    13: "1 దినవృత్తాంతములు",
    14: "2 దినవృత్తాంతములు",
    15: "ఎజ్రా",
    16: "నెహెమ్యా",
    17: "ఎస్తేరు",
    18: "యోబు గ్రంథము",
    19: "కీర్తనల గ్రంథము",
    20: "సామెతలు",
    21: "ప్రసంగి",
    22: "పరమగీతము",
    23: "యెషయా గ్రంథము",
    24: "యిర్మియా గ్రంథము",
    25: "విలాపవాక్యములు",
    26: "యెహెజ్కేలు",
    27: "దానియేలు",
    28: "హోషేయ",
    29: "యోవేలు",
    30: "ఆమోసు",
    31: "ఓబద్యా",
    32: "యోనా",
    33: "మీకా",
    34: "నహూము",
    35: "హబక్కూకు",
    36: "జెఫన్యా",
    37: "హగ్గయి",
    38: "జెకర్యా",
    39: "మలాకీ",
    40: "మత్తయి సువార్త",
    41: "మార్కు సువార్త",
    42: "లూకా సువార్త",
    43: "యోహాను సువార్త",
    44: "అపొస్తలుల కార్యములు",
    45: "రోమీయులకు",
    46: "1 కొరింథీయులకు",
    47: "2 కొరింథీయులకు",
    48: "గలతీయులకు",
    49: "ఎఫెసీయులకు",
    50: "ఫిలిప్పీయులకు",
    51: "కొలొస్సయులకు",
    52: "1 థెస్సలొనీకయులకు",
    53: "2 థెస్సలొనీకయులకు",
    54: "1 తిమోతయుకు",
    55: "2 తిమోతయుకు",
    56: "తీతుకు",
    57: "ఫిలేమోనుకు",
    58: "హెబ్రీయులకు",
    59: "యాకోబు",
    60: "1 పేతురు",
    61: "2 పేతురు",
    62: "1 యోహాను",
    63: "2 యోహాను",
    64: "3 యోహాను",
    65: "యూదా",
    66: "ప్రకటన గ్రంథము",
}


def apply_cli_config(output: str) -> None:
    global OUT_DIR
    OUT_DIR = Path(output)
