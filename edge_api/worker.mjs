import { BSI_BOOK_NAMES } from "./bsiBookNames.mjs";
import CROSSREFS from "./crossrefsMobile.mjs";

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
const READER_CSS_HREF = "/bible/assets/style.css";
const READER_JS_HREF = "/bible/assets/reader.js";
const INTERLINEAR_CSS_HREF = "/bible/assets/interlinear.css";
const STRONGS_JS_HREF = "/bible/assets/strongs.js";
const PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.biblestudywithsteffi.app";
const READER_FONT_HREF = "https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Lora:ital,wght@0,400;0,500;1,400&display=swap";
const INTERLINEAR_INLINE_CSS = ".interlinear-verse{display:flex;flex-wrap:wrap;gap:8px;align-items:stretch}.inter-token{display:inline-flex;flex-direction:column;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:8px;min-width:88px;text-align:left;cursor:pointer;white-space:normal;overflow-wrap:anywhere}.inter-token .w{display:block;font-size:13px;color:var(--text);font-weight:600}.inter-token .g{display:block;font-size:11px;color:var(--muted);margin-top:2px}.inter-token .s{display:block;font-size:10px;color:var(--accent);margin-top:3px;font-family:'Cinzel',serif}";

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
const ENGLISH_BOOK_NUM = {
  Genesis: 1, Exodus: 2, Leviticus: 3, Numbers: 4, Deuteronomy: 5, Joshua: 6, Judges: 7, Ruth: 8,
  "1 Samuel": 9, "2 Samuel": 10, "1 Kings": 11, "2 Kings": 12, "1 Chronicles": 13, "2 Chronicles": 14,
  Ezra: 15, Nehemiah: 16, Esther: 17, Job: 18, Psalm: 19, Psalms: 19, Proverbs: 20, Ecclesiastes: 21,
  "Song of Solomon": 22, "Song of Songs": 22, Isaiah: 23, Jeremiah: 24, Lamentations: 25, Ezekiel: 26,
  Daniel: 27, Hosea: 28, Joel: 29, Amos: 30, Obadiah: 31, Jonah: 32, Micah: 33, Nahum: 34, Habakkuk: 35,
  Zephaniah: 36, Haggai: 37, Zechariah: 38, Malachi: 39, Matthew: 40, Mark: 41, Luke: 42, John: 43,
  Acts: 44, Romans: 45, "1 Corinthians": 46, "2 Corinthians": 47, Galatians: 48, Ephesians: 49,
  Philippians: 50, Colossians: 51, "1 Thessalonians": 52, "2 Thessalonians": 53, "1 Timothy": 54,
  "2 Timothy": 55, Titus: 56, Philemon: 57, Hebrews: 58, James: 59, "1 Peter": 60, "2 Peter": 61,
  "1 John": 62, "2 John": 63, "3 John": 64, Jude: 65, Revelation: 66,
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

function readerHeadAssets({ interlinear = false } = {}) {
  return `
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="${READER_FONT_HREF}" rel="stylesheet" />
  <link rel="stylesheet" href="${READER_CSS_HREF}" />${interlinear ? `
  <link rel="stylesheet" href="${INTERLINEAR_CSS_HREF}" />
  <style>${INTERLINEAR_INLINE_CSS}</style>` : ""}`;
}

function themeSheetHtml() {
  return `<div id="tsheet">
  <h3>Choose Theme</h3>
  <div class="t-swatches"></div>
</div>`;
}

function readerScriptHtml() {
  return `<script src="${READER_JS_HREF}" defer></script>`;
}

function notFoundHtml(message = "The page you were looking for could not be found.") {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex,follow" />
  <title>Page not found | Bible Study with Steffi</title>
  ${readerHeadAssets()}
  <style>
    .nf-page{min-height:calc(100svh - 52px);position:relative;overflow:hidden;padding:28px 14px 88px;background:radial-gradient(circle at 18% 8%,color-mix(in srgb,var(--accent) 18%,transparent),transparent 28%),radial-gradient(circle at 88% 22%,color-mix(in srgb,var(--muted) 18%,transparent),transparent 30%),var(--bg)}
    .nf-card{position:relative;width:min(1060px,100%);margin:0 auto;display:grid;grid-template-columns:minmax(0,1.05fr) minmax(280px,.8fr);gap:clamp(22px,5vw,52px);align-items:center;background:color-mix(in srgb,var(--card) 94%,transparent);border:1px solid var(--border);border-radius:32px;padding:clamp(22px,5vw,58px);box-shadow:0 30px 90px rgba(0,0,0,.18)}
    .nf-kicker{display:inline-flex;align-items:center;gap:9px;font-family:'Cinzel',serif;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:14px}
    .nf-kicker svg,.nf-action svg{width:18px;height:18px;color:currentColor;flex:0 0 auto}
    .nf-title{font-family:'Cinzel',serif;font-size:clamp(34px,8vw,78px);line-height:.98;color:var(--accent);max-width:760px;margin:0 0 18px;text-wrap:balance}
    .nf-copy{font-size:clamp(16px,2.2vw,20px);line-height:1.8;color:var(--text);max-width:650px;margin:0 0 24px}
    .nf-actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;max-width:560px}
    .nf-action{min-height:52px;display:inline-flex;align-items:center;justify-content:center;gap:10px;border-radius:16px;padding:14px 16px;border:1px solid var(--border);font-family:'Cinzel',serif;font-size:12px;font-weight:600;text-align:center;text-decoration:none;transition:transform .18s ease,background .18s ease,border-color .18s ease}
    .nf-action:hover{text-decoration:none;transform:translateY(-1px);border-color:var(--accent)}
    .nf-primary{grid-column:1/-1;background:var(--accent);color:var(--bg);border-color:var(--accent)}
    .nf-secondary{background:var(--bg2);color:var(--text)}
    .nf-proof{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px;color:var(--muted);font-size:12px}
    .nf-proof span{border:1px solid var(--border);background:var(--bg2);border-radius:999px;padding:7px 10px}
    .nf-phone-wrap{display:grid;place-items:center}.nf-phone{width:min(312px,78vw);aspect-ratio:9/18.5;border:1px solid var(--border);border-radius:38px;background:linear-gradient(180deg,var(--bg2),var(--card));padding:13px;box-shadow:0 22px 70px rgba(0,0,0,.22);position:relative}.nf-phone::before{content:"";position:absolute;top:9px;left:50%;width:76px;height:6px;border-radius:999px;background:var(--border);transform:translateX(-50%)}.nf-screen{height:100%;border-radius:28px;border:1px solid var(--border);background:var(--bg);padding:30px 16px 16px;display:flex;flex-direction:column;gap:14px;overflow:hidden}.nf-app-chip{align-self:flex-start;border:1px solid var(--border);border-radius:999px;padding:6px 10px;font-family:'Cinzel',serif;font-size:10px;color:var(--accent);background:var(--card)}.nf-verse-card{border:1px solid var(--border);border-radius:18px;background:var(--card);padding:16px}.nf-verse-ref{font-family:'Cinzel',serif;font-size:11px;color:var(--accent);margin-bottom:8px}.nf-verse-line{height:10px;border-radius:999px;background:color-mix(in srgb,var(--text) 22%,transparent);margin:8px 0}.nf-verse-line.short{width:64%}.nf-mini-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:auto}.nf-mini{border:1px solid var(--border);border-radius:16px;background:var(--card);min-height:76px;padding:12px}.nf-mini svg{width:22px;height:22px;color:var(--accent);margin-bottom:12px}.nf-mini div{height:8px;border-radius:999px;background:color-mix(in srgb,var(--muted) 28%,transparent)}
    @media(prefers-reduced-motion:reduce){.nf-action{transition:none}.nf-action:hover{transform:none}}
    @media(max-width:820px){.nf-card{grid-template-columns:1fr;border-radius:26px}.nf-phone-wrap{order:-1}.nf-phone{width:min(268px,76vw)}.nf-actions{grid-template-columns:1fr}.nf-primary{grid-column:auto}}
    @media(max-width:430px){.nf-page{padding:18px 10px 72px}.nf-card{padding:20px;border-radius:22px}.nf-title{font-size:clamp(31px,12vw,48px)}.nf-phone{width:min(236px,74vw);border-radius:30px}.nf-screen{border-radius:22px}.nf-action{min-height:50px}}
  </style>
</head>
<body>
  <header id="topbar">
    <a href="/" class="icon-btn" aria-label="Back to main website">Home</a>
    <a href="/bible/" class="icon-btn" aria-label="Go to Bible index">Bibles</a>
    <span class="logo">Bible Study with Steffi</span>
    <span class="crumb">Page not found</span>
    <button type="button" id="theme-btn" class="icon-btn" aria-label="Reading theme and colors">Aa</button>
  </header>
  <div id="wrap">
    <main class="nf-page">
      <section class="nf-card" aria-labelledby="not-found-title">
        <div>
          <p class="nf-kicker"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 19.5V6.75A2.75 2.75 0 0 1 6.75 4H20v15.5H6.75A2.75 2.75 0 0 0 4 22.25" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 8h8M8 11.5h6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>Page 404</p>
          <h1 id="not-found-title" class="nf-title">You found a quiet corner.</h1>
          <p class="nf-copy">${escapeHtml(message)} Open the Bible online, return home, or download the app for daily verse memory in your language.</p>
          <div class="nf-actions" aria-label="Page recovery actions">
            <a class="nf-action nf-primary" href="${PLAY_STORE_URL}" target="_blank" rel="noopener"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 3.5v17l11-8.5-11-8.5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="m7 3.5 7.5 8.5L7 20.5" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>Download the free app</a>
            <a class="nf-action nf-secondary" href="/"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 11.5 12 5l8 6.5V20a1 1 0 0 1-1 1h-5v-6h-4v6H5a1 1 0 0 1-1-1v-8.5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>Home page</a>
            <a class="nf-action nf-secondary" href="/bible/"><svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 4.5h10.5A3.5 3.5 0 0 1 19 8v11.5H8.5A3.5 3.5 0 0 1 5 16V4.5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M8.5 8H16M8.5 11.5H15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>Bible pages</a>
          </div>
          <div class="nf-proof" aria-label="Reader highlights"><span>Telugu Bible</span><span>15+ languages</span><span>No ads</span><span>Daily memorization</span></div>
        </div>
        <div class="nf-phone-wrap" aria-hidden="true">
          <div class="nf-phone"><div class="nf-screen"><div class="nf-app-chip">Bible Study with Steffi</div><div class="nf-verse-card"><div class="nf-verse-ref">John 1:1</div><div class="nf-verse-line"></div><div class="nf-verse-line"></div><div class="nf-verse-line short"></div></div><div class="nf-mini-grid"><div class="nf-mini"><svg viewBox="0 0 24 24" fill="none"><path d="M6 5h12v15l-6-3-6 3V5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg><div></div></div><div class="nf-mini"><svg viewBox="0 0 24 24" fill="none"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg><div></div></div></div></div></div>
        </div>
      </section>
    </main>
  </div>
  ${themeSheetHtml()}
  ${readerScriptHtml()}
</body>
</html>`;
}

function notFoundResponse(message, wantsJson, status = 404) {
  if (wantsJson) return jsonResponse({ error: message }, status);
  return htmlResponse(notFoundHtml(message), status);
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
  const raw = await res.json();
  return normalizeBibleData(raw);
}

function normalizeBibleData(raw) {
  if (raw && typeof raw === "object" && Array.isArray(raw.books)) {
    return raw;
  }
  if (!raw || typeof raw !== "object") {
    return { books: [] };
  }
  const books = [];
  let seqNum = 1;
  for (const [bookKey, chaptersRaw] of Object.entries(raw)) {
    let bNum = null;
    const m = /^Book(\d+)$/i.exec(bookKey);
    if (m) {
      bNum = Number(m[1]);
    } else if (ENGLISH_BOOK_NUM[bookKey]) {
      bNum = ENGLISH_BOOK_NUM[bookKey];
    } else {
      bNum = seqNum;
    }
    seqNum += 1;
    const chArr = [];
    if (chaptersRaw && typeof chaptersRaw === "object") {
      for (const [cKey, versesRaw] of Object.entries(chaptersRaw)) {
        const cNum = Number(cKey);
        if (!Number.isInteger(cNum) || cNum < 1) continue;
        const v = {};
        if (versesRaw && typeof versesRaw === "object") {
          for (const [vKey, txt] of Object.entries(versesRaw)) {
            const vNum = Number(vKey);
            if (!Number.isInteger(vNum) || vNum < 1) continue;
            const s = String(txt ?? "").trim();
            if (!s) continue;
            v[vNum] = s;
          }
        }
        chArr.push({ c: cNum, v });
      }
    }
    chArr.sort((a, b) => a.c - b.c);
    books.push({ b: bNum, n: bookKey, ch: chArr });
  }
  books.sort((a, b) => a.b - b.b);
  return { books };
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
      return CROSSREFS || {};
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

function findVerseText(data, bookNum, chapterNum, verseNum) {
  const { chapter } = findChapter(data, bookNum, chapterNum);
  if (!chapter) return "";
  return (chapter.v || {})[String(verseNum)] ?? (chapter.v || {})[verseNum] ?? "";
}

function versionOptions(selected) {
  return [...ALL_VERSIONS]
    .map((version) => {
      const isSelected = version === selected ? " selected" : "";
      return `<option value="${version}"${isSelected}>${escapeHtml(displayVersion(version))}</option>`;
    })
    .join("");
}

function lexDrawerHtml() {
  return `<div id="lex-drawer" aria-live="polite">
  <button type="button" id="lex-close-btn" class="icon-btn close" aria-label="Close word study">Close</button>
  <h4 id="lex-strong"></h4>
  <p id="lex-lemma"></p>
  <p id="lex-def"></p>
  <p id="lex-kjv"></p>
  <p id="lex-deriv"></p>
</div>`;
}

function chapterHtml({ version, bookSlug, chapterNum, chapter, canonical, bookName }) {
  const verses = Object.entries(chapter?.v || {}).sort((a, b) => Number(a[0]) - Number(b[0]));
  const verseLines = verses
    .map(([n, t]) => {
      const href = `/bible/${version}/${bookSlug}/${chapterNum}/${n}/`;
      return `<a class="v-row" href="${href}" data-ref="${escapeHtml(bookName)} ${chapterNum}:${n} (${escapeHtml(displayVersion(version))})"><span class="v-num">${n}</span><span class="v-txt">${escapeHtml(t || "")}</span></a>`;
    })
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
  ${readerHeadAssets()}
</head>
<body>
  <header id="topbar">
    <a href="/" class="icon-btn" aria-label="Back to main website">Home</a>
    <a href="/bible/" class="icon-btn" aria-label="Go to Bible index">Bibles</a>
    <span class="logo">Bible Study with Steffi</span>
    <span class="crumb">${escapeHtml(bookName)} ${chapterNum} · ${escapeHtml(versionLabel)}</span>
    <a class="icon-btn" href="/bible/parallel/${version}/${secondary}/${bookSlug}/${chapterNum}/" aria-label="Open parallel two-column view">||</a>
    <button type="button" id="theme-btn" class="icon-btn" aria-label="Reading theme and colors">Aa</button>
  </header>
  <div id="wrap">
    <main id="reader">
      <div class="ch-head">
        <h1>${escapeHtml(bookName)}</h1>
        <h2>Chapter ${chapterNum}</h2>
        <span class="version-tag">${escapeHtml(versionLabel)}</span>
      </div>
      ${verseLines}
      <nav class="ch-nav"><a href="/bible/${version}/">Back to language index</a></nav>
    </main>
  </div>
  ${themeSheetHtml()}
  ${readerScriptHtml()}
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
    ? `<div class="detail-panel"><h3>Cross references</h3><div class="xref-list">${crossrefs
      .map((r) => `<div class="xref-item"><a href="${r.url}">${escapeHtml(r.label)}</a>${r.text ? `<p class="x-txt">${escapeHtml(r.text)}</p>` : ""}</div>`)
      .join("")}</div></div>`
    : `<div class="detail-panel"><h3>Cross references</h3><p class="verse-detail-meta">No cross references available for this verse.</p></div>`;
  const interlinearHtml = interlinearTokens.length
    ? `<div class="detail-panel"><h3>Interlinear</h3><div class="interlinear-verse">${interlinearTokens
      .map((t) => `<button class="inter-token" type="button" data-strong="${escapeHtml(t.s || "")}"><span class="w">${escapeHtml(t.w || "")}</span><span class="g">${escapeHtml(t.t || "")}</span><span class="s">${escapeHtml(t.s || "")}</span></button>`)
      .join("")}</div></div>`
    : `<div class="detail-panel"><h3>Interlinear</h3><p class="verse-detail-meta">Interlinear data is unavailable for this verse.</p></div>`;
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${escapeHtml(bookName)} ${chapterNum}:${verseNum} — ${escapeHtml(versionLabel)} | Dynamic Reader</title>
  <link rel="canonical" href="${canonical}" />
  <meta name="robots" content="index,follow" />
  ${readerHeadAssets({ interlinear: true })}
</head>
<body>
  <header id="topbar">
    <a href="/" class="icon-btn" aria-label="Back to main website">Home</a>
    <a href="/bible/" class="icon-btn" aria-label="Go to Bible index">Bibles</a>
    <span class="logo">Bible Study with Steffi</span>
    <span class="crumb">${escapeHtml(bookName)} ${chapterNum}:${verseNum} · ${escapeHtml(versionLabel)}</span>
    <button type="button" id="theme-btn" class="icon-btn" aria-label="Reading theme and colors">Aa</button>
  </header>
  <div id="wrap">
    <main id="reader">
      <div class="verse-detail-card">
        <div class="verse-detail-ref">${escapeHtml(bookName)} ${chapterNum}:${verseNum} · ${escapeHtml(versionLabel)}</div>
        <p class="verse-detail-text">${escapeHtml(verseText || "")}</p>
        <p class="verse-detail-links"><a href="/bible/${version}/${bookSlug}/${chapterNum}/">Back to chapter</a></p>
      </div>
      <nav class="ch-nav">${navPrev}${navNext}</nav>
      <div class="detail-grid">${crossrefHtml}${interlinearHtml}</div>
    </main>
  </div>
  ${lexDrawerHtml()}
  ${themeSheetHtml()}
  ${readerScriptHtml()}
  <script src="${STRONGS_JS_HREF}" defer></script>
</body>
</html>`;
}

async function handleDynamic(version, bookSlug, chapterNum, verseNum, requestUrl, wantsJson) {
  if (!ALL_VERSIONS.has(version)) {
    return notFoundResponse(`Unsupported Bible version '${version}'.`, wantsJson);
  }
  const bookNum = BOOK_INDEX[bookSlug];
  if (!bookNum) {
    return notFoundResponse(`Unknown Bible book '${bookSlug}'.`, wantsJson);
  }

  let data;
  try {
    data = await fetchBibleJson(version, requestUrl);
  } catch (err) {
    return jsonResponse({ error: String(err.message || err) }, 502);
  }

  const { book, chapter } = findChapter(data, bookNum, chapterNum);
  if (!book || !chapter) {
    return notFoundResponse("That chapter is not available for this Bible version.", wantsJson);
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
    return notFoundResponse("That verse is not available for this Bible version.", wantsJson);
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
      text: findVerseText(data, rb, rc, rv),
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
  const selectorHtml = `<div class="detail-panel" aria-label="Parallel Bible version selectors">
    <h3>Change versions</h3>
    <div class="detail-grid" style="margin:0">
      <label class="verse-detail-meta">Left Bible
        <select class="par-ver-select" onchange="if(this.value && this.value !== '${secondary}') window.location='/bible/parallel/'+this.value+'/${secondary}/${bookSlug}/${chapterNum}/'">${versionOptions(primary)}</select>
      </label>
      <label class="verse-detail-meta">Right Bible
        <select class="par-ver-select" onchange="if(this.value && this.value !== '${primary}') window.location='/bible/parallel/${primary}/'+this.value+'/${bookSlug}/${chapterNum}/'">${versionOptions(secondary)}</select>
      </label>
    </div>
  </div>`;
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
    const href = `/bible/parallel/${primary}/${secondary}/${bookSlug}/${chapterNum}/${v}/`;
    return `<div class="par-row">
      <div class="par-cell"><a class="v-row" href="${href}"><span class="v-num">${v}</span><span class="v-txt">${escapeHtml(pv)}</span></a></div>
      <div class="par-cell"><a class="v-row" href="${href}"><span class="v-num">${v}</span><span class="v-txt">${escapeHtml(sv)}</span></a></div>
    </div>`;
  }).join("\n");

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Parallel ${escapeHtml(primaryBookName)} ${chapterNum} — ${escapeHtml(primaryLabel)} / ${escapeHtml(secondaryLabel)}</title>
  <link rel="canonical" href="${canonical}" />
  <meta name="robots" content="index,follow" />
  ${readerHeadAssets()}
</head>
<body>
  <header id="topbar">
    <a href="/" class="icon-btn" aria-label="Back to main website">Home</a>
    <a href="/bible/" class="icon-btn" aria-label="Go to Bible index">Bibles</a>
    <span class="logo">Bible Study with Steffi</span>
    <span class="crumb">Parallel ${escapeHtml(primaryBookName)} ${chapterNum}</span>
    <button type="button" id="theme-btn" class="icon-btn" aria-label="Reading theme and colors">Aa</button>
  </header>
  <div id="wrap">
    <main id="reader" class="parallel-reader">
      <div class="ch-head">
        <h1>Parallel ${escapeHtml(primaryBookName)}</h1>
        <h2>Chapter ${chapterNum}</h2>
        <span class="version-tag">${escapeHtml(primaryLabel)} · ${escapeHtml(secondaryLabel)}</span>
      </div>
      ${selectorHtml}
      <p class="verse-detail-links"><a href="/bible/${primary}/${bookSlug}/${chapterNum}/">Back to ${escapeHtml(primaryLabel)} chapter</a><a href="/bible/${secondary}/${bookSlug}/${chapterNum}/">Back to ${escapeHtml(secondaryLabel)} chapter</a></p>
      <div class="par-rows" aria-label="Verse-by-verse parallel columns">
        <div class="par-row par-skip-row" aria-hidden="true">
          <div class="par-cell"><div class="par-col-label">${escapeHtml(primaryLabel)}</div></div>
          <div class="par-cell"><div class="par-col-label">${escapeHtml(secondaryLabel)}</div></div>
        </div>
        ${rows}
      </div>
    </main>
  </div>
  ${themeSheetHtml()}
  ${readerScriptHtml()}
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
  const selectorHtml = `<div class="detail-panel" aria-label="Parallel Bible version selectors">
    <h3>Change versions</h3>
    <div class="detail-grid" style="margin:0">
      <label class="verse-detail-meta">Left Bible
        <select class="par-ver-select" onchange="if(this.value && this.value !== '${secondary}') window.location='/bible/parallel/'+this.value+'/${secondary}/${bookSlug}/${chapterNum}/${verseNum}/'">${versionOptions(primary)}</select>
      </label>
      <label class="verse-detail-meta">Right Bible
        <select class="par-ver-select" onchange="if(this.value && this.value !== '${primary}') window.location='/bible/parallel/${primary}/'+this.value+'/${bookSlug}/${chapterNum}/${verseNum}/'">${versionOptions(secondary)}</select>
      </label>
    </div>
  </div>`;
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Parallel ${escapeHtml(primaryBookName)} ${chapterNum}:${verseNum} — ${escapeHtml(primaryLabel)} / ${escapeHtml(secondaryLabel)}</title>
  <link rel="canonical" href="${canonical}" />
  <meta name="robots" content="index,follow" />
  ${readerHeadAssets()}
</head>
<body>
  <header id="topbar">
    <a href="/" class="icon-btn" aria-label="Back to main website">Home</a>
    <a href="/bible/" class="icon-btn" aria-label="Go to Bible index">Bibles</a>
    <span class="logo">Bible Study with Steffi</span>
    <span class="crumb">Parallel ${escapeHtml(primaryBookName)} ${chapterNum}:${verseNum}</span>
    <button type="button" id="theme-btn" class="icon-btn" aria-label="Reading theme and colors">Aa</button>
  </header>
  <div id="wrap">
    <main id="reader">
      <div class="ch-head">
        <h1>${escapeHtml(primaryBookName)} ${chapterNum}:${verseNum}</h1>
        <h2>Parallel verse</h2>
        <span class="version-tag">${escapeHtml(primaryLabel)} · ${escapeHtml(secondaryLabel)}</span>
      </div>
      ${selectorHtml}
      <p class="verse-detail-links"><a href="/bible/parallel/${primary}/${secondary}/${bookSlug}/${chapterNum}/">Back to parallel chapter</a></p>
      <div class="detail-grid">
        <div class="detail-panel"><h3>${escapeHtml(primaryLabel)}</h3><p class="verse-detail-text">${escapeHtml(primaryText)}</p></div>
        <div class="detail-panel"><h3>${escapeHtml(secondaryLabel)}</h3><p class="verse-detail-text">${escapeHtml(secondaryText)}</p></div>
      </div>
    </main>
  </div>
  ${themeSheetHtml()}
  ${readerScriptHtml()}
</body>
</html>`;
}

async function handleDynamicParallel(primary, secondary, bookSlug, chapterNum, verseNum, requestUrl, wantsJson) {
  if (!ALL_VERSIONS.has(primary) || !ALL_VERSIONS.has(secondary)) {
    return notFoundResponse("That parallel Bible version pair is not supported.", wantsJson);
  }
  if (primary === secondary) {
    return jsonResponse({ error: "parallel versions must be different" }, 400);
  }
  const bookNum = BOOK_INDEX[bookSlug];
  if (!bookNum) {
    return notFoundResponse(`Unknown Bible book '${bookSlug}'.`, wantsJson);
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
    return notFoundResponse("That parallel chapter is not available for this Bible pair.", wantsJson);
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
    return notFoundResponse("That parallel verse is not available for this Bible pair.", wantsJson);
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

    return notFoundResponse("The page you were looking for could not be found.", wantsJson);
  },
};
