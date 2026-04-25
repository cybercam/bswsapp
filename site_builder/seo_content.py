"""Curated SEO copy and verse lists — data-driven, not hand-edited HTML per page."""
from __future__ import annotations

# Top Telugu books for richer landing pages (URL slugs).
TELUGU_SEO_BOOK_SLUGS: frozenset[str] = frozenset(
    {
        "john",
        "psalms",
        "matthew",
        "genesis",
        "romans",
        "isaiah",
        "proverbs",
        "revelation",
        "acts",
        "luke",
    }
)

# (version_id, book_slug) -> HTML intro (one short block). Telugu-focused per plan.
BOOK_INTRO_HTML: dict[tuple[str, str], str] = {
    ("telugu", "john"): (
        "<p>యోహాను సువార్త మీకు యేసు క్రీస్తు జీవితం, మరణం, పునరుత్థానం మరియు "
        "నిత్యజీవం గురించి స్పష్టమైన సాక్ష్యాన్ని ఇస్తుంది. ఇక్కడ ప్రతి అధ్యాయాన్ని "
        "తెలుగులో చదవండి.</p>"
    ),
    ("telugu", "psalms"): (
        "<p>కీర్తనల గ్రంథం ఆరాధన, ప్రార్థన మరియు దేవునితో నడిచే జీవితానికి ఒక "
        "భాష. తెలుగు బైబిల్‌లో అధ్యాయం అధ్యాయంగా చదవండి.</p>"
    ),
    ("telugu", "matthew"): (
        "<p>మత్తయి సువార్త యేసు క్రీస్తు రాజ్య ప్రకటనను మరియు శిష్యులకు బోధనను "
        "వివరిస్తుంది. తెలుగులో మత్తయి అధ్యాయాలను ఇక్కడ నుండి తెరవండి.</p>"
    ),
    ("telugu", "genesis"): (
        "<p>ఆదికాండము సృష్టి, నిబంధనలు మరియు దేవుని ప్రజల చరిత్రను ప్రారంభిస్తుంది. "
        "తెలుగు బైబిల్‌లో ప్రతి అధ్యాయాన్ని చదవండి.</p>"
    ),
    ("telugu", "romans"): (
        "<p>రోమీయులకు రాసిన పత్రిక విశ్వాసం, కృప మరియు జీవించు మార్గం గురించి "
        "లోతైన బోధన ఇస్తుంది. అధ్యాయాలను తెలుగులో ఇక్కడ నుండి ఎంచుకోండి.</p>"
    ),
    ("telugu", "isaiah"): (
        "<p>యెషయా ప్రవచన గ్రంథం న్యాయాధిపత్యం, విమోచన మరియు రాబోయే రాజ్యం గురించి "
        "బలమైన సందేశాలు ఇస్తుంది. తెలుగులో అధ్యాయాలను చదవండి.</p>"
    ),
    ("telugu", "proverbs"): (
        "<p>సామెతలు జ్ఞానం, నడత మరియు దైవభీతి గురించి సంక్షిప్త బోధనలు ఇస్తుంది. "
        "తెలుగు బైబిల్‌లో ప్రతి అధ్యాయాన్ని ఇక్కడ నుండి తెరవండి.</p>"
    ),
    ("telugu", "revelation"): (
        "<p>ప్రకటన గ్రంథం క్రీస్తు విజయం మరియు నూతన సృష్టి గురించి దృశ్య రూపకాలతో "
        "వివరిస్తుంది. తెలుగులో అధ్యాయాలను చదవండి.</p>"
    ),
    ("telugu", "acts"): (
        "<p>అపొస్తలుల కార్యములు సువార్త వ్యాప్తి మరియు మొదటి సంఘం చరిత్రను వివరిస్తుంది. "
        "తెలుగు బైబిల్‌లో అధ్యాయాలను ఇక్కడ నుండి ఎంచుకోండి.</p>"
    ),
    ("telugu", "luke"): (
        "<p>లూకా సువార్త రక్షకుని కరుణ మరియు ప్రజలకు దేవుని వాక్కు సాక్ష్యాన్ని "
        "అందంగా చిత్రీకరిస్తుంది. తెలుగులో అధ్యాయాలను చదవండి.</p>"
    ),
}

# (version_id, book_slug) -> list of (chapter, verse) for “famous verses” links on book pages.
BOOK_FAMOUS_VERSES: dict[tuple[str, str], list[tuple[int, int]]] = {
    ("telugu", "john"): [(1, 1), (1, 14), (3, 16), (3, 17), (14, 6), (15, 13)],
    ("telugu", "psalms"): [(23, 1), (23, 4), (51, 10), (91, 1), (119, 105)],
    ("telugu", "matthew"): [(5, 3), (6, 9), (6, 33), (11, 28), (28, 19)],
    ("telugu", "genesis"): [(1, 1), (1, 27), (12, 2), (50, 20)],
    ("telugu", "romans"): [(3, 23), (5, 8), (8, 28), (10, 9), (12, 2)],
    ("telugu", "isaiah"): [(9, 6), (40, 31), (53, 5), (61, 1)],
    ("telugu", "proverbs"): [(3, 5), (3, 6), (16, 3), (22, 6)],
    ("telugu", "revelation"): [(1, 8), (3, 20), (21, 4), (22, 17)],
    ("telugu", "acts"): [(1, 8), (2, 38), (4, 12), (16, 31)],
    ("telugu", "luke"): [(2, 11), (6, 31), (15, 11), (19, 10)],
}

# version:slug:chapter -> verse numbers for “Popular in this chapter” (curated only).
CHAPTER_NOTABLE_VERSES: dict[str, list[int]] = {
    "telugu:john:3": [16, 17, 36],
    "telugu:psalms:23": [1, 4, 6],
    "telugu:romans:8": [28, 31, 38, 39],
    "telugu:genesis:1": [1, 27],
    "telugu:matthew:5": [3, 16, 44],
}

# Optional FAQ for users / clarity — not relied on for Google FAQ rich results.
CHAPTER_FAQ: dict[str, list[tuple[str, str]]] = {
    "telugu:john:3": [
        (
            "యోహాను 3:16 లో ఏమి చెప్పబడింది?",
            "దేవుడు లోకాన్ని ఎంతగా ప్రేమించాడో మరియు ఆయన కుమారుడిలో విశ్వసించేవారికి "
            "నిత్యజీవం లభించే విధంగా ఆయనను ఇచ్చాడో ఈ అధ్యాయం వివరిస్తుంది.",
        ),
    ],
    "telugu:psalms:23": [
        (
            "కీర్తన 23 ఎవరి గురించి?",
            "దేవుడు మేపరిగా తన ప్రజలను నడిపించే విధానాన్ని ఈ కీర్తన చిత్రీకరిస్తుంది.",
        ),
    ],
}

# Curated popular-verse landing pages: slug URL under /bible/{version_id}/{slug}/
POPULAR_VERSE_LANDING_PAGES: list[dict[str, int | str]] = [
    {"version_id": "telugu", "slug": "john-3-16", "bslug": "john", "ch": 3, "v": 16},
    {"version_id": "telugu", "slug": "john-1-1", "bslug": "john", "ch": 1, "v": 1},
    {"version_id": "telugu", "slug": "psalm-23", "bslug": "psalms", "ch": 23, "v": 1},
    {"version_id": "telugu", "slug": "romans-8-28", "bslug": "romans", "ch": 8, "v": 28},
    {"version_id": "telugu", "slug": "genesis-1-1", "bslug": "genesis", "ch": 1, "v": 1},
    {"version_id": "telugu", "slug": "matthew-5-3", "bslug": "matthew", "ch": 5, "v": 3},
    {"version_id": "telugu", "slug": "philippians-4-13", "bslug": "philippians", "ch": 4, "v": 13},
    {"version_id": "telugu", "slug": "jeremiah-29-11", "bslug": "jeremiah", "ch": 29, "v": 11},
    {"version_id": "telugu", "slug": "isaiah-53-5", "bslug": "isaiah", "ch": 53, "v": 5},
    {"version_id": "telugu", "slug": "proverbs-3-5", "bslug": "proverbs", "ch": 3, "v": 5},
    {"version_id": "telugu", "slug": "joshua-1-9", "bslug": "joshua", "ch": 1, "v": 9},
    {"version_id": "telugu", "slug": "matthew-28-19", "bslug": "matthew", "ch": 28, "v": 19},
    {"version_id": "telugu", "slug": "acts-16-31", "bslug": "acts", "ch": 16, "v": 31},
    {"version_id": "telugu", "slug": "revelation-3-20", "bslug": "revelation", "ch": 3, "v": 20},
    {"version_id": "telugu", "slug": "romans-10-9", "bslug": "romans", "ch": 10, "v": 9},
    {"version_id": "telugu", "slug": "ephesians-2-8", "bslug": "ephesians", "ch": 2, "v": 8},
    {"version_id": "telugu", "slug": "2-timothy-3-16", "bslug": "2-timothy", "ch": 3, "v": 16},
    {"version_id": "telugu", "slug": "hebrews-11-1", "bslug": "hebrews", "ch": 11, "v": 1},
    {"version_id": "telugu", "slug": "1-john-4-8", "bslug": "1-john", "ch": 4, "v": 8},
    {"version_id": "telugu", "slug": "psalm-91-1", "bslug": "psalms", "ch": 91, "v": 1},
    {"version_id": "telugu", "slug": "psalm-119-105", "bslug": "psalms", "ch": 119, "v": 105},
    {"version_id": "telugu", "slug": "luke-2-11", "bslug": "luke", "ch": 2, "v": 11},
    {"version_id": "telugu", "slug": "mark-16-15", "bslug": "mark", "ch": 16, "v": 15},
    {"version_id": "telugu", "slug": "john-14-6", "bslug": "john", "ch": 14, "v": 6},
    {"version_id": "telugu", "slug": "john-15-13", "bslug": "john", "ch": 15, "v": 13},
    {"version_id": "telugu", "slug": "exodus-20-12", "bslug": "exodus", "ch": 20, "v": 12},
    {"version_id": "telugu", "slug": "deuteronomy-6-5", "bslug": "deuteronomy", "ch": 6, "v": 5},
    {"version_id": "telugu", "slug": "micah-6-8", "bslug": "micah", "ch": 6, "v": 8},
    {"version_id": "telugu", "slug": "matthew-6-9", "bslug": "matthew", "ch": 6, "v": 9},
    {"version_id": "telugu", "slug": "galatians-5-22", "bslug": "galatians", "ch": 5, "v": 22},
    {"version_id": "telugu", "slug": "colossians-3-23", "bslug": "colossians", "ch": 3, "v": 23},
]


def book_intro_html(version_id: str, bslug: str, display_name: str) -> str:
    """Rich intro for configured books; generic fallback for others."""
    key = (version_id, bslug)
    if key in BOOK_INTRO_HTML:
        return BOOK_INTRO_HTML[key]
    return (
        f"<p>Read <strong>{display_name}</strong> online in this Bible reader — "
        "pick a chapter below to start.</p>"
    )


def famous_verse_pairs(version_id: str, bslug: str) -> list[tuple[int, int]]:
    return list(BOOK_FAMOUS_VERSES.get((version_id, bslug), ()))


def chapter_notable_verses(version_id: str, bslug: str, ch_num: int) -> list[int]:
    return list(CHAPTER_NOTABLE_VERSES.get(f"{version_id}:{bslug}:{ch_num}", ()))


def chapter_faq_items(version_id: str, bslug: str, ch_num: int) -> list[tuple[str, str]]:
    return list(CHAPTER_FAQ.get(f"{version_id}:{bslug}:{ch_num}", ()))


def is_telugu_seo_book(bslug: str) -> bool:
    return bslug in TELUGU_SEO_BOOK_SLUGS
