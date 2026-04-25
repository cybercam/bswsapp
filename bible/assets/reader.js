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

  const vbarEl = document.getElementById('vbar');
  document.getElementById('vbar-more-btn')?.addEventListener('click', () => {
    if (!vbarEl) return;
    const open = !vbarEl.classList.contains('vbar-expanded');
    vbarEl.classList.toggle('vbar-expanded', open);
    document.body.classList.toggle('vbar-expanded', open);
    const more = document.getElementById('vbar-more-btn');
    if (more) {
      more.setAttribute('aria-expanded', open ? 'true' : 'false');
      more.textContent = open ? 'Less' : 'More';
    }
  });
  document.getElementById('vbar-close-btn')?.addEventListener('click', () => {
    document.body.classList.toggle('vbar-hidden');
    try { localStorage.setItem('bsws_vbar_hidden', document.body.classList.contains('vbar-hidden') ? '1' : '0'); } catch (e) {}
  });
  try {
    if (localStorage.getItem('bsws_vbar_hidden') === '1') document.body.classList.add('vbar-hidden');
  } catch (e) {}

  // Copy btn (supports multi-select) — heading, one quoted verse per line, URL last
  document.getElementById('copy-btn')?.addEventListener('click', () => {
    const selected = getSelectedVerses();
    if (!selected.length) return;
    const block = buildClipBlock(selected);
    navigator.clipboard.writeText(block).then(() => {
      const btn = document.getElementById('copy-btn');
      btn.textContent = 'Copied ✓';
      setTimeout(() => { btn.textContent = 'Copy'; }, 1800);
    });
  });

  // Share btn (supports multi-select)
  document.getElementById('share-btn')?.addEventListener('click', () => {
    const selected = getSelectedVerses();
    if (!selected.length) return;
    const url = window.location.href;
    const heading = buildShareHeading(selected);
    const quotes = selected.map(v => '"' + (v.txt || '').trim() + '"').join('\\n');
    const textBody = heading + '\\n\\n' + quotes;
    const title = heading;
    if (navigator.share) {
      navigator.share({ title, text: textBody, url });
    } else {
      navigator.clipboard.writeText(buildClipBlock(selected));
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

function verseNumFromRow(row) {
  const n = parseInt(row.querySelector('.v-num')?.textContent || '', 10);
  return Number.isFinite(n) ? n : 0;
}

function buildShareHeading(selected) {
  const book = window.__BSWS_SHARE_BOOK__ || '';
  const ch = window.__BSWS_CH__ ?? '';
  const vl = window.__BSWS_VLABEL__ || '';
  const nums = selected.map((s) => s.num).filter((n) => n > 0).sort((a, b) => a - b);
  if (!nums.length) return (selected[0] && selected[0].ref) || book;
  const r = nums.length === 1 ? String(nums[0]) : `${nums[0]}–${nums[nums.length - 1]}`;
  return `${book} ${ch}:${r} (${vl})`;
}

function buildClipBlock(selected) {
  const url = window.location.href;
  const heading = buildShareHeading(selected);
  const quotes = selected.map((v) => '"' + (v.txt || '').trim() + '"').join('\\n');
  return heading + '\\n\\n' + quotes + '\\n\\n' + url;
}

function getSelectedVerses() {
  return [...document.querySelectorAll('.v-row.sel')].map((sel) => ({
    ref: sel.dataset.ref || '',
    txt: sel.querySelector('.v-txt')?.textContent || '',
    num: verseNumFromRow(sel),
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
  let text;
  if (hasSelection) {
    text = buildClipBlock(selected);
  } else {
    const rows = [...document.querySelectorAll('.v-row')];
    const fake = rows.map((r) => ({
      ref: r.dataset.ref || '',
      txt: r.querySelector('.v-txt')?.textContent || '',
      num: verseNumFromRow(r),
    }));
    text = fake.length ? buildClipBlock(fake) : '';
  }

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
