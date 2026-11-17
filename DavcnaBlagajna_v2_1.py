"""Zagon Davčna Blagajna 3.0 — SQL EvidencaFirm, zavihki akcij po področjih."""

from __future__ import annotations

import os
import sys
from pathlib import Path


def _sanitize_tk_env() -> None:
    """Po zagonu PyInstaller EXE lahko TCL_LIBRARY/TK_LIBRARY kažeta na pobrisano mapo _MEI…"""
    frozen = bool(getattr(sys, "frozen", False))
    for key in ("TCL_LIBRARY", "TK_LIBRARY", "TCLLIBPATH"):
        raw = (os.environ.get(key) or "").strip().strip('"')
        if not raw:
            continue
        looks_mei = "_MEI" in raw.replace("\\", "/").upper()
        missing = not Path(raw).exists()
        if (looks_mei and not frozen) or missing:
            os.environ.pop(key, None)


def main() -> int:
    _sanitize_tk_env()
    import DavcnaBlagajna as core
    from v2.app_v21 import AppV21
    from v2.version_journal import get_current_patch_version

    core.log_info(f"PROGRAM START ({get_current_patch_version()})")
    app = AppV21()
    app.mainloop()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        try:
            _sanitize_tk_env()
            import DavcnaBlagajna as core

            core.log_error("startup v2.1", exc)
            import tkinter as _tk
            from tkinter import messagebox as _messagebox

            _root = _tk.Tk()
            _root.withdraw()
            _messagebox.showerror(
                "Napaka ob zagonu (v2.1)",
                f"{exc}\n\nPreveri log:\n{core.LOG_FILE}",
            )
            _root.destroy()
        except Exception:
            pass
        raise
