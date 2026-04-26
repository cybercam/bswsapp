"""Theme-aware 404 pages."""

from .. import config
from ..config import ASSET_READER_JS_PATH, PLAY_STORE_URL, SITE_URL
from ..layout import html_head, output_asset_href, theme_sheet


def generate_not_found_page() -> str:
    canonical = f"{SITE_URL}/404.html"
    head = html_head(
        title="Page not found | Bible Study with Steffi",
        description=(
            "The page you were looking for could not be found. Continue reading the "
            "Bible online in Telugu, Indian languages, and English."
        ),
        canonical=canonical,
        lang="en-IN",
        hreflang_links="",
        keywords="Bible Study with Steffi 404, Bible reader, Telugu Bible online",
        robots_meta='<meta name="robots" content="noindex,follow"/>',
        extra_head="""
<style>
.nf-page{min-height:calc(100svh - 52px);position:relative;overflow:hidden;padding:28px 14px 88px;background:radial-gradient(circle at 18% 8%,color-mix(in srgb,var(--accent) 18%,transparent),transparent 28%),radial-gradient(circle at 88% 22%,color-mix(in srgb,var(--muted) 18%,transparent),transparent 30%),var(--bg)}
.nf-page::before{content:"";position:absolute;inset:auto -18% -26% -18%;height:48%;background:linear-gradient(90deg,transparent,color-mix(in srgb,var(--accent) 15%,transparent),transparent);transform:rotate(-4deg);pointer-events:none}
.nf-card{position:relative;width:min(1060px,100%);margin:0 auto;display:grid;grid-template-columns:minmax(0,1.05fr) minmax(280px,.8fr);gap:clamp(22px,5vw,52px);align-items:center;background:color-mix(in srgb,var(--card) 94%,transparent);border:1px solid var(--border);border-radius:32px;padding:clamp(22px,5vw,58px);box-shadow:0 30px 90px rgba(0,0,0,.18)}
.nf-kicker{display:inline-flex;align-items:center;gap:9px;font-family:'Cinzel',serif;font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--muted);margin-bottom:14px}
.nf-kicker svg{width:18px;height:18px;color:var(--accent)}
.nf-title{font-family:'Cinzel',serif;font-size:clamp(34px,8vw,78px);line-height:.98;color:var(--accent);max-width:760px;margin:0 0 18px;text-wrap:balance}
.nf-copy{font-size:clamp(16px,2.2vw,20px);line-height:1.8;color:var(--text);max-width:650px;margin:0 0 24px}
.nf-actions{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;max-width:560px}
.nf-action{min-height:52px;display:inline-flex;align-items:center;justify-content:center;gap:10px;border-radius:16px;padding:14px 16px;border:1px solid var(--border);font-family:'Cinzel',serif;font-size:12px;font-weight:600;text-align:center;text-decoration:none;transition:transform .18s ease,background .18s ease,border-color .18s ease}
.nf-action:hover{text-decoration:none;transform:translateY(-1px);border-color:var(--accent)}
.nf-action svg{width:18px;height:18px;flex:0 0 auto}
.nf-primary{grid-column:1/-1;background:var(--accent);color:var(--bg);border-color:var(--accent)}
.nf-secondary{background:var(--bg2);color:var(--text)}
.nf-proof{display:flex;flex-wrap:wrap;gap:8px;margin-top:20px;color:var(--muted);font-size:12px}
.nf-proof span{border:1px solid var(--border);background:var(--bg2);border-radius:999px;padding:7px 10px}
.nf-phone-wrap{display:grid;place-items:center}
.nf-phone{width:min(312px,78vw);aspect-ratio:9/18.5;border:1px solid var(--border);border-radius:38px;background:linear-gradient(180deg,var(--bg2),var(--card));padding:13px;box-shadow:0 22px 70px rgba(0,0,0,.22);position:relative}
.nf-phone::before{content:"";position:absolute;top:9px;left:50%;width:76px;height:6px;border-radius:999px;background:var(--border);transform:translateX(-50%)}
.nf-screen{height:100%;border-radius:28px;border:1px solid var(--border);background:var(--bg);padding:30px 16px 16px;display:flex;flex-direction:column;gap:14px;overflow:hidden}
.nf-app-chip{align-self:flex-start;border:1px solid var(--border);border-radius:999px;padding:6px 10px;font-family:'Cinzel',serif;font-size:10px;color:var(--accent);background:var(--card)}
.nf-verse-card{border:1px solid var(--border);border-radius:18px;background:var(--card);padding:16px}
.nf-verse-ref{font-family:'Cinzel',serif;font-size:11px;color:var(--accent);margin-bottom:8px}
.nf-verse-line{height:10px;border-radius:999px;background:color-mix(in srgb,var(--text) 22%,transparent);margin:8px 0}
.nf-verse-line.short{width:64%}
.nf-mini-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:auto}
.nf-mini{border:1px solid var(--border);border-radius:16px;background:var(--card);min-height:76px;padding:12px}
.nf-mini svg{width:22px;height:22px;color:var(--accent);margin-bottom:12px}
.nf-mini div{height:8px;border-radius:999px;background:color-mix(in srgb,var(--muted) 28%,transparent)}
.nf-bottom-note{margin-top:16px;font-size:12px;line-height:1.6;color:var(--muted);max-width:560px}
@media(prefers-reduced-motion:reduce){.nf-action{transition:none}.nf-action:hover{transform:none}}
@media(max-width:820px){.nf-card{grid-template-columns:1fr;border-radius:26px}.nf-phone-wrap{order:-1}.nf-phone{width:min(268px,76vw)}.nf-actions{grid-template-columns:1fr}.nf-primary{grid-column:auto}}
@media(max-width:430px){.nf-page{padding:18px 10px 72px}.nf-card{padding:20px;border-radius:22px}.nf-title{font-size:clamp(31px,12vw,48px)}.nf-phone{width:min(236px,74vw);border-radius:30px}.nf-screen{border-radius:22px}.nf-action{min-height:50px}}
</style>""",
    )
    return f"""{head}
<body>
<header id="topbar">
  <a href="/" class="icon-btn" aria-label="Back to main website">Home</a>
  <a href="/{config.OUT_DIR}/" class="icon-btn" aria-label="Go to Bible index">Bibles</a>
  <span class="logo">Bible Study with Steffi</span>
  <span class="crumb">Page not found</span>
  <button type="button" id="theme-btn" class="icon-btn" aria-label="Reading theme and colors">Aa</button>
</header>
<div id="wrap">
  <main class="nf-page">
    <section class="nf-card" aria-labelledby="not-found-title">
      <div>
        <p class="nf-kicker">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 19.5V6.75A2.75 2.75 0 0 1 6.75 4H20v15.5H6.75A2.75 2.75 0 0 0 4 22.25" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/><path d="M8 8h8M8 11.5h6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
          Page 404
        </p>
        <h1 id="not-found-title" class="nf-title">You found a quiet corner.</h1>
        <p class="nf-copy">
          This page is missing, but the reader is close by. Open the Bible online,
          return home, or download the app for daily verse memory in your language.
        </p>
        <div class="nf-actions" aria-label="Page recovery actions">
          <a class="nf-action nf-primary" href="{PLAY_STORE_URL}" target="_blank" rel="noopener">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 3.5v17l11-8.5-11-8.5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="m7 3.5 7.5 8.5L7 20.5" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>
            Download the free app
          </a>
          <a class="nf-action nf-secondary" href="/">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 11.5 12 5l8 6.5V20a1 1 0 0 1-1 1h-5v-6h-4v6H5a1 1 0 0 1-1-1v-8.5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg>
            Home page
          </a>
          <a class="nf-action nf-secondary" href="/{config.OUT_DIR}/">
            <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 4.5h10.5A3.5 3.5 0 0 1 19 8v11.5H8.5A3.5 3.5 0 0 1 5 16V4.5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/><path d="M8.5 8H16M8.5 11.5H15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>
            Bible pages
          </a>
        </div>
        <div class="nf-proof" aria-label="Reader highlights">
          <span>Telugu Bible</span><span>15+ languages</span><span>No ads</span><span>Daily memorization</span>
        </div>
        <p class="nf-bottom-note">Tip: use the Aa button to preview this page in every reader theme.</p>
      </div>
      <div class="nf-phone-wrap" aria-hidden="true">
        <div class="nf-phone">
          <div class="nf-screen">
            <div class="nf-app-chip">Bible Study with Steffi</div>
            <div class="nf-verse-card">
              <div class="nf-verse-ref">John 1:1</div>
              <div class="nf-verse-line"></div>
              <div class="nf-verse-line"></div>
              <div class="nf-verse-line short"></div>
            </div>
            <div class="nf-mini-grid">
              <div class="nf-mini"><svg viewBox="0 0 24 24" fill="none"><path d="M6 5h12v15l-6-3-6 3V5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/></svg><div></div></div>
              <div class="nf-mini"><svg viewBox="0 0 24 24" fill="none"><path d="M12 5v14M5 12h14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg><div></div></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</div>
{theme_sheet()}
<script src="{output_asset_href(ASSET_READER_JS_PATH)}" defer></script>
</body>
</html>"""
