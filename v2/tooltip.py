"""Preprost tooltip (namig ob miški) za tk/ttk widgete."""

from __future__ import annotations

from typing import Optional

import tkinter as tk


class ToolTip:
    def __init__(self, widget: tk.Misc, text: str, *, wraplength: int = 380) -> None:
        self.widget = widget
        self.text = (text or "").strip()
        self.wraplength = wraplength
        self._tip: Optional[tk.Toplevel] = None
        if not self.text:
            return
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _show(self, _event: tk.Event | None = None) -> None:
        if self._tip is not None:
            return
        x = self.widget.winfo_rootx() + 12
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self._tip = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#ffffe0",
            foreground="#1e293b",
            relief="solid",
            borderwidth=1,
            font=("Segoe UI", 9),
            wraplength=self.wraplength,
            padx=8,
            pady=6,
        ).pack()

    def _hide(self, _event: tk.Event | None = None) -> None:
        if self._tip is not None:
            self._tip.destroy()
            self._tip = None


def attach_tooltip(widget: tk.Misc, text: str, *, wraplength: int = 380) -> None:
    """Prikaže rumen namig ob prehodu miške čez widget."""
    ToolTip(widget, text, wraplength=wraplength)
