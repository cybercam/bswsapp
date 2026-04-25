"""Skip-if-unchanged writes and module flags."""
import hashlib
from pathlib import Path

from .config import ALL_MODULES

def parse_modules(raw_modules: str) -> set[str]:
    raw = (raw_modules or "all").strip().lower()
    if raw == "all":
        return set(ALL_MODULES)
    selected = {m.strip() for m in raw.split(",") if m.strip()}
    unknown = selected - ALL_MODULES
    if unknown:
        raise SystemExit(
            f"Unknown module(s): {sorted(unknown)}. Valid modules: {sorted(ALL_MODULES)}"
        )
    return selected


def should_run(module: str, selected_modules: set[str]) -> bool:
    return module in selected_modules


def append_url_to_sitemap_log(log_path: Path, url: str, dry_run: bool) -> None:
    """Append one absolute URL line for later sitemap generation (book-wise + prune workflow)."""
    if dry_run or not url.strip():
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(url.strip() + "\n")
        f.flush()


def write_if_changed(path: Path, content: str, dry_run: bool) -> bool:
    new_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    hash_path = path.with_suffix(path.suffix + ".hash")
    try:
        old_hash = hash_path.read_text(encoding="utf-8").strip() if hash_path.exists() else ""
    except OSError as exc:
        print(f"    [warn] could not read {hash_path}: {exc}; rewriting {path}")
        old_hash = ""
    if old_hash == new_hash and path.exists():
        print(f"    [skip] {path}")
        return False
    if dry_run:
        print(f"    [dry-run] write {path}")
        return True
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    hash_path.write_text(new_hash, encoding="utf-8")
    return True
