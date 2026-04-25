
(function() {
  const NAV = [[1,"genesis","Genesis",50],[2,"exodus","Exodus",40],[3,"leviticus","Leviticus",27],[4,"numbers","Numbers",36],[5,"deuteronomy","Deuteronomy",34],[6,"joshua","Joshua",24],[7,"judges","Judges",21],[8,"ruth","Ruth",4],[9,"1-samuel","1 Samuel",31],[10,"2-samuel","2 Samuel",24],[11,"1-kings","1 Kings",22],[12,"2-kings","2 Kings",25],[13,"1-chronicles","1 Chronicles",29],[14,"2-chronicles","2 Chronicles",36],[15,"ezra","Ezra",10],[16,"nehemiah","Nehemiah",13],[17,"esther","Esther",10],[18,"job","Job",42],[19,"psalms","Psalm",150],[20,"proverbs","Proverbs",31],[21,"ecclesiastes","Ecclesiastes",12],[22,"song-of-solomon","Song of Solomon",8],[23,"isaiah","Isaiah",66],[24,"jeremiah","Jeremiah",52],[25,"lamentations","Lamentations",5],[26,"ezekiel","Ezekiel",48],[27,"daniel","Daniel",12],[28,"hosea","Hosea",14],[29,"joel","Joel",3],[30,"amos","Amos",9],[31,"obadiah","Obadiah",1],[32,"jonah","Jonah",4],[33,"micah","Micah",7],[34,"nahum","Nahum",3],[35,"habakkuk","Habakkuk",3],[36,"zephaniah","Zephaniah",3],[37,"haggai","Haggai",2],[38,"zechariah","Zechariah",14],[39,"malachi","Malachi",4],[40,"matthew","Matthew",28],[41,"mark","Mark",16],[42,"luke","Luke",24],[43,"john","John",21],[44,"acts","Acts",28],[45,"romans","Romans",16],[46,"1-corinthians","1 Corinthians",16],[47,"2-corinthians","2 Corinthians",13],[48,"galatians","Galatians",6],[49,"ephesians","Ephesians",6],[50,"philippians","Philippians",4],[51,"colossians","Colossians",4],[52,"1-thessalonians","1 Thessalonians",5],[53,"2-thessalonians","2 Thessalonians",3],[54,"1-timothy","1 Timothy",6],[55,"2-timothy","2 Timothy",4],[56,"titus","Titus",3],[57,"philemon","Philemon",1],[58,"hebrews","Hebrews",13],[59,"james","James",5],[60,"1-peter","1 Peter",5],[61,"2-peter","2 Peter",3],[62,"1-john","1 John",5],[63,"2-john","2 John",1],[64,"3-john","3 John",1],[65,"jude","Jude",1],[66,"revelation","Revelation",22]];
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
