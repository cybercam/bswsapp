// Shared reader UI behaviors for generated Bible pages.
const THEMES = {
  reader: { "--bg": "#FAFAF8", "--bg2": "#F2EFE8", "--card": "#FFFFFF", "--border": "#DDD8CE", "--text": "#1C1917", "--muted": "#57534E", "--accent": "#9A3412", "--vnum": "#B45309" },
  royal: { "--bg": "#0D0A1A", "--bg2": "#1A1530", "--card": "#221D3A", "--border": "#3D3560", "--text": "#F0EAD6", "--muted": "#9B91C1", "--accent": "#F5C842", "--vnum": "#F5C842" },
  minimalist: { "--bg": "#FFFFFF", "--bg2": "#F8F8F6", "--card": "#FFFFFF", "--border": "#E5E5E0", "--text": "#1A1A1A", "--muted": "#888880", "--accent": "#1A1A1A", "--vnum": "#BBBBBB" },
  ocean: { "--bg": "#0A1628", "--bg2": "#0F1F3D", "--card": "#132A52", "--border": "#1E3F6E", "--text": "#E8F4FD", "--muted": "#7BAFD4", "--accent": "#38BDF8", "--vnum": "#38BDF8" },
  nature: { "--bg": "#0A1A0F", "--bg2": "#0F2418", "--card": "#143220", "--border": "#1E4A2E", "--text": "#E8F5EC", "--muted": "#7BB88A", "--accent": "#4ADE80", "--vnum": "#4ADE80" },
  blossom: { "--bg": "#1A0A14", "--bg2": "#2D1020", "--card": "#3D1530", "--border": "#5C2248", "--text": "#FDF0F6", "--muted": "#C47EA0", "--accent": "#F472B6", "--vnum": "#F472B6" },
  ember: { "--bg": "#1A0E08", "--bg2": "#2A1810", "--card": "#3A2218", "--border": "#5A3828", "--text": "#FDF4EE", "--muted": "#C49070", "--accent": "#FB923C", "--vnum": "#FB923C" },
  midnight: { "--bg": "#080C1A", "--bg2": "#0E1428", "--card": "#141E3C", "--border": "#1E2E58", "--text": "#E8EAF6", "--muted": "#7B8EC8", "--accent": "#818CF8", "--vnum": "#818CF8" },
  parchment: { "--bg": "#F5F0E8", "--bg2": "#EDE8DC", "--card": "#FBF8F2", "--border": "#D4C9A8", "--text": "#2C2416", "--muted": "#8B7D5A", "--accent": "#8B4513", "--vnum": "#B8860B" },
};

function applyTheme(id) {
  const theme = THEMES[id] || THEMES.reader;
  Object.entries(theme).forEach(([k, v]) => document.documentElement.style.setProperty(k, v));
  document.documentElement.setAttribute("data-theme", id);
  localStorage.setItem("bsws_theme", id);
  document.querySelectorAll(".t-btn").forEach((btn) => btn.classList.toggle("on", btn.dataset.t === id));
}

const VERSE_LINKS_STORAGE_KEY = "bsws_enable_verse_links";

function areVerseLinksEnabled() {
  return localStorage.getItem(VERSE_LINKS_STORAGE_KEY) === "1";
}

function setVerseLinksEnabled(enabled) {
  localStorage.setItem(VERSE_LINKS_STORAGE_KEY, enabled ? "1" : "0");
  renderVerseLinksToggle();
}

function renderVerseLinksToggle() {
  const btn = document.getElementById("verse-links-btn");
  if (!btn) return;
  const enabled = areVerseLinksEnabled();
  btn.textContent = enabled ? "Verse Details On" : "Verse Details Off";
  btn.classList.toggle("on", enabled);
  btn.setAttribute("aria-pressed", enabled ? "true" : "false");
}

function initVerseLinksToggle() {
  if (localStorage.getItem(VERSE_LINKS_STORAGE_KEY) === null) {
    localStorage.setItem(VERSE_LINKS_STORAGE_KEY, "0");
  }
  renderVerseLinksToggle();
  document.getElementById("verse-links-btn")?.addEventListener("click", () => {
    setVerseLinksEnabled(!areVerseLinksEnabled());
  });
}

function openSidebar() {
  document.getElementById("sidebar")?.classList.add("open");
  document.getElementById("overlay")?.classList.add("active");
}

function closeSidebar() {
  document.getElementById("sidebar")?.classList.remove("open");
  document.getElementById("overlay")?.classList.remove("active");
}

function isDesktopSidebarMode() {
  return window.matchMedia("(min-width: 900px)").matches;
}

function toggleSidebarFromMenu() {
  if (isDesktopSidebarMode()) {
    document.body.classList.toggle("sidebar-collapsed");
    closeSidebar();
    return;
  }

  const sidebar = document.getElementById("sidebar");
  if (sidebar?.classList.contains("open")) {
    closeSidebar();
  } else {
    openSidebar();
  }
}

function isChapterPage() {
  return document.querySelector(".v-row") !== null;
}

function injectVerseActionBar() {
  if (!isChapterPage() || document.getElementById("vbar")) return;
  const bar = document.createElement("div");
  bar.id = "vbar";
  bar.innerHTML = `
  <div id="vbar-meta" class="vbar-meta">0 verses selected</div>
  <button id="vbar-close-btn" aria-label="Hide action bar">▾</button>
  <button id="font-dec-vbar-btn" aria-label="Decrease verse font size">A-</button>
  <button id="font-inc-vbar-btn" aria-label="Increase verse font size">A+</button>
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
  <a class="cta-btn" href="https://play.google.com/store/apps/details?id=com.biblestudywithsteffi.app" target="_blank" rel="noopener">Memorize in App ↗</a>`;
  document.body.appendChild(bar);
}

function initMobileVbarBehavior() {
  const bar = document.getElementById("vbar");
  if (!bar) return;
  const closeBtn = document.getElementById("vbar-close-btn");
  let lastY = window.scrollY || 0;
  let ticking = false;
  const hide = () => document.body.classList.add("vbar-hidden");
  const show = () => document.body.classList.remove("vbar-hidden");
  closeBtn?.addEventListener("click", hide);
  window.addEventListener("scroll", () => {
    if (window.innerWidth >= 900) return;
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      const y = window.scrollY || 0;
      if (y > lastY + 10 && y > 80) hide();
      if (y < lastY - 10) show();
      lastY = y;
      ticking = false;
    });
  }, { passive: true });
}

function initVerseDetailInteractions() {
  const drawer = document.getElementById("lex-drawer");
  if (!drawer) return;
  const strongEl = document.getElementById("lex-strong");
  const lemmaEl = document.getElementById("lex-lemma");
  const defEl = document.getElementById("lex-def");
  const kjvEl = document.getElementById("lex-kjv");
  const derivEl = document.getElementById("lex-deriv");
  const close = () => drawer.classList.remove("on");
  document.getElementById("lex-close-btn")?.addEventListener("click", close);
  document.querySelectorAll(".inter-token").forEach((btn) => {
    btn.addEventListener("click", () => {
      strongEl.textContent = btn.dataset.strong || "Strong's";
      lemmaEl.textContent = [btn.dataset.lemma, btn.dataset.xlit].filter(Boolean).join(" · ");
      defEl.textContent = btn.dataset.def || "";
      kjvEl.textContent = btn.dataset.kjv ? `KJV: ${btn.dataset.kjv}` : "";
      derivEl.textContent = btn.dataset.deriv ? `Derivation: ${btn.dataset.deriv}` : "";
      drawer.classList.add("on");
    });
  });
}

function updateVbarState() {
  const selectedRows = document.querySelectorAll(".v-row.sel");
  const meta = document.getElementById("vbar-meta");
  if (!meta) return;
  const n = selectedRows.length;
  meta.textContent = `${n} verse${n === 1 ? "" : "s"} selected`;
}

function getSelectedVerses() {
  return [...document.querySelectorAll(".v-row.sel")].map((sel) => ({
    ref: sel.dataset.ref || "",
    txt: sel.querySelector(".v-txt")?.textContent || "",
  }));
}

function cleanVerseRef(ref) {
  return String(ref || "").replace(/\s*\([^)]*\)\s*$/, "").trim();
}

function buildSelectedExportPayload(selected) {
  const verseText = selected
    .map((v) => `"${v.txt}" — ${cleanVerseRef(v.ref)}`)
    .join("\n\n");
  return verseText ? `${verseText}\n\n${window.location.href}` : window.location.href;
}

function clearSelectedVerses() {
  document.querySelectorAll(".v-row.sel").forEach((row) => row.classList.remove("sel"));
  updateVbarState();
}

function selectVerse(row) {
  row.classList.toggle("sel");
  updateVbarState();
}

function initFontScale() {
  const saved = Number(localStorage.getItem("bsws_font_scale") || "1.0");
  const clamped = Math.min(1.5, Math.max(0.8, saved));
  localStorage.setItem("bsws_font_scale", String(clamped));
  applyFontScale(clamped);
}

function applyFontScale(scale) {
  document.documentElement.style.setProperty("--verse-font-size", `${(18 * scale).toFixed(1)}px`);
}

function updateFontScale(delta) {
  const current = Number(localStorage.getItem("bsws_font_scale") || "1.0");
  const next = Math.min(1.5, Math.max(0.8, Math.round((current + delta) * 10) / 10));
  localStorage.setItem("bsws_font_scale", String(next));
  applyFontScale(next);
}

function bestVoiceForLang(lang) {
  const voices = speechSynthesis?.getVoices?.() || [];
  if (!voices.length) return null;
  const normalized = (lang || "en").toLowerCase();
  const byLang = voices.filter((v) => (v.lang || "").toLowerCase().startsWith(normalized));
  const pool = byLang.length ? byLang : voices;
  const score = (v) => {
    const n = (v.name || "").toLowerCase();
    let s = 0;
    if (n.includes("neural")) s += 5;
    if (n.includes("google")) s += 4;
    if (n.includes("microsoft")) s += 3;
    if (n.includes("premium") || n.includes("enhanced")) s += 2;
    if (v.default) s += 1;
    return s;
  };
  return [...pool].sort((a, b) => score(b) - score(a))[0] || null;
}

function getTtsRate() {
  const rate = Number(document.getElementById("tts-rate")?.value || "1.0");
  return Math.min(1.5, Math.max(0.7, rate));
}

function getLoopMode() {
  return localStorage.getItem("bsws_tts_loop") === "1";
}

function speakText(text) {
  if (!text || !("speechSynthesis" in window)) return;
  speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = document.documentElement.lang || "en";
  const voice = bestVoiceForLang(utterance.lang);
  if (voice) utterance.voice = voice;
  utterance.rate = getTtsRate();
  utterance.onend = () => {
    if (getLoopMode()) setTimeout(() => speakText(text), 250);
  };
  speechSynthesis.speak(utterance);
}

function speakSelection() {
  const selected = getSelectedVerses();
  if (!selected.length) return;
  const text = selected.map((v) => `${v.ref}. ${v.txt}`).join(" ");
  speakText(text);
}

function primaryVerseRowsForReading() {
  const prim = [...document.querySelectorAll(".v-row.v-pr")];
  if (prim.length) return prim;
  return [...document.querySelectorAll(".v-row")];
}

function speakChapter() {
  const rows = primaryVerseRowsForReading();
  if (!rows.length) return;
  const text = rows
    .map((r) => {
      const ref = r.dataset.ref || "";
      const verse = r.querySelector(".v-txt")?.textContent || "";
      return `${ref}. ${verse}`;
    })
    .join(" ");
  speakText(text);
}

function toggleLoopMode() {
  localStorage.setItem("bsws_tts_loop", getLoopMode() ? "0" : "1");
  renderTtsToggles();
}

function toggleAutoReadMode() {
  const enabled = localStorage.getItem("bsws_auto_read_chapter") === "1";
  localStorage.setItem("bsws_auto_read_chapter", enabled ? "0" : "1");
  renderTtsToggles();
}

function renderTtsToggles() {
  const loopBtn = document.getElementById("tts-loop-btn");
  const autoBtn = document.getElementById("tts-auto-btn");
  const loopOn = getLoopMode();
  const autoOn = localStorage.getItem("bsws_auto_read_chapter") === "1";
  if (loopBtn) {
    loopBtn.textContent = loopOn ? "Loop On" : "Loop Off";
    loopBtn.classList.toggle("on", loopOn);
  }
  if (autoBtn) {
    autoBtn.textContent = autoOn ? "Auto-Read On" : "Auto-Read Off";
    autoBtn.classList.toggle("on", autoOn);
  }
}

function initTtsToggles() {
  if (localStorage.getItem("bsws_tts_loop") === null) localStorage.setItem("bsws_tts_loop", "0");
  if (localStorage.getItem("bsws_auto_read_chapter") === null) localStorage.setItem("bsws_auto_read_chapter", "0");
  renderTtsToggles();
}

function downloadAudioFallback() {
  const selected = getSelectedVerses();
  const hasSelection = selected.length > 0;
  const text = hasSelection
    ? buildSelectedExportPayload(selected)
    : primaryVerseRowsForReading()
        .map((r) => `"${r.querySelector(".v-txt")?.textContent || ""}" — ${cleanVerseRef(r.dataset.ref || "")}`)
        .join("\n\n") + `\n\n${window.location.href}`;
  const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = hasSelection ? "selected-verses.txt" : "chapter-verses.txt";
  link.click();
  setTimeout(() => URL.revokeObjectURL(link.href), 1500);
}

const PARALLEL_SECONDARY_KEY = "bsws_parallel_secondary";

function applyStoredParallelHref() {
  const a = document.getElementById("par-link");
  if (!a) return;
  const href = a.getAttribute("href");
  if (!href || href.indexOf("/parallel/") === -1) return;
  let sec = "";
  try {
    sec = localStorage.getItem(PARALLEL_SECONDARY_KEY) || "";
  } catch (_) {
    return;
  }
  if (!sec || !/^[a-z0-9-]+$/.test(sec)) return;
  let u;
  try {
    u = new URL(href, window.location.origin);
  } catch (_) {
    return;
  }
  const parts = u.pathname.split("/").filter(Boolean);
  if (parts.length < 6 || parts[0] !== "bible" || parts[1] !== "parallel") return;
  const primary = parts[2];
  if (sec === primary) return;
  parts[3] = sec;
  const nextPath = `/${parts.join("/")}/`;
  a.setAttribute("href", nextPath);
}

function sidebarSearch(q) {
  const rows = document.querySelectorAll(".v-row.v-pr").length
    ? document.querySelectorAll(".v-row.v-pr")
    : document.querySelectorAll(".v-row");
  const lowerQ = q.toLowerCase();
  const results = [];
  rows.forEach((r) => {
    const txt = r.querySelector(".v-txt")?.textContent || "";
    if (txt.toLowerCase().includes(lowerQ)) {
      results.push({ ref: r.dataset.ref, txt, el: r });
    }
    if (results.length >= 15) return;
  });

  const sr = document.getElementById("sr");
  if (!sr) return;
  sr.textContent = "";

  results.forEach((res) => {
    const item = document.createElement("div");
    item.className = "sr-item";
    const refEl = document.createElement("div");
    refEl.className = "sr-ref";
    refEl.textContent = res.ref || "";
    const txtEl = document.createElement("div");
    txtEl.className = "sr-txt";
    txtEl.textContent = res.txt || "";
    item.appendChild(refEl);
    item.appendChild(txtEl);
    item.addEventListener("click", () => {
      const verseUrl = res.el.dataset.verseUrl;
      if (verseUrl && areVerseLinksEnabled()) {
        window.location.href = verseUrl;
        return;
      }
      res.el.scrollIntoView({ behavior: "smooth", block: "center" });
      selectVerse(res.el);
      closeSidebar();
    });
    sr.appendChild(item);
  });

  if (!results.length) {
    const p = document.createElement("p");
    p.style.padding = "10px 14px";
    p.style.fontSize = "12px";
    p.style.color = "var(--muted)";
    p.textContent = "No results in this chapter.";
    sr.appendChild(p);
  }
}

function initReaderUi() {
  document.getElementById("menu-btn")?.addEventListener("click", toggleSidebarFromMenu);
  document.getElementById("overlay")?.addEventListener("click", closeSidebar);

  document.getElementById("theme-btn")?.addEventListener("click", () => {
    document.getElementById("tsheet")?.classList.toggle("on");
  });

  const swatches = document.querySelector(".t-swatches");
  if (swatches && swatches.children.length === 0) {
    Object.keys(THEMES).forEach((id) => {
      const theme = THEMES[id];
      const btn = document.createElement("button");
      btn.className = "t-btn";
      btn.dataset.t = id;
      btn.textContent = id.charAt(0).toUpperCase() + id.slice(1);
      btn.style.background = theme["--bg2"];
      btn.style.color = theme["--text"];
      btn.style.borderColor = theme["--border"];
      btn.addEventListener("click", () => applyTheme(id));
      swatches.appendChild(btn);
    });
  }

  applyTheme(localStorage.getItem("bsws_theme") || "reader");
  injectVerseActionBar();
  initMobileVbarBehavior();
  initVerseDetailInteractions();

  document.getElementById("par-btn")?.addEventListener("click", () => {
    if (!document.getElementById("par-panel")) return;
    document.getElementById("par-panel")?.classList.toggle("on");
    document.getElementById("wrap")?.classList.toggle("par-open");
  });

  applyStoredParallelHref();

  initFontScale();
  document.getElementById("font-inc-btn")?.addEventListener("click", () => updateFontScale(0.1));
  document.getElementById("font-dec-btn")?.addEventListener("click", () => updateFontScale(-0.1));
  document.getElementById("font-inc-vbar-btn")?.addEventListener("click", () => updateFontScale(0.1));
  document.getElementById("font-dec-vbar-btn")?.addEventListener("click", () => updateFontScale(-0.1));

  initVerseLinksToggle();

  document.querySelectorAll(".v-row").forEach((row) => {
    row.addEventListener("click", (e) => {
      if (e.defaultPrevented) return;
      if (e.button !== 0) return;

      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) {
        e.preventDefault();
        selectVerse(row);
        return;
      }

      if (!areVerseLinksEnabled()) {
        e.preventDefault();
        selectVerse(row);
      }
    });
  });

  document.addEventListener("click", (e) => {
    if (!e.target.closest(".v-row") && !e.target.closest("#vbar")) clearSelectedVerses();
  });

  document.getElementById("copy-btn")?.addEventListener("click", () => {
    const selected = getSelectedVerses();
    if (!selected.length) return;
    const payload = buildSelectedExportPayload(selected);
    navigator.clipboard.writeText(payload).then(() => {
      const btn = document.getElementById("copy-btn");
      if (!btn) return;
      btn.textContent = "Copied ✓";
      setTimeout(() => {
        btn.textContent = "Copy";
      }, 1800);
    });
  });

  document.getElementById("share-btn")?.addEventListener("click", () => {
    const selected = getSelectedVerses();
    if (!selected.length) return;
    const url = window.location.href;
    const payload = buildSelectedExportPayload(selected);
    const title = selected.length === 1 ? cleanVerseRef(selected[0].ref) : `${selected.length} verses`;
    if (navigator.share) {
      navigator.share({ title, text: payload, url });
    } else {
      navigator.clipboard.writeText(payload);
    }
  });

  initTtsToggles();
  document.getElementById("tts-play-btn")?.addEventListener("click", speakSelection);
  document.getElementById("tts-chapter-btn")?.addEventListener("click", speakChapter);
  document.getElementById("tts-stop-btn")?.addEventListener("click", () => speechSynthesis?.cancel());
  document.getElementById("tts-loop-btn")?.addEventListener("click", toggleLoopMode);
  document.getElementById("tts-auto-btn")?.addEventListener("click", toggleAutoReadMode);
  document.getElementById("tts-download-btn")?.addEventListener("click", downloadAudioFallback);
  document.getElementById("clear-sel-btn")?.addEventListener("click", clearSelectedVerses);

  const searchInput = document.getElementById("s-search");
  if (searchInput) {
    let st;
    searchInput.addEventListener("input", (e) => {
      clearTimeout(st);
      const q = e.target.value.trim();
      if (q.length < 3) {
        const sr = document.getElementById("sr");
        if (sr) sr.innerHTML = "";
        return;
      }
      st = setTimeout(() => sidebarSearch(q), 280);
    });
  }

  if (isChapterPage() && localStorage.getItem("bsws_auto_read_chapter") === "1") {
    setTimeout(() => speakChapter(), 500);
  }
}

document.addEventListener("DOMContentLoaded", initReaderUi);

