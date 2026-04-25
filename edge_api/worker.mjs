import { BSI_BOOK_NAMES } from "./bsiBookNames.mjs";

const CDN_FALLBACK = "https://raw.githubusercontent.com/cybercam/bibles_json/main";
const INTERLINEAR_BASE = "https://raw.githubusercontent.com/cybercam/interlinear/main";
const ALL_VERSIONS = new Set([
  "bbe",
  "kjv",
  "nkjv",
  "web",
  "ylt",
  "bengali",
  "gujarati",
  "hindi",
  "kannada",
  "malayalam",
  "marathi",
  "nepali",
  "odia",
  "tamil",
  "telugu",
]);
const VERSION_DISPLAY = {
  bbe: "Bible in Basic English",
  kjv: "King James Version",
  nkjv: "New King James Version",
  web: "World English Bible",
  ylt: "Young's Literal Translation",
  bengali: "বাংলা বাইবেল",
  gujarati: "ગુજરાતી બાઇબલ",
  hindi: "हिन्दी बाइबिल",
  kannada: "ಕನ್ನಡ ಬೈಬಲ್",
  malayalam: "മലയാളം ബൈബിൾ",
  marathi: "मराठी बायबल",
  nepali: "नेपाली बाइबल",
  odia: "ଓଡ଼ିଆ ବାଇବେଲ",
  tamil: "தமிழ் பரிசுத்த வேதாகமம்",
  telugu: "తెలుగు బైబిల్",
};
const DYNAMIC_VERSIONS = new Set([
  "bengali",
  "gujarati",
  "hindi",
  "kannada",
  "malayalam",
  "marathi",
  "nepali",
  "odia",
  "tamil",
]);

const BOOK_INDEX = {
  genesis: 1, exodus: 2, leviticus: 3, numbers: 4, deuteronomy: 5, joshua: 6, judges: 7, ruth: 8,
  "1-samuel": 9, "2-samuel": 10, "1-kings": 11, "2-kings": 12, "1-chronicles": 13, "2-chronicles": 14,
  ezra: 15, nehemiah: 16, esther: 17, job: 18, psalms: 19, proverbs: 20, ecclesiastes: 21, "song-of-solomon": 22,
  isaiah: 23, jeremiah: 24, lamentations: 25, ezekiel: 26, daniel: 27, hosea: 28, joel: 29, amos: 30,
  obadiah: 31, jonah: 32, micah: 33, nahum: 34, habakkuk: 35, zephaniah: 36, haggai: 37, zechariah: 38,
  malachi: 39, matthew: 40, mark: 41, luke: 42, john: 43, acts: 44, romans: 45, "1-corinthians": 46,
  "2-corinthians": 47, galatians: 48, ephesians: 49, philippians: 50, colossians: 51, "1-thessalonians": 52,
  "2-thessalonians": 53, "1-timothy": 54, "2-timothy": 55, titus: 56, philemon: 57, hebrews: 58, james: 59,
  "1-peter": 60, "2-peter": 61, "1-john": 62, "2-john": 63, "3-john": 64, jude: 65, revelation: 66,
};
const BOOK_SLUG_BY_NUM = Object.fromEntries(
  Object.entries(BOOK_INDEX).map(([slug, num]) => [num, slug]),
);
const BOOK_TITLE_BY_NUM = Object.fromEntries(
  Object.entries(BOOK_SLUG_BY_NUM).map(([num, slug]) => [num, slug.replaceAll("-", " ")]),
);

let crossrefsPromise = null;
let interlinearBookMappingPromise = null;
const interlinearBookDataPromiseCache = new Map();

function jsonResponse(payload, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "public, max-age=300",
    },
  });
}

function htmlResponse(html, status = 200) {
  return new Response(html, {
    status,
    headers: {
      "content-type": "text/html; charset=utf-8",
      "cache-control": "public, max-age=120",
    },
  });
}

function escapeHtml(input) {
  return String(input ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function displayVersion(version) {
  return VERSION_DISPLAY[version] || version;
}

function displayBookName(version, bookNum, fallbackName) {
  const list = BSI_BOOK_NAMES[version];
  if (Array.isArray(list) && Number.isInteger(bookNum) && bookNum >= 1 && bookNum <= 66) {
    const mapped = list[bookNum - 1];
    if (mapped && String(mapped).trim()) {
      return String(mapped);
    }
  }
  return fallbackName || "";
}

async function fetchBibleJson(version, requestUrl) {
  const sameHostUrl = `${requestUrl.origin}/bible/data/bible_${version}.json`;
  let res = await fetch(sameHostUrl);
  if (!res.ok) {
    res = await fetch(`${CDN_FALLBACK}/bible_${version}.json`);
  }
  if (!res.ok) {
    throw new Error(`Bible JSON unavailable for '${version}'`);
  }
  return res.json();
}

async function loadCrossrefs(requestUrl) {
  if (!crossrefsPromise) {
    crossrefsPromise = (async () => {
      const sameHost = `${requestUrl.origin}/bible/data/crossrefs_mobile.json`;
      const altHost = `${requestUrl.origin}/data/crossrefs_mobile.json`;
      for (const url of [sameHost, altHost]) {
        try {
          const res = await fetch(url);
          if (res.ok) return await res.json();
        } catch {
          // continue
        }
      }
      return {};
    })();
  }
  return crossrefsPromise;
}

async function loadInterlinearBookMapping() {
  if (!interlinearBookMappingPromise) {
    interlinearBookMappingPromise = (async () => {
      try {
        const res = await fetch(`${INTERLINEAR_BASE}/bookMapping.json`);
        if (!res.ok) return {};
        return await res.json();
      } catch {
        return {};
      }
    })();
  }
  return interlinearBookMappingPromise;
}

async function loadInterlinearBookData(abbrev) {
  if (!abbrev) return {};
  if (!interlinearBookDataPromiseCache.has(abbrev)) {
    interlinearBookDataPromiseCache.set(abbrev, (async () => {
      try {
        const res = await fetch(`${INTERLINEAR_BASE}/${abbrev}.json`);
        if (!res.ok) return {};
        return await res.json();
      } catch {
        return {};
      }
    })());
  }
  return interlinearBookDataPromiseCache.get(abbrev);
}

function findChapter(data, bookNum, chapterNum) {
  const book = (data.books || []).find((b) => Number(b.b) === bookNum);
  if (!book) return { book: null, chapter: null };
  const chapter = (book.ch || []).find((c) => Number(c.c) === chapterNum);
  return { book, chapter: chapter || null };
}

function chapterHtml({ version, bookSlug, chapterNum, chapter, canonical, bookName }) {
  const verses = Object.entries(chapter?.v || {}).sort((a, b) => Number(a[0]) - Number(b[0]));
  const verseLines = verses
    .map(([n, t]) => `<p><sup>${n}</sup> <a href="/bible/${version}/${bookSlug}/${chapterNum}/${n}/">${escapeHtml(t || "")}</a></p>`)
    .join("\n");
  const secondary = version === "web" ? "kjv" : "web";
  const versionLabel = displayVersion(version);
  const secondaryLabel = displayVersion(secondary);
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${escapeHtml(bookName)} ${chapterNum} — ${escapeHtml(versionLabel)} | Dynamic Reader</title>
  <link rel="canonical" href="${canonical}" />
  <meta name="robots" content="index,follow" />
  <style>body{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:860px;margin:24px auto;padding:0 16px;line-height:1.6}sup{color:#7a35d7;font-weight:700}a{color:#7a35d7}</style>
</head>
<body>
  <h1>${escapeHtml(bookName)} ${chapterNum} · ${escapeHtml(versionLabel)}</h1>
  <p><a href="/bible/${version}/">Back to language index</a></p>
  <p><a href="/bible/parallel/${version}/${secondary}/${bookSlug}/${chapterNum}/">Parallel view (${escapeHtml(versionLabel)} + ${escapeHtml(secondaryLabel)})</a></p>
  ${verseLines}
</body>
</html>`;
}

function verseHtml({
  version,
  bookSlug,
  chapterNum,
  verseNum,
  verseText,
  canonical,
  bookName,
  prevVerseNum,
  nextVerseNum,
  crossrefs,
  interlinearTokens,
}) {
  const versionLabel = displayVersion(version);
  const navPrev = prevVerseNum
    ? `<a href="/bible/${version}/${bookSlug}/${chapterNum}/${prevVerseNum}/">← Previous verse</a>`
    : `<span style="opacity:.5">← Previous verse</span>`;
  const navNext = nextVerseNum
    ? `<a href="/bible/${version}/${bookSlug}/${chapterNum}/${nextVerseNum}/">Next verse →</a>`
    : `<span style="opacity:.5">Next verse →</span>`;
  const crossrefHtml = crossrefs.length
    ? `<section><h2>Cross references</h2><ul>${crossrefs
      .map((r) => `<li><a href="${r.url}">${escapeHtml(r.label)}</a></li>`)
      .join("")}</ul></section>`
    : `<section><h2>Cross references</h2><p>No cross references available for this verse.</p></section>`;
  const interlinearHtml = interlinearTokens.length
    ? `<section><h2>Interlinear</h2><div style="display:flex;flex-wrap:wrap;gap:8px">${interlinearTokens
      .map((t) => `<span style="display:inline-flex;flex-direction:column;border:1px solid #ececec;border-radius:8px;padding:6px 8px;min-width:84px"><strong>${escapeHtml(t.w || "")}</strong><small>${escapeHtml(t.t || "")}</small><small style="color:#6b3fa0">${escapeHtml(t.s || "")}</small></span>`)
      .join("")}</div></section>`
    : `<section><h2>Interlinear</h2><p>Interlinear data is unavailable for this verse.</p></section>`;
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${escapeHtml(bookName)} ${chapterNum}:${verseNum} — ${escapeHtml(versionLabel)} | Dynamic Reader</title>
  <link rel="canonical" href="${canonical}" />
  <meta name="robots" content="index,follow" />
  <style>body{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:980px;margin:24px auto;padding:0 16px;line-height:1.6}sup{color:#7a35d7;font-weight:700}a{color:#7a35d7}section{margin-top:20px}.row{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap}</style>
</head>
<body>
  <h1>${escapeHtml(bookName)} ${chapterNum}:${verseNum} · ${escapeHtml(versionLabel)}</h1>
  <p><a href="/bible/${version}/${bookSlug}/${chapterNum}/">Back to chapter</a></p>
  <p><sup>${verseNum}</sup> ${escapeHtml(verseText || "")}</p>
  <div class="row">${navPrev}${navNext}</div>
  ${crossrefHtml}
  ${interlinearHtml}
</body>
</html>`;
}

async function handleDynamic(version, bookSlug, chapterNum, verseNum, requestUrl, wantsJson) {
  if (!ALL_VERSIONS.has(version)) {
    return jsonResponse({ error: `unsupported version '${version}'` }, 404);
  }
  const bookNum = BOOK_INDEX[bookSlug];
  if (!bookNum) {
    return jsonResponse({ error: `unknown book slug '${bookSlug}'` }, 404);
  }

  let data;
  try {
    data = await fetchBibleJson(version, requestUrl);
  } catch (err) {
    return jsonResponse({ error: String(err.message || err) }, 502);
  }

  const { book, chapter } = findChapter(data, bookNum, chapterNum);
  if (!book || !chapter) {
    return jsonResponse({ error: "chapter not found" }, 404);
  }
  const bookName = displayBookName(version, bookNum, book.n || bookSlug);

  if (verseNum == null) {
    if (wantsJson) {
      return jsonResponse({
        version,
        bookSlug,
        chapter: chapterNum,
        bookNumber: bookNum,
        bookName,
        verses: chapter.v || {},
      });
    }
    const canonical = `${requestUrl.origin}/bible/${version}/${bookSlug}/${chapterNum}/`;
    return htmlResponse(chapterHtml({ version, bookSlug, chapterNum, chapter, canonical, bookName }));
  }

  const verseText = (chapter.v || {})[String(verseNum)] ?? (chapter.v || {})[verseNum];
  if (!verseText) {
    return jsonResponse({ error: "verse not found" }, 404);
  }
  const verseKeys = Object.keys(chapter.v || {})
    .map((n) => Number(n))
    .filter((n) => Number.isInteger(n) && n > 0)
    .sort((a, b) => a - b);
  const verseIdx = verseKeys.indexOf(verseNum);
  const prevVerseNum = verseIdx > 0 ? verseKeys[verseIdx - 1] : null;
  const nextVerseNum = verseIdx >= 0 && verseIdx < verseKeys.length - 1 ? verseKeys[verseIdx + 1] : null;

  const crossrefsData = await loadCrossrefs(requestUrl);
  const bcv = `${bookNum}_${chapterNum}_${verseNum}`;
  const refs = Array.isArray(crossrefsData?.[bcv]) ? crossrefsData[bcv] : [];
  const crossrefs = refs.slice(0, 40).map((ref) => {
    const [rb, rc, rv] = String(ref).split("_").map((n) => Number(n));
    const slug = BOOK_SLUG_BY_NUM[rb];
    if (!slug || !rc || !rv) return null;
    const label = `${displayBookName(version, rb, BOOK_TITLE_BY_NUM[rb] || slug)} ${rc}:${rv}`;
    return {
      key: `${rb}_${rc}_${rv}`,
      label,
      url: `/bible/${version}/${slug}/${rc}/${rv}/`,
    };
  }).filter(Boolean);

  const mapping = await loadInterlinearBookMapping();
  const mapItem = mapping?.[String(bookNum)] || mapping?.[bookNum];
  const abbrev = mapItem?.abbrev || "";
  let interlinearTokens = [];
  if (abbrev) {
    const interBook = await loadInterlinearBookData(abbrev);
    const chapterMap = interBook?.chapters?.[String(chapterNum)] || interBook?.chapters?.[chapterNum];
    const verseTokens = chapterMap?.[String(verseNum)] || chapterMap?.[verseNum];
    if (Array.isArray(verseTokens)) {
      interlinearTokens = verseTokens.slice(0, 80);
    }
  }

  if (wantsJson) {
    return jsonResponse({
      version,
      bookSlug,
      chapter: chapterNum,
      verse: verseNum,
      bookName,
      text: verseText,
      prevVerseNum,
      nextVerseNum,
      crossrefs,
      interlinearTokens,
    });
  }
  const canonical = `${requestUrl.origin}/bible/${version}/${bookSlug}/${chapterNum}/${verseNum}/`;
  return htmlResponse(verseHtml({
    version,
    bookSlug,
    chapterNum,
    verseNum,
    verseText,
    canonical,
    bookName,
    prevVerseNum,
    nextVerseNum,
    crossrefs,
    interlinearTokens,
  }));
}

function parallelChapterHtml({
  primary,
  secondary,
  bookSlug,
  chapterNum,
  primaryChapter,
  secondaryChapter,
  canonical,
  primaryBookName,
  secondaryBookName,
}) {
  const primaryLabel = displayVersion(primary);
  const secondaryLabel = displayVersion(secondary);
  const primaryVerses = primaryChapter?.v || {};
  const secondaryVerses = secondaryChapter?.v || {};
  const verseNums = [...new Set([
    ...Object.keys(primaryVerses),
    ...Object.keys(secondaryVerses),
  ])]
    .map((n) => Number(n))
    .filter((n) => Number.isInteger(n) && n > 0)
    .sort((a, b) => a - b);

  const rows = verseNums.map((v) => {
    const pv = primaryVerses[String(v)] ?? primaryVerses[v] ?? "";
    const sv = secondaryVerses[String(v)] ?? secondaryVerses[v] ?? "";
    return `<tr>
      <td><a href="/bible/parallel/${primary}/${secondary}/${bookSlug}/${chapterNum}/${v}/"><sup>${v}</sup> ${escapeHtml(pv)}</a></td>
      <td><a href="/bible/parallel/${primary}/${secondary}/${bookSlug}/${chapterNum}/${v}/"><sup>${v}</sup> ${escapeHtml(sv)}</a></td>
    </tr>`;
  }).join("\n");

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Parallel ${escapeHtml(primaryBookName)} ${chapterNum} — ${escapeHtml(primaryLabel)} / ${escapeHtml(secondaryLabel)}</title>
  <link rel="canonical" href="${canonical}" />
  <meta name="robots" content="index,follow" />
  <style>
    body{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:1100px;margin:24px auto;padding:0 16px}
    table{width:100%;border-collapse:collapse}
    th,td{vertical-align:top;padding:10px;border-bottom:1px solid #ececec;text-align:left;line-height:1.55}
    a{color:inherit;text-decoration:none}
    sup{color:#7a35d7;font-weight:700}
  </style>
</head>
<body>
  <h1>Parallel ${escapeHtml(primaryBookName)} ${chapterNum} · ${escapeHtml(primaryLabel)} + ${escapeHtml(secondaryLabel)}</h1>
  <p><a href="/bible/${primary}/${bookSlug}/${chapterNum}/">Back to ${escapeHtml(primaryLabel)} chapter</a> · <a href="/bible/${secondary}/${bookSlug}/${chapterNum}/">Back to ${escapeHtml(secondaryLabel)} chapter</a></p>
  <table>
    <thead><tr><th>${escapeHtml(primaryLabel)}</th><th>${escapeHtml(secondaryLabel)}</th></tr></thead>
    <tbody>${rows}</tbody>
  </table>
</body>
</html>`;
}

function parallelVerseHtml({
  primary,
  secondary,
  bookSlug,
  chapterNum,
  verseNum,
  primaryText,
  secondaryText,
  canonical,
  primaryBookName,
  secondaryBookName,
}) {
  const primaryLabel = displayVersion(primary);
  const secondaryLabel = displayVersion(secondary);
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Parallel ${escapeHtml(primaryBookName)} ${chapterNum}:${verseNum} — ${escapeHtml(primaryLabel)} / ${escapeHtml(secondaryLabel)}</title>
  <link rel="canonical" href="${canonical}" />
  <meta name="robots" content="index,follow" />
  <style>
    body{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:980px;margin:24px auto;padding:0 16px}
    .grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}
    .card{border:1px solid #ececec;border-radius:10px;padding:12px}
    sup{color:#7a35d7;font-weight:700}
  </style>
</head>
<body>
  <h1>Parallel ${escapeHtml(primaryBookName)} ${chapterNum}:${verseNum} · ${escapeHtml(primaryLabel)} + ${escapeHtml(secondaryLabel)}</h1>
  <p><a href="/bible/parallel/${primary}/${secondary}/${bookSlug}/${chapterNum}/">Back to parallel chapter</a></p>
  <div class="grid">
    <div class="card"><h3>${escapeHtml(primaryLabel)}</h3><p><sup>${verseNum}</sup> ${escapeHtml(primaryText)}</p></div>
    <div class="card"><h3>${escapeHtml(secondaryLabel)}</h3><p><sup>${verseNum}</sup> ${escapeHtml(secondaryText)}</p></div>
  </div>
</body>
</html>`;
}

async function handleDynamicParallel(primary, secondary, bookSlug, chapterNum, verseNum, requestUrl, wantsJson) {
  if (!ALL_VERSIONS.has(primary) || !ALL_VERSIONS.has(secondary)) {
    return jsonResponse({ error: "unsupported parallel version pair" }, 404);
  }
  if (primary === secondary) {
    return jsonResponse({ error: "parallel versions must be different" }, 400);
  }
  const bookNum = BOOK_INDEX[bookSlug];
  if (!bookNum) {
    return jsonResponse({ error: `unknown book slug '${bookSlug}'` }, 404);
  }

  let primaryData;
  let secondaryData;
  try {
    [primaryData, secondaryData] = await Promise.all([
      fetchBibleJson(primary, requestUrl),
      fetchBibleJson(secondary, requestUrl),
    ]);
  } catch (err) {
    return jsonResponse({ error: String(err.message || err) }, 502);
  }

  const { book: primaryBook, chapter: primaryChapter } = findChapter(primaryData, bookNum, chapterNum);
  const { book: secondaryBook, chapter: secondaryChapter } = findChapter(secondaryData, bookNum, chapterNum);
  if (!primaryChapter || !secondaryChapter) {
    return jsonResponse({ error: "parallel chapter not found" }, 404);
  }
  const primaryBookName = displayBookName(primary, bookNum, primaryBook?.n || bookSlug);
  const secondaryBookName = displayBookName(secondary, bookNum, secondaryBook?.n || bookSlug);

  if (verseNum == null) {
    if (wantsJson) {
      return jsonResponse({
        primary,
        secondary,
        bookSlug,
        chapter: chapterNum,
        primaryBookName,
        secondaryBookName,
        primaryVerses: primaryChapter.v || {},
        secondaryVerses: secondaryChapter.v || {},
      });
    }
    const canonical = `${requestUrl.origin}/bible/parallel/${primary}/${secondary}/${bookSlug}/${chapterNum}/`;
    return htmlResponse(
      parallelChapterHtml({
        primary,
        secondary,
        bookSlug,
        chapterNum,
        primaryChapter,
        secondaryChapter,
        canonical,
        primaryBookName,
        secondaryBookName,
      }),
    );
  }

  const primaryText = (primaryChapter.v || {})[String(verseNum)] ?? (primaryChapter.v || {})[verseNum];
  const secondaryText = (secondaryChapter.v || {})[String(verseNum)] ?? (secondaryChapter.v || {})[verseNum];
  if (!primaryText && !secondaryText) {
    return jsonResponse({ error: "parallel verse not found" }, 404);
  }
  if (wantsJson) {
    return jsonResponse({
      primary,
      secondary,
      bookSlug,
      chapter: chapterNum,
      verse: verseNum,
      primaryBookName,
      secondaryBookName,
      primaryText: primaryText || "",
      secondaryText: secondaryText || "",
    });
  }
  const canonical = `${requestUrl.origin}/bible/parallel/${primary}/${secondary}/${bookSlug}/${chapterNum}/${verseNum}/`;
  return htmlResponse(
    parallelVerseHtml({
      primary,
      secondary,
      bookSlug,
      chapterNum,
      verseNum,
      primaryText: primaryText || "",
      secondaryText: secondaryText || "",
      canonical,
      primaryBookName,
      secondaryBookName,
    }),
  );
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    const parts = url.pathname.split("/").filter(Boolean);
    const wantsJson = url.pathname.startsWith("/api/");

    let p = parts;
    if (wantsJson) {
      // /api/bible/{version}/{book}/{chapter}/{verse?}
      p = parts.slice(1);
    }
    // /bible/parallel/{primary}/{secondary}/{book}/{chapter}/{verse?}
    if (p.length >= 6 && p[0] === "bible" && p[1] === "parallel") {
      const primary = p[2];
      const secondary = p[3];
      const bookSlug = p[4];
      const chapterNum = Number(p[5]);
      const verseNum = p.length >= 7 ? Number(p[6]) : null;
      if (!Number.isInteger(chapterNum) || chapterNum < 1) {
        return jsonResponse({ error: "invalid chapter" }, 400);
      }
      if (verseNum !== null && (!Number.isInteger(verseNum) || verseNum < 1)) {
        return jsonResponse({ error: "invalid verse" }, 400);
      }
      return handleDynamicParallel(primary, secondary, bookSlug, chapterNum, verseNum, url, wantsJson);
    }

    // /bible/{version}/{book}/{chapter}/{verse?}
    if (p.length >= 4 && p[0] === "bible") {
      const version = p[1];
      const bookSlug = p[2];
      const chapterNum = Number(p[3]);
      const verseNum = p.length >= 5 ? Number(p[4]) : null;
      if (!Number.isInteger(chapterNum) || chapterNum < 1) {
        return jsonResponse({ error: "invalid chapter" }, 400);
      }
      if (verseNum !== null && (!Number.isInteger(verseNum) || verseNum < 1)) {
        return jsonResponse({ error: "invalid verse" }, 400);
      }
      return handleDynamic(version, bookSlug, chapterNum, verseNum, url, wantsJson);
    }

    return new Response("Not found", { status: 404 });
  },
};
