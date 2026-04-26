# Dynamic Bible Edge Backend

This folder contains a deployable edge handler for dynamic Bible chapter/verse rendering for non-English Indian languages.

## Why this exists

- Telugu + English stay fully static for SEO-stable high-volume pages.
- Other Indian-language versions use static language/book indexes, but chapters/verses are served dynamically.
- This avoids generating and shipping massive static chapter trees while still preserving clean URLs.

## Route shape

- `GET /api/bible/{version}/{book}/{chapter}`
- `GET /api/bible/{version}/{book}/{chapter}/{verse}`
- `GET /api/bible/parallel/{primary}/{secondary}/{book}/{chapter}`
- `GET /api/bible/parallel/{primary}/{secondary}/{book}/{chapter}/{verse}`
- `GET /bible/{version}/{book}/{chapter}/`
- `GET /bible/{version}/{book}/{chapter}/{verse}/`
- `GET /bible/parallel/{primary}/{secondary}/{book}/{chapter}/`
- `GET /bible/parallel/{primary}/{secondary}/{book}/{chapter}/{verse}/`

`/api/...` returns JSON, while `/bible/...` returns rendered HTML.

Notes:
- Dynamic chapter + verse routes are now available for dynamic and static versions as fallback.
- Parallel routes are dynamically rendered so they can be enabled for dynamic versions immediately.
- Telugu can remain a static chapter/verse language. Mixed pairs like
  `/bible/parallel/telugu/hindi/john/1/` still need the `/bible/parallel/*`
  worker route, because the static generator intentionally does not emit every
  static/dynamic parallel combination.

## Deploy notes

1. Deploy `worker.mjs` to Cloudflare Workers or another edge runtime that supports the Fetch API.
2. Configure route mapping so `/bible/*` requests that do not match static files are forwarded to the worker.
3. Keep static assets (`/bible/assets/*`) and static index/book pages served by the existing static host.

## Data source

The worker pulls Bible JSON from:

- local static host path (if exposed): `/bible/data/bible_{version}.json`
- fallback GitHub raw source: `https://raw.githubusercontent.com/cybercam/bibles_json/main/bible_{version}.json`

## Validation expectation

Before enabling indexing for dynamic languages:

- canonical URL correctness
- localized (BSI-standard) book names in UI
- route health for sample chapter + verse URLs
- route health for sample parallel chapter + verse URLs
- parity checks against static generator metadata
