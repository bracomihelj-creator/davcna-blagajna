"""Postavitev obrazca Minimax knjižbe (KIR/KPR) — shranjeno v JSON, urejanje v Nastavitve."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

KNJIZBA_FORM_FILE = Path(__file__).resolve().parent.parent / "blagajna_kirkpr_knjizba_form.json"

# key -> (privzeta oznaka, tip polja)
KNJIZBA_FORM_FIELD_CATALOG_KIR: Dict[str, Tuple[str, str]] = {
    "document_type": ("Tip dokumenta", "document_type"),
    "status": ("Status", "status_kir"),
    "datum": ("Datum", "date_picker"),
    "datum_zapadlosti": ("Datum zapadlosti", "date_picker"),
    "datum_transakcije": ("Datum transakcije", "date_picker"),
    "opis": ("Opis knjižbe", "text"),
    "sklic": ("Sklic plačila", "text"),
    "stranka_id": ("Stranka", "customer"),
    "konto": ("Konto prihodkov", "konto"),
    "vrednost": ("Znesek plačila", "amount"),
    "osnova22": ("Osnova 22 %", "amount"),
    "davek22": ("Davek 22 %", "amount"),
    "osnova95": ("Osnova 9,5 %", "amount"),
    "davek95": ("Davek 9,5 %", "amount"),
    "neobdavcljive": ("Neobdavčljive dobave", "amount"),
    "oproscene": ("Oproščene dobave", "amount"),
}

_KPR_AMOUNT_KEYS: Tuple[Tuple[str, str], ...] = (
    ("p8", "P8 Blago in storitve"),
    ("p9", "P9 Samoobdavčitev"),
    ("p10", "P10 Pridobitev blaga"),
    ("p11", "P11 Prejete storitve"),
    ("p12", "P12 Nepremičnine"),
    ("p13", "P13 Druga OS"),
    ("p14", "P14 Oproščene nabave"),
    ("p15", "P15 Oproščene nepremičnine"),
    ("p16", "P16 Oproščena druga OS"),
    ("p17", "P17 DDV se ne odbija"),
    ("p18", "P18 DDV 22%"),
    ("p19", "P19 DDV 9,5%"),
    ("p20", "P20 DDV 5%"),
    ("p21", "P21 Pavšalno nadomestilo"),
)

KNJIZBA_FORM_FIELD_CATALOG_KPR: Dict[str, Tuple[str, str]] = {
    "status": ("Status", "status_kpr"),
    "datum": ("Datum prejema (P2)", "date_picker"),
    "datum_racuna": ("Datum računa (P4)", "date_picker"),
    "datum_zapadlosti": ("Datum zapadlosti", "date_picker"),
    "st_listine": ("Št. listine (P3)", "text"),
    "vezni_dokument": ("Vezni dokument", "text"),
    "opis": ("Opis (prejeti račun;P3)", "text"),
    "sklic": ("Sklic plačila", "text"),
    "dobavitelj_id": ("Dobavitelj", "customer"),
    "konto": ("Konto stroškov", "konto"),
    "vrednost": ("Vrednost računa", "amount"),
}
for _key, _label in _KPR_AMOUNT_KEYS:
    KNJIZBA_FORM_FIELD_CATALOG_KPR[_key] = (_label, "amount")

# Združeni katalog (nastavitve, migracija)
KNJIZBA_FORM_FIELD_CATALOG: Dict[str, Tuple[str, str]] = {
    **KNJIZBA_FORM_FIELD_CATALOG_KIR,
    **KNJIZBA_FORM_FIELD_CATALOG_KPR,
}

KPR_FIELD_KEY_TO_SUM_COL: Dict[str, str] = {k: label for k, label in _KPR_AMOUNT_KEYS}


def knjizba_form_catalog_for_book(book: str) -> Dict[str, Tuple[str, str]]:
    if (book or "").strip().upper() == "KPR":
        return KNJIZBA_FORM_FIELD_CATALOG_KPR
    return KNJIZBA_FORM_FIELD_CATALOG_KIR


def knjizba_form_fields_key(book: str) -> str:
    return "fields_kpr" if (book or "").strip().upper() == "KPR" else "fields_kir"


def kpr_sum_col_for_field_key(key: str) -> Optional[str]:
    return KPR_FIELD_KEY_TO_SUM_COL.get((key or "").strip())


def kpr_field_key_for_sum_col(col: str) -> Optional[str]:
    col = (col or "").strip()
    for key, label in KPR_FIELD_KEY_TO_SUM_COL.items():
        if label == col:
            return key
    m = re.match(r"^P(\d+)\b", col)
    if m:
        return f"p{m.group(1)}"
    return None


def _default_fields_for_catalog(catalog: Dict[str, Tuple[str, str]]) -> List[Dict[str, Any]]:
    return [
        {"key": key, "visible": True, "label": "", "row": -1, "col": -1, "entry_width": 0}
        for key in catalog
    ]


DEFAULT_KNJIZBA_FORM_FIELDS_KIR: Tuple[Dict[str, Any], ...] = tuple(
    _default_fields_for_catalog(KNJIZBA_FORM_FIELD_CATALOG_KIR)
)
DEFAULT_KNJIZBA_FORM_FIELDS_KPR: Tuple[Dict[str, Any], ...] = tuple(
    _default_fields_for_catalog(KNJIZBA_FORM_FIELD_CATALOG_KPR)
)

DEFAULT_KNJIZBA_FORM_FIELDS: Tuple[Dict[str, Any], ...] = DEFAULT_KNJIZBA_FORM_FIELDS_KIR

DEFAULT_KNJIZBA_FORM_LAYOUT: Dict[str, Any] = {
    "dialog_width": 720,
    "dialog_height": 720,
    "label_width": 22,
    "entry_width": 48,
    "columns": 1,
    "show_api_summary": True,
    "fields_kir": [copy.deepcopy(f) for f in DEFAULT_KNJIZBA_FORM_FIELDS_KIR],
    "fields_kpr": [copy.deepcopy(f) for f in DEFAULT_KNJIZBA_FORM_FIELDS_KPR],
}


def _merge_field_list(
    raw_fields: List[Any],
    catalog: Dict[str, Tuple[str, str]],
) -> List[Dict[str, Any]]:
    by_key: Dict[str, Dict[str, Any]] = {}
    order: List[str] = []
    for item in raw_fields:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or "").strip()
        if key not in catalog:
            continue
        label = str(item.get("label") or "").strip()
        try:
            row = int(item.get("row", -1))
        except (TypeError, ValueError):
            row = -1
        try:
            col = int(item.get("col", -1))
        except (TypeError, ValueError):
            col = -1
        try:
            entry_width = int(item.get("entry_width") or 0)
        except (TypeError, ValueError):
            entry_width = 0
        by_key[key] = {
            "key": key,
            "visible": bool(item.get("visible", True)),
            "label": label,
            "row": row if row >= 0 else -1,
            "col": col if col in (0, 1) else -1,
            "entry_width": max(0, min(80, entry_width)),
        }
        order.append(key)

    merged: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for key in order:
        if key in seen:
            continue
        seen.add(key)
        merged.append(by_key[key])

    for key in catalog:
        if key not in seen:
            merged.append(
                copy.deepcopy(
                    by_key.get(key)
                    or {
                        "key": key,
                        "visible": True,
                        "label": "",
                        "row": -1,
                        "col": -1,
                        "entry_width": 0,
                    }
                )
            )
    return merged


def normalize_knjizba_form_layout(raw: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    out = copy.deepcopy(DEFAULT_KNJIZBA_FORM_LAYOUT)
    if not raw:
        return out

    for key in ("dialog_width", "dialog_height", "label_width", "entry_width", "columns"):
        if key in raw:
            try:
                val = int(raw[key])
            except (TypeError, ValueError):
                continue
            if key == "columns":
                out[key] = 1 if val < 2 else 2
            elif key in ("dialog_width", "dialog_height"):
                out[key] = max(400, min(1400, val))
            else:
                out[key] = max(4, min(80, val))

    if "show_api_summary" in raw:
        out["show_api_summary"] = bool(raw["show_api_summary"])

    # Migracija: stari "fields" -> fields_kir
    if isinstance(raw.get("fields_kir"), list):
        out["fields_kir"] = _merge_field_list(raw["fields_kir"], KNJIZBA_FORM_FIELD_CATALOG_KIR)
    elif isinstance(raw.get("fields"), list):
        out["fields_kir"] = _merge_field_list(raw["fields"], KNJIZBA_FORM_FIELD_CATALOG_KIR)
    else:
        out["fields_kir"] = _merge_field_list(out["fields_kir"], KNJIZBA_FORM_FIELD_CATALOG_KIR)

    if isinstance(raw.get("fields_kpr"), list):
        out["fields_kpr"] = _merge_field_list(raw["fields_kpr"], KNJIZBA_FORM_FIELD_CATALOG_KPR)
    else:
        out["fields_kpr"] = _merge_field_list(out["fields_kpr"], KNJIZBA_FORM_FIELD_CATALOG_KPR)

    return out


def load_knjizba_form_layout_from_disk() -> Dict[str, Any]:
    if not KNJIZBA_FORM_FILE.exists():
        return copy.deepcopy(DEFAULT_KNJIZBA_FORM_LAYOUT)
    try:
        raw = json.loads(KNJIZBA_FORM_FILE.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("root must be object")
        return normalize_knjizba_form_layout(raw)
    except Exception:
        return copy.deepcopy(DEFAULT_KNJIZBA_FORM_LAYOUT)


def save_knjizba_form_layout_to_disk(layout: Dict[str, Any]) -> None:
    data = normalize_knjizba_form_layout(layout)
    KNJIZBA_FORM_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def resolve_knjizba_form_fields(
    layout: Dict[str, Any],
    *,
    book: str,
    show_due: bool = True,
    show_tx: bool = True,
    show_customer: bool = True,
    show_invoice_date: bool = True,
) -> List[Dict[str, Any]]:
    """Vrne polja za prikaz glede na postavitev, knjigo (KIR/KPR) in kontekst dokumenta."""
    catalog = knjizba_form_catalog_for_book(book)
    fields_key = knjizba_form_fields_key(book)
    raw_fields = layout.get(fields_key) or []

    skip: set[str] = set()
    book_u = (book or "KIR").strip().upper()
    if book_u == "KIR":
        if not show_due:
            skip.add("datum_zapadlosti")
        if not show_tx:
            skip.add("datum_transakcije")
        if not show_customer:
            skip.add("stranka_id")
    else:
        if not show_invoice_date:
            skip.add("datum_racuna")

    resolved: List[Dict[str, Any]] = []
    for item in raw_fields:
        if not isinstance(item, dict):
            continue
        key = str(item.get("key") or "").strip()
        if key not in catalog or key in skip:
            continue
        if not bool(item.get("visible", True)):
            continue
        default_label, kind = catalog[key]
        custom = str(item.get("label") or "").strip()
        try:
            entry_width = int(item.get("entry_width") or 0)
        except (TypeError, ValueError):
            entry_width = 0
        resolved.append(
            {
                "key": key,
                "label": custom or default_label,
                "kind": kind,
                "row": int(item.get("row", -1)) if int(item.get("row", -1) or -1) >= 0 else -1,
                "col": int(item.get("col", -1)) if int(item.get("col", -1) or -1) in (0, 1) else -1,
                "entry_width": max(0, min(80, entry_width)),
            }
        )
    return resolved


def knjizba_form_grid_positions(
    fields: List[Dict[str, Any]],
    *,
    columns: int,
) -> List[Tuple[int, int]]:
    """Za vsako polje (grid_row, grid_col_label)."""
    cols = 1 if columns < 2 else 2
    positions: List[Tuple[int, int]] = []
    auto_idx = 0
    used: set[Tuple[int, int]] = set()

    for field in fields:
        row = field.get("row", -1)
        col = field.get("col", -1)
        if isinstance(row, int) and row >= 0 and isinstance(col, int) and col in (0, 1) and cols == 2:
            grid_row = row
            grid_col = col * 2
        elif isinstance(row, int) and row >= 0 and cols == 1:
            grid_row = row
            grid_col = 0
        else:
            grid_row = auto_idx // cols
            grid_col = (auto_idx % cols) * 2
            auto_idx += 1

        while (grid_row, grid_col) in used:
            grid_row += 1
        used.add((grid_row, grid_col))
        positions.append((grid_row, grid_col))

    return positions
