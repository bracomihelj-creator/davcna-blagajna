"""Combobox z live filtrom med tipkanjem (dobavitelj, konto, …)."""

from __future__ import annotations

import re
from typing import Callable, Dict, List, Optional

import tkinter as tk
from tkinter import ttk


def _konto_code_from_label(label: str, label_to_code: Dict[str, str]) -> str:
    mapped = (label_to_code.get(label) or "").strip()
    if mapped:
        return mapped
    text = (label or "").strip()
    if " — " in text:
        return text.split(" — ", 1)[0].strip()
    m = re.match(r"^(\S+)", text)
    return m.group(1) if m else text


def filter_combobox_values(
    all_values: List[str],
    query: str,
    *,
    mode: str = "text",
    label_to_code: Optional[Dict[str, str]] = None,
) -> List[str]:
    q = (query or "").strip().lower()
    if not q:
        return list(all_values)
    out: List[str] = []
    for label in all_values:
        low = label.lower()
        if mode == "konto":
            code = _konto_code_from_label(label, label_to_code or {}).lower()
            if q in low or code.startswith(q) or q in code:
                out.append(label)
        elif mode == "customer":
            name = low.split(" — ", 1)[-1] if " — " in low else low
            if q in low or q in name:
                out.append(label)
        else:
            if q in low:
                out.append(label)
    return out if out else list(all_values)


def attach_filtered_combobox(
    cb: ttk.Combobox,
    all_values: List[str],
    *,
    mode: str = "text",
    label_to_code: Optional[Dict[str, str]] = None,
    on_filter: Optional[Callable[[], None]] = None,
) -> None:
    """Veže KeyRelease filter na combobox (ne moti puščic / Tab)."""
    state: Dict[str, object] = {
        "all": list(all_values),
        "label_to_code": dict(label_to_code or {}),
    }

    def _apply_filter(_event: Optional[tk.Event] = None) -> None:
        if str(cb.cget("state")) == "disabled":
            return
        keysym = getattr(_event, "keysym", "") if _event is not None else ""
        if keysym in {"Up", "Down", "Left", "Right", "Return", "Tab", "Escape", "Shift_L", "Shift_R"}:
            return
        typed = cb.get()
        filtered = filter_combobox_values(
            list(state["all"]),  # type: ignore[arg-type]
            typed,
            mode=mode,
            label_to_code=state["label_to_code"],  # type: ignore[arg-type]
        )
        cb.configure(values=filtered)
        if on_filter:
            on_filter()

    cb.bind("<KeyRelease>", _apply_filter, add="+")

    def set_all_values(values: List[str]) -> None:
        state["all"] = list(values)
        cb.configure(values=values)

    cb._filtered_set_all_values = set_all_values  # type: ignore[attr-defined]
