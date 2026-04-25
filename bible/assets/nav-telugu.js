
(function() {
  const NAV = [[1,"genesis","ఆదికాండము",50],[2,"exodus","నిర్గమకాండము",40],[3,"leviticus","లేవీయకాండము",27],[4,"numbers","సంఖ్యాకాండము",36],[5,"deuteronomy","ద్వితీయోపదేశకాండము",34],[6,"joshua","యెహోషువ",24],[7,"judges","న్యాయాధిపతులు",21],[8,"ruth","రూతు",4],[9,"1-samuel","1 సాముయేలు",31],[10,"2-samuel","2 సాముయేలు",24],[11,"1-kings","1 రాజులు",22],[12,"2-kings","2 రాజులు",25],[13,"1-chronicles","1 దినవృత్తాంతములు",29],[14,"2-chronicles","2 దినవృత్తాంతములు",36],[15,"ezra","ఎజ్రా",10],[16,"nehemiah","నెహెమ్యా",13],[17,"esther","ఎస్తేరు",10],[18,"job","యోబు గ్రంథము",42],[19,"psalms","కీర్తనల గ్రంథము",150],[20,"proverbs","సామెతలు",31],[21,"ecclesiastes","ప్రసంగి",12],[22,"song-of-solomon","పరమగీతము",8],[23,"isaiah","యెషయా గ్రంథము",66],[24,"jeremiah","యిర్మియా గ్రంథము",52],[25,"lamentations","విలాపవాక్యములు",5],[26,"ezekiel","యెహెజ్కేలు",48],[27,"daniel","దానియేలు",12],[28,"hosea","హోషేయ",14],[29,"joel","యోవేలు",3],[30,"amos","ఆమోసు",9],[31,"obadiah","ఓబద్యా",1],[32,"jonah","యోనా",4],[33,"micah","మీకా",7],[34,"nahum","నహూము",3],[35,"habakkuk","హబక్కూకు",3],[36,"zephaniah","జెఫన్యా",3],[37,"haggai","హగ్గయి",2],[38,"zechariah","జెకర్యా",14],[39,"malachi","మలాకీ",4],[40,"matthew","మత్తయి సువార్త",28],[41,"mark","మార్కు సువార్త",16],[42,"luke","లూకా సువార్త",24],[43,"john","యోహాను సువార్త",21],[44,"acts","అపొస్తలుల కార్యములు",28],[45,"romans","రోమీయులకు",16],[46,"1-corinthians","1 కొరింథీయులకు",16],[47,"2-corinthians","2 కొరింథీయులకు",13],[48,"galatians","గలతీయులకు",6],[49,"ephesians","ఎఫెసీయులకు",6],[50,"philippians","ఫిలిప్పీయులకు",4],[51,"colossians","కొలొస్సయులకు",4],[52,"1-thessalonians","1 థెస్సలొనీకయులకు",5],[53,"2-thessalonians","2 థెస్సలొనీకయులకు",3],[54,"1-timothy","1 తిమోతయుకు",6],[55,"2-timothy","2 తిమోతయుకు",4],[56,"titus","తీతుకు",3],[57,"philemon","ఫిలేమోనుకు",1],[58,"hebrews","హెబ్రీయులకు",13],[59,"james","యాకోబు",5],[60,"1-peter","1 పేతురు",5],[61,"2-peter","2 పేతురు",3],[62,"1-john","1 యోహాను",5],[63,"2-john","2 యోహాను",1],[64,"3-john","3 యోహాను",1],[65,"jude","యూదా",1],[66,"revelation","ప్రకటన గ్రంథము",22]];
  const SECTIONS = [[1,"ధర్మశాస్త్రము"],[6,"చరిత్ర గ్రంథములు"],[18,"కీర్తనా గ్రంథములు"],[23,"ప్రధాన ప్రవచన గ్రంథములు"],[28,"అల్ప ప్రవచన గ్రంథములు"],[40,"సువార్తలు"],[44,"సంఘ చరిత్ర"],[45,"పౌలు రాసిన పత్రికలు"],[58,"సాధారణ పత్రికలు"],[66,"ప్రవచన గ్రంథము"]];
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
