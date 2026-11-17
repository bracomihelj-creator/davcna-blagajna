"""Slovenski DT picker — vnos dd.mm.yyyy + padajoči koledar."""

from __future__ import annotations

import calendar
import datetime as dt
import re
import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Tuple

_SL_MONTHS = (
    "januar",
    "februar",
    "marec",
    "april",
    "maj",
    "junij",
    "julij",
    "avgust",
    "september",
    "oktober",
    "november",
    "december",
)
_DAY_HEADERS = ("Pon", "Tor", "Sre", "Čet", "Pet", "Sob", "Ned")


def _parse_sl_date_parts(value: str) -> Optional[Tuple[int, int, int]]:
    raw = (value or "").strip()
    if not raw:
        return None
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", raw)
    if m:
        return int(m.group(3)), int(m.group(2)), int(m.group(1))
    m = re.fullmatch(r"(\d{1,2})\.(\d{1,2})\.(\d{4})", raw)
    if m:
        return int(m.group(1)), int(m.group(2)), int(m.group(3))
    return None


def _format_sl_date(day: int, month: int, year: int) -> str:
    return f"{int(day):02d}.{int(month):02d}.{int(year):04d}"


def _clamp_parts(day: int, month: int, year: int) -> Tuple[int, int, int]:
    month = max(1, min(int(month), 12))
    year = max(1990, min(int(year), 2099))
    day = max(1, min(int(day), calendar.monthrange(year, month)[1]))
    return day, month, year


def _today_parts() -> Tuple[int, int, int]:
    t = dt.date.today()
    return t.day, t.month, t.year


class _CalendarPopup(tk.Toplevel):
    def __init__(
        self,
        master: tk.Misc,
        *,
        anchor: tk.Widget,
        initial: Optional[Tuple[int, int, int]],
        on_select: Callable[[int, int, int], None],
    ) -> None:
        super().__init__(master)
        self._on_select = on_select
        self.withdraw()
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(borderwidth=1, relief="solid")

        if initial:
            day, month, year = _clamp_parts(*initial)
        else:
            day, month, year = _today_parts()
        self._sel_day, self._sel_month, self._sel_year = day, month, year
        self._view_month, self._view_year = month, year

        outer = ttk.Frame(self, padding=4)
        outer.pack(fill="both", expand=True)

        nav = ttk.Frame(outer)
        nav.pack(fill="x", pady=(0, 4))
        ttk.Button(nav, text="◀", width=3, command=self._prev_month).pack(side="left")
        self._title_var = tk.StringVar()
        ttk.Label(nav, textvariable=self._title_var, width=18, anchor="center").pack(
            side="left", expand=True
        )
        ttk.Button(nav, text="▶", width=3, command=self._next_month).pack(side="left")

        self._grid_frm = ttk.Frame(outer)
        self._grid_frm.pack()
        self._day_buttons: list[ttk.Button] = []

        self._render_grid()
        self.update_idletasks()
        self._place_near(anchor)
        self.deiconify()
        self.grab_set()
        self.bind("<Escape>", lambda _e: self.destroy())

    def _place_near(self, anchor: tk.Widget) -> None:
        try:
            x = anchor.winfo_rootx()
            y = anchor.winfo_rooty() + anchor.winfo_height() + 2
        except tk.TclError:
            x, y = 100, 100
        self.geometry(f"+{x}+{y}")

    def _title_text(self) -> str:
        return f"{_SL_MONTHS[self._view_month - 1].capitalize()} {self._view_year}"

    def _prev_month(self) -> None:
        if self._view_month == 1:
            self._view_month = 12
            self._view_year -= 1
        else:
            self._view_month -= 1
        self._render_grid()

    def _next_month(self) -> None:
        if self._view_month == 12:
            self._view_month = 1
            self._view_year += 1
        else:
            self._view_month += 1
        self._render_grid()

    def _pick(self, day: int, month: int, year: int) -> None:
        d, m, y = _clamp_parts(day, month, year)
        self._on_select(d, m, y)
        self.destroy()

    def destroy(self) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass
        super().destroy()

    def _render_grid(self) -> None:
        for child in self._grid_frm.winfo_children():
            child.destroy()
        self._day_buttons.clear()
        self._title_var.set(self._title_text())

        ttk.Label(self._grid_frm, text="", width=3, anchor="center").grid(row=0, column=0)
        for col, hdr in enumerate(_DAY_HEADERS, start=1):
            ttk.Label(self._grid_frm, text=hdr, width=3, anchor="center").grid(
                row=0, column=col, padx=1, pady=1
            )

        weeks = calendar.monthcalendar(self._view_year, self._view_month)
        today = _today_parts()

        for row_i, week in enumerate(weeks, start=1):
            iso_week = row_i
            for d in week:
                if d != 0:
                    iso_week = dt.date(self._view_year, self._view_month, d).isocalendar()[1]
                    break
            ttk.Label(self._grid_frm, text=str(iso_week), width=3, anchor="center").grid(
                row=row_i, column=0, padx=1, pady=1
            )

            for col_i, day in enumerate(week, start=1):
                if day == 0:
                    ttk.Label(self._grid_frm, text="", width=3).grid(
                        row=row_i, column=col_i, padx=1, pady=1
                    )
                    continue
                is_sel = (
                    day == self._sel_day
                    and self._view_month == self._sel_month
                    and self._view_year == self._sel_year
                )
                is_today = (
                    day == today[0]
                    and self._view_month == today[1]
                    and self._view_year == today[2]
                )
                btn = tk.Button(
                    self._grid_frm,
                    text=f"{day:02d}",
                    width=3,
                    relief="flat",
                    bg="#cce4f7" if is_sel else ("#f5f5f5" if is_today else "white"),
                    command=lambda d=day, mo=self._view_month, y=self._view_year: self._pick(d, mo, y),
                )
                btn.grid(row=row_i, column=col_i, padx=1, pady=1)
                self._day_buttons.append(btn)


class SlDatePicker(ttk.Frame):
    """DT picker: polje dd.mm.yyyy + gumb za koledar (+ po želji počisti)."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        textvariable: Optional[tk.StringVar] = None,
        entry_width: int = 12,
        show_clear: bool = True,
        **kwargs: object,
    ) -> None:
        super().__init__(master, **kwargs)
        self._var = textvariable or tk.StringVar()
        self._syncing = False
        self._popup: Optional[_CalendarPopup] = None

        self._entry = ttk.Entry(self, textvariable=self._var, width=entry_width)
        self._entry.pack(side="left")
        self._entry.bind("<FocusOut>", self._on_entry_focus_out)
        self._entry.bind("<Return>", self._on_entry_focus_out)

        ttk.Button(self, text="▼", width=2, command=self._open_calendar).pack(side="left", padx=(2, 0))
        if show_clear:
            ttk.Button(self, text="×", width=2, command=self._clear).pack(side="left", padx=(2, 0))

        self._var.trace_add("write", self._on_external_var)

    def get(self) -> str:
        return self._var.get()

    def set(self, value: str) -> None:
        self._var.set(value or "")

    def _clear(self) -> None:
        self._var.set("")

    def _on_external_var(self, *_args: object) -> None:
        if self._syncing:
            return
        parts = _parse_sl_date_parts(self._var.get())
        if parts is None:
            return
        d, m, y = _clamp_parts(*parts)
        formatted = _format_sl_date(d, m, y)
        if formatted != self._var.get():
            self._syncing = True
            try:
                self._var.set(formatted)
            finally:
                self._syncing = False

    def _on_entry_focus_out(self, _event: Optional[tk.Event] = None) -> None:
        raw = self._var.get().strip()
        if not raw:
            return
        parts = _parse_sl_date_parts(raw)
        if parts is None:
            return
        d, m, y = _clamp_parts(*parts)
        self._syncing = True
        try:
            self._var.set(_format_sl_date(d, m, y))
        finally:
            self._syncing = False

    def _open_calendar(self) -> None:
        if self._popup is not None:
            try:
                if self._popup.winfo_exists():
                    self._popup.destroy()
            except tk.TclError:
                pass
        parts = _parse_sl_date_parts(self._var.get())
        self._popup = _CalendarPopup(
            self.winfo_toplevel(),
            anchor=self._entry,
            initial=parts,
            on_select=self._on_calendar_pick,
        )

    def _on_calendar_pick(self, day: int, month: int, year: int) -> None:
        self._syncing = True
        try:
            self._var.set(_format_sl_date(day, month, year))
        finally:
            self._syncing = False
