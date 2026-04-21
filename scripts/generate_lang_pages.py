#!/usr/bin/env python3
"""Generate *-bible.html language landing pages from a single template."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT

LANGS = [
    {
        "slug": "english-bible.html",
        "hreflang": "en",
        "lang": "en",
        "dir": "ltr",
        "font_query": "family=Lora:ital,wght@0,400;0,600;1,400&family=DM+Sans:wght@400;600;700",
        "font_var": "'Lora', Georgia, serif",
        "title": "English Bible Memorization (ESV, NKJV, KJV) — Bible Study with Steffi | Android",
        "desc": "Memorize Bible verses in English (ESV, NKJV, KJV bundled) with spaced repetition, quizzes, and parallel reading with Indian languages. Free Android app on Google Play.",
        "h1": "Memorize Scripture in English — with ESV, NKJV, or KJV",
        "lead": "Pair trusted English translations with Telugu, Hindi, Tamil, and more using parallel Bible and spaced repetition — free on Google Play.",
        "bullets": [
            "SM2-style scheduling: reviews land right before you forget.",
            "Parallel Bible: study English beside your heart language.",
            "Free. No ads. No in-app purchases.",
        ],
        "cta": "Install from Google Play",
        "card_kw": "English Bible memorization",
        "og_loc": "en_IN",
    },
    {
        "slug": "telugu-bible.html",
        "hreflang": "te",
        "lang": "te",
        "font_query": "family=Noto+Sans+Telugu:wght@400;500;600;700&family=DM+Sans:wght@400;600;700",
        "font_var": "'Noto Sans Telugu', sans-serif",
        "title": "తెలుగు బైబిల్ వచనాల జాపనం — Bible Study with Steffi | Android",
        "desc": "తెలుగులో బైబిల్ వచనాలను గుర్తుంచుకోండి. స్పేస్డ్ రిపిటిషన్, పాడలెల్ బైబిల్, రోజువారీ రివ్యూ — Google Playలో ఉచిత Android యాప్.",
        "h1": "తెలుగులో బైబిల్ వచనాలను గట్టిగా గుర్తుంచుకోండి",
        "lead": "Memorize Scripture in <strong>Telugu</strong> with spaced repetition, daily reviews, and parallel English — free Bible Study with Steffi on Google Play.",
        "bullets": [
            "మీరు మరచిపోయే ముందే రివ్యూ వచ్చేలా స్మార్ట్ షెడ్యూలింగ్ (SM2 శైలి).",
            "ESV, NKJV, KJV లాంటి ఇంగ్లీష్ అనువాదాలతో పక్కపక్కనే చదవడం.",
            "ఉచితం. ప్రకటనలు లేవు. ఇన్-అప్ పర్చేస్ లేవు.",
        ],
        "cta": "Google Play నుండి ఇన్‌స్టాల్ చేయండి",
        "card_kw": "Telugu Bible",
        "og_loc": "te_IN",
    },
    {
        "slug": "hindi-bible.html",
        "hreflang": "hi",
        "lang": "hi",
        "font_query": "family=Noto+Sans+Devanagari:wght@400;500;600;700&family=DM+Sans:wght@400;600;700",
        "font_var": "'Noto Sans Devanagari', sans-serif",
        "title": "हिंदी बाइबिल वचन याद करें — Bible Study with Steffi | Android",
        "desc": "हिंदी में बाइबिल वचन याद रखें। स्पेस्ड रिपीटिशन, पैरेलल बाइबिल, रोज़ाना रिव्यू — Google Play पर मुफ्त Android ऐप।",
        "h1": "हिंदी में बाइबिल वचन दिल तक उतारें",
        "lead": "Memorize Scripture in <strong>Hindi</strong> with spaced repetition, daily reviews, and trusted English side-by-side — free Bible Study with Steffi on Google Play.",
        "bullets": [
            "स्मार्ट शेड्यूलिंग: जब आप भूलने वाले हों, तभी रिव्यू — SM2-स्टाइल।",
            "ESV, NKJV, KJV जैसे अंग्रेज़ी संस्करणों के साथ पैरेलल पढ़ना।",
            "मुफ्त। कोई विज्ञापन नहीं। कोई इन-ऐप खरीदारी नहीं।",
        ],
        "cta": "Google Play से इंस्टॉल करें",
        "card_kw": "Hindi Bible",
        "og_loc": "hi_IN",
    },
    {
        "slug": "tamil-bible.html",
        "hreflang": "ta",
        "lang": "ta",
        "font_query": "family=Noto+Sans+Tamil:wght@400;500;600;700&family=DM+Sans:wght@400;600;700",
        "font_var": "'Noto Sans Tamil', sans-serif",
        "title": "தமிழ் பைபிள் வசன மனனம் — Bible Study with Steffi | Android",
        "desc": "தமிழில் பைபிள் வசனங்களை மனனம் செய்யுங்கள். இடைவெளி மீள்நினைவு, இணை நூல், தினசரி மதிப்பீடு — Google Play இல் இலவச Android செயலி.",
        "h1": "தமிழில் பைபிள் வசனங்களை உறுதியாக நினைவில் வைத்துக்கொள்ளுங்கள்",
        "lead": "Memorize Scripture in <strong>Tamil</strong> with spaced repetition, daily reviews, and English parallel reading — free Bible Study with Steffi on Google Play.",
        "bullets": [
            "SM2 பாணியிலான திட்டமிடல்: மறக்கும் தருணத்திற்கு முன் மதிப்பீடு திரும்ப வரும்.",
            "ESV, NKJV, KJV போன்ற ஆங்கில மொழிபெயர்ப்புகளுடன் இணையாக வாசித்தல்.",
            "இலவசம். விளம்பரங்கள் இல்லை. இன்-ஆப் வாங்குதல்கள் இல்லை.",
        ],
        "cta": "Google Play இல் நிறுவவும்",
        "card_kw": "Tamil Bible",
        "og_loc": "ta_IN",
    },
    {
        "slug": "kannada-bible.html",
        "hreflang": "kn",
        "lang": "kn",
        "font_query": "family=Noto+Sans+Kannada:wght@400;500;600;700&family=DM+Sans:wght@400;600;700",
        "font_var": "'Noto Sans Kannada', sans-serif",
        "title": "ಕನ್ನಡ ಬೈಬಲ್ ವಚನಗಳ ನೆನಪು — Bible Study with Steffi | Android",
        "desc": "ಕನ್ನಡದಲ್ಲಿ ಬೈಬಲ್ ವಚನಗಳನ್ನು ನೆನಪಿಟ್ಟುಕೊಳ್ಳಿ. ಸ್ಪೇಸ್ಡ್ ರಿಪಿಟಿಶನ್, ಪ್ಯಾರಲೆಲ್ ಬೈಬಲ್ — Google Play ನಲ್ಲಿ ಉಚಿತ ಆ್ಯಪ್.",
        "h1": "ಕನ್ನಡದಲ್ಲಿ ಬೈಬಲ್ ವಚನಗಳನ್ನು ಗಟ್ಟಿಯಾಗಿ ನೆನಪಿಟ್ಟುಕೊಳ್ಳಿ",
        "lead": "Memorize Scripture in <strong>Kannada</strong> with spaced repetition and parallel English — free Bible Study with Steffi on Google Play.",
        "bullets": [
            "SM2 ಶೈಲಿಯ ಶೆಡ್ಯೂಲಿಂಗ್: ಮರೆತುಹೋಗುವ ಮೊದಲು ಪುನರಾವೃತ್ತಿ.",
            "ESV, NKJV, KJV ಜೊತೆ ಪ್ಯಾರಲೆಲ್ ಓದುವಿಕೆ.",
            "ಉಚಿತ. ಜಾಹೀರಾತುಗಳಿಲ್ಲ. ಇನ್-ಆ್ಯಪ್ ಖರೀದಿಗಳಿಲ್ಲ.",
        ],
        "cta": "Google Play ನಿಂದ ಇನ್‌ಸ್ಟಾಲ್ ಮಾಡಿ",
        "card_kw": "Kannada Bible",
        "og_loc": "kn_IN",
    },
    {
        "slug": "malayalam-bible.html",
        "hreflang": "ml",
        "lang": "ml",
        "font_query": "family=Noto+Sans+Malayalam:wght@400;500;600;700&family=DM+Sans:wght@400;600;700",
        "font_var": "'Noto Sans Malayalam', sans-serif",
        "title": "മലയാളം ബൈബിൾ വചനങ്ങൾ ഓർമ്മിക്കുക — Bible Study with Steffi",
        "desc": "മലയാളത്തിൽ ബൈബിൾ വചനങ്ങൾ ഓർമ്മിച്ചുവയ്ക്കുക. സ്പേസ് റിപ്പിറ്റിഷൻ, പാരലൽ ബൈബിൾ — Google Play-ൽ സൗജന്യ ആപ്പ്.",
        "h1": "മലയാളത്തിൽ ദൈവവചനം മനഃപാഠമാക്കുക",
        "lead": "Memorize Scripture in <strong>Malayalam</strong> with spaced repetition and parallel English — free Bible Study with Steffi on Google Play.",
        "bullets": [
            "SM2 ശൈലിയിലുള്ള ഷെഡ്യൂളിംഗ്: മറക്കുന്നതിനുമുമ്പ് റിവ്യൂ.",
            "ESV, NKJV, KJV എന്നിവയോടൊപ്പം പാരലൽ വായന.",
            "സൗജന്യം. പരസ്യങ്ങളില്ല. ഇൻ-ആപ്പ് വാങ്ങലുകളില്ല.",
        ],
        "cta": "Google Play-ൽ ഇൻസ്റ്റാൾ ചെയ്യുക",
        "card_kw": "Malayalam Bible",
        "og_loc": "ml_IN",
    },
    {
        "slug": "bengali-bible.html",
        "hreflang": "bn",
        "lang": "bn",
        "font_query": "family=Noto+Sans+Bengali:wght@400;500;600;700&family=DM+Sans:wght@400;600;700",
        "font_var": "'Noto Sans Bengali', sans-serif",
        "title": "বাংলা বাইবেল শ্লোক মুখস্থ — Bible Study with Steffi | Android",
        "desc": "বাংলায় বাইবেলের শ্লোক মনে রাখুন। স্পেসড রিপিটিশন, প্যারালেল বাইবেল — Google Play-এ বিনামূল্যে।",
        "h1": "বাংলায় বাইবেলের শ্লোক দৃঢ়ভাবে মুখস্থ করুন",
        "lead": "Memorize Scripture in <strong>Bengali</strong> with spaced repetition and parallel English — free Bible Study with Steffi on Google Play.",
        "bullets": [
            "SM2-স্টাইল শিডিউলিং: ভুলে যাওয়ার আগেই রিভিউ।",
            "ESV, NKJV, KJV-এর সাথে প্যারালেল পাঠ।",
            "বিনামূল্যে। বিজ্ঞাপন নেই। ইন-অ্যাপ কেনাকাটা নেই।",
        ],
        "cta": "Google Play থেকে ইনস্টল করুন",
        "card_kw": "Bengali Bible",
        "og_loc": "bn_IN",
    },
    {
        "slug": "odia-bible.html",
        "hreflang": "or",
        "lang": "or",
        "font_query": "family=Noto+Sans+Oriya:wght@400;500;600;700&family=DM+Sans:wght@400;600;700",
        "font_var": "'Noto Sans Oriya', sans-serif",
        "title": "ଓଡ଼ିଆ ବାଇବେଲ ଶ୍ଳୋକ ମନେରଖନ୍ତୁ — Bible Study with Steffi",
        "desc": "ଓଡ଼ିଆରେ ବାଇବେଲ ଶ୍ଳୋକ ମନେରଖନ୍ତୁ। ସ୍ପେସ୍ଡ ରିପିଟିସନ୍, ପ୍ୟାରାଲେଲ୍ ବାଇବେଲ୍ — Google Playରେ ମାଗଣା ଆପ୍।",
        "h1": "ଓଡ଼ିଆରେ ବାଇବେଲ ଶ୍ଳୋକ ଦୃଢ଼ ଭାବେ ମନେରଖନ୍ତୁ",
        "lead": "Memorize Scripture in <strong>Odia</strong> with spaced repetition and parallel English — free Bible Study with Steffi on Google Play.",
        "bullets": [
            "SM2-ଶୈଳୀ ସିଡୁଲିଂ: ଭୁଲିବା ପୂର୍ବରୁ ପୁନରାବୃତ୍ତି।",
            "ESV, NKJV, KJV ସହିତ ପ୍ୟାରାଲେଲ୍ ପଠନ।",
            "ମାଗଣା। ବିଜ୍ଞାପନ ନାହିଁ। ଇନ୍-ଆପ୍ କିଣାକିଣି ନାହିଁ।",
        ],
        "cta": "Google Playରୁ ଇନଷ୍ଟଲ୍ କରନ୍ତୁ",
        "card_kw": "Odia Bible",
        "og_loc": "or_IN",
    },
    {
        "slug": "marathi-bible.html",
        "hreflang": "mr",
        "lang": "mr",
        "font_query": "family=Noto+Sans+Devanagari:wght@400;500;600;700&family=DM+Sans:wght@400;600;700",
        "font_var": "'Noto Sans Devanagari', sans-serif",
        "title": "मराठी बायबल वचने लक्षात ठेवा — Bible Study with Steffi",
        "desc": "मराठीत बायबलच्या वचनांचे स्मरण ठेवा. स्पेस्ड रिपीटिशन, पॅरेलल बायबल — Google Play वर मोफत अॅप.",
        "h1": "मराठीत बायबल वचने तळहातावर ठेवा",
        "lead": "Memorize Scripture in <strong>Marathi</strong> with spaced repetition and parallel English — free Bible Study with Steffi on Google Play.",
        "bullets": [
            "SM2-स्टाइल शेड्युलिंग: विसरण्यापूर्वी पुनरावलोकन.",
            "ESV, NKJV, KJV सोबत समांतर वाचन.",
            "मोफत. जाहिराती नाहीत. इन-अॅप खरेदी नाही.",
        ],
        "cta": "Google Play वरून इंस्टॉल करा",
        "card_kw": "Marathi Bible",
        "og_loc": "mr_IN",
    },
    {
        "slug": "gujarati-bible.html",
        "hreflang": "gu",
        "lang": "gu",
        "font_query": "family=Noto+Sans+Gujarati:wght@400;500;600;700&family=DM+Sans:wght@400;600;700",
        "font_var": "'Noto Sans Gujarati', sans-serif",
        "title": "ગુજરાતી બાઇબલ શ્લોક યાદ રાખો — Bible Study with Steffi",
        "desc": "ગુજરાતીમાં બાઇબલના શ્લોકો યાદ રાખો. સ્પેસ્ડ રિપિટિશન, પેરેલલ બાઇબલ — Google Play પર મફત એપ.",
        "h1": "ગુજરાતીમાં બાઇબલના શ્લોકો મજબૂતી થી યાદ રાખો",
        "lead": "Memorize Scripture in <strong>Gujarati</strong> with spaced repetition and parallel English — free Bible Study with Steffi on Google Play.",
        "bullets": [
            "SM2 શૈલીનું શેડ્યુલિંગ: ભૂલાતા પહેલાં રિવ્યુ.",
            "ESV, NKJV, KJV સાથે સમાંતર વાંચન.",
            "મફત. જાહેરાતો નહીં. ઇન-એપ ખરીદી નહીં.",
        ],
        "cta": "Google Play પરથી ઇન્સ્ટોલ કરો",
        "card_kw": "Gujarati Bible",
        "og_loc": "gu_IN",
    },
    {
        "slug": "punjabi-bible.html",
        "hreflang": "pa",
        "lang": "pa",
        "font_query": "family=Noto+Sans+Gurmukhi:wght@400;500;600;700&family=DM+Sans:wght@400;600;700",
        "font_var": "'Noto Sans Gurmukhi', sans-serif",
        "title": "ਪੰਜਾਬੀ ਬਾਈਬਲ ਆਇਤਾਂ ਯਾਦ ਰੱਖੋ — Bible Study with Steffi",
        "desc": "ਪੰਜਾਬੀ ਵਿੱਚ ਬਾਈਬਲ ਦੀਆਂ ਆਇਤਾਂ ਯਾਦ ਰੱਖੋ। ਸਪੇਸਡ ਰਿਪੀਟਿਸ਼ਨ, ਪੈਰਾਲਲ ਬਾਈਬਲ — Google Play ਤੇ ਮੁਫ਼ਤ ਐਪ।",
        "h1": "ਪੰਜਾਬੀ ਵਿੱਚ ਬਾਈਬਲ ਦੀਆਂ ਆਇਤਾਂ ਠੋਸ ਤੌਰ ਤੇ ਯਾਦ ਰੱਖੋ",
        "lead": "Memorize Scripture in <strong>Punjabi (Gurmukhi)</strong> with spaced repetition and parallel English — free Bible Study with Steffi on Google Play.",
        "bullets": [
            "SM2-ਸਟਾਈਲ ਸ਼ੈਡਿਊਲਿੰਗ: ਭੁੱਲਣ ਤੋਂ ਪਹਿਲਾਂ ਦੁਹਰਾਓ।",
            "ESV, NKJV, KJV ਨਾਲ ਪੈਰਾਲਲ ਪੜ੍ਹਨਾ।",
            "ਮੁਫ਼ਤ। ਕੋਈ ਇਸ਼ਤਿਹਾਰ ਨਹੀਂ। ਇਨ-ਐਪ ਖਰੀਦ ਨਹੀਂ।",
        ],
        "cta": "Google Play ਤੋਂ ਇੰਸਟਾਲ ਕਰੋ",
        "card_kw": "Punjabi Bible",
        "og_loc": "pa_IN",
    },
    {
        "slug": "urdu-bible.html",
        "hreflang": "ur",
        "lang": "ur",
        "dir": "rtl",
        "font_query": "family=Noto+Nastaliq+Urdu:wght@400;600;700&family=DM+Sans:wght@400;600;700",
        "font_var": "'Noto Nastaliq Urdu', serif",
        "title": "اردو بائبل آیات یاد رکھیں — Bible Study with Steffi",
        "desc": "اردو میں بائبل کی آیات یاد رکھیں۔ اسپیسڈ ریپیٹیشن، متوازی بائبل — Google Play پر مفت ایپ۔",
        "h1": "اردو میں بائبل کی آیات مضبوطی سے یاد رکھیں",
        "lead": "Memorize Scripture in <strong>Urdu</strong> with spaced repetition and parallel English — free Bible Study with Steffi on Google Play.",
        "bullets": [
            "SM2 طرز کا شیڈول: بھولنے سے پہلے دوبارہ نظرثانی۔",
            "ESV, NKJV, KJV کے ساتھ متوازی مطالعہ۔",
            "مفت۔ کوئی اشتہارات نہیں۔ ان ایپ خریداری نہیں۔",
        ],
        "cta": "Google Play سے انسٹال کریں",
        "card_kw": "Urdu Bible",
        "og_loc": "ur_PK",
    },
    {
        "slug": "assamese-bible.html",
        "hreflang": "as",
        "lang": "as",
        "font_query": "family=Noto+Sans+Assamese:wght@400;500;600;700&family=DM+Sans:wght@400;600;700",
        "font_var": "'Noto Sans Assamese', sans-serif",
        "title": "অসমীয়া বাইবেল শ্লোক মনত ৰাখক — Bible Study with Steffi",
        "desc": "অসমীয়াত বাইবেলৰ শ্লোক মনত ৰাখক। স্পেচড ৰিপিটিশ্বন, পেৰালেল বাইবেল — Google Playত বিনামূলীয়া এপ্।",
        "h1": "অসমীয়াত বাইবেলৰ শ্লোক দৃঢ়ভাৱে মনত ৰাখক",
        "lead": "Memorize Scripture in <strong>Assamese</strong> with spaced repetition and parallel English — free Bible Study with Steffi on Google Play.",
        "bullets": [
            "SM2-শৈলীৰ শ্বিডিউলিং: পাহৰোৱাৰ আগতে পুনৰীক্ষণ।",
            "ESV, NKJV, KJVৰ লগতে পেৰালেল পঠন।",
            "বিনামূলীয়া। বিজ্ঞাপন নাই। ইন-এপ ক্ৰয় নাই।",
        ],
        "cta": "Google Playৰ পৰা ইনষ্টল কৰক",
        "card_kw": "Assamese Bible",
        "og_loc": "as_IN",
    },
]

MENU = [
    ("english-bible.html", "English", "ESV · NKJV · KJV"),
    ("telugu-bible.html", "తెలుగు", "Telugu"),
    ("hindi-bible.html", "हिन्दी", "Hindi"),
    ("tamil-bible.html", "தமிழ்", "Tamil"),
    ("kannada-bible.html", "ಕನ್ನಡ", "Kannada"),
    ("malayalam-bible.html", "മലയാളം", "Malayalam"),
    ("bengali-bible.html", "বাংলা", "Bengali"),
    ("odia-bible.html", "ଓଡ଼ିଆ", "Odia"),
    ("marathi-bible.html", "मराठी", "Marathi"),
    ("gujarati-bible.html", "ગુજરાતી", "Gujarati"),
    ("punjabi-bible.html", "ਪੰਜਾਬੀ", "Punjabi"),
    ("urdu-bible.html", "اردو", "Urdu"),
    ("assamese-bible.html", "অসমীয়া", "Assamese"),
]

PLAY = "https://play.google.com/store/apps/details?id=com.biblestudywithsteffi.app"
SITE = "https://bswsapp.com"


def dropdown(current_slug: str) -> str:
    lines = [
        '<details class="nav-lang-details">',
        '  <summary>Bible languages</summary>',
        '  <nav class="nav-lang-panel" aria-label="Choose language page">',
    ]
    for href, primary, sub in MENU:
        cur = ' aria-current="page"' if href == current_slug else ""
        lines.append(
            f'    <a href="{href}"{cur}><span>{primary}</span><span class="sub">{sub}</span></a>'
        )
    lines.append("  </nav>")
    lines.append("</details>")
    return "\n".join(lines)


def render(lang: dict) -> str:
    slug = lang["slug"]
    url = f"{SITE}/{slug}"
    bullets_html = "\n".join(f"      <li>{b}</li>" for b in lang["bullets"])
    menu = dropdown(slug)
    ld = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Bible Study with Steffi",
        "inLanguage": lang["hreflang"],
        "description": lang["desc"][:220],
        "applicationCategory": "LifestyleApplication",
        "operatingSystem": "Android",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "installUrl": PLAY,
        "url": url,
    }
    ld_json = json.dumps(ld, ensure_ascii=False)
    hreflang_extra = ""
    if lang["hreflang"] != "en":
        hreflang_extra = f'<link rel="alternate" hreflang="en" href="{SITE}/">\n'
    dir_attr = lang.get("dir", "ltr")
    return f"""<!DOCTYPE html>
<html lang="{lang["lang"]}" dir="{dir_attr}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{lang["title"]}</title>
<meta name="description" content="{lang["desc"]}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="x-default" href="{SITE}/">
{hreflang_extra}<link rel="alternate" hreflang="{lang["hreflang"]}" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{lang["title"][:80]}">
<meta property="og:description" content="{lang["desc"][:200]}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{lang["og_loc"]}">
<meta name="twitter:card" content="summary_large_image">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?{lang["font_query"]}&display=swap" rel="stylesheet">
<style>:root {{ --font-script: {lang["font_var"]}; }}</style>
<link rel="stylesheet" href="css/lang-landing.css">
<script type="application/ld+json">
{ld_json}
</script>
</head>
<body>
<a href="#main" class="skip-link">Skip to main content</a>
<header>
  <div class="header-inner">
    <a href="/" class="brand">Bible Study with Steffi</a>
    {menu}
  </div>
</header>
<main id="main">
  <div class="inner">
    <div class="hero-badge">Google Play · Android</div>
    <h1>{lang["h1"]}</h1>
    <p class="lead-en">{lang["lead"]}</p>
    <p class="trust-note">We do not publish download counts on this site. See recent <strong>ratings and reviews on Google Play</strong> before you install.</p>
    <ul class="bullets">
{bullets_html}
    </ul>
    <a href="{PLAY}" class="cta" target="_blank" rel="noopener noreferrer">
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3.609 1.814L13.792 12 3.61 22.186a.996.996 0 0 1-.61-.92V2.734a1 1 0 0 1 .609-.92zm10.89 10.893l2.302 2.302-10.937 6.333 8.635-8.635zm3.199-1.38l2.473 1.449c.63.369.63.997 0 1.366l-2.473 1.449-2.507-2.507 2.507-2.757zM5.864 2.658L16.8 9.002l-2.302 2.302-8.634-8.646z"/></svg>
      {lang["cta"]}
    </a>
    <div class="card">
      <h2>About this page</h2>
      <p>This page helps people searching for <strong>{lang["card_kw"]}</strong> memorization find the official Android app. Policies: Privacy and Terms below.</p>
    </div>
  </div>
</main>
<footer>
  <nav class="footer-links" aria-label="Footer">
    <a href="/">Home</a>
    <a href="privacy-policy.html">Privacy</a>
    <a href="terms-of-service.html">Terms</a>
  </nav>
</footer>
</body>
</html>
"""


def main():
    for lang in LANGS:
        path = OUT / lang["slug"]
        path.write_text(render(lang), encoding="utf-8")
        print("Wrote", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
