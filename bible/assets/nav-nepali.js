
(function() {
  const NAV = [[1,"उत्पत्ति","उत्पत्ति",50],[2,"प्रस्थान-","प्रस्थान ",40],[3,"लेवी","लेवी",27],[4,"गन्ती","गन्ती",36],[5,"व्यवस्था","व्यवस्था",34],[6,"यहोशू","यहोशू",24],[7,"न्यायकर्ता","न्यायकर्ता",21],[8,"रूथ","रूथ",4],[9,"1-शमूएल","1 शमूएल",31],[10,"2-शमूएल","2 शमूएल",24],[11,"1-राजा","1 राजा",22],[12,"2-राजा","2 राजा",25],[13,"1-इतिहास","1 इतिहास",29],[14,"2-इतिहास","2 इतिहास",36],[15,"एज्रा","एज्रा",10],[16,"नहेम्याह","नहेम्याह",13],[17,"एस्तर","एस्तर",10],[18,"अय्यूब","अय्यूब",42],[19,"भजनसंग्रह","भजनसंग्रह",150],[20,"हितोपदेश","हितोपदेश",31],[21,"उपदेशक","उपदेशक",12],[22,"श्रेष्ठगीत","श्रेष्ठगीत",8],[23,"यशैया","यशैया",66],[24,"यर्मिया","यर्मिया",52],[25,"विलाप","विलाप",5],[26,"इजकिएल","इजकिएल",48],[27,"दानियल","दानियल",12],[28,"होशे","होशे",14],[29,"योएल","योएल",3],[30,"आमोस","आमोस",9],[31,"ओबदिया","ओबदिया",1],[32,"योना","योना",4],[33,"मीका","मीका",7],[34,"नहूम","नहूम",3],[35,"हबकूक","हबकूक",3],[36,"सपन्याह","सपन्याह",3],[37,"हाग्गै","हाग्गै",2],[38,"जकरिया","जकरिया",14],[39,"मलाकी","मलाकी",4],[40,"मत्ती","मत्ती",28],[41,"मर्कूस","मर्कूस",16],[42,"लूका","लूका",24],[43,"यूहन्ना","यूहन्ना",21],[44,"प्रेरित","प्रेरित",28],[45,"रोमी","रोमी",16],[46,"1-कोरिन्थी","1 कोरिन्थी",16],[47,"2-कोरिन्थी","2 कोरिन्थी",13],[48,"गलाती","गलाती",6],[49,"एफिसी","एफिसी",6],[50,"फिलिप्पी","फिलिप्पी",4],[51,"कलस्सी","कलस्सी",4],[52,"1-थिस्सलोनिकी","1 थिस्सलोनिकी",5],[53,"2-थिस्सलोनिकी","2 थिस्सलोनिकी",3],[54,"1-तिमोथी","1 तिमोथी",6],[55,"2-तिमोथी","2 तिमोथी",4],[56,"तीतस","तीतस",3],[57,"फिलेमोन","फिलेमोन",1],[58,"हिब्रू","हिब्रू",13],[59,"याकूब","याकूब",5],[60,"1-पत्रुस","1 पत्रुस",5],[61,"2-पत्रुस","2 पत्रुस",3],[62,"1-यूहन्ना","1 यूहन्ना",5],[63,"2-यूहन्ना","2 यूहन्ना",1],[64,"3-यूहन्ना","3 यूहन्ना",1],[65,"यहूदा","यहूदा",1],[66,"प्रकाश","प्रकाश",22]];
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
