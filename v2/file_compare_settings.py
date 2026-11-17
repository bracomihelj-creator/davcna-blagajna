"""Nastavitve definicij primerjav datotek (v2)."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

V2_FILE_COMPARE_FILE = Path(__file__).resolve().parent.parent / "blagajna_v2_file_compare.json"

FILE_COMPARE_BOOKS: Tuple[str, ...] = ("BLAGAJNA", "KIR", "KPR")
FILE_COMPARE_SOURCES: Tuple[str, ...] = ("blagajna", "ddv", "custom")
FILE_COMPARE_KINDS: Tuple[str, ...] = (
    "month_zip",
    "edavki_kirkpr_zip",
    "analysis_xlsx",
    "minimax_kirkpr_xml",
    "custom_path",
)
FILE_COMPARE_FORMATS: Tuple[str, ...] = ("auto", "zip", "xml", "csv", "excel")
FILE_COMPARE_EXCEL_MODES: Tuple[str, ...] = ("auto", "analysis", "monthly", "daily")

FILE_COMPARE_BOOK_LABELS_SL: Dict[str, str] = {
    "BLAGAJNA": "Blagajna",
    "KIR": "KIR",
    "KPR": "KPR",
}
FILE_COMPARE_SOURCE_LABELS_SL: Dict[str, str] = {
    "blagajna": "Blagajna",
    "ddv": "DDV",
    "custom": "Ročna pot",
}
FILE_COMPARE_KIND_LABELS_SL: Dict[str, str] = {
    "month_zip": "YYYY-MM.zip",
    "edavki_kirkpr_zip": "Evidenca eDavki KIRKPR_YYYYMM.zip",
    "analysis_xlsx": "Analiza_YYYY_*.xlsx (Shranjevanje)",
    "minimax_kirkpr_xml": "Evidenca minimax KIRKPR_YYYYMM.xml",
    "custom_path": "Poljubna pot",
}
FILE_COMPARE_FORMAT_LABELS_SL: Dict[str, str] = {
    "auto": "Auto",
    "zip": "ZIP",
    "xml": "XML",
    "csv": "CSV",
    "excel": "Excel",
}
FILE_COMPARE_EXCEL_MODE_LABELS_SL: Dict[str, str] = {
    "auto": "Auto (zaznaj)",
    "analysis": "Analiza (Mesečno + Dnevno)",
    "monthly": "Mesečno",
    "daily": "Dnevno",
}

DEFAULT_FILE_COMPARE_DEFINITIONS: List[Dict[str, Any]] = [
    {
        "name": "Blagajna KIR ↔ Blagajna ZIP",
        "enabled": True,
        "selected": True,
        "book": "KIR",
        "label_a": "Blagajna KIR",
        "label_b": "Blagajna ZIP",
        "left": {
            "source": "blagajna",
            "kind": "edavki_kirkpr_zip",
            "format": "zip",
            "path": "",
            "sheet": "",
            "excel_mode": "auto",
        },
        "right": {
            "source": "blagajna",
            "kind": "month_zip",
            "format": "zip",
            "path": "",
            "sheet": "",
            "excel_mode": "auto",
        },
    },
    {
        "name": "Blagajna Excel ↔ eDavki ZIP",
        "enabled": True,
        "selected": False,
        "book": "KIR",
        "label_a": "Blagajna Excel",
        "label_b": "eDavki ZIP",
        "left": {
            "source": "blagajna",
            "kind": "analysis_xlsx",
            "format": "excel",
            "path": "",
            "sheet": "",
            "excel_mode": "analysis",
        },
        "right": {
            "source": "blagajna",
            "kind": "edavki_kirkpr_zip",
            "format": "zip",
            "path": "",
            "sheet": "",
            "excel_mode": "auto",
        },
    },
    {
        "name": "KIR Blagajna ↔ DDV",
        "enabled": True,
        "selected": False,
        "book": "KIR",
        "label_a": "Blagajna KIR",
        "label_b": "DDV KIR",
        "left": {
            "source": "blagajna",
            "kind": "edavki_kirkpr_zip",
            "format": "zip",
            "path": "",
            "sheet": "",
            "excel_mode": "auto",
        },
        "right": {
            "source": "ddv",
            "kind": "minimax_kirkpr_xml",
            "format": "xml",
            "path": "",
            "sheet": "",
            "excel_mode": "auto",
        },
    },
    {
        "name": "KPR Blagajna ↔ DDV",
        "enabled": True,
        "selected": False,
        "book": "KPR",
        "label_a": "Blagajna KPR",
        "label_b": "DDV KPR",
        "left": {
            "source": "blagajna",
            "kind": "edavki_kirkpr_zip",
            "format": "zip",
            "path": "",
            "sheet": "",
            "excel_mode": "auto",
        },
        "right": {
            "source": "ddv",
            "kind": "minimax_kirkpr_xml",
            "format": "xml",
            "path": "",
            "sheet": "",
            "excel_mode": "auto",
        },
    },
]


def _normalize_side(raw: Any) -> Dict[str, str]:
    src = raw if isinstance(raw, dict) else {}
    source = str(src.get("source") or "blagajna").strip().lower()
    if source not in FILE_COMPARE_SOURCES:
        source = "blagajna"
    kind = str(src.get("kind") or "month_zip").strip().lower()
    if kind not in FILE_COMPARE_KINDS:
        kind = "custom_path" if source == "custom" else "month_zip"
    fmt = str(src.get("format") or "auto").strip().lower()
    if fmt not in FILE_COMPARE_FORMATS:
        fmt = "auto"
    excel_mode = str(src.get("excel_mode") or "auto").strip().lower()
    if excel_mode not in FILE_COMPARE_EXCEL_MODES:
        excel_mode = "auto"
    path = str(src.get("path") or "").strip()
    sheet = str(src.get("sheet") or "").strip()
    return {
        "source": source,
        "kind": kind,
        "format": fmt,
        "path": path,
        "sheet": sheet,
        "excel_mode": excel_mode,
    }


def _normalize_definition(raw: Any, fallback_name: str) -> Dict[str, Any]:
    src = raw if isinstance(raw, dict) else {}
    book = str(src.get("book") or "KIR").strip().upper()
    if book not in FILE_COMPARE_BOOKS:
        book = "KIR"
    left = _normalize_side(src.get("left"))
    right = _normalize_side(src.get("right"))
    name = str(src.get("name") or fallback_name).strip() or fallback_name
    label_a = str(src.get("label_a") or _default_label(left, book)).strip() or _default_label(left, book)
    label_b = str(src.get("label_b") or _default_label(right, book)).strip() or _default_label(right, book)
    return {
        "name": name,
        "enabled": bool(src.get("enabled", True)),
        "selected": bool(src.get("selected", False)),
        "book": book,
        "label_a": label_a,
        "label_b": label_b,
        "left": left,
        "right": right,
    }


def normalize_file_compare_settings(raw: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {"version": 2, "definitions": []}
    defs_src: Any
    if isinstance(raw, dict):
        defs_src = raw.get("definitions", [])
        if "version" in raw:
            try:
                out["version"] = int(raw["version"])
            except (TypeError, ValueError):
                out["version"] = 2
    else:
        defs_src = []
    if not isinstance(defs_src, list):
        defs_src = []
    defs: List[Dict[str, Any]] = []
    for idx, item in enumerate(defs_src, start=1):
        defs.append(_normalize_definition(item, f"Primerjava {idx}"))
    if not defs:
        defs = [_normalize_definition(copy.deepcopy(item), item["name"]) for item in DEFAULT_FILE_COMPARE_DEFINITIONS]
    out["definitions"] = defs
    return out


def _read_compare_file() -> Dict[str, Any]:
    if not V2_FILE_COMPARE_FILE.is_file():
        return {}
    try:
        raw = json.loads(V2_FILE_COMPARE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def load_file_compare_settings_from_disk() -> Dict[str, Any]:
    return normalize_file_compare_settings(_read_compare_file())


def load_file_compare_definitions_from_disk() -> List[Dict[str, Any]]:
    cfg = load_file_compare_settings_from_disk()
    defs = cfg.get("definitions")
    return defs if isinstance(defs, list) else []


def save_file_compare_settings_to_disk(data: Dict[str, Any]) -> None:
    payload = normalize_file_compare_settings(data)
    V2_FILE_COMPARE_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _default_label(side: Dict[str, str], book: str) -> str:
    source = str(side.get("source") or "blagajna").strip().lower()
    src_label = FILE_COMPARE_SOURCE_LABELS_SL.get(source, source)
    book_u = (book or "KIR").strip().upper()
    if source == "custom":
        return "Datoteka"
    if book_u == "BLAGAJNA":
        return src_label
    return f"{src_label} {book_u}"


def describe_compare_side(side: Dict[str, Any]) -> str:
    side_n = _normalize_side(side)
    source = FILE_COMPARE_SOURCE_LABELS_SL.get(side_n["source"], side_n["source"])
    kind = FILE_COMPARE_KIND_LABELS_SL.get(side_n["kind"], side_n["kind"])
    parts: List[str] = []
    if side_n["kind"] == "custom_path" and side_n["path"]:
        parts.append(f"{source}: {side_n['path']}")
    else:
        parts.append(f"{source}: {kind}")
    if side_n.get("format") == "excel" or side_n["path"].lower().endswith((".xlsx", ".xlsm")):
        mode = FILE_COMPARE_EXCEL_MODE_LABELS_SL.get(side_n["excel_mode"], side_n["excel_mode"])
        parts.append(f"Excel {mode}")
        if side_n["sheet"]:
            parts.append(f"list={side_n['sheet']}")
    return " | ".join(parts)
