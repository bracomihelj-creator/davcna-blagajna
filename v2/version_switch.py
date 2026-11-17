"""Preklapljanje / zgodovina verzij (3.0 + arhiv 2.2)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import tkinter as tk

from v2.version_journal import VERSIONS_DIR, get_current_patch_version

APP_ROOT = Path(__file__).resolve().parent.parent
ARCHIVE_229 = APP_ROOT / "Arhiv" / "2.2.29" / "DavcnaBlagajna_v2_1.py"


def _open_versions_folder() -> None:
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)
    os.startfile(str(VERSIONS_DIR))  # type: ignore[attr-defined]


def _open_archive_folder() -> None:
    path = APP_ROOT / "Arhiv" / "2.2.29"
    path.mkdir(parents=True, exist_ok=True)
    os.startfile(str(path))  # type: ignore[attr-defined]


def launch_archive_2_2_29(app: tk.Tk) -> None:
    script = ARCHIVE_229
    if not script.is_file():
        from tkinter import messagebox

        messagebox.showerror("Arhiv", f"Datoteka ni najdena:\n{script}", parent=app)
        return
    subprocess.Popen([sys.executable, str(script)], cwd=str(script.parent))
    app.after(150, app.destroy)


def add_version_menu(menubar: tk.Menu, app: tk.Tk, *, current: str) -> None:
    from v2.version_history_ui import open_version_history_window

    menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Verzija", menu=menu)

    patch = get_current_patch_version()
    menu.add_command(label=f"Davčna Blagajna {patch}  (trenutna)", state="disabled")
    menu.add_separator()
    menu.add_command(
        label="Zgodovina sprememb…",
        command=lambda: open_version_history_window(app),  # type: ignore[arg-type]
    )
    menu.add_command(label="Odpri mapo verzije", command=_open_versions_folder)
    menu.add_separator()
    menu.add_command(
        label="Zaženi arhiv 2.2.29 (Excel)…",
        command=lambda: launch_archive_2_2_29(app),
    )
    menu.add_command(label="Odpri mapo arhiva 2.2.29", command=_open_archive_folder)
