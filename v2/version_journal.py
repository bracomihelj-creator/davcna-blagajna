"""Vodenje popravnih verzij — dnevnik promptov in sprememb (serija 5.1.xx)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

APP_ROOT = Path(__file__).resolve().parent.parent
VERSIONS_DIR = APP_ROOT / "verzije"
VERSIONS_INDEX = VERSIONS_DIR / "davcna_blagajna_verzije.json"

SERIES = "5.1"
INITIAL_PATCH = 1


def _log_filename(patch_id: str) -> str:
    return f"Davčna blagajna ver {patch_id}.txt"


def _ensure_versions_dir() -> None:
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)


def _default_index() -> Dict[str, Any]:
    return {"series": SERIES, "current": f"{SERIES}.00", "versions": []}


def load_versions_index() -> Dict[str, Any]:
    _ensure_versions_dir()
    if not VERSIONS_INDEX.is_file():
        return _default_index()
    try:
        raw = json.loads(VERSIONS_INDEX.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return _default_index()
        raw.setdefault("series", SERIES)
        raw.setdefault("versions", [])
        raw.setdefault("current", f"{SERIES}.00")
        return raw
    except (OSError, json.JSONDecodeError):
        return _default_index()


def save_versions_index(data: Dict[str, Any]) -> None:
    _ensure_versions_dir()
    VERSIONS_INDEX.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def get_current_patch_version() -> str:
    return str(load_versions_index().get("current") or f"{SERIES}.00")


def list_version_entries() -> List[Dict[str, Any]]:
    index = load_versions_index()
    versions = index.get("versions") or []
    if not isinstance(versions, list):
        return []
    return list(reversed(versions))


def version_log_path(entry: Dict[str, Any]) -> Path:
    log_file = str(entry.get("log_file") or _log_filename(str(entry.get("id", ""))))
    return VERSIONS_DIR / log_file


def read_version_log(entry: Dict[str, Any]) -> str:
    path = version_log_path(entry)
    if not path.is_file():
        return f"(Datoteka ni najdena: {path.name})"
    return path.read_text(encoding="utf-8")


def _next_patch_id(index: Dict[str, Any]) -> str:
    versions = index.get("versions") or []
    # Trenutna serija iz kode (npr. skok 2.2 → 3.0), ne iz zadnjega zapisa.
    series = str(SERIES).strip() or "3.0"
    index["series"] = series
    in_series = [
        v
        for v in versions
        if isinstance(v, dict) and str(v.get("id") or "").startswith(f"{series}.")
    ]
    if not in_series:
        return f"{series}.{INITIAL_PATCH:02d}"
    last = str(in_series[-1].get("id") or "")
    try:
        _last_series, num = last.rsplit(".", 1)
        n = int(num) + 1
    except (ValueError, AttributeError):
        n = len(in_series) + INITIAL_PATCH
    return f"{series}.{n:02d}"


def record_version(
    *,
    user_prompt: str,
    changes: str,
    files_changed: Optional[List[str]] = None,
    title: Optional[str] = None,
    version_date: Optional[str] = None,
) -> str:
    """Zapiše novo verzijo (JSON + TXT) in vrne njen ID, npr. 2.1.09."""
    _ensure_versions_dir()
    index = load_versions_index()
    patch_id = _next_patch_id(index)
    when = version_date or date.today().isoformat()
    log_name = _log_filename(patch_id)
    log_path = VERSIONS_DIR / log_name

    title_line = (title or "").strip() or f"Posodobitev {patch_id}"
    files = files_changed or []

    file_lines = [f"  • {f}" for f in files] if files else ["  (ni evidence po datotekah)"]
    body = "\n".join(
        [
            f"Davčna Blagajna — verzija {patch_id}",
            f"Datum: {when}",
            "",
            "=== VAŠ ZAHTEVEK (prompt) ===",
            user_prompt.strip(),
            "",
            "=== SPREMEMBE / IZBOLJŠAVE ===",
            changes.strip(),
            "",
            "=== SPREMENJENE DATOTEKE ===",
            *file_lines,
            "",
            "=== OPOMBA ===",
            "Ta dnevnik služi sledenju napredku. Za povrnitev kode uporabite git ali",
            "ročno primerjajte datoteke iz navedenega obdobja.",
            "",
        ]
    )
    log_path.write_text(body, encoding="utf-8")

    entry: Dict[str, Any] = {
        "id": patch_id,
        "date": when,
        "title": title_line,
        "log_file": log_name,
        "user_prompt": user_prompt.strip(),
        "changes": changes.strip(),
        "files_changed": files,
    }
    versions = index.setdefault("versions", [])
    if not isinstance(versions, list):
        versions = []
        index["versions"] = versions
    versions.append(entry)
    index["current"] = patch_id
    save_versions_index(index)
    return patch_id


def bootstrap_index_if_missing(entries: List[Dict[str, Any]], *, current: str) -> None:
    """Enkratno zapolni indeks, če še ni verzij (ne prepisuje obstoječih)."""
    index = load_versions_index()
    if index.get("versions"):
        return
    _ensure_versions_dir()
    index["series"] = SERIES
    index["current"] = current
    index["versions"] = entries
    save_versions_index(index)
