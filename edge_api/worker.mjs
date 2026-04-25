const CDN_FALLBACK = "https://raw.githubusercontent.com/cybercam/bibles_json/main";
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

function findChapter(data, bookNum, chapterNum) {
  const book = (data.books || []).find((b) => Number(b.b) === bookNum);
  if (!book) return { book: null, chapter: null };
  const chapter = (book.ch || []).find((c) => Number(c.c) === chapterNum);
  return { book, chapter: chapter || null };
}

function chapterHtml({ version, bookSlug, chapterNum, chapter, canonical }) {
  const verses = Object.entries(chapter?.v || {}).sort((a, b) => Number(a[0]) - Number(b[0]));
  const verseLines = verses
    .map(([n, t]) => `<p><sup>${n}</sup> ${String(t || "")}</p>`)
    .join("\n");
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${version} ${bookSlug} ${chapterNum} | Dynamic Reader</title>
  <link rel="canonical" href="${canonical}" />
  <meta name="robots" content="index,follow" />
  <style>body{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:860px;margin:24px auto;padding:0 16px;line-height:1.6}sup{color:#7a35d7;font-weight:700}a{color:#7a35d7}</style>
</head>
<body>
  <h1>${version} / ${bookSlug} / ${chapterNum}</h1>
  <p><a href="/bible/${version}/">Back to language index</a></p>
  ${verseLines}
</body>
</html>`;
}

function verseHtml({ version, bookSlug, chapterNum, verseNum, verseText, canonical }) {
  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>${version} ${bookSlug} ${chapterNum}:${verseNum} | Dynamic Reader</title>
  <link rel="canonical" href="${canonical}" />
  <meta name="robots" content="index,follow" />
  <style>body{font-family:system-ui,Segoe UI,Arial,sans-serif;max-width:860px;margin:24px auto;padding:0 16px;line-height:1.6}sup{color:#7a35d7;font-weight:700}a{color:#7a35d7}</style>
</head>
<body>
  <h1>${version} / ${bookSlug} / ${chapterNum}:${verseNum}</h1>
  <p><a href="/bible/${version}/${bookSlug}/${chapterNum}/">Back to chapter</a></p>
  <p><sup>${verseNum}</sup> ${String(verseText || "")}</p>
</body>
</html>`;
}

async function handleDynamic(version, bookSlug, chapterNum, verseNum, requestUrl, wantsJson) {
  if (!DYNAMIC_VERSIONS.has(version)) {
    return jsonResponse({ error: `version '${version}' is not configured for dynamic routing` }, 404);
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

  if (verseNum == null) {
    if (wantsJson) {
      return jsonResponse({
        version,
        bookSlug,
        chapter: chapterNum,
        bookNumber: bookNum,
        verses: chapter.v || {},
      });
    }
    const canonical = `${requestUrl.origin}/bible/${version}/${bookSlug}/${chapterNum}/`;
    return htmlResponse(chapterHtml({ version, bookSlug, chapterNum, chapter, canonical }));
  }

  const verseText = (chapter.v || {})[String(verseNum)] ?? (chapter.v || {})[verseNum];
  if (!verseText) {
    return jsonResponse({ error: "verse not found" }, 404);
  }
  if (wantsJson) {
    return jsonResponse({
      version,
      bookSlug,
      chapter: chapterNum,
      verse: verseNum,
      text: verseText,
    });
  }
  const canonical = `${requestUrl.origin}/bible/${version}/${bookSlug}/${chapterNum}/${verseNum}/`;
  return htmlResponse(verseHtml({ version, bookSlug, chapterNum, verseNum, verseText, canonical }));
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
