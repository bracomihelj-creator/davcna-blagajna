"""Zložljivi paneli (+/−) za prostorsko stisko v v2.1."""

from __future__ import annotations

from typing import Any, Callable, Optional

import tkinter as tk
from tkinter import ttk


def wrap_collapsible_labelframe(
    parent: ttk.Misc,
    title: str,
    build_body: Callable[[ttk.Frame], None],
    app: Any,
    state_attr: str,
    *,
    collapsed_default: bool = False,
    padding: int = 6,
    body_fill: str = "x",
    body_expand: bool = False,
    lf_fill: str = "x",
    lf_expand: bool = False,
    collapse_hint: str = "Skrči panel (−).",
    expand_hint: str = "Razširi panel (+).",
) -> ttk.Frame:
    """
    Labelframe z gumboma +/−. state_attr na app: True = skrčen.
    build_body(body_frame) zapolni vsebino.
    outer.labelframe → notranji Labelframe (za .configure(text=…)).
    """
    outer = ttk.Frame(parent)
    lf = ttk.Labelframe(outer, text=title, padding=(padding, 2, padding, padding))
    lf.pack(fill=lf_fill, expand=lf_expand)
    setattr(outer, "labelframe", lf)

    hdr = ttk.Frame(lf)
    hdr.pack(fill="x", pady=(0, 2))
    body = ttk.Frame(lf)
    build_body(body)

    setattr(app, state_attr, collapsed_default)
    toggle_key = f"{state_attr}_toggle_btn"

    def _apply(collapsed: bool) -> None:
        setattr(app, state_attr, collapsed)
        btn = getattr(app, toggle_key, None)
        if collapsed:
            body.pack_forget()
            if btn is not None:
                btn.configure(text="+")
        else:
            body.pack(fill=body_fill, expand=body_expand)
            if btn is not None:
                btn.configure(text="−")

    def _collapse() -> None:
        _apply(True)

    def _expand() -> None:
        _apply(False)

    minus_btn = ttk.Button(hdr, text="−", width=3, command=_collapse)
    minus_btn.pack(side="right", padx=(2, 0))
    plus_btn = ttk.Button(hdr, text="+", width=3, command=_expand)
    plus_btn.pack(side="right")
    try:
        from v2.tooltip import attach_tooltip

        attach_tooltip(minus_btn, collapse_hint)
        attach_tooltip(plus_btn, expand_hint)
    except Exception:
        pass
    setattr(app, toggle_key, minus_btn)

    setattr(app, f"{state_attr}_set", _apply)

    if collapsed_default:
        _apply(True)
    else:
        _apply(False)

    return outer


def wrap_collapsible_frame(
    parent: ttk.Misc,
    title: str,
    build_body: Callable[[ttk.Frame], None],
    app: Any,
    state_attr: str,
    *,
    collapsed_default: bool = False,
) -> ttk.Frame:
    """Enostaven zložljiv okvir brez Labelframe (npr. export area)."""
    outer = ttk.Frame(parent)
    hdr = ttk.Frame(outer)
    hdr.pack(fill="x")
    ttk.Label(hdr, text=title, foreground="#444444").pack(side="left", padx=(2, 8))
    body = ttk.Frame(outer)
    build_body(body)

    setattr(app, state_attr, collapsed_default)
    toggle_key = f"{state_attr}_toggle_btn"

    def _apply(collapsed: bool) -> None:
        setattr(app, state_attr, collapsed)
        btn = getattr(app, toggle_key, None)
        if collapsed:
            body.pack_forget()
            if btn is not None:
                btn.configure(text="+")
        else:
            body.pack(fill="x", pady=(2, 0))
            if btn is not None:
                btn.configure(text="−")

    minus_btn = ttk.Button(hdr, text="−", width=3, command=lambda: _apply(True))
    minus_btn.pack(side="right", padx=(2, 0))
    plus_btn = ttk.Button(hdr, text="+", width=3, command=lambda: _apply(False))
    plus_btn.pack(side="right")
    setattr(app, toggle_key, minus_btn)
    setattr(app, f"{state_attr}_set", _apply)

    if collapsed_default:
        _apply(True)
    else:
        _apply(False)

    return outer
