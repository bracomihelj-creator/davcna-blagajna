"""eDavki povezave — kot list internet v Evidence podjetij (SQL dbo.RefInternetLink)."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

APP_ROOT = Path(__file__).resolve().parent.parent
LINKS_FILE = APP_ROOT / "blagajna_edavki_links.json"
DEFAULT_SQL_CONFIG = APP_ROOT.parent / "EvidencaFirm" / "config.json"

EDAVKI_PORTAL_PREFIX = "https://edavki.durs.si/EdavkiPortal/[{durs}]/"

# Privzete vrstice (list internet iz Evidence podjetij)
DEFAULT_EDAVKI_LINKS: Tuple[Dict[str, Any], ...] = (
    {
        "sort_order": 1,
        "label": "Preveri DDV-O obdobje",
        "path": "/PersonalPortal/CommonPages/Documents/New_DDV_0.aspx?formType=DDV_0",
        "col_c": "",
        "col_d": "",
        "enabled": True,
        "action": "url",
    },
    {
        "sort_order": 2,
        "label": "Preveri MRN",
        "path": "/PersonalPortal/CommonPages/Documents/DDV_Deklaracija.aspx?RepresentedTaxPayerProfileId=",
        "col_c": "&ifDura",
        "col_d": "DDV-Deklaracija — Seznam carinskih deklaracij",
        "enabled": True,
        "action": "url",
    },
    {
        "sort_order": 3,
        "label": "Preveri KIR/KPR evidenco DDV",
        "path": "/PersonalPortal/CommonPages/Documents/DDV_Evidenci_Poslane.aspx",
        "col_c": "",
        "col_d": "",
        "enabled": True,
        "action": "url",
    },
    {
        "sort_order": 4,
        "label": "Preveri vložen DDV",
        "path": "/PersonalPortal/Pages/Documents/ListPosted.aspx?RepresentedTaxPayerProfileId=",
        "col_c": "&Asynch=0",
        "col_d": "",
        "enabled": True,
        "action": "url",
    },
    {
        "sort_order": 5,
        "label": "Evidenci obračunanega DDV in odbitka DDV",
        "path": "/PersonalPortal/CommonPages/Documents/DDV_Evidenci_Oddane.aspx",
        "col_c": "",
        "col_d": "",
        "enabled": True,
        "action": "url",
    },
    {
        "sort_order": 6,
        "label": "Preveri oddajo DDV-O (semafor)",
        "path": "/PersonalPortal/CommonPages/Documents/Overview.aspx",
        "col_c": "",
        "col_d": "",
        "enabled": True,
        "action": "url",
    },
    {
        "sort_order": 7,
        "label": "Preveri oddane dokumente na FURS-u",
        "path": "/PersonalPortal/Pages/Documents/ListPosted.aspx?Asynch=0",
        "col_c": "",
        "col_d": "",
        "enabled": True,
        "action": "url",
    },
    {
        "sort_order": 8,
        "label": "Preveri saldo oz. stanje kartice davčnega zavezanca",
        "path": "/PersonalPortal/CommonPages/Documents/eKartica.aspx?RepresentedTaxPayerProfileId=",
        "col_c": "&ifDura&form=eKartica",
        "col_d": "Knjigovodska kartica davčnega zavezanca",
        "enabled": True,
        "action": "url",
    },
    {
        "sort_order": 9,
        "label": "Uvoz dokumenta",
        "path": "/PersonalPortal/CommonPages/Documents/import.aspx",
        "col_c": "",
        "col_d": "",
        "enabled": True,
        "action": "url",
    },
    {
        "sort_order": 10,
        "label": "Odpri eDavki OSS sistem",
        "path": "/PersonalPortal/CommonPages/Documents/New_OSS.aspx",
        "col_c": "",
        "col_d": "",
        "enabled": True,
        "action": "url",
    },
    {
        "sort_order": 11,
        "label": "Oddaj v OSS sistem",
        "path": "",
        "col_c": "",
        "col_d": "",
        "enabled": False,
        "action": "none",
    },
    {
        "sort_order": 12,
        "label": "Pridobitev podatkov o davčno potrjenih računih",
        "path": "/PersonalPortal/CommonPages/Documents/DPR_PakR.aspx",
        "col_c": "",
        "col_d": "Davčno potrjeni računi",
        "enabled": True,
        "action": "url",
    },
    {
        "sort_order": 13,
        "label": "Izvoz dokumenti",
        "path": "https://moj.minimax.si/SI/VA/WebUI/Dokument/DokumentView.aspx?docs_id=7949265U&pgat=pgatv",
        "col_c": "",
        "col_d": "Minimax — prilagodi docs_id po firmi",
        "enabled": True,
        "action": "external",
    },
    {
        "sort_order": 14,
        "label": "Pridobi eMail nabiralnika minimaxa",
        "path": "",
        "col_c": "",
        "col_d": "strNabiralnik",
        "enabled": True,
        "action": "email_field",
    },
    {
        "sort_order": 15,
        "label": "Pridobi eMail stranke",
        "path": "",
        "col_c": "",
        "col_d": "strEmail",
        "enabled": True,
        "action": "email_field",
    },
)


def _normalize_link_row(raw: Any, fallback_order: int) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raw = {}
    action = str(raw.get("action") or "").strip().lower()
    col_d = str(raw.get("col_d") or "").strip()
    path = str(raw.get("path") or raw.get("path_or_url") or "").strip()
    if not action:
        if col_d in ("strNabiralnik", "strEmail"):
            action = "email_field"
        elif not path:
            action = "none"
        elif path.lower().startswith("http"):
            action = "external"
        else:
            action = "url"
    try:
        sort_order = int(raw.get("sort_order") or fallback_order)
    except (TypeError, ValueError):
        sort_order = fallback_order
    return {
        "sort_order": sort_order,
        "label": str(raw.get("label") or raw.get("naziv") or "").strip(),
        "path": path,
        "col_c": str(raw.get("col_c") or "").strip(),
        "col_d": col_d,
        "enabled": bool(raw.get("enabled", True)),
        "action": action,
    }


def normalize_edavki_links_config(raw: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "version": 1,
        "sql_connection_string": "",
        "sql_config_path": "../EvidencaFirm/config.json",
        "refresh_from_sql_on_startup": False,
        "links": [],
    }
    if not isinstance(raw, dict):
        raw = {}
    if raw.get("version"):
        out["version"] = int(raw["version"])
    out["sql_connection_string"] = str(raw.get("sql_connection_string") or "").strip()
    out["sql_config_path"] = str(raw.get("sql_config_path") or out["sql_config_path"]).strip()
    out["refresh_from_sql_on_startup"] = bool(raw.get("refresh_from_sql_on_startup", False))
    src_links = raw.get("links")
    if not isinstance(src_links, list):
        src_links = []
    if not src_links:
        out["links"] = [copy.deepcopy(x) for x in DEFAULT_EDAVKI_LINKS]
        return out
    links: List[Dict[str, Any]] = []
    for idx, item in enumerate(src_links, 1):
        row = _normalize_link_row(item, idx)
        if row["label"]:
            links.append(row)
    links.sort(key=lambda x: int(x.get("sort_order") or 0))
    for i, row in enumerate(links, 1):
        row["sort_order"] = i
    out["links"] = links
    return out


def load_edavki_links_from_disk() -> Dict[str, Any]:
    if not LINKS_FILE.is_file():
        return normalize_edavki_links_config({})
    try:
        raw = json.loads(LINKS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return normalize_edavki_links_config({})
    return normalize_edavki_links_config(raw)


def save_edavki_links_to_disk(config: Dict[str, Any]) -> None:
    payload = normalize_edavki_links_config(config)
    LINKS_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def resolve_sql_connection_string(config: Optional[Dict[str, Any]] = None) -> str:
    cfg = normalize_edavki_links_config(config or load_edavki_links_from_disk())
    direct = str(cfg.get("sql_connection_string") or "").strip()
    if direct:
        return direct
    rel = str(cfg.get("sql_config_path") or "").strip()
    if not rel:
        return ""
    cfg_path = Path(rel)
    if not cfg_path.is_absolute():
        cfg_path = (APP_ROOT / rel).resolve()
    if not cfg_path.is_file():
        return ""
    try:
        data = json.loads(cfg_path.read_text(encoding="utf-8"))
        sql = data.get("sql_express") if isinstance(data, dict) else {}
        if isinstance(sql, dict) and sql.get("enabled"):
            return str(sql.get("connection_string") or "").strip()
    except (OSError, json.JSONDecodeError):
        return ""
    return ""


def load_links_from_sql(connection_string: str = "") -> List[Dict[str, Any]]:
    """Naloži dbo.RefInternetLink (Evidence podjetij / EvidencaFirm)."""
    cs = (connection_string or "").strip() or resolve_sql_connection_string()
    if not cs:
        raise RuntimeError(
            "Manjka SQL povezava. Nastavi sql_connection_string v blagajna_edavki_links.json "
            "ali sql_config_path do EvidencaFirm/config.json."
        )
    try:
        import pyodbc  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError("Za SQL uvoz namesti pyodbc (pip install pyodbc).") from exc

    conn = pyodbc.connect(cs, timeout=15)
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT SortOrder, Naziv, PathOrUrl, ColC, ColD
            FROM dbo.RefInternetLink
            ORDER BY SortOrder
            """
        )
        out: List[Dict[str, Any]] = []
        for row in cur.fetchall():
            out.append(
                _normalize_link_row(
                    {
                        "sort_order": row[0],
                        "label": row[1] or "",
                        "path": row[2] or "",
                        "col_c": row[3] or "",
                        "col_d": row[4] or "",
                    },
                    len(out) + 1,
                )
            )
        return out
    finally:
        conn.close()


def refresh_edavki_links_from_sql(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Naloži povezave iz SQL in vrne posodobljen config (še ne shrani)."""
    cfg = normalize_edavki_links_config(config or load_edavki_links_from_disk())
    cs = resolve_sql_connection_string(cfg)
    rows = load_links_from_sql(cs)
    cfg["links"] = rows
    return cfg


def maybe_refresh_edavki_links_on_startup() -> Tuple[bool, str]:
    """
    Če je vklopljeno refresh_from_sql_on_startup, naloži RefInternetLink in shrani.
    Vrne (uspeh, sporočilo za log).
    """
    cfg = load_edavki_links_from_disk()
    if not cfg.get("refresh_from_sql_on_startup"):
        return False, ""
    try:
        updated = refresh_edavki_links_from_sql(cfg)
        save_edavki_links_to_disk(updated)
        n = len(updated.get("links") or [])
        return True, f"SQL ob zagonu: {n} povezav (RefInternetLink)"
    except Exception as exc:
        return False, f"SQL ob zagonu ni uspel: {exc}"


def combo_labels(config: Optional[Dict[str, Any]] = None) -> List[str]:
    cfg = normalize_edavki_links_config(config or load_edavki_links_from_disk())
    labels: List[str] = []
    for row in cfg.get("links") or []:
        if not isinstance(row, dict):
            continue
        if not row.get("enabled", True):
            continue
        label = str(row.get("label") or "").strip()
        if not label:
            continue
        action = str(row.get("action") or "url")
        if action == "none" and not str(row.get("path") or "").strip():
            continue
        labels.append(label)
    return labels


def find_link_by_label(config: Dict[str, Any], label: str) -> Optional[Dict[str, Any]]:
    needle = (label or "").strip()
    for row in config.get("links") or []:
        if str(row.get("label") or "").strip() == needle:
            return row
    return None


def _append_col_c(url: str, col_c: str) -> str:
    extra = (col_c or "").strip()
    if not extra:
        return url
    if not extra.startswith("&") and not extra.startswith("?"):
        extra = "&" + extra
    return url + extra


def resolve_edavki_link_url(
    link: Dict[str, Any],
    *,
    durs: str,
) -> Optional[str]:
    """Sestavi polni URL za eDavki / zunanjo povezavo."""
    path = str(link.get("path") or "").strip()
    if not path:
        return None
    d = re.sub(r"\D", "", str(durs or ""))
    if not d and not path.lower().startswith("http"):
        return None
    action = str(link.get("action") or "url").lower()
    col_c = str(link.get("col_c") or "").strip()

    if action == "external" or path.lower().startswith("http"):
        return _append_col_c(path, col_c)

    prefix = EDAVKI_PORTAL_PREFIX.format(durs=d)
    url = prefix.rstrip("/") + (path if path.startswith("/") else "/" + path)

    if "RepresentedTaxPayerProfileId=" in url:
        url = re.sub(
            r"(RepresentedTaxPayerProfileId=)(?=&|$)",
            rf"\1{d}",
            url,
        )
    elif "?" not in url:
        url = f"{url}?RepresentedTaxPayerProfileId={d}"
    elif "RepresentedTaxPayerProfileId" not in url:
        url = f"{url}&RepresentedTaxPayerProfileId={d}"

    return _append_col_c(url, col_c)


def resolve_email_clipboard_text(
    link: Dict[str, Any],
    company: Optional[Dict[str, str]],
) -> str:
    """strEmail / strNabiralnik — kopiraj e-pošto iz izbrane firme."""
    field = str(link.get("col_d") or "").strip()
    email = ""
    if company:
        email = str(company.get("Email") or "").strip()
    if field == "strNabiralnik" and email:
        # Prvi naslov (nabiralnik) — v Excelu je pogosto več naslovov
        return email.split(",")[0].strip()
    return email
