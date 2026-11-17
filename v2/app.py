"""AppV2 — podrazred v1 z novo temo in preurejenim vmesnikom."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any, Dict, List, Tuple

import DavcnaBlagajna as core
from v2.menubar import setup_app_menubar
from v2.theme import V2Layout, V2Theme, apply_v2_ttk_styles, load_v2_theme_from_disk
from v2.ui_build import build_ui_v2


class AppV2(core.App):
    """Celotna funkcionalnost v1, vizualno in prostorsko preurejena različica 2.0."""

    def __init__(self) -> None:
        load_v2_theme_from_disk()
        self._v2_chrome_frames: List[tk.Widget] = []
        self._v2_footer_frames: List[tk.Widget] = []
        self._v2_chrome_labels: List[Tuple[tk.Label, str]] = []
        self._v2_yellow_entries: List[tk.Entry] = []
        self._v2_yellow_comboboxes: List[ttk.Combobox] = []
        self._v2_tk_hint_labels: List[tk.Label] = []
        self._v2_layout_widgets: Dict[str, List[Any]] = {}
        self._v2_tab_bars: List[Any] = []
        self._v2_notebooks: List[Any] = []
        super().__init__()
        self.title(V2Theme.APP_TITLE)
        self.geometry("1680x940")
        self.minsize(1320, 780)
        self.apply_v2_theme()

    def register_layout_widget(self, layout_key: str, widget: Any) -> None:
        self._v2_layout_widgets.setdefault(layout_key, []).append(widget)

    def register_v2_tab_bar(self, bar: Any) -> None:
        self._v2_tab_bars.append(bar)

    def register_v2_notebook(self, nb: Any) -> None:
        self._v2_notebooks.append(nb)

    def refresh_v2_chrome_tabs(self) -> None:
        from v2.theme import refresh_notebook_active_tab

        for nb in self._v2_notebooks:
            try:
                refresh_notebook_active_tab(nb)
            except Exception:
                pass
        for bar in self._v2_tab_bars:
            try:
                bar.apply_theme()
            except Exception:
                pass

    def apply_v2_layout(self) -> None:
        for key, widgets in self._v2_layout_widgets.items():
            val = int(getattr(V2Layout, key, 0))
            for widget in widgets:
                try:
                    if key == "help_wraplength":
                        widget.configure(wraplength=val)
                    else:
                        widget.configure(width=val)
                except tk.TclError:
                    pass

    def apply_v2_theme(self) -> None:
        try:
            self.configure(bg=V2Theme.WINDOW_BG)
        except tk.TclError:
            pass
        self._setup_ui_styles()
        for frame in self._v2_chrome_frames:
            try:
                frame.configure(bg=V2Theme.HEADER_BG)
            except tk.TclError:
                pass
        for frame in self._v2_footer_frames:
            try:
                frame.configure(bg=V2Theme.FOOTER_BG)
            except tk.TclError:
                pass
        for label, role in self._v2_chrome_labels:
            self._style_chrome_label(label, role)
        for ent in self._v2_yellow_entries:
            self._style_yellow_entry(ent)
        for cb in self._v2_yellow_comboboxes:
            self._tint_combobox(cb)
        for lbl in self._v2_tk_hint_labels:
            try:
                lbl.configure(
                    fg=V2Theme.ACCENT_TEXT,
                    font=V2Theme.ui_font(bold=True),
                    bg=ttk.Style().lookup("TFrame", "background") or V2Theme.PANEL_BG,
                )
            except tk.TclError:
                pass
        if hasattr(self, "tree") and getattr(self, "_tree_sel_tag", None):
            try:
                self.tree.tag_configure(
                    self._tree_sel_tag,
                    foreground=V2Theme.TREE_ACTIVE_TAG,
                    font=V2Theme.ui_font(bold=True),
                )
                self.tree.tag_configure("zip_disabled", foreground=V2Theme.TREE_ZIP_DISABLED)
                self.tree.tag_configure(
                    "kirkpr_date_outside",
                    foreground="#cc0000",
                    background="#ffe8e8",
                )
            except tk.TclError:
                pass
        self.apply_v2_layout()
        self.refresh_v2_chrome_tabs()

    def _style_chrome_label(self, label: tk.Label, role: str) -> None:
        cfg: dict[str, Any] = {"font": V2Theme.ui_font()}
        if role == "header_bg":
            cfg.update(bg=V2Theme.HEADER_BG, fg=V2Theme.HEADER_FG)
        elif role == "header_title":
            cfg.update(bg=V2Theme.HEADER_BG, fg=V2Theme.HEADER_FG, font=V2Theme.ui_font(size_delta=7, bold=True))
        elif role == "header_muted":
            cfg.update(bg=V2Theme.HEADER_BG, fg=V2Theme.HEADER_MUTED)
        elif role == "header_accent":
            cfg.update(bg=V2Theme.HEADER_BG, fg=V2Theme.HEADER_ACCENT_FG)
        elif role == "header_company":
            cfg.update(bg=V2Theme.HEADER_BG, fg=V2Theme.HEADER_FG, font=V2Theme.ui_font(size_delta=1, bold=True))
        elif role == "badge":
            cfg.update(bg=V2Theme.BADGE_BG, fg=V2Theme.BADGE_FG, font=V2Theme.ui_font(size_delta=-1, bold=True))
        elif role == "footer":
            cfg.update(bg=V2Theme.FOOTER_BG, fg=V2Theme.FOOTER_FG, font=V2Theme.ui_font(size_delta=-1))
        try:
            label.configure(**cfg)
        except tk.TclError:
            pass

    def _style_yellow_entry(self, entry: tk.Entry) -> None:
        try:
            entry.configure(
                bg=V2Theme.ENTRY_BG,
                fg=V2Theme.ENTRY_FG,
                readonlybackground=V2Theme.ENTRY_BG,
                disabledbackground=V2Theme.ENTRY_DISABLED,
                insertbackground=V2Theme.ENTRY_FG,
                highlightbackground=V2Theme.BORDER,
                highlightcolor=V2Theme.ACCENT,
                font=V2Theme.ui_font(),
            )
        except tk.TclError:
            pass

    def _setup_ui_styles(self) -> None:
        apply_v2_ttk_styles(self)

    def _yellow_entry(self, parent: tk.Widget, **kwargs: Any) -> tk.Entry:
        show = kwargs.pop("show", None)
        entry = tk.Entry(
            parent,
            bg=V2Theme.ENTRY_BG,
            fg=V2Theme.ENTRY_FG,
            readonlybackground=V2Theme.ENTRY_BG,
            disabledbackground=V2Theme.ENTRY_DISABLED,
            insertbackground=V2Theme.ENTRY_FG,
            relief="flat",
            highlightthickness=1,
            highlightbackground=V2Theme.BORDER,
            highlightcolor=V2Theme.ACCENT,
            font=V2Theme.ui_font(),
            **kwargs,
        )
        if show is not None:
            entry.configure(show=show)
        self._v2_yellow_entries.append(entry)
        return entry

    def _yellow_combobox(self, parent: tk.Widget, **kwargs: Any) -> ttk.Combobox:
        cb = ttk.Combobox(parent, style="Yellow.TCombobox", **kwargs)
        self._v2_yellow_comboboxes.append(cb)
        self._tint_combobox(cb)
        return cb

    def _tint_combobox(self, cb: ttk.Combobox) -> None:
        def _apply() -> None:
            try:
                for child in cb.winfo_children():
                    if isinstance(child, tk.Entry):
                        child.configure(
                            bg=V2Theme.ENTRY_BG,
                            fg=V2Theme.ENTRY_FG,
                            readonlybackground=V2Theme.ENTRY_BG,
                            disabledbackground=V2Theme.ENTRY_DISABLED,
                            insertbackground=V2Theme.ENTRY_FG,
                            selectbackground="#bae6fd",
                            selectforeground=V2Theme.ENTRY_FG,
                            font=V2Theme.ui_font(),
                        )
            except tk.TclError:
                pass

        cb.after_idle(_apply)
        cb.bind("<<ComboboxSelected>>", lambda _e: _apply(), add="+")
        cb.bind("<FocusOut>", lambda _e: _apply(), add="+")

    def _accent_button(self, parent: tk.Widget, **kwargs: Any) -> ttk.Button:
        return ttk.Button(parent, style="V2.Accent.TButton", **kwargs)

    def _primary_button(self, parent: tk.Widget, **kwargs: Any) -> ttk.Button:
        return ttk.Button(parent, style="V2.Accent.TButton", **kwargs)

    def _build_ui(self) -> None:
        setup_app_menubar(self, ui_version="2.0")
        build_ui_v2(self)

    def register_v2_chrome_frame(self, widget: tk.Widget, *, footer: bool = False) -> None:
        if footer:
            self._v2_footer_frames.append(widget)
            try:
                widget.configure(bg=V2Theme.FOOTER_BG)
            except tk.TclError:
                pass
        else:
            self._v2_chrome_frames.append(widget)
            try:
                widget.configure(bg=V2Theme.HEADER_BG)
            except tk.TclError:
                pass

    def register_v2_chrome_label(self, label: tk.Label, role: str) -> tk.Label:
        self._v2_chrome_labels.append((label, role))
        self._style_chrome_label(label, role)
        return label

    def register_v2_hint_label(self, label: tk.Label) -> tk.Label:
        self._v2_tk_hint_labels.append(label)
        return label
