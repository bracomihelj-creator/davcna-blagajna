# -*- coding: utf-8 -*-
"""Zagon Davčna Blagajna 5.0.2 — pywebview + Edge WebView2, isti AppV21."""
from __future__ import annotations

import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _sanitize_tk_env() -> None:
    frozen = bool(getattr(sys, "frozen", False))
    for key in ("TCL_LIBRARY", "TK_LIBRARY", "TCLLIBPATH"):
        raw = (os.environ.get(key) or "").strip().strip('"')
        if not raw:
            continue
        looks_mei = "_MEI" in raw.replace("\\", "/").upper()
        missing = not Path(raw).exists()
        if (looks_mei and not frozen) or missing:
            os.environ.pop(key, None)


if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

_sanitize_tk_env()
os.chdir(str(HERE))

from host_webview import desktop

if __name__ == "__main__":
    desktop()
