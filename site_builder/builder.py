"""CLI orchestration for static Bible site."""
import argparse
from pathlib import Path

from . import assets
from . import config
from .config import (
    DEFAULT_VERSION_ID,
    LOCAL_CROSSREFS_JSON,
    LOCAL_STRONGS_JSON,
    PARALLEL_LINK_MODE,
    SITE_URL,
    VERSIONS,
    apply_cli_config,
    version_has_verse_detail_features,
)
from . import seo_content
from .data_loader import (
    build_bcv_text_map,
    build_verse_lookup,
    download_json,
    load_interlinear_book_mapping,
    load_interlinear_book_tokens,
    load_local_json,
    normalise,
)
from .helpers import (
    book_slug,
    display_book_name,
    iter_parallel_version_pairs,
    verse_detail_rel_url,
    verse_get,
    version_label,
    version_lang,
)
from .io_utils import append_url_to_sitemap_log, parse_modules, should_run, write_if_changed
from .templates import sitemap
from .templates.chapter import generate_chapter_page
from .templates.index_pages import (
    generate_bible_index,
    generate_book_index_page,
    generate_version_index_page,
)
from .templates.parallel import generate_parallel_chapter_page
from .templates.popular_verses import generate_popular_verse_landing_page
from .templates.verse_detail import generate_verse_detail_page

def resolve_active_versions(only_csv: str):
    """Return VERSIONS rows to build. Empty only_csv means all versions."""
    valid_ids = {v[0] for v in VERSIONS}
    if not (only_csv or "").strip():
        return list(VERSIONS)
    wanted = {x.strip() for x in only_csv.split(",") if x.strip()}
    unknown = wanted - valid_ids
    if unknown:
        raise SystemExit(
            f"Unknown version id(s): {sorted(unknown)}. Valid ids: {sorted(valid_ids)}"
        )
    return [v for v in VERSIONS if v[0] in wanted]


def parse_books_filter(books_csv: str, bible_by_id: dict) -> frozenset[str] | None:
    """Lowercase book URL slugs to include, or None = all books."""
    if not (books_csv or "").strip():
        return None
    if not bible_by_id:
        raise SystemExit("--books requires at least one successfully loaded Bible JSON")
    first = next(iter(bible_by_id.values()))
    valid_lower = {book_slug(b["n"]).lower() for b in first.get("books", [])}
    wanted = {x.strip().lower() for x in books_csv.split(",") if x.strip()}
    unknown = wanted - valid_lower
    if unknown:
        raise SystemExit(
            f"Unknown book slug(s): {sorted(unknown)}. "
            f"Use URL slugs like genesis, john (see BOOK_SLUGS / book names in JSON)."
        )
    return frozenset(wanted)


def book_in_filter(bslug: str, books_filter: frozenset[str] | None) -> bool:
    return books_filter is None or bslug.lower() in books_filter


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate static Bible HTML under ./bible/",
    )
    parser.add_argument(
        "--only",
        metavar="IDS",
        default="",
        help=(
            "Comma-separated version ids to build (e.g. telugu). Default: all versions. "
            "Note: /bible/ index still lists all VERSIONS as reader cards; only chapter/verse "
            "pages are limited by this flag."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Count and report outputs without writing files.",
    )
    parser.add_argument(
        "--output",
        default="bible",
        help="Output directory (default: bible).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip chapter/verse generation for versions that already have output.",
    )
    parser.add_argument(
        "--modules",
        default="all",
        help="Comma-separated modules: assets,indexes,chapters,verses,parallel,popular,sitemap (default: all).",
    )
    parser.add_argument(
        "--books",
        metavar="SLUGS",
        default="",
        help=(
            "Comma-separated book URL slugs (e.g. genesis,john). When set, only those books get "
            "per-book indexes (with indexes module) and chapter/verse/parallel output. "
            "Prev/next nav still uses the full Bible."
        ),
    )
    parser.add_argument(
        "--sitemap-url-log",
        metavar="PATH",
        default="",
        help=(
            "Append each chapter/verse sitemap URL to this file as it is generated. "
            "With --modules sitemap, if the file exists its unique lines replace in-memory URLs "
            "(for book-wise runs after local prune)."
        ),
    )
    args = parser.parse_args()
    apply_cli_config(args.output)
    selected_modules = parse_modules(args.modules)
    effective_modules = set(selected_modules)
    asset_dependent_modules = {"indexes", "chapters", "verses", "popular"}
    if asset_dependent_modules.intersection(effective_modules) and "assets" not in effective_modules:
        print(
            "[modules] Auto-enabling 'assets' because selected modules depend on shared assets."
        )
        effective_modules.add("assets")

    print("=" * 60)
    print("  BSWS Phase 3 — Static Bible Site Generator")
    print("=" * 60)

    valid_ids = {v[0] for v in VERSIONS}
    if DEFAULT_VERSION_ID not in valid_ids:
        raise SystemExit(
            f"DEFAULT_VERSION_ID {DEFAULT_VERSION_ID!r} must be one of: {sorted(valid_ids)}"
        )

    active_versions = resolve_active_versions(args.only)
    active_ids = {v[0] for v in active_versions}
    # Keep x-default stable across partial builds. Production may regenerate one
    # translation at a time, but hreflang x-default should still point at the
    # neutral/default reader rather than the currently active regional version.
    x_default_id = DEFAULT_VERSION_ID

    config.OUT_DIR.mkdir(parents=True, exist_ok=True)

    all_sitemap_urls = []
    index_sitemap_urls: list[str] = []
    popular_sitemap_urls: list[str] = []
    sitemap_summary_count: int | None = None
    total_pages = 0
    bible_by_id = {}
    global_strongs_dict = {}

    print(
        f"\n[prep] Loading JSON data for {len(active_versions)} version(s): "
        f"{', '.join(v[0] for v in active_versions)}..."
    )
    for version_id, vlabel, lang_code, script, group in active_versions:
        data_raw = download_json(version_id)
        if not data_raw:
            print(f"  [warn] skipped {version_id} — could not load JSON")
            continue

        bible = normalise(data_raw)
        bible_by_id[version_id] = bible

    books_filter = parse_books_filter(args.books, bible_by_id)

    english_bcv_map: dict[str, str] = {}
    english_parallel_source_id = ""
    for _eid in ("web", "kjv", "bbe"):
        if _eid in bible_by_id:
            english_bcv_map = build_bcv_text_map(bible_by_id[_eid])
            english_parallel_source_id = _eid
            break
    sitemap_log_path = Path(args.sitemap_url_log) if (args.sitemap_url_log or "").strip() else None
    if books_filter:
        print(f"\n[books] Restricting content to {len(books_filter)} book(s): {', '.join(sorted(books_filter))}")
    if sitemap_log_path:
        print(f"\n[sitemap-log] Appending chapter/verse URLs to {sitemap_log_path}")

    if should_run("assets", effective_modules):
        if not global_strongs_dict:
            global_strongs_dict = load_local_json(LOCAL_STRONGS_JSON, "strongs dictionary")
        print("\n[assets] Writing shared assets...")
        assets.write_shared_assets(
            dry_run=args.dry_run,
            strongs_dict=global_strongs_dict,
            bible_by_id=bible_by_id,
            active_versions=active_versions,
        )

    if should_run("indexes", effective_modules):
        print("\n[indexes] Writing bible and version indexes...")
        index_sitemap_urls.append(f"{SITE_URL}/bible/")
        write_if_changed(
            config.OUT_DIR / "index.html",
            generate_bible_index(active_versions, x_default_id),
            args.dry_run,
        )
        for version_id, vlabel, lang_code, script, group in active_versions:
            bible = bible_by_id.get(version_id)
            if not bible:
                continue
            ver_dir = config.OUT_DIR / version_id
            ver_dir.mkdir(parents=True, exist_ok=True)
            index_sitemap_urls.append(f"{SITE_URL}/bible/{version_id}/")
            write_if_changed(
                ver_dir / "index.html",
                generate_version_index_page(version_id, vlabel, lang_code, bible["books"]),
                args.dry_run,
            )
            for book in bible["books"]:
                bslug = book_slug(book["n"])
                if not book_in_filter(bslug, books_filter):
                    continue
                index_sitemap_urls.append(f"{SITE_URL}/bible/{version_id}/{bslug}/")
                write_if_changed(
                    ver_dir / bslug / "index.html",
                    generate_book_index_page(version_id, vlabel, lang_code, book),
                    args.dry_run,
                )

    if should_run("chapters", effective_modules) or should_run("verses", effective_modules):
        print(
            f"\n[content] Generating chapters/verses for {len(active_versions)} version(s): "
            f"{', '.join(v[0] for v in active_versions)}..."
        )

    for version_id, vlabel, lang_code, script, group in active_versions:
        if not (should_run("chapters", effective_modules) or should_run("verses", effective_modules)):
            break

        print(f"\n  ▸ {vlabel} ({version_id})")
        bible = bible_by_id.get(version_id)
        if not bible:
            print(f"    Skipped — could not load JSON")
            continue
        all_books = bible["books"]
        verse_lookup = build_verse_lookup(all_books, version_id)

        crossrefs_data = {}
        strongs_dict = {}
        interlinear_map = {}
        interlinear_book_cache = {}
        if version_has_verse_detail_features(version_id):
            crossrefs_data = load_local_json(LOCAL_CROSSREFS_JSON, "crossrefs_mobile.json")
            strongs_dict = global_strongs_dict or load_local_json(LOCAL_STRONGS_JSON, "strongs dictionary")
            interlinear_map = load_interlinear_book_mapping()

        # Flat list of all (book, chapter) for prev/next navigation
        all_chapters = []
        for bk in all_books:
            for ch in bk["ch"]:
                all_chapters.append((bk, ch))

        ver_dir = config.OUT_DIR / version_id
        ver_dir.mkdir(exist_ok=True)

        if args.resume and ver_dir.exists() and any(ver_dir.iterdir()):
            print(f"    [RESUME] Skipping {version_id} — output already exists.")
            continue

        version_pages = 0
        version_verse_pages = 0
        for idx, (book, chapter) in enumerate(all_chapters):
            bslug  = book_slug(book["n"])
            ch_num = chapter["c"]
            if not book_in_filter(bslug, books_filter):
                continue

            # Prev / next URLs
            prev_url = None
            next_url = None
            if idx > 0:
                pb, pc = all_chapters[idx - 1]
                prev_url = f"/{config.OUT_DIR}/{version_id}/{book_slug(pb['n'])}/{pc['c']}/"
            if idx < len(all_chapters) - 1:
                nb, nc = all_chapters[idx + 1]
                next_url = f"/{config.OUT_DIR}/{version_id}/{book_slug(nb['n'])}/{nc['c']}/"

            html = generate_chapter_page(
                bible_data=bible,
                version_id=version_id,
                vlabel=vlabel,
                lang_code=lang_code,
                book=book,
                chapter=chapter,
                all_books=all_books,
                prev_url=prev_url,
                next_url=next_url,
                active_versions=active_versions,
                x_default_id=x_default_id,
            )

            out_path = ver_dir / bslug / str(ch_num)
            out_path.mkdir(parents=True, exist_ok=True)
            if should_run("chapters", effective_modules):
                write_if_changed(out_path / "index.html", html, args.dry_run)

            page_url = f"{SITE_URL}/{config.OUT_DIR}/{version_id}/{bslug}/{ch_num}/"
            if should_run("chapters", effective_modules):
                all_sitemap_urls.append(page_url)
                if sitemap_log_path:
                    append_url_to_sitemap_log(sitemap_log_path, page_url, args.dry_run)
                total_pages += 1
                version_pages += 1

            interlinear_chapters_for_book = {}
            if version_has_verse_detail_features(version_id):
                abbrev = interlinear_map.get(book.get("b"), "")
                if abbrev:
                    if abbrev not in interlinear_book_cache:
                        interlinear_book_cache[abbrev] = load_interlinear_book_tokens(abbrev)
                    interlinear_chapters_for_book = interlinear_book_cache.get(abbrev, {})

            verse_items = sorted(chapter["v"].items(), key=lambda x: int(x[0]))
            for v_idx, (vnum, vtext) in enumerate(verse_items):
                prev_verse_url = (
                    verse_detail_rel_url(version_id, bslug, ch_num, verse_items[v_idx - 1][0])
                    if v_idx > 0
                    else None
                )
                next_verse_url = (
                    verse_detail_rel_url(version_id, bslug, ch_num, verse_items[v_idx + 1][0])
                    if v_idx < len(verse_items) - 1
                    else None
                )
                chapter_url = f"/{config.OUT_DIR}/{version_id}/{bslug}/{ch_num}/"
                bcv_key = f"{book['b']}_{ch_num}_{vnum}"
                en_text = (
                    english_bcv_map.get(bcv_key, "").strip()
                    if english_bcv_map
                    else ""
                )
                en_lbl = (
                    f"{version_label(english_parallel_source_id)} (reference)"
                    if english_parallel_source_id and en_text
                    else ""
                )
                verse_html = generate_verse_detail_page(
                    version_id=version_id,
                    vlabel=vlabel,
                    lang_code=lang_code,
                    book_name=display_book_name(book, version_id),
                    book_name_source=book["n"],
                    bslug=bslug,
                    ch_num=ch_num,
                    vnum=vnum,
                    verse_text=vtext,
                    prev_verse_url=prev_verse_url,
                    next_verse_url=next_verse_url,
                    chapter_url=chapter_url,
                    active_versions=active_versions,
                    x_default_id=x_default_id,
                    verse_lookup=verse_lookup,
                    crossrefs_data=crossrefs_data,
                    strongs_dict=strongs_dict,
                    interlinear_chapters=interlinear_chapters_for_book,
                    english_verse_text=en_text,
                    english_source_label=en_lbl,
                )
                verse_out_path = ver_dir / bslug / str(ch_num) / str(vnum)
                verse_out_path.mkdir(parents=True, exist_ok=True)
                if should_run("verses", effective_modules):
                    write_if_changed(verse_out_path / "index.html", verse_html, args.dry_run)
                    vu = f"{SITE_URL}/{config.OUT_DIR}/{version_id}/{bslug}/{ch_num}/{vnum}/"
                    all_sitemap_urls.append(vu)
                    if sitemap_log_path:
                        append_url_to_sitemap_log(sitemap_log_path, vu, args.dry_run)
                    total_pages += 1
                    version_verse_pages += 1

        print(
            f"    ✓ {version_pages} chapter pages + {version_verse_pages} verse pages "
            f"for {version_id} (running total: {total_pages})"
        )

    # Parallel two-column chapters (same book/chapter, two built translations)
    if should_run("parallel", effective_modules):
        print(
            f"\n[parallel] Generating parallel chapter pages (mode={PARALLEL_LINK_MODE!r})..."
        )
    parallel_pages = 0
    par_root = config.OUT_DIR / "parallel"
    pairs = list(iter_parallel_version_pairs(active_versions, x_default_id))
    for vp, vs in pairs:
        if not should_run("parallel", effective_modules):
            break
        bible_p = bible_by_id.get(vp)
        bible_s = bible_by_id.get(vs)
        if not bible_p or not bible_s:
            continue
        vlabel_p = version_label(vp)
        vlabel_s = version_label(vs)
        all_books_p = bible_p["books"]
        all_chapters = []
        for bk in all_books_p:
            for ch in bk["ch"]:
                all_chapters.append((bk, ch))

        for idx, (book, chapter) in enumerate(all_chapters):
            bslug = book_slug(book["n"])
            ch_num = chapter["c"]
            if not book_in_filter(bslug, books_filter):
                continue
            pref = f"/{config.OUT_DIR}/parallel/{vp}/{vs}"
            prev_url = None
            next_url = None
            if idx > 0:
                pb, pc = all_chapters[idx - 1]
                prev_url = f"{pref}/{book_slug(pb['n'])}/{pc['c']}/"
            if idx < len(all_chapters) - 1:
                nb, nc = all_chapters[idx + 1]
                next_url = f"{pref}/{book_slug(nb['n'])}/{nc['c']}/"

            html_par = generate_parallel_chapter_page(
                bible_p=bible_p,
                bible_s=bible_s,
                vp=vp,
                vs=vs,
                vlabel_p=vlabel_p,
                vlabel_s=vlabel_s,
                lang_p=version_lang(vp),
                book_p=book,
                chapter_p=chapter,
                all_books=all_books_p,
                prev_url=prev_url,
                next_url=next_url,
                active_versions=active_versions,
                x_default_id=x_default_id,
            )
            out_path = par_root / vp / vs / bslug / str(ch_num)
            out_path.mkdir(parents=True, exist_ok=True)
            write_if_changed(out_path / "index.html", html_par, args.dry_run)
            parallel_pages += 1
            total_pages += 1

    if should_run("parallel", effective_modules):
        print(f"    ✓ {parallel_pages} parallel chapter pages (not added to sitemap; noindex)")

    if should_run("popular", effective_modules):
        print("\n[popular] Writing curated popular-verse landing pages...")
        popular_pages = 0
        en_lbl_full = (
            version_label(english_parallel_source_id)
            if english_parallel_source_id
            else "English"
        )
        for spec in seo_content.POPULAR_VERSE_LANDING_PAGES:
            vid = str(spec["version_id"])
            if vid not in active_ids:
                continue
            bible = bible_by_id.get(vid)
            if not bible:
                continue
            bslug = str(spec["bslug"])
            if books_filter and bslug.lower() not in books_filter:
                continue
            slug = str(spec["slug"])
            ch_i = int(spec["ch"])
            v_i = int(spec["v"])
            primary_txt = ""
            bnum = None
            book_row = None
            for bk in bible.get("books", []):
                if book_slug(bk.get("n", "")) != bslug:
                    continue
                book_row = bk
                bnum = bk.get("b")
                for chobj in bk.get("ch", []):
                    if int(chobj.get("c", -1)) != ch_i:
                        continue
                    primary_txt = verse_get(chobj.get("v") or {}, v_i)
                    break
                break
            if not (primary_txt or "").strip():
                print(f"    [warn] popular skip {vid}/{slug} — missing verse text")
                continue
            bcv_key = f"{bnum}_{ch_i}_{v_i}" if bnum is not None else ""
            en_body = english_bcv_map.get(bcv_key, "").strip() if bcv_key else ""
            if not book_row:
                print(f"    [warn] popular skip {vid}/{slug} — unknown book slug")
                continue
            book_disp = display_book_name(book_row, vid)
            vrow = next((v for v in active_versions if v[0] == vid), active_versions[0])
            _vid, vlabel_p, lang_p, *_rest = vrow
            html_pop = generate_popular_verse_landing_page(
                version_id=vid,
                vlabel=vlabel_p,
                lang_code=lang_p,
                page_slug=slug,
                book_display=book_disp,
                bslug=bslug,
                ch_num=ch_i,
                vnum=v_i,
                primary_text=primary_txt,
                english_text=en_body,
                english_label=f"{en_lbl_full} (reference)",
            )
            out_pop = config.OUT_DIR / vid / slug
            out_pop.mkdir(parents=True, exist_ok=True)
            write_if_changed(out_pop / "index.html", html_pop, args.dry_run)
            pu = f"{SITE_URL}/bible/{vid}/{slug}/"
            popular_sitemap_urls.append(pu)
            if sitemap_log_path:
                append_url_to_sitemap_log(sitemap_log_path, pu, args.dry_run)
            popular_pages += 1
            total_pages += 1
        print(f"    ✓ {popular_pages} popular verse landing page(s)")

    if should_run("sitemap", effective_modules):
        if sitemap_log_path and sitemap_log_path.exists():
            from_log = set(sitemap.urls_from_log_file(sitemap_log_path))
            sitemap_urls = sorted(
                from_log
                | set(index_sitemap_urls)
                | set(popular_sitemap_urls)
            )
            print(
                f"\n[sitemap] Merged {len(from_log)} URL(s) from log {sitemap_log_path} "
                f"+ index/popular extras → {len(sitemap_urls)} unique (in-memory chapters this run: "
                f"{len(all_sitemap_urls)})."
            )
        else:
            sitemap_urls = sorted(
                set(all_sitemap_urls) | set(index_sitemap_urls) | set(popular_sitemap_urls)
            )
            if sitemap_log_path and not sitemap_log_path.exists():
                print(
                    f"\n[sitemap] Log {sitemap_log_path} not found yet — using "
                    f"{len(sitemap_urls)} URL(s) from this run."
                )
            else:
                print(f"\n[sitemap] Writing sitemap file(s) ({len(sitemap_urls)} unique URLs)...")
        sitemap_files = sitemap.generate_sitemap_files(sitemap_urls)
        for rel, body in sitemap_files:
            write_if_changed(config.OUT_DIR / rel, body, args.dry_run)
        sitemap_summary_count = len(sitemap.normalize_sitemap_urls(sitemap_urls))

        # robots.txt in repo root
        write_if_changed(Path("robots.txt"), sitemap.ROBOTS_TXT, args.dry_run)

    print("\n" + "=" * 60)
    if args.dry_run:
        print(f"  [DRY RUN] Would write/update {total_pages} content pages.")
    else:
        print(f"  ✅ Done! {total_pages} pages generated (chapters + verses + parallel + popular).")
    print(f"  📁 Output: ./{config.OUT_DIR}/")
    if should_run("sitemap", effective_modules) and sitemap_summary_count is not None:
        print(
            f"  🗺  Sitemap: ./{config.OUT_DIR}/sitemap.xml (+ parts if split) "
            f"({sitemap_summary_count} URLs)"
        )
        print(f"  🤖 robots.txt: ./robots.txt")
    print()
    print("  Next steps: run targeted modules and verify output.")
    print("=" * 60)
