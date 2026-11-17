"""Vrstica zavihkov z aktivnim zavihkom krepko + rdeče (zanesljivo na Windows)."""

from __future__ import annotations

from typing import Callable, List, Sequence

import tkinter as tk

from v2.theme import V2Borders, V2Theme


class TabBar(tk.Frame):
    """Ročna vrstica zavihkov — aktivni: krepko barvno besedilo + črta spodaj."""

    def __init__(
        self,
        parent: tk.Misc,
        labels: Sequence[str],
        on_select: Callable[[int], None],
        *,
        compact: bool = False,
    ) -> None:
        super().__init__(parent, bg=V2Theme.PANEL_BG, highlightthickness=0, bd=0)
        self._on_select = on_select
        self._active = 0
        self._compact = compact
        self._labels: List[tk.Label] = []
        self._cells: List[tk.Frame] = []
        self._underlines: List[tk.Frame] = []

        pad_x = 10 if compact else 14
        pad_y = 4 if compact else 6

        for i, text in enumerate(labels):
            cell = tk.Frame(self, bg=V2Borders.tab_inactive_bg, highlightthickness=0, bd=0)
            cell.pack(side="left", padx=(0, 1))
            lbl = tk.Label(
                cell,
                text=text,
                bg=V2Borders.tab_inactive_bg,
                fg=V2Theme.TEXT,
                font=V2Theme.ui_font(),
                padx=pad_x,
                pady=pad_y,
                cursor="hand2",
            )
            lbl.pack()
            ul = tk.Frame(cell, height=max(1, int(V2Borders.tab_active_underline_px)), bg=V2Borders.tab_inactive_bg)
            ul.pack(fill="x")

            lbl.bind("<Button-1>", lambda _e, idx=i: self.select(idx))
            cell.bind("<Button-1>", lambda _e, idx=i: self.select(idx))
            ul.bind("<Button-1>", lambda _e, idx=i: self.select(idx))

            self._cells.append(cell)
            self._labels.append(lbl)
            self._underlines.append(ul)

        if labels:
            self.select(0, fire=False)

    @property
    def active_index(self) -> int:
        return self._active

    def apply_theme(self) -> None:
        """Osveži barve in obrobe po spremembi nastavitev."""
        self.configure(bg=V2Theme.PANEL_BG)
        ul_h = max(1, int(V2Borders.tab_active_underline_px))
        border_px = max(0, int(V2Borders.tab_border_px))
        border_col = V2Borders.tab_border_color
        for ul in self._underlines:
            try:
                ul.configure(height=ul_h)
            except tk.TclError:
                pass
        self.select(self._active, fire=False)

    def _apply_cell_border(self, cell: tk.Frame, *, active: bool) -> None:
        border_px = max(0, int(V2Borders.tab_border_px))
        if border_px <= 0:
            cell.configure(highlightthickness=0)
            return
        cell.configure(
            highlightthickness=border_px,
            highlightbackground=V2Borders.tab_border_color,
            highlightcolor=V2Borders.tab_active_fg if active else V2Borders.tab_border_color,
        )

    def select(self, index: int, *, fire: bool = True) -> None:
        if not self._labels:
            return
        index = max(0, min(index, len(self._labels) - 1))
        self._active = index
        inactive_bg = V2Borders.tab_inactive_bg
        active_bg = V2Borders.tab_active_bg
        active_fg = V2Borders.tab_active_fg
        ul_h = max(1, int(V2Borders.tab_active_underline_px))
        for i, (cell, lbl, ul) in enumerate(zip(self._cells, self._labels, self._underlines)):
            if i == index:
                cell.configure(bg=active_bg)
                lbl.configure(
                    font=V2Theme.ui_font(bold=True),
                    fg=active_fg,
                    bg=active_bg,
                )
                ul.configure(bg=active_fg, height=ul_h)
                self._apply_cell_border(cell, active=True)
            else:
                cell.configure(bg=inactive_bg)
                lbl.configure(
                    font=V2Theme.ui_font(),
                    fg=V2Theme.TEXT,
                    bg=inactive_bg,
                )
                ul.configure(bg=inactive_bg, height=ul_h)
                self._apply_cell_border(cell, active=False)
        if fire:
            self._on_select(index)
