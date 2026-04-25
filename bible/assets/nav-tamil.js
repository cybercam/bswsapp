
(function() {
  const NAV = [];
  const SECTIONS = [[1,"Old Testament"],[40,"New Testament"]];
  const mountBooks = document.getElementById('bsws-nav-books');
  const mountChapters = document.getElementById('ch-grid');
  if (!mountBooks || !mountChapters) return;
  const outDir = window.__BSWS_OUT_DIR__;
  const versionId = window.__BSWS_VERSION_ID__;
  const currentBookNum = Number(window.__BSWS_BOOK_NUM__ || 1);
  const currentChapter = Number(window.__BSWS_CH__ || 1);

  const activeBook = NAV.find((b) => Number(b[0]) === currentBookNum) || NAV[0];
  const currentSlug = activeBook ? activeBook[1] : 'genesis';

  let chapterHtml = '';
  const chapterCount = activeBook ? Number(activeBook[3]) : 0;
  for (let c = 1; c <= chapterCount; c++) {
    const active = c === currentChapter ? 'on' : '';
    chapterHtml += `<a href="/${outDir}/${versionId}/${currentSlug}/${c}/" class="ch-btn ${active}">${c}</a>`;
  }
  mountChapters.innerHTML = chapterHtml;

  const sectionStarts = new Set(SECTIONS.map((s) => Number(s[0])));
  let booksHtml = '';
  for (const [bookNum, slug, dname] of NAV) {
    if (sectionStarts.has(Number(bookNum))) {
      const label = SECTIONS.find((s) => Number(s[0]) === Number(bookNum));
      if (label) booksHtml += `<div class="s-section">${label[1]}</div>`;
    }
    const active = Number(bookNum) === currentBookNum ? 'on' : '';
    booksHtml += `<a href="/${outDir}/${versionId}/${slug}/1/" class="book-btn ${active}">${dname}</a>`;
  }
  mountBooks.innerHTML = booksHtml;
})();
