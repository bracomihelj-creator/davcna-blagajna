"""Lokalna JSON konfiguracija za Minimax spletni uvoz (WebView2 / opcijsko CDP)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from v2.version_journal import APP_ROOT

CONFIG_PATH = APP_ROOT / "minimax_uvoz_config.json"

_DEFAULTS: Dict[str, Any] = {
    # webview2 / auto = samostojno WebView2 okno (app profil) — privzeto
    # chrome_cdp = attach ChromeMinimax :9223 / Edge debug (opcijsko)
    "engine": "webview2",
    "click_import": True,
    "open_temeljnica": True,
    "vrsta_temeljnice_id": "2",
    "vrsta_temeljnice_label": "IR - Izdani račun",
    "tip_prometa": "KN",
    "remote_debugging_port": 9333,
    "organisation_id": None,
    "notes": (
        "ZAKLENJENO 3.0.42: webview2 = samostojno okno "
        "(data/webview2/minimax_uvoz_profile), klik naziva firme, "
        "KN→radio→IR/datum→Excel CDP :9333→Uvozi. "
        "Ni Chrome vtičnika / :9223. chrome_cdp samo če engine=chrome_cdp."
    ),
}


def load_minimax_uvoz_config() -> Dict[str, Any]:
    data = dict(_DEFAULTS)
    try:
        if CONFIG_PATH.is_file():
            raw = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                data.update({k: v for k, v in raw.items() if k in _DEFAULTS or k.startswith("_")})
    except Exception:
        pass
    return data


def save_minimax_uvoz_config(updates: Dict[str, Any]) -> Dict[str, Any]:
    data = load_minimax_uvoz_config()
    data.update(updates or {})
    CONFIG_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return data
