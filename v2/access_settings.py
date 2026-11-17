"""Nastavitve dostopa eDavki / Minimax — ročno, avtomatika, odložišče."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

V2_ACCESS_FILE = Path(__file__).resolve().parent.parent / "blagajna_v2_access.json"

ACCESS_SERVICES: Tuple[str, ...] = (
    "edavki_blagajna",
    "edavki_kirkpr",
    "minimax_kirkpr",
)

ACCESS_FLAGS: Tuple[str, ...] = (
    "direct_link",
    "clipboard_path",
    "selenium_auto",
    "manual_fallback",
)

ACCESS_OPTION_KEYS: Tuple[str, ...] = (
    "show_manual_info",
    "show_transfer_dialogs",
    "show_action_result_dialogs",
    "confirm_manual_fallback",
)

ACCESS_SERVICE_LABELS_SL: Dict[str, str] = {
    "edavki_blagajna": "eDavki — davčna blagajna (DPR-PakR)",
    "edavki_kirkpr": "eDavki — prenos KIR/KPR (DDV evidenca oddanih → Blagajna)",
    "minimax_kirkpr": "Minimax — prenos KIR/KPR (ObracunDDV → DDV)",
}

ACCESS_FLAG_LABELS_SL: Dict[str, str] = {
    "direct_link": "Direct link — odpri povezavo v novem zavihku Chrome",
    "clipboard_path": "Kopiraj ciljno pot datoteke v odložišče",
    "selenium_auto": "Avtomatika (Minimax KIR/KPR / FURS Pripravi+ZIP). eDavki KIR/KPR vedno CDP Od/do — brez Selenium.",
    "manual_fallback": "Ob napaki avtomatike ponudi ročni način",
}

ACCESS_OPTION_LABELS_SL: Dict[str, str] = {
    "show_manual_info": "Prikaži okno z navodili ob ročnem prenosu",
    "show_transfer_dialogs": "Prikaži obvestilo ob uspehu ali napaki prenosa",
    "show_action_result_dialogs": "Prikaži obvestilo ob koncu akcije (npr. uvoz KIR/KPR)",
    "confirm_manual_fallback": "Vprašaj pred preklopom na ročni način",
}

DEFAULT_ACCESS: Dict[str, Dict[str, bool]] = {
    "edavki_blagajna": {
        "direct_link": False,
        "clipboard_path": True,
        "selenium_auto": False,
        "manual_fallback": True,
    },
    "edavki_kirkpr": {
        "direct_link": True,
        "clipboard_path": True,
        "selenium_auto": False,
        "manual_fallback": True,
    },
    "minimax_kirkpr": {
        "direct_link": True,
        "clipboard_path": True,
        "selenium_auto": False,
        "manual_fallback": True,
    },
}

DEFAULT_ACCESS_OPTIONS: Dict[str, bool] = {
    "show_manual_info": False,
    "show_transfer_dialogs": True,
    "show_action_result_dialogs": True,
    "confirm_manual_fallback": True,
}

DEFAULT_MINIMAX_KIRKPR_PAGE_URL = (
    "https://moj.minimax.si/SI/VA/WebUI/ObracunDDV/ObracunDDV.aspx"
)

DEFAULT_ACCESS_URLS: Dict[str, Any] = {
    "minimax_kirkpr_page": DEFAULT_MINIMAX_KIRKPR_PAGE_URL,
    "append_organisation_id": True,
}

ACCESS_URL_LABELS_SL: Dict[str, str] = {
    "minimax_kirkpr_page": "Minimax KIR/KPR — povezava (ObracunDDV)",
    "append_organisation_id": "Na povezavo dodaj ?OrganisationId= (izbrane firme)",
}


def normalize_access_urls(raw: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = copy.deepcopy(DEFAULT_ACCESS_URLS)
    if not isinstance(raw, dict):
        return out
    page = str(raw.get("minimax_kirkpr_page") or "").strip()
    if page:
        out["minimax_kirkpr_page"] = page
    if "append_organisation_id" in raw:
        out["append_organisation_id"] = bool(raw["append_organisation_id"])
    return out


def load_v2_access_urls_from_disk() -> Dict[str, Any]:
    raw = _read_access_file()
    return normalize_access_urls(raw.get("urls"))


def resolve_kirkpr_minimax_page_url(organisation_id: Optional[int] = None) -> str:
    """Povezava za gumb Prenos KIR/KPR (iz Nastavitve → Dostop)."""
    urls = load_v2_access_urls_from_disk()
    base = str(urls.get("minimax_kirkpr_page") or DEFAULT_MINIMAX_KIRKPR_PAGE_URL).strip()
    if not base:
        base = DEFAULT_MINIMAX_KIRKPR_PAGE_URL
    if not urls.get("append_organisation_id", True):
        return base
    if organisation_id is None or int(organisation_id) <= 0:
        return base
    if "organisationid=" in base.lower():
        return base
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}OrganisationId={int(organisation_id)}"


def normalize_access_options(raw: Any) -> Dict[str, bool]:
    out = copy.deepcopy(DEFAULT_ACCESS_OPTIONS)
    if not isinstance(raw, dict):
        return out
    for key in ACCESS_OPTION_KEYS:
        if key in raw:
            out[key] = bool(raw[key])
    return out


def normalize_access_dict(raw: Any) -> Dict[str, Dict[str, bool]]:
    out = copy.deepcopy(DEFAULT_ACCESS)
    if not isinstance(raw, dict):
        return out
    for service in ACCESS_SERVICES:
        src = raw.get(service)
        if not isinstance(src, dict):
            continue
        for flag in ACCESS_FLAGS:
            if flag in src:
                out[service][flag] = bool(src[flag])
        # Združljivost: stari ključ open_url → direct_link
        if "direct_link" not in src and "open_url" in src:
            out[service]["direct_link"] = bool(src["open_url"])
    return out


def access_direct_link_enabled(access: Dict[str, bool]) -> bool:
    """Ali naj gumb odpre direct link v novem zavihku Chrome."""
    if "direct_link" in access:
        return bool(access.get("direct_link"))
    return bool(access.get("open_url", True))


def access_selenium_enabled(access: Dict[str, bool]) -> bool:
    return bool(access.get("selenium_auto", False))


def _read_access_file() -> Dict[str, Any]:
    if not V2_ACCESS_FILE.is_file():
        return {}
    try:
        raw = json.loads(V2_ACCESS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return raw if isinstance(raw, dict) else {}


def load_v2_access_from_disk() -> Dict[str, Dict[str, bool]]:
    raw = _read_access_file()
    if "services" in raw:
        return normalize_access_dict(raw.get("services"))
    return normalize_access_dict(raw)


def load_v2_access_options_from_disk() -> Dict[str, bool]:
    raw = _read_access_file()
    return normalize_access_options(raw.get("options"))


def save_v2_access_to_disk(
    services: Dict[str, Dict[str, bool]],
    *,
    options: Optional[Dict[str, bool]] = None,
    urls: Optional[Dict[str, Any]] = None,
) -> None:
    opts = normalize_access_options(options)
    if options is None and V2_ACCESS_FILE.is_file():
        opts = load_v2_access_options_from_disk()
    url_cfg = normalize_access_urls(urls)
    if urls is None and V2_ACCESS_FILE.is_file():
        url_cfg = load_v2_access_urls_from_disk()
    payload = {
        "version": 1,
        "options": opts,
        "urls": url_cfg,
        "services": normalize_access_dict(services),
    }
    V2_ACCESS_FILE.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def get_service_access(service: str) -> Dict[str, bool]:
    all_access = load_v2_access_from_disk()
    return dict(all_access.get(service, DEFAULT_ACCESS.get(service, {})))


def get_access_options() -> Dict[str, bool]:
    return load_v2_access_options_from_disk()
