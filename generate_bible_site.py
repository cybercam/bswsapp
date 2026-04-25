#!/usr/bin/env python3
"""
BSWS Phase 3 — Static Bible Site Generator
==========================================
Implementation lives in the ``site_builder`` package; this file is the CLI entry point.

Run from the repo root:
  python3 generate_bible_site.py
  python3 generate_bible_site.py --only telugu
  python3 generate_bible_site.py --dry-run --only kjv

Book-wise KJV + Telugu (git commit + local prune of chapter trees) is scripted as:
  ./scripts/bookwise_kjv_telugu.sh

Lower memory (one version per Python process; checkpoint file bible/.bookwise_checkpoint):
  ./scripts/bookwise_kjv_telugu_sequential.sh

All versions, one (version, book) per job with bounded parallel workers, per-job push,
and temp worktree cleanup:
  ./scripts/bookwise_all_versions_parallel.sh

Manual book slice + URL log for a custom sitemap workflow:
  python3 generate_bible_site.py --only kjv,telugu --modules chapters,verses \\
    --books genesis --sitemap-url-log bible/_generated_urls.txt
  python3 generate_bible_site.py --only kjv,telugu --modules sitemap \\
    --sitemap-url-log bible/_generated_urls.txt

Curated popular verse URLs (slug pages) + SEO checks:
  python3 generate_bible_site.py --only telugu --modules popular
  python3 scripts/seo_validate_bible.py
"""
from site_builder.builder import main

if __name__ == "__main__":
    main()
