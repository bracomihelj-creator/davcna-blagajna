"""Okno zgodovine verzij 2.1.xx."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from typing import TYPE_CHECKING, Any, Dict, Optional

from v2.theme import V2Theme
from v2.version_journal import (
    get_current_patch_version,
    list_version_entries,
    read_version_log,
    version_log_path,
)

if TYPE_CHECKING:
    from v2.app import AppV2


def open_version_history_window(app: "AppV2") -> None:
    if getattr(app, "_v2_version_history_win", None) is not None:
        try:
            if app._v2_version_history_win.winfo_exists():
                app._v2_version_history_win.lift()
                app._v2_version_history_win.focus_force()
                return
        except tk.TclError:
            pass

    win = tk.Toplevel(app)
    app._v2_version_history_win = win
    win.title("Zgodovina verzij — Davčna Blagajna")
    win.transient(app)
    win.geometry("820x520")
    win.minsize(640, 400)

    outer = ttk.Frame(win, padding=10)
    outer.pack(fill="both", expand=True)
    outer.rowconfigure(1, weight=1)
    outer.columnconfigure(0, weight=1)

    current = get_current_patch_version()
    ttk.Label(
        outer,
        text=f"Trenutna verzija: {current}",
        font=V2Theme.ui_font(bold=True),
    ).grid(row=0, column=0, sticky="w", pady=(0, 8))

    paned = ttk.Panedwindow(outer, orient="horizontal")
    paned.grid(row=1, column=0, sticky="nsew")

    left = ttk.Frame(paned, padding=(0, 0, 6, 0))
    right = ttk.Frame(paned, padding=(6, 0, 0, 0))
    paned.add(left, weight=1)
    paned.add(right, weight=2)

    cols = ("id", "date", "title")
    tree = ttk.Treeview(left, columns=cols, show="headings", height=16)
    tree.heading("id", text="Verzija")
    tree.heading("date", text="Datum")
    tree.heading("title", text="Kratek opis")
    tree.column("id", width=72, stretch=False)
    tree.column("date", width=88, stretch=False)
    tree.column("title", width=220, stretch=True)
    tree.pack(fill="both", expand=True)

    vsb = ttk.Scrollbar(left, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")

    detail = tk.Text(
        right,
        wrap="word",
        font=V2Theme.ui_font(),
        state="disabled",
        padx=8,
        pady=8,
    )
    detail.pack(fill="both", expand=True)
    detail_sb = ttk.Scrollbar(right, orient="vertical", command=detail.yview)
    detail.configure(yscrollcommand=detail_sb.set)
    detail_sb.place(relx=1.0, rely=0, relheight=1.0, anchor="ne")

    entries = list_version_entries()
    entry_by_id: Dict[str, Dict[str, Any]] = {}
    for entry in entries:
        vid = str(entry.get("id", ""))
        entry_by_id[vid] = entry
        tree.insert(
            "",
            "end",
            iid=vid,
            values=(vid, entry.get("date", ""), entry.get("title", "")),
        )

    def _show_entry(entry: Optional[Dict[str, Any]]) -> None:
        detail.configure(state="normal")
        detail.delete("1.0", "end")
        if entry:
            detail.insert("1.0", read_version_log(entry))
        detail.configure(state="disabled")

    def _on_select(_event: tk.Event) -> None:
        sel = tree.selection()
        if not sel:
            return
        _show_entry(entry_by_id.get(sel[0]))

    tree.bind("<<TreeviewSelect>>", _on_select)

    if entries:
        first_id = str(entries[0].get("id", ""))
        if first_id:
            tree.selection_set(first_id)
            tree.focus(first_id)
            _show_entry(entry_by_id.get(first_id))

    btns = ttk.Frame(outer)
    btns.grid(row=2, column=0, sticky="ew", pady=(10, 0))

    def _open_txt() -> None:
        sel = tree.selection()
        if not sel:
            return
        entry = entry_by_id.get(sel[0])
        if not entry:
            return
        path = version_log_path(entry)
        if not path.is_file():
            messagebox.showerror("Zgodovina", f"Datoteka ni najdena:\n{path}", parent=win)
            return
        import os
        import subprocess
        import sys

        try:
            os.startfile(str(path))  # type: ignore[attr-defined]
        except Exception:
            if sys.platform == "darwin":
                subprocess.Popen(["open", str(path)])
            else:
                subprocess.Popen(["xdg-open", str(path)])

    ttk.Button(btns, text="Odpri TXT v urejevalniku", command=_open_txt).pack(side="left")
    ttk.Button(btns, text="Zapri", command=win.destroy).pack(side="right")

    ttk.Label(
        btns,
        text="Izberi verzijo na seznamu — desno je celoten dnevnik. Mapa: verzije\\",
        foreground="#555",
    ).pack(side="left", padx=(12, 0))

    win.grab_set()
