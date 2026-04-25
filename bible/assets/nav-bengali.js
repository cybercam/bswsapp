
(function() {
  const NAV = [[1,"book1","Book1",50],[2,"book2","Book2",40],[3,"book3","Book3",27],[4,"book4","Book4",36],[5,"book5","Book5",34],[6,"book6","Book6",24],[7,"book7","Book7",21],[8,"book8","Book8",4],[9,"book9","Book9",31],[10,"book10","Book10",24],[11,"book11","Book11",22],[12,"book12","Book12",25],[13,"book13","Book13",29],[14,"book14","Book14",36],[15,"book15","Book15",10],[16,"book16","Book16",13],[17,"book17","Book17",10],[18,"book18","Book18",42],[19,"book19","Book19",150],[20,"book20","Book20",31],[21,"book21","Book21",12],[22,"book22","Book22",8],[23,"book23","Book23",66],[24,"book24","Book24",52],[25,"book25","Book25",5],[26,"book26","Book26",48],[27,"book27","Book27",12],[28,"book28","Book28",14],[29,"book29","Book29",3],[30,"book30","Book30",9],[31,"book31","Book31",1],[32,"book32","Book32",4],[33,"book33","Book33",7],[34,"book34","Book34",3],[35,"book35","Book35",3],[36,"book36","Book36",3],[37,"book37","Book37",2],[38,"book38","Book38",14],[39,"book39","Book39",4],[40,"book40","Book40",28],[41,"book41","Book41",16],[42,"book42","Book42",24],[43,"book43","Book43",21],[44,"book44","Book44",28],[45,"book45","Book45",16],[46,"book46","Book46",16],[47,"book47","Book47",13],[48,"book48","Book48",6],[49,"book49","Book49",6],[50,"book50","Book50",4],[51,"book51","Book51",4],[52,"book52","Book52",5],[53,"book53","Book53",3],[54,"book54","Book54",6],[55,"book55","Book55",4],[56,"book56","Book56",3],[57,"book57","Book57",1],[58,"book58","Book58",13],[59,"book59","Book59",5],[60,"book60","Book60",5],[61,"book61","Book61",3],[62,"book62","Book62",5],[63,"book63","Book63",1],[64,"book64","Book64",1],[65,"book65","Book65",1],[66,"book66","Book66",22]];
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
