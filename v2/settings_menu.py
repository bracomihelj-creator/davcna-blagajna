"""Meni Nastavitve — tema, barve, fonti in širine polj (v2)."""

from __future__ import annotations

import copy
from pathlib import Path
import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox, ttk
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from v2.theme import (
    BORDER_COLOR_KEYS,
    BORDER_INT_KEYS,
    BORDER_KEYS,
    BORDER_LABELS_SL,
    DEFAULT_BORDERS,
    DEFAULT_LAYOUT,
    DEFAULT_THEME,
    DEFAULT_UI,
    FONT_FAMILIES,
    LAYOUT_KEYS,
    LAYOUT_LABELS_SL,
    THEME_COLOR_KEYS,
    THEME_LABELS_SL,
    THEME_PRESETS,
    UI_OPTION_KEYS,
    UI_OPTION_LABELS_SL,
    V2Theme,
    apply_preset,
    class_to_theme_data,
    normalize_borders_dict,
    normalize_layout_dict,
    normalize_ui_dict,
    save_v2_theme_to_disk,
    theme_data_to_class,
)
from v2.edavki_links_settings import (
    DEFAULT_EDAVKI_LINKS,
    load_edavki_links_from_disk,
    load_links_from_sql,
    normalize_edavki_links_config,
    resolve_sql_connection_string,
    save_edavki_links_to_disk,
)
from v2.kirkpr_knjizba_form_layout import (
    DEFAULT_KNJIZBA_FORM_LAYOUT,
    KNJIZBA_FORM_FIELD_CATALOG,
    KNJIZBA_FORM_FILE,
    knjizba_form_catalog_for_book,
    knjizba_form_fields_key,
    load_knjizba_form_layout_from_disk,
    normalize_knjizba_form_layout,
    save_knjizba_form_layout_to_disk,
)
from v2.collapsible import wrap_collapsible_labelframe
from v2.knjizba_form_designer import KnjizbaFormDesigner
from v2.access_settings import (
    ACCESS_FLAG_LABELS_SL,
    ACCESS_FLAGS,
    ACCESS_OPTION_KEYS,
    ACCESS_OPTION_LABELS_SL,
    ACCESS_SERVICE_LABELS_SL,
    ACCESS_SERVICES,
    ACCESS_URL_LABELS_SL,
    DEFAULT_ACCESS,
    DEFAULT_ACCESS_OPTIONS,
    DEFAULT_ACCESS_URLS,
    DEFAULT_MINIMAX_KIRKPR_PAGE_URL,
    load_v2_access_from_disk,
    load_v2_access_options_from_disk,
    load_v2_access_urls_from_disk,
    normalize_access_dict,
    normalize_access_options,
    normalize_access_urls,
    save_v2_access_to_disk,
)
from v2.file_compare_settings import (
    DEFAULT_FILE_COMPARE_DEFINITIONS,
    FILE_COMPARE_BOOKS,
    FILE_COMPARE_EXCEL_MODES,
    FILE_COMPARE_FORMATS,
    FILE_COMPARE_KINDS,
    FILE_COMPARE_SOURCES,
    load_file_compare_settings_from_disk,
    normalize_file_compare_settings,
    save_file_compare_settings_to_disk,
)

if TYPE_CHECKING:
    from v2.app import AppV2


def _launch_edavki_chrome(app: "AppV2") -> None:
    launch = getattr(app, "_launch_edavki_debug_chrome", None)
    if callable(launch):
        launch()
        return
    messagebox.showwarning(
        "eDavki Chrome",
        "Ta različica aplikacije nima samodejnega zagona Chrome.\n"
        "Zaženi ZAZENI_CHROME_EDAVKI_DEBUG.bat.",
        parent=app,
    )


def _launch_minimax_chrome(app: "AppV2") -> None:
    launch = getattr(app, "_launch_minimax_debug_chrome", None)
    if callable(launch):
        launch()
        return
    messagebox.showwarning(
        "Minimax Chrome",
        "Ta različica aplikacije nima samodejnega zagona Chrome.\n"
        "Zaženi ZAZENI_CHROME_MINIMAX_DEBUG.bat.",
        parent=app,
    )


def setup_settings_submenu(menubar: tk.Menu, app: "AppV2") -> None:
    menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Nastavitve", menu=menu)

    tema = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Tema", menu=tema)
    tema.add_command(label="Privzeta (2.0)", command=lambda: _apply_named_preset(app, "privzeta"))
    tema.add_command(label="Temna", command=lambda: _apply_named_preset(app, "temna"))
    tema.add_command(label="Svetla", command=lambda: _apply_named_preset(app, "svetla"))
    tema.add_command(label="Klasična (v1)", command=lambda: _apply_named_preset(app, "klasicna"))

    menu.add_command(label="Videz in postavitev…", command=lambda: open_settings_dialog(app))
    menu.add_separator()
    menu.add_command(
        label="Odpri eDavki Chrome…",
        command=lambda: _launch_edavki_chrome(app),
    )
    menu.add_command(
        label="Odpri Minimax Chrome…",
        command=lambda: _launch_minimax_chrome(app),
    )
    menu.add_separator()
    menu.add_command(label="Ponastavi privzeto", command=lambda: _apply_named_preset(app, "privzeta"))


def setup_settings_menu(app: "AppV2") -> None:
    """Združljivost — samo Nastavitve (brez Verzija)."""
    menubar = tk.Menu(app)
    app.config(menu=menubar)
    setup_settings_submenu(menubar, app)


def _apply_named_preset(app: "AppV2", key: str) -> None:
    data = apply_preset(key)
    save_v2_theme_to_disk(data)
    app.apply_v2_theme()
    app.update_idletasks()
    messagebox.showinfo("Nastavitve", f"Tema «{key}» je shranjena.", parent=app)


def _make_scrollable(parent: ttk.Frame) -> ttk.Frame:
    """Vrne notranji okvir z vsebino; parent mora imeti row/column weight=1."""
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    canvas = tk.Canvas(parent, highlightthickness=0, borderwidth=0)
    vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    canvas.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")

    inner = ttk.Frame(canvas, padding=4)
    window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_inner_configure(_event: tk.Event) -> None:
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(event: tk.Event) -> None:
        canvas.itemconfigure(window_id, width=event.width)

    inner.bind("<Configure>", _on_inner_configure)
    canvas.bind("<Configure>", _on_canvas_configure)
    canvas.configure(yscrollcommand=vsb.set)

    def _on_mousewheel(event: tk.Event) -> None:
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_wheel(_event: tk.Event) -> None:
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def _unbind_wheel(_event: tk.Event) -> None:
        canvas.unbind_all("<MouseWheel>")

    for widget in (canvas, inner):
        widget.bind("<Enter>", _bind_wheel)
        widget.bind("<Leave>", _unbind_wheel)

    return inner


class V2SettingsDialog(tk.Toplevel):
    """Dialog: zavihek barve/fonti + zavihek širine polj. Drsnik, Shrani na obeh zavihkih."""

    def __init__(self, app: "AppV2") -> None:
        super().__init__(app)
        self.app = app
        self.title("Nastavitve — videz in postavitev")
        self.transient(app)
        self.resizable(True, True)

        self._working = copy.deepcopy(class_to_theme_data())
        self._color_vars: Dict[str, tk.StringVar] = {}
        self._swatches: Dict[str, tk.Label] = {}
        self._layout_vars: Dict[str, tk.IntVar] = {}
        self._border_color_vars: Dict[str, tk.StringVar] = {}
        self._border_int_vars: Dict[str, tk.IntVar] = {}
        self._border_swatches: Dict[str, tk.Label] = {}
        self._ui_option_vars: Dict[str, tk.BooleanVar] = {}
        self._access_vars: Dict[str, Dict[str, tk.BooleanVar]] = {}
        self._access_option_vars: Dict[str, tk.BooleanVar] = {}
        self._access_url_vars: Dict[str, Any] = {}
        self._access_working = copy.deepcopy(load_v2_access_from_disk())
        self._access_options_working = copy.deepcopy(load_v2_access_options_from_disk())
        self._access_urls_working = copy.deepcopy(load_v2_access_urls_from_disk())
        self._links_working = copy.deepcopy(load_edavki_links_from_disk())
        self._link_row_vars: List[Dict[str, Any]] = []
        self._links_rows_host: Optional[ttk.Frame] = None
        self._file_compare_working = copy.deepcopy(load_file_compare_settings_from_disk())
        self._file_compare_row_vars: List[Dict[str, Any]] = []
        self._file_compare_rows_host: Optional[ttk.Frame] = None
        self._sql_config_var = tk.StringVar(
            value=str(self._links_working.get("sql_config_path") or "../EvidencaFirm/config.json")
        )
        self._refresh_sql_on_startup_var = tk.BooleanVar(
            value=bool(self._links_working.get("refresh_from_sql_on_startup", False))
        )
        self._knjizba_working = copy.deepcopy(load_knjizba_form_layout_from_disk())
        self._knjizba_tree: Optional[ttk.Treeview] = None
        self._knjizba_sel_visible = tk.BooleanVar(value=True)
        self._knjizba_sel_label = tk.StringVar(value="")
        self._knjizba_sel_row = tk.IntVar(value=-1)
        self._knjizba_sel_col = tk.StringVar(value="-1")
        self._knjizba_sel_entry_w = tk.IntVar(value=0)
        self._knjizba_dialog_w = tk.IntVar(value=int(self._knjizba_working.get("dialog_width") or 720))
        self._knjizba_dialog_h = tk.IntVar(value=int(self._knjizba_working.get("dialog_height") or 640))
        self._knjizba_label_w = tk.IntVar(value=int(self._knjizba_working.get("label_width") or 22))
        self._knjizba_entry_w = tk.IntVar(value=int(self._knjizba_working.get("entry_width") or 48))
        self._knjizba_columns = tk.IntVar(value=int(self._knjizba_working.get("columns") or 1))
        self._knjizba_show_summary = tk.BooleanVar(
            value=bool(self._knjizba_working.get("show_api_summary", True))
        )
        self._knjizba_book = tk.StringVar(value="KIR")
        self._knjizba_designer: Optional[KnjizbaFormDesigner] = None
        self._status_var = tk.StringVar(value="")

        outer = ttk.Frame(self, padding=10)
        outer.pack(fill="both", expand=True)
        outer.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)

        nb = ttk.Notebook(outer)
        nb.grid(row=0, column=0, sticky="nsew")

        tab_appearance = ttk.Frame(nb, padding=(4, 4, 4, 0))
        tab_layout = ttk.Frame(nb, padding=(4, 4, 4, 0))
        tab_borders = ttk.Frame(nb, padding=(4, 4, 4, 0))
        tab_access = ttk.Frame(nb, padding=(4, 4, 4, 0))
        tab_links = ttk.Frame(nb, padding=(4, 4, 4, 0))
        tab_behavior = ttk.Frame(nb, padding=(4, 4, 4, 0))
        tab_file_compare = ttk.Frame(nb, padding=(4, 4, 4, 0))
        tab_knjizba = ttk.Frame(nb, padding=(4, 4, 4, 0))
        nb.add(tab_appearance, text="Barve in fonti")
        nb.add(tab_layout, text="Širine polj")
        nb.add(tab_borders, text="Obrobe")
        nb.add(tab_access, text="Dostop eDavki, Minimax")
        nb.add(tab_links, text="Povezave")
        nb.add(tab_behavior, text="Vedenje")
        nb.add(tab_file_compare, text="Primerjave datotek")
        nb.add(tab_knjizba, text="Minimax knjižba")

        tab_appearance.rowconfigure(0, weight=1)
        tab_appearance.columnconfigure(0, weight=1)
        tab_layout.rowconfigure(0, weight=1)
        tab_layout.columnconfigure(0, weight=1)
        tab_borders.rowconfigure(0, weight=1)
        tab_borders.columnconfigure(0, weight=1)
        tab_access.rowconfigure(0, weight=1)
        tab_access.columnconfigure(0, weight=1)
        tab_links.rowconfigure(0, weight=1)
        tab_links.columnconfigure(0, weight=1)
        tab_behavior.rowconfigure(0, weight=1)
        tab_behavior.columnconfigure(0, weight=1)
        tab_file_compare.rowconfigure(0, weight=1)
        tab_file_compare.columnconfigure(0, weight=1)
        tab_knjizba.rowconfigure(0, weight=1)
        tab_knjizba.columnconfigure(0, weight=1)

        appearance_scroll_host = ttk.Frame(tab_appearance)
        appearance_scroll_host.grid(row=0, column=0, sticky="nsew")
        layout_scroll_host = ttk.Frame(tab_layout)
        layout_scroll_host.grid(row=0, column=0, sticky="nsew")
        borders_scroll_host = ttk.Frame(tab_borders)
        borders_scroll_host.grid(row=0, column=0, sticky="nsew")
        access_scroll_host = ttk.Frame(tab_access)
        access_scroll_host.grid(row=0, column=0, sticky="nsew")
        links_scroll_host = ttk.Frame(tab_links)
        links_scroll_host.grid(row=0, column=0, sticky="nsew")
        behavior_scroll_host = ttk.Frame(tab_behavior)
        behavior_scroll_host.grid(row=0, column=0, sticky="nsew")
        file_compare_scroll_host = ttk.Frame(tab_file_compare)
        file_compare_scroll_host.grid(row=0, column=0, sticky="nsew")
        knjizba_scroll_host = ttk.Frame(tab_knjizba)
        knjizba_scroll_host.grid(row=0, column=0, sticky="nsew")

        self._build_appearance_tab(_make_scrollable(appearance_scroll_host))
        self._build_layout_tab(_make_scrollable(layout_scroll_host))
        self._build_borders_tab(_make_scrollable(borders_scroll_host))
        self._build_access_tab(_make_scrollable(access_scroll_host))
        self._build_links_tab(_make_scrollable(links_scroll_host))
        self._build_behavior_tab(_make_scrollable(behavior_scroll_host))
        self._build_file_compare_tab(_make_scrollable(file_compare_scroll_host))
        self._build_knjizba_form_tab(_make_scrollable(knjizba_scroll_host))

        self._build_tab_action_row(tab_appearance, row=1)
        self._build_tab_action_row(tab_layout, row=1)
        self._build_tab_action_row(tab_borders, row=1)
        self._build_tab_action_row(tab_access, row=1)
        self._build_tab_action_row(tab_links, row=1)
        self._build_tab_action_row(tab_behavior, row=1)
        self._build_tab_action_row(tab_file_compare, row=1)
        self._build_tab_action_row(tab_knjizba, row=1)

        footer = ttk.Frame(outer)
        footer.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        footer.columnconfigure(0, weight=1)

        ttk.Label(footer, textvariable=self._status_var, foreground="#2e7d32").grid(
            row=0, column=0, sticky="w"
        )

        btns = ttk.Frame(footer)
        btns.grid(row=0, column=1, sticky="e")
        ttk.Button(btns, text="Prekliči", command=self.destroy).pack(side="right", padx=(6, 0))
        ttk.Button(btns, text="Shrani in zapri", command=self._save_close).pack(side="right", padx=(6, 0))
        self._accent_save = self.app._accent_button(btns, text="Shrani", command=self._save)
        self._accent_save.pack(side="right", padx=(6, 0))
        ttk.Button(btns, text="Uporabi", command=self._apply_preview).pack(side="right", padx=(6, 0))

        self.geometry("720x720")
        self.minsize(480, 480)
        self.update_idletasks()
        self.grab_set()

    def _build_tab_action_row(self, parent: ttk.Frame, *, row: int) -> None:
        row_frame = ttk.Frame(parent)
        row_frame.grid(row=row, column=0, sticky="ew", pady=(8, 4))
        self.app._accent_button(row_frame, text="Shrani", command=self._save).pack(side="right")
        ttk.Button(row_frame, text="Uporabi", command=self._apply_preview).pack(side="right", padx=(0, 6))

    def _build_appearance_tab(self, body: ttk.Frame) -> None:
        body.columnconfigure(1, weight=1)

        ttk.Label(body, text="Pisava", font=V2Theme.ui_font(bold=True)).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )
        ttk.Label(body, text="Družina:").grid(row=1, column=0, sticky="w", padx=(0, 8), pady=4)
        self._font_family = tk.StringVar(value=self._working.get("font_family", "Segoe UI"))
        ttk.Combobox(
            body,
            textvariable=self._font_family,
            values=list(FONT_FAMILIES),
            state="readonly",
            width=24,
        ).grid(row=1, column=1, sticky="w", pady=4)

        ttk.Label(body, text="Velikost:").grid(row=2, column=0, sticky="w", padx=(0, 8), pady=4)
        self._font_size = tk.IntVar(value=int(self._working.get("font_size") or 9))
        ttk.Spinbox(body, from_=7, to=16, textvariable=self._font_size, width=6).grid(
            row=2, column=1, sticky="w", pady=4
        )

        ttk.Separator(body, orient="horizontal").grid(row=3, column=0, columnspan=4, sticky="ew", pady=12)
        ttk.Label(body, text="Barve in ozadje", font=V2Theme.ui_font(bold=True)).grid(
            row=4, column=0, columnspan=3, sticky="w", pady=(0, 8)
        )

        colors: Dict[str, str] = self._working.setdefault("colors", {})
        row_i = 5
        for key in THEME_COLOR_KEYS:
            if key not in colors and key in DEFAULT_THEME["colors"]:
                colors[key] = DEFAULT_THEME["colors"][key]
            ttk.Label(body, text=THEME_LABELS_SL.get(key, key) + ":", width=28).grid(
                row=row_i, column=0, sticky="w", padx=(0, 8), pady=3
            )
            var = tk.StringVar(value=colors.get(key, "#000000"))
            self._color_vars[key] = var
            ttk.Entry(body, textvariable=var, width=10).grid(row=row_i, column=1, sticky="w", pady=3)
            sw = tk.Label(body, text="   ", bg=var.get(), width=4, relief="groove")
            sw.grid(row=row_i, column=2, sticky="w", padx=(6, 0), pady=3)
            self._swatches[key] = sw
            ttk.Button(
                body,
                text="…",
                width=3,
                command=lambda k=key: self._pick_color(k),
            ).grid(row=row_i, column=3, sticky="w", padx=(4, 0), pady=3)
            var.trace_add("write", lambda *_a, k=key: self._sync_swatch(k))
            row_i += 1

    def _build_layout_tab(self, body: ttk.Frame) -> None:
        layout = normalize_layout_dict(self._working.get("layout"))
        self._working["layout"] = layout

        ttk.Label(
            body,
            text="Vsako polje ima svojo širino (znaki). Po Shrani se glavno okno takoj posodobi.",
            wraplength=460,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        grid = ttk.Frame(body)
        grid.pack(anchor="w", fill="x")
        for row_i, key in enumerate(LAYOUT_KEYS):
            ttk.Label(grid, text=LAYOUT_LABELS_SL.get(key, key) + ":", width=36).grid(
                row=row_i, column=0, sticky="w", padx=(0, 8), pady=4
            )
            lo = 200 if key == "help_wraplength" else 4
            hi = 1200 if key == "help_wraplength" else 120
            var = tk.IntVar(value=int(layout.get(key, DEFAULT_LAYOUT[key])))
            self._layout_vars[key] = var
            ttk.Spinbox(grid, from_=lo, to=hi, textvariable=var, width=8).grid(
                row=row_i, column=1, sticky="w", pady=4
            )

        ttk.Button(
            body,
            text="Ponastavi širine",
            command=self._reset_layout_defaults,
        ).pack(anchor="w", pady=(12, 0))

    def _build_borders_tab(self, body: ttk.Frame) -> None:
        borders = normalize_borders_dict(self._working.get("borders"))
        self._working["borders"] = borders

        ttk.Label(
            body,
            text="Obrobe zavihkov, panelov (okvirjev) in ločilnih črt. Po Shrani se glavno okno takoj posodobi.",
            wraplength=480,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        grid = ttk.Frame(body)
        grid.pack(anchor="w", fill="x")
        row_i = 0
        for key in BORDER_INT_KEYS:
            ttk.Label(grid, text=BORDER_LABELS_SL.get(key, key) + ":", width=36).grid(
                row=row_i, column=0, sticky="w", padx=(0, 8), pady=4
            )
            lo = 0 if "border_px" in key and key != "tab_active_underline_px" else 1
            hi = 12 if "underline" in key or "separator" in key else 8
            var = tk.IntVar(value=int(borders.get(key, DEFAULT_BORDERS[key])))
            self._border_int_vars[key] = var
            ttk.Spinbox(grid, from_=lo, to=hi, textvariable=var, width=8).grid(
                row=row_i, column=1, sticky="w", pady=4
            )
            row_i += 1

        ttk.Separator(body, orient="horizontal").pack(fill="x", pady=10)

        for key in BORDER_COLOR_KEYS:
            row_frm = ttk.Frame(body)
            row_frm.pack(fill="x", pady=3)
            ttk.Label(row_frm, text=BORDER_LABELS_SL.get(key, key) + ":", width=36).pack(side="left")
            var = tk.StringVar(value=str(borders.get(key, DEFAULT_BORDERS[key])))
            self._border_color_vars[key] = var
            ttk.Entry(row_frm, textvariable=var, width=10).pack(side="left", padx=(0, 4))
            sw = tk.Label(row_frm, text="   ", bg=var.get(), width=4, relief="groove")
            sw.pack(side="left", padx=(0, 4))
            self._border_swatches[key] = sw
            ttk.Button(
                row_frm,
                text="…",
                width=3,
                command=lambda k=key: self._pick_border_color(k),
            ).pack(side="left")
            var.trace_add("write", lambda *_a, k=key: self._sync_border_swatch(k))

        ttk.Button(
            body,
            text="Ponastavi obrobe",
            command=self._reset_border_defaults,
        ).pack(anchor="w", pady=(12, 0))

    def _build_access_tab(self, body: ttk.Frame) -> None:
        access = normalize_access_dict(self._access_working)
        self._access_working = access
        options = normalize_access_options(self._access_options_working)
        self._access_options_working = options

        notify_grp = ttk.Labelframe(body, text="Obvestila", padding=8)
        notify_grp.pack(fill="x", anchor="w", pady=(0, 12))
        for key in ACCESS_OPTION_KEYS:
            var = tk.BooleanVar(value=bool(options.get(key, False)))
            self._access_option_vars[key] = var
            ttk.Checkbutton(
                notify_grp,
                text=ACCESS_OPTION_LABELS_SL.get(key, key),
                variable=var,
            ).pack(anchor="w", pady=2)

        ttk.Label(
            body,
            text=(
                "1) Direct link — odpre stran v Chrome (pri KIR/KPR; pri FURS rezervni način).\n"
                "2) Odložišče — skopira ciljno pot datoteke (npr. ZIP) za CTRL+V.\n"
                "3) Avtomatika — FURS Blagajna v APLIKACIJI (CDP/Chrome, BREZ vtičnika): "
                "Od/do + Pripravi + Shrani + izhod. Brez kljukice = samo odpri + Od/do.\n"
                "Chrome: Nastavitve → Odpri eDavki Chrome (debug). Vtičnik Minimax podjetja ni potreben."
            ),
            wraplength=520,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        url_grp = ttk.Labelframe(body, text="Povezava Minimax ObracunDDV", padding=8)
        url_grp.pack(fill="x", anchor="w", pady=(0, 12))
        urls = normalize_access_urls(self._access_urls_working)
        self._access_urls_working = urls
        url_row = ttk.Frame(url_grp)
        url_row.pack(fill="x", pady=(0, 4))
        ttk.Label(url_row, text=ACCESS_URL_LABELS_SL["minimax_kirkpr_page"] + ":").pack(
            anchor="w"
        )
        page_var = tk.StringVar(value=str(urls.get("minimax_kirkpr_page") or DEFAULT_MINIMAX_KIRKPR_PAGE_URL))
        self._access_url_vars["minimax_kirkpr_page"] = page_var
        ttk.Entry(url_row, textvariable=page_var, width=72).pack(fill="x", pady=(2, 0))
        org_var = tk.BooleanVar(value=bool(urls.get("append_organisation_id", True)))
        self._access_url_vars["append_organisation_id"] = org_var
        ttk.Checkbutton(
            url_grp,
            text=ACCESS_URL_LABELS_SL["append_organisation_id"],
            variable=org_var,
        ).pack(anchor="w", pady=(4, 0))

        for service in ACCESS_SERVICES:
            grp = ttk.Labelframe(
                body,
                text=ACCESS_SERVICE_LABELS_SL.get(service, service),
                padding=8,
            )
            grp.pack(fill="x", anchor="w", pady=(0, 10))
            svc_vars: Dict[str, tk.BooleanVar] = {}
            for flag in ACCESS_FLAGS:
                var = tk.BooleanVar(value=bool(access.get(service, {}).get(flag, False)))
                svc_vars[flag] = var
                ttk.Checkbutton(
                    grp,
                    text=ACCESS_FLAG_LABELS_SL.get(flag, flag),
                    variable=var,
                ).pack(anchor="w", pady=2)
            self._access_vars[service] = svc_vars

        ttk.Button(
            body,
            text="Ponastavi dostop",
            command=self._reset_access_defaults,
        ).pack(anchor="w", pady=(4, 0))

    def _build_links_tab(self, body: ttk.Frame) -> None:
        links = normalize_edavki_links_config(self._links_working)
        self._links_working = links

        ttk.Label(
            body,
            text=(
                "Povezave eDavki (combo v levem panelu). Enako kot list «internet» v Evidence podjetij "
                "(SQL dbo.RefInternetLink). Pot je relativna na EdavkiPortal/[DURS]/ ali polni URL."
            ),
            wraplength=520,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        sql_frm = ttk.Labelframe(body, text="SQL (EvidencaFirm)", padding=8)
        sql_frm.pack(fill="x", anchor="w", pady=(0, 10))
        ttk.Label(sql_frm, text="Pot do config.json:").pack(anchor="w")
        ttk.Entry(sql_frm, textvariable=self._sql_config_var, width=72).pack(fill="x", pady=(2, 6))
        sql_btns = ttk.Frame(sql_frm)
        sql_btns.pack(fill="x")
        ttk.Button(
            sql_btns,
            text="Naloži iz SQL (RefInternetLink)",
            command=self._load_links_from_sql_ui,
        ).pack(side="left")
        ttk.Checkbutton(
            sql_frm,
            text="Osveži iz SQL ob zagonu",
            variable=self._refresh_sql_on_startup_var,
        ).pack(anchor="w", pady=(6, 0))

        hdr = ttk.Frame(body)
        hdr.pack(fill="x", pady=(0, 4))
        ttk.Label(hdr, text="Naziv", width=34).pack(side="left", padx=(0, 4))
        ttk.Label(hdr, text="Pot / URL", width=36).pack(side="left", padx=(0, 4))
        ttk.Label(hdr, text="Param.", width=14).pack(side="left", padx=(0, 4))
        ttk.Label(hdr, text="Opomba", width=18).pack(side="left")

        self._links_rows_host = ttk.Frame(body)
        self._links_rows_host.pack(fill="x", anchor="w")
        self._link_row_vars = []
        for row in links.get("links") or []:
            self._append_link_row(row)

        row_btns = ttk.Frame(body)
        row_btns.pack(anchor="w", pady=(8, 0))
        ttk.Button(row_btns, text="Dodaj vrstico", command=self._add_empty_link_row).pack(side="left")
        ttk.Button(
            row_btns,
            text="Ponastavi privzete povezave",
            command=self._reset_links_defaults,
        ).pack(side="left", padx=(8, 0))

    def _append_link_row(self, row: Dict[str, Any]) -> None:
        if self._links_rows_host is None:
            return
        frm = ttk.Frame(self._links_rows_host)
        frm.pack(fill="x", pady=2)
        label_var = tk.StringVar(value=str(row.get("label") or ""))
        path_var = tk.StringVar(value=str(row.get("path") or ""))
        col_c_var = tk.StringVar(value=str(row.get("col_c") or ""))
        col_d_var = tk.StringVar(value=str(row.get("col_d") or ""))
        enabled_var = tk.BooleanVar(value=bool(row.get("enabled", True)))
        ttk.Checkbutton(frm, variable=enabled_var).pack(side="left", padx=(0, 4))
        ttk.Entry(frm, textvariable=label_var, width=34).pack(side="left", padx=(0, 4))
        ttk.Entry(frm, textvariable=path_var, width=36).pack(side="left", padx=(0, 4))
        ttk.Entry(frm, textvariable=col_c_var, width=14).pack(side="left", padx=(0, 4))
        ttk.Entry(frm, textvariable=col_d_var, width=18).pack(side="left", padx=(0, 4))

        def _remove() -> None:
            self._link_row_vars = [x for x in self._link_row_vars if x.get("frame") is not frm]
            frm.destroy()

        ttk.Button(frm, text="✕", width=3, command=_remove).pack(side="left")
        self._link_row_vars.append(
            {
                "frame": frm,
                "label": label_var,
                "path": path_var,
                "col_c": col_c_var,
                "col_d": col_d_var,
                "enabled": enabled_var,
            }
        )

    def _add_empty_link_row(self) -> None:
        self._append_link_row(
            {
                "label": "Nova povezava",
                "path": "/PersonalPortal/",
                "col_c": "",
                "col_d": "",
                "enabled": True,
            }
        )

    def _reset_links_defaults(self) -> None:
        if self._links_rows_host is None:
            return
        for child in self._links_rows_host.winfo_children():
            child.destroy()
        self._link_row_vars = []
        for row in DEFAULT_EDAVKI_LINKS:
            self._append_link_row(copy.deepcopy(row))

    def _collect_links(self) -> Dict[str, Any]:
        rows: List[Dict[str, Any]] = []
        for idx, item in enumerate(self._link_row_vars, 1):
            label = str(item["label"].get()).strip()
            if not label:
                continue
            rows.append(
                {
                    "sort_order": idx,
                    "label": label,
                    "path": str(item["path"].get()).strip(),
                    "col_c": str(item["col_c"].get()).strip(),
                    "col_d": str(item["col_d"].get()).strip(),
                    "enabled": bool(item["enabled"].get()),
                }
            )
        raw = {
            "sql_config_path": str(self._sql_config_var.get()).strip(),
            "refresh_from_sql_on_startup": bool(self._refresh_sql_on_startup_var.get()),
            "links": rows,
        }
        return normalize_edavki_links_config(raw)

    def _load_links_from_sql_ui(self) -> None:
        try:
            cfg = self._collect_links()
            cfg["sql_config_path"] = str(self._sql_config_var.get()).strip()
            cs = resolve_sql_connection_string(cfg)
            rows = load_links_from_sql(cs)
        except Exception as exc:
            messagebox.showerror("SQL povezave", str(exc), parent=self)
            return
        if self._links_rows_host is None:
            return
        for child in self._links_rows_host.winfo_children():
            child.destroy()
        self._link_row_vars = []
        for row in rows:
            self._append_link_row(row)
        self._status_var.set(f"Naloženo iz SQL: {len(rows)} povezav.")

    def _save_links_and_refresh_combo(self) -> None:
        links = self._collect_links()
        save_edavki_links_to_disk(links)
        self._links_working = copy.deepcopy(links)
        if hasattr(self.app, "_reload_edavki_links_config"):
            self.app._reload_edavki_links_config()

    def _build_behavior_tab(self, body: ttk.Frame) -> None:
        ui = normalize_ui_dict(self._working.get("ui"))
        self._working["ui"] = ui

        ttk.Label(
            body,
            text="Interakcije v glavnem oknu. Spremembe veljajo takoj po Shrani ali Uporabi.",
            wraplength=480,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        for key in UI_OPTION_KEYS:
            var = tk.BooleanVar(value=bool(ui.get(key, DEFAULT_UI.get(key, False))))
            self._ui_option_vars[key] = var
            ttk.Checkbutton(
                body,
                text=UI_OPTION_LABELS_SL.get(key, key),
                variable=var,
            ).pack(anchor="w", pady=4)

        ttk.Button(
            body,
            text="Ponastavi vedenje",
            command=self._reset_behavior_defaults,
        ).pack(anchor="w", pady=(12, 0))

    def _reset_behavior_defaults(self) -> None:
        for key in UI_OPTION_KEYS:
            if key in self._ui_option_vars:
                self._ui_option_vars[key].set(DEFAULT_UI[key])

    def _build_file_compare_tab(self, body: ttk.Frame) -> None:
        ttk.Label(
            body,
            text=(
                "Definiraj primerjave datotek po imenu, knjigi in paru datotek. "
                "Podprto: ZIP, XML, CSV, Excel (auto / analiza Mesečno+Dnevno / mesečno / dnevno). "
                "Pot podpira predloge {yyyy}, {mm}, {yyyymm}, {yyyy-mm}."
            ),
            wraplength=560,
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        hdr = ttk.Frame(body)
        hdr.pack(fill="x", pady=(0, 4))
        ttk.Label(hdr, text="Akt.", width=4).pack(side="left")
        ttk.Label(hdr, text="Naziv", width=22).pack(side="left", padx=(0, 4))
        ttk.Label(hdr, text="Knjiga", width=10).pack(side="left", padx=(0, 4))
        ttk.Label(hdr, text="Leva datoteka", width=34).pack(side="left", padx=(0, 4))
        ttk.Label(hdr, text="Desna datoteka", width=34).pack(side="left", padx=(0, 4))

        self._file_compare_rows_host = ttk.Frame(body)
        self._file_compare_rows_host.pack(fill="x", anchor="w")
        self._file_compare_row_vars = []
        cfg = normalize_file_compare_settings(self._file_compare_working)
        self._file_compare_working = cfg
        for row in cfg.get("definitions", []):
            self._append_file_compare_row(row)

        btns = ttk.Frame(body)
        btns.pack(anchor="w", pady=(8, 0))
        ttk.Button(btns, text="Dodaj primerjavo", command=self._add_empty_file_compare_row).pack(side="left")
        ttk.Button(btns, text="Podvoji izbrano", command=self._duplicate_file_compare_row).pack(side="left", padx=(8, 0))
        ttk.Button(
            btns,
            text="Ponastavi privzete primerjave",
            command=self._reset_file_compare_defaults,
        ).pack(side="left", padx=(8, 0))

    def _file_compare_refresh_sheet_names(
        self,
        path_var: tk.StringVar,
        sheet_var: tk.StringVar,
        sheet_combo: ttk.Combobox,
    ) -> None:
        import DavcnaBlagajna as core

        raw_path = str(path_var.get() or "").strip()
        if not raw_path:
            return
        try:
            names = core.list_excel_workbook_sheet_names(Path(raw_path))
        except Exception as exc:
            messagebox.showwarning("Excel listi", str(exc), parent=self)
            return
        sheet_combo.configure(values=names)
        if names and not str(sheet_var.get() or "").strip():
            sheet_var.set(names[0])

    def _file_compare_browse_excel(
        self,
        path_var: tk.StringVar,
        format_var: tk.StringVar,
        sheet_var: tk.StringVar,
        sheet_combo: ttk.Combobox,
    ) -> None:
        picked = filedialog.askopenfilename(
            parent=self,
            title="Izberi Excel datoteko",
            filetypes=[
                ("Excel", "*.xlsx;*.xlsm"),
                ("Vse datoteke", "*.*"),
            ],
        )
        if not picked:
            return
        path_var.set(picked)
        format_var.set("excel")
        self._file_compare_refresh_sheet_names(path_var, sheet_var, sheet_combo)

    def _append_file_compare_row(self, row: Dict[str, Any]) -> None:
        if self._file_compare_rows_host is None:
            return
        norm = normalize_file_compare_settings({"definitions": [row]}).get("definitions", [])[0]
        frm = ttk.Labelframe(self._file_compare_rows_host, text=str(norm.get("name") or "Primerjava"), padding=6)
        frm.pack(fill="x", pady=4)

        enabled_var = tk.BooleanVar(value=bool(norm.get("enabled", True)))
        selected_var = tk.BooleanVar(value=bool(norm.get("selected", False)))
        name_var = tk.StringVar(value=str(norm.get("name") or ""))
        book_var = tk.StringVar(value=str(norm.get("book") or "KIR"))
        label_a_var = tk.StringVar(value=str(norm.get("label_a") or ""))
        label_b_var = tk.StringVar(value=str(norm.get("label_b") or ""))

        left = dict(norm.get("left") or {})
        right = dict(norm.get("right") or {})
        left_source = tk.StringVar(value=str(left.get("source") or "blagajna"))
        left_kind = tk.StringVar(value=str(left.get("kind") or "edavki_kirkpr_zip"))
        left_format = tk.StringVar(value=str(left.get("format") or "auto"))
        left_path = tk.StringVar(value=str(left.get("path") or ""))
        left_sheet = tk.StringVar(value=str(left.get("sheet") or ""))
        left_excel_mode = tk.StringVar(value=str(left.get("excel_mode") or "auto"))
        right_source = tk.StringVar(value=str(right.get("source") or "ddv"))
        right_kind = tk.StringVar(value=str(right.get("kind") or "minimax_kirkpr_xml"))
        right_format = tk.StringVar(value=str(right.get("format") or "auto"))
        right_path = tk.StringVar(value=str(right.get("path") or ""))
        right_sheet = tk.StringVar(value=str(right.get("sheet") or ""))
        right_excel_mode = tk.StringVar(value=str(right.get("excel_mode") or "auto"))

        top = ttk.Frame(frm)
        top.pack(fill="x", pady=(0, 4))
        ttk.Checkbutton(top, variable=enabled_var).pack(side="left")
        ttk.Checkbutton(top, text="privzeto označi", variable=selected_var).pack(side="left", padx=(0, 8))
        ttk.Entry(top, textvariable=name_var, width=26).pack(side="left", padx=(0, 8))
        ttk.Combobox(
            top,
            textvariable=book_var,
            values=list(FILE_COMPARE_BOOKS),
            state="readonly",
            width=12,
        ).pack(side="left")

        name_var.trace_add("write", lambda *_a: frm.configure(text=str(name_var.get()).strip() or "Primerjava"))

        mid = ttk.Frame(frm)
        mid.pack(fill="x", pady=(0, 4))
        ttk.Label(mid, text="Leva oznaka:", width=12).pack(side="left")
        ttk.Entry(mid, textvariable=label_a_var, width=18).pack(side="left", padx=(0, 8))
        ttk.Label(mid, text="Desna oznaka:", width=12).pack(side="left")
        ttk.Entry(mid, textvariable=label_b_var, width=18).pack(side="left")

        left_sheet_combo = ttk.Combobox(frm, textvariable=left_sheet, values=[], width=18)
        right_sheet_combo = ttk.Combobox(frm, textvariable=right_sheet, values=[], width=18)

        def _build_side_block(
            parent: ttk.Frame,
            title: str,
            source_var: tk.StringVar,
            kind_var: tk.StringVar,
            format_var: tk.StringVar,
            path_var: tk.StringVar,
            sheet_var: tk.StringVar,
            excel_mode_var: tk.StringVar,
            sheet_combo: ttk.Combobox,
        ) -> None:
            row_frm = ttk.Frame(parent)
            row_frm.pack(fill="x", pady=2)
            ttk.Label(row_frm, text=title, width=10).pack(side="left")
            ttk.Combobox(
                row_frm,
                textvariable=source_var,
                values=list(FILE_COMPARE_SOURCES),
                state="readonly",
                width=13,
            ).pack(side="left", padx=(0, 4))
            ttk.Combobox(
                row_frm,
                textvariable=kind_var,
                values=list(FILE_COMPARE_KINDS),
                state="readonly",
                width=21,
            ).pack(side="left", padx=(0, 4))
            ttk.Combobox(
                row_frm,
                textvariable=format_var,
                values=list(FILE_COMPARE_FORMATS),
                state="readonly",
                width=10,
            ).pack(side="left", padx=(0, 4))
            ttk.Entry(row_frm, textvariable=path_var, width=28).pack(side="left", fill="x", expand=True, padx=(0, 4))
            ttk.Button(
                row_frm,
                text="…",
                width=3,
                command=lambda: self._file_compare_browse_excel(path_var, format_var, sheet_var, sheet_combo),
            ).pack(side="left")

            excel_frm = ttk.Frame(parent)
            excel_frm.pack(fill="x", pady=(0, 2), padx=(10, 0))
            ttk.Label(excel_frm, text="Excel:", width=10).pack(side="left")
            ttk.Combobox(
                excel_frm,
                textvariable=excel_mode_var,
                values=list(FILE_COMPARE_EXCEL_MODES),
                state="readonly",
                width=14,
            ).pack(side="left", padx=(0, 6))
            ttk.Label(excel_frm, text="List:").pack(side="left")
            sheet_combo.pack(in_=excel_frm, side="left", padx=(4, 4))
            ttk.Button(
                excel_frm,
                text="Osveži liste",
                command=lambda: self._file_compare_refresh_sheet_names(path_var, sheet_var, sheet_combo),
            ).pack(side="left")

        _build_side_block(
            frm, "Leva:", left_source, left_kind, left_format, left_path, left_sheet, left_excel_mode, left_sheet_combo
        )
        _build_side_block(
            frm,
            "Desna:",
            right_source,
            right_kind,
            right_format,
            right_path,
            right_sheet,
            right_excel_mode,
            right_sheet_combo,
        )

        if str(left_path.get() or "").lower().endswith((".xlsx", ".xlsm")):
            self._file_compare_refresh_sheet_names(left_path, left_sheet, left_sheet_combo)
        if str(right_path.get() or "").lower().endswith((".xlsx", ".xlsm")):
            self._file_compare_refresh_sheet_names(right_path, right_sheet, right_sheet_combo)

        def _strip_combo_value(var: tk.StringVar, valid: tuple[str, ...], default: str) -> str:
            raw = str(var.get() or "").strip().lower()
            if default.isupper():
                raw = raw.upper()
            if raw not in valid:
                return default
            return raw

        def _remove() -> None:
            self._file_compare_row_vars = [x for x in self._file_compare_row_vars if x.get("frame") is not frm]
            frm.destroy()

        row_item = {
            "frame": frm,
            "enabled": enabled_var,
            "selected": selected_var,
            "name": name_var,
            "book": book_var,
            "label_a": label_a_var,
            "label_b": label_b_var,
            "left_source": left_source,
            "left_kind": left_kind,
            "left_format": left_format,
            "left_path": left_path,
            "left_sheet": left_sheet,
            "left_excel_mode": left_excel_mode,
            "right_source": right_source,
            "right_kind": right_kind,
            "right_format": right_format,
            "right_path": right_path,
            "right_sheet": right_sheet,
            "right_excel_mode": right_excel_mode,
            "strip_combo": _strip_combo_value,
            "definition": copy.deepcopy(norm),
        }

        def _duplicate_self() -> None:
            dup = copy.deepcopy(row_item.get("definition") or norm)
            dup["name"] = f"{str(dup.get('name') or 'Primerjava')} (kopija)"
            dup["selected"] = False
            self._append_file_compare_row(dup)

        ttk.Button(top, text="⧉", width=3, command=_duplicate_self).pack(side="right", padx=(0, 4))
        ttk.Button(top, text="✕", width=3, command=_remove).pack(side="right")
        self._file_compare_row_vars.append(row_item)

    def _duplicate_file_compare_row(self) -> None:
        if not self._file_compare_row_vars:
            messagebox.showinfo("Primerjave datotek", "Ni vrstice za podvojitev.", parent=self)
            return
        item = self._file_compare_row_vars[-1]
        strip_combo = item["strip_combo"]
        base = {
            "name": f"{str(item['name'].get()).strip()} (kopija)",
            "enabled": bool(item["enabled"].get()),
            "selected": False,
            "book": strip_combo(item["book"], FILE_COMPARE_BOOKS, "KIR"),
            "label_a": str(item["label_a"].get()).strip(),
            "label_b": str(item["label_b"].get()).strip(),
            "left": {
                "source": strip_combo(item["left_source"], FILE_COMPARE_SOURCES, "blagajna"),
                "kind": strip_combo(item["left_kind"], FILE_COMPARE_KINDS, "edavki_kirkpr_zip"),
                "format": strip_combo(item["left_format"], FILE_COMPARE_FORMATS, "auto"),
                "path": str(item["left_path"].get()).strip(),
                "sheet": str(item["left_sheet"].get()).strip(),
                "excel_mode": strip_combo(item["left_excel_mode"], FILE_COMPARE_EXCEL_MODES, "auto"),
            },
            "right": {
                "source": strip_combo(item["right_source"], FILE_COMPARE_SOURCES, "ddv"),
                "kind": strip_combo(item["right_kind"], FILE_COMPARE_KINDS, "minimax_kirkpr_xml"),
                "format": strip_combo(item["right_format"], FILE_COMPARE_FORMATS, "auto"),
                "path": str(item["right_path"].get()).strip(),
                "sheet": str(item["right_sheet"].get()).strip(),
                "excel_mode": strip_combo(item["right_excel_mode"], FILE_COMPARE_EXCEL_MODES, "auto"),
            },
        }
        self._append_file_compare_row(base)

    def _add_empty_file_compare_row(self) -> None:
        self._append_file_compare_row(
            {
                "name": "Nova primerjava",
                "enabled": True,
                "selected": False,
                "book": "KIR",
                "label_a": "Leva",
                "label_b": "Desna",
                "left": {
                    "source": "blagajna",
                    "kind": "edavki_kirkpr_zip",
                    "format": "zip",
                    "path": "",
                    "sheet": "",
                    "excel_mode": "auto",
                },
                "right": {
                    "source": "ddv",
                    "kind": "minimax_kirkpr_xml",
                    "format": "xml",
                    "path": "",
                    "sheet": "",
                    "excel_mode": "auto",
                },
            }
        )

    def _reset_file_compare_defaults(self) -> None:
        if self._file_compare_rows_host is None:
            return
        for child in self._file_compare_rows_host.winfo_children():
            child.destroy()
        self._file_compare_row_vars = []
        for row in DEFAULT_FILE_COMPARE_DEFINITIONS:
            self._append_file_compare_row(copy.deepcopy(row))
        self._status_var.set("Primerjave datotek ponastavljene.")

    def _collect_file_compare_settings(self) -> Dict[str, Any]:
        defs: List[Dict[str, Any]] = []
        for item in self._file_compare_row_vars:
            name = str(item["name"].get()).strip()
            if not name:
                continue
            strip_combo = item["strip_combo"]
            defs.append(
                {
                    "name": name,
                    "enabled": bool(item["enabled"].get()),
                    "selected": bool(item["selected"].get()),
                    "book": strip_combo(item["book"], FILE_COMPARE_BOOKS, "KIR"),
                    "label_a": str(item["label_a"].get()).strip(),
                    "label_b": str(item["label_b"].get()).strip(),
                    "left": {
                        "source": strip_combo(item["left_source"], FILE_COMPARE_SOURCES, "blagajna"),
                        "kind": strip_combo(item["left_kind"], FILE_COMPARE_KINDS, "edavki_kirkpr_zip"),
                        "format": strip_combo(item["left_format"], FILE_COMPARE_FORMATS, "auto"),
                        "path": str(item["left_path"].get()).strip(),
                        "sheet": str(item["left_sheet"].get()).strip(),
                        "excel_mode": strip_combo(item["left_excel_mode"], FILE_COMPARE_EXCEL_MODES, "auto"),
                    },
                    "right": {
                        "source": strip_combo(item["right_source"], FILE_COMPARE_SOURCES, "ddv"),
                        "kind": strip_combo(item["right_kind"], FILE_COMPARE_KINDS, "minimax_kirkpr_xml"),
                        "format": strip_combo(item["right_format"], FILE_COMPARE_FORMATS, "auto"),
                        "path": str(item["right_path"].get()).strip(),
                        "sheet": str(item["right_sheet"].get()).strip(),
                        "excel_mode": strip_combo(item["right_excel_mode"], FILE_COMPARE_EXCEL_MODES, "auto"),
                    },
                }
            )
        return normalize_file_compare_settings({"definitions": defs})

    def _save_file_compare_settings_ui(self) -> None:
        cfg = self._collect_file_compare_settings()
        save_file_compare_settings_to_disk(cfg)
        self._file_compare_working = copy.deepcopy(cfg)
        if hasattr(self.app, "_rebuild_v21_file_compare_presets"):
            self.app._rebuild_v21_file_compare_presets()

    def _knjizba_field_list(self) -> List[Dict[str, Any]]:
        fields_key = knjizba_form_fields_key(self._knjizba_book.get())
        fields = self._knjizba_working.get(fields_key)
        if not isinstance(fields, list):
            return []
        return [f for f in fields if isinstance(f, dict)]

    def _knjizba_on_book_change(self, _event: Any = None) -> None:
        if getattr(self, "_knjizba_last_selected", None):
            self._knjizba_apply_detail_to_field(
                self._knjizba_last_selected, include_position=False
            )
        self._knjizba_last_selected = None
        self._refresh_knjizba_tree()
        self._knjizba_load_detail_from_field(None)
        if self._knjizba_designer is not None:
            self._knjizba_designer.refresh()

    def _knjizba_get_fields_copy(self) -> List[Dict[str, Any]]:
        key = knjizba_form_fields_key(self._knjizba_book.get())
        raw = self._knjizba_working.get(key)
        if not isinstance(raw, list):
            return []
        return [copy.deepcopy(f) for f in raw if isinstance(f, dict)]

    def _knjizba_set_fields_copy(self, fields: List[Dict[str, Any]]) -> None:
        key = knjizba_form_fields_key(self._knjizba_book.get())
        self._knjizba_working[key] = copy.deepcopy(fields)

    def _knjizba_on_designer_changed(self) -> None:
        self._refresh_knjizba_tree()
        key: Optional[str] = None
        if self._knjizba_designer is not None:
            key = self._knjizba_designer.selected_key()
        if not key:
            key = self._knjizba_selected_key()
        if key:
            self._knjizba_last_selected = key
            self._knjizba_load_detail_from_field(key)

    def _knjizba_on_designer_select(self, key: Optional[str]) -> None:
        if not key or self._knjizba_tree is None:
            return
        if self._knjizba_tree.exists(key):
            if getattr(self, "_knjizba_last_selected", None):
                self._knjizba_apply_detail_to_field(
                    self._knjizba_last_selected, include_position=False
                )
            self._knjizba_tree.selection_set(key)
            self._knjizba_tree.focus(key)
            self._knjizba_tree.see(key)
            self._knjizba_last_selected = key
            self._knjizba_load_detail_from_field(key)

    def _knjizba_selected_key(self) -> Optional[str]:
        if self._knjizba_tree is None:
            return None
        sel = self._knjizba_tree.selection()
        if not sel:
            return None
        return str(sel[0])

    def _knjizba_find_field(self, key: str) -> Optional[Dict[str, Any]]:
        for item in self._knjizba_field_list():
            if str(item.get("key")) == key:
                return item
        return None

    def _knjizba_apply_detail_to_field(
        self, key: Optional[str], *, include_position: bool = True
    ) -> None:
        if not key:
            return
        item = self._knjizba_find_field(key)
        if item is None:
            return
        item["visible"] = bool(self._knjizba_sel_visible.get())
        item["label"] = str(self._knjizba_sel_label.get()).strip()
        if include_position:
            try:
                item["row"] = int(self._knjizba_sel_row.get())
            except (TypeError, ValueError):
                item["row"] = -1
            col_raw = str(self._knjizba_sel_col.get()).strip()
            if col_raw in {"0", "1"}:
                item["col"] = int(col_raw)
            else:
                item["col"] = -1
        try:
            item["entry_width"] = max(0, min(80, int(self._knjizba_sel_entry_w.get())))
        except (TypeError, ValueError):
            item["entry_width"] = 0

    def _knjizba_load_detail_from_field(self, key: Optional[str]) -> None:
        item = self._knjizba_find_field(key) if key else None
        if item is None:
            self._knjizba_sel_visible.set(True)
            self._knjizba_sel_label.set("")
            self._knjizba_sel_row.set(-1)
            self._knjizba_sel_col.set("-1")
            self._knjizba_sel_entry_w.set(0)
            return
        default_label = knjizba_form_catalog_for_book(self._knjizba_book.get()).get(
            str(item.get("key")), (str(item.get("key")), "")
        )[0]
        self._knjizba_sel_visible.set(bool(item.get("visible", True)))
        self._knjizba_sel_label.set(str(item.get("label") or ""))
        self._knjizba_sel_row.set(int(item.get("row", -1) or -1))
        col = int(item.get("col", -1) or -1)
        self._knjizba_sel_col.set(str(col) if col in (0, 1) else "-1")
        try:
            self._knjizba_sel_entry_w.set(int(item.get("entry_width") or 0))
        except (TypeError, ValueError):
            self._knjizba_sel_entry_w.set(0)
        if not self._knjizba_sel_label.get().strip():
            self._knjizba_sel_label.set("")

    def _refresh_knjizba_tree(self) -> None:
        if self._knjizba_tree is None:
            return
        selected = self._knjizba_selected_key()
        for iid in self._knjizba_tree.get_children():
            self._knjizba_tree.delete(iid)
        catalog = knjizba_form_catalog_for_book(self._knjizba_book.get())
        for item in self._knjizba_field_list():
            key = str(item.get("key") or "")
            if key not in catalog:
                continue
            default_label = catalog[key][0]
            custom = str(item.get("label") or "").strip()
            label = custom or default_label
            visible = "Da" if bool(item.get("visible", True)) else "Ne"
            row = item.get("row", -1)
            col = item.get("col", -1)
            pos = ""
            if int(row or -1) >= 0:
                pos = f"vrstica {row}"
                if int(col or -1) in (0, 1):
                    pos += f", stolpec {col}"
            self._knjizba_tree.insert("", "end", iid=key, values=(visible, key, label, pos))
        if selected and self._knjizba_tree.exists(selected):
            self._knjizba_tree.selection_set(selected)
            self._knjizba_tree.focus(selected)

    def _knjizba_on_tree_select(self, _event: Any = None) -> None:
        prev = getattr(self, "_knjizba_last_selected", None)
        if prev:
            self._knjizba_apply_detail_to_field(prev, include_position=False)
        key = self._knjizba_selected_key()
        self._knjizba_last_selected = key
        self._knjizba_load_detail_from_field(key)

    def _knjizba_toggle_visible(self) -> None:
        key = self._knjizba_selected_key()
        if not key:
            return
        item = self._knjizba_find_field(key)
        if item is None:
            return
        item["visible"] = not bool(item.get("visible", True))
        self._knjizba_load_detail_from_field(key)
        self._refresh_knjizba_tree()
        self._knjizba_designer_refresh_safe()

    def _knjizba_move_field(self, delta: int) -> None:
        key = self._knjizba_selected_key()
        if not key:
            return
        self._knjizba_apply_detail_to_field(key)
        fields = self._knjizba_field_list()
        idx = next((i for i, f in enumerate(fields) if str(f.get("key")) == key), -1)
        if idx < 0:
            return
        new_idx = idx + delta
        if new_idx < 0 or new_idx >= len(fields):
            return
        fields[idx], fields[new_idx] = fields[new_idx], fields[idx]
        self._knjizba_working[knjizba_form_fields_key(self._knjizba_book.get())] = fields
        self._knjizba_designer_refresh_safe()
        self._refresh_knjizba_tree()
        if self._knjizba_tree is not None:
            self._knjizba_tree.selection_set(key)

    def _knjizba_apply_detail(self) -> None:
        key = self._knjizba_selected_key()
        self._knjizba_apply_detail_to_field(key, include_position=True)
        self._refresh_knjizba_tree()
        self._knjizba_designer_refresh_safe()
        self._status_var.set("Polje posodobljeno.")

    def _knjizba_set_column(self, col: int) -> None:
        key = self._knjizba_selected_key()
        if not key:
            return
        if int(self._knjizba_columns.get() or 1) < 2:
            self._status_var.set("Za dva stolpca nastavi «Število stolpcev» = 2.")
            return
        item = self._knjizba_find_field(key)
        if item is None:
            return
        row = int(item.get("row", -1) or -1)
        if row < 0:
            row = 0
            item["row"] = row
        item["col"] = col
        self._knjizba_sel_col.set(str(col))
        self._knjizba_sel_row.set(row)
        self._refresh_knjizba_tree()
        self._knjizba_designer_refresh_safe()
        self._status_var.set(f"Polje {key} → stolpec {col}.")

    def _knjizba_sync_globals_to_working(self) -> None:
        self._knjizba_working["dialog_width"] = int(self._knjizba_dialog_w.get())
        self._knjizba_working["dialog_height"] = int(self._knjizba_dialog_h.get())
        self._knjizba_working["label_width"] = int(self._knjizba_label_w.get())
        self._knjizba_working["entry_width"] = int(self._knjizba_entry_w.get())
        self._knjizba_working["columns"] = int(self._knjizba_columns.get())
        self._knjizba_working["show_api_summary"] = bool(self._knjizba_show_summary.get())

    def _collect_knjizba_form_layout(self) -> Dict[str, Any]:
        if getattr(self, "_knjizba_last_selected", None):
            self._knjizba_apply_detail_to_field(
                self._knjizba_last_selected, include_position=False
            )
        self._knjizba_sync_globals_to_working()
        return normalize_knjizba_form_layout(self._knjizba_working)

    def _reset_knjizba_form_defaults(self) -> None:
        book = (self._knjizba_book.get() or "KIR").strip().upper()
        defaults = copy.deepcopy(DEFAULT_KNJIZBA_FORM_LAYOUT)
        if book == "KPR":
            self._knjizba_working["fields_kpr"] = copy.deepcopy(defaults["fields_kpr"])
        else:
            self._knjizba_working["fields_kir"] = copy.deepcopy(defaults["fields_kir"])
        self._knjizba_dialog_w.set(int(self._knjizba_working["dialog_width"]))
        self._knjizba_dialog_h.set(int(self._knjizba_working["dialog_height"]))
        self._knjizba_label_w.set(int(self._knjizba_working["label_width"]))
        self._knjizba_entry_w.set(int(self._knjizba_working["entry_width"]))
        self._knjizba_columns.set(int(self._knjizba_working["columns"]))
        self._knjizba_show_summary.set(bool(self._knjizba_working["show_api_summary"]))
        self._knjizba_last_selected = None
        self._refresh_knjizba_tree()
        self._knjizba_load_detail_from_field(None)
        self._knjizba_designer_refresh_safe()
        self._status_var.set("Postavitev knjižbe ponastavljena.")

    def _knjizba_bump_int(self, var: tk.IntVar, lo: int, hi: int, delta: int) -> None:
        try:
            val = int(var.get())
        except (TypeError, ValueError, tk.TclError):
            val = lo
        var.set(max(lo, min(hi, val + delta)))

    def _knjizba_spin_row(
        self,
        parent: ttk.Frame,
        row: int,
        label: str,
        var: tk.IntVar,
        lo: int,
        hi: int,
        *,
        step: int = 1,
    ) -> None:
        ttk.Label(parent, text=f"{label}:").grid(row=row, column=0, sticky="w", pady=2)
        row_frm = ttk.Frame(parent)
        row_frm.grid(row=row, column=1, sticky="w", padx=(6, 0), pady=2)
        ttk.Spinbox(row_frm, from_=lo, to=hi, textvariable=var, width=8).pack(side="left")
        ttk.Button(
            row_frm,
            text="−",
            width=3,
            command=lambda: self._knjizba_bump_int(var, lo, hi, -step),
        ).pack(side="left", padx=(6, 2))
        ttk.Button(
            row_frm,
            text="+",
            width=3,
            command=lambda: self._knjizba_bump_int(var, lo, hi, step),
        ).pack(side="left")

    def _build_knjizba_form_tab(self, body: ttk.Frame) -> None:
        ttk.Label(
            body,
            text=(
                "Obrazec Minimax knjižbe (dvojni klik ali gumb «Dodaj nov zapis»). "
                "KIR = izdani računi, KPR = prejeti računi. "
                "Širino in višino okna nastavi v «Okno in mreža» spodaj."
            ),
            wraplength=640,
            justify="left",
        ).pack(anchor="w", pady=(0, 10))

        book_row = ttk.Frame(body)
        book_row.pack(fill="x", pady=(0, 8))
        ttk.Label(book_row, text="Knjiga:").pack(side="left")
        book_cb = ttk.Combobox(
            book_row,
            textvariable=self._knjizba_book,
            values=("KIR", "KPR"),
            state="readonly",
            width=8,
        )
        book_cb.pack(side="left", padx=(6, 0))
        book_cb.bind("<<ComboboxSelected>>", self._knjizba_on_book_change)

        def _build_glob_panel(glob: ttk.Frame) -> None:
            for r, (label, var, lo, hi) in enumerate(
                (
                    ("Širina okna (px)", self._knjizba_dialog_w, 480, 1400),
                    ("Višina okna (px)", self._knjizba_dialog_h, 360, 1000),
                    ("Širina oznake", self._knjizba_label_w, 8, 40),
                    ("Širina vnosa", self._knjizba_entry_w, 12, 80),
                )
            ):
                self._knjizba_spin_row(glob, r, label, var, lo, hi, step=2 if "okna" in label else 1)
            ttk.Label(glob, text="Število stolpcev:").grid(row=4, column=0, sticky="w", pady=2)
            ttk.Combobox(
                glob,
                textvariable=self._knjizba_columns,
                values=(1, 2),
                state="readonly",
                width=6,
            ).grid(row=4, column=1, sticky="w", padx=(6, 0), pady=2)
            ttk.Checkbutton(
                glob,
                text="Prikaži povzetek API (DDV / plačila)",
                variable=self._knjizba_show_summary,
            ).grid(row=5, column=0, columnspan=2, sticky="w", pady=(6, 0))

        wrap_collapsible_labelframe(
            body,
            "Okno in mreža — širina / višina obrazca",
            _build_glob_panel,
            self,
            "_knjizba_panel_glob_collapsed",
            collapsed_default=False,
        ).pack(fill="x", pady=(0, 8))

        def _build_designer_panel(frm: ttk.Frame) -> None:
            self._knjizba_designer = KnjizbaFormDesigner(
                frm,
                get_book=lambda: self._knjizba_book.get(),
                get_columns=lambda: int(self._knjizba_columns.get() or 1),
                get_fields=self._knjizba_get_fields_copy,
                set_fields=self._knjizba_set_fields_copy,
                get_entry_width=lambda: int(self._knjizba_entry_w.get() or 48),
                on_changed=self._knjizba_on_designer_changed,
                on_select=self._knjizba_on_designer_select,
            )
            self._knjizba_designer.pack(fill="both", expand=True)
            self._knjizba_columns.trace_add("write", lambda *_a: self._knjizba_designer_refresh_safe())

        wrap_collapsible_labelframe(
            body,
            "Vizualni designer (povleci in spusti)",
            _build_designer_panel,
            self,
            "_knjizba_panel_designer_collapsed",
            body_fill="both",
            body_expand=True,
        ).pack(fill="both", expand=False, pady=(0, 8))

        def _build_list_panel(list_frm: ttk.Frame) -> None:
            list_frm.rowconfigure(0, weight=1)
            list_frm.columnconfigure(0, weight=1)

            cols = ("visible", "key", "label", "pos")
            tree = ttk.Treeview(list_frm, columns=cols, show="headings", height=10)
            tree.heading("visible", text="Vidno")
            tree.heading("key", text="Ključ")
            tree.heading("label", text="Oznaka")
            tree.heading("pos", text="Pozicija")
            tree.column("visible", width=48, anchor="center")
            tree.column("key", width=120, anchor="w")
            tree.column("label", width=200, anchor="w")
            tree.column("pos", width=120, anchor="w")
            tree.grid(row=0, column=0, sticky="nsew")
            vsb = ttk.Scrollbar(list_frm, orient="vertical", command=tree.yview)
            vsb.grid(row=0, column=1, sticky="ns")
            tree.configure(yscrollcommand=vsb.set)
            self._knjizba_tree = tree
            self._knjizba_last_selected = None
            tree.bind("<<TreeviewSelect>>", self._knjizba_on_tree_select)
            tree.bind("<Double-1>", lambda _e: self._knjizba_toggle_visible())

            btn_row = ttk.Frame(list_frm)
            btn_row.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))
            ttk.Button(btn_row, text="↑ Gor", command=lambda: self._knjizba_move_field(-1)).pack(
                side="left", padx=(0, 4)
            )
            ttk.Button(btn_row, text="↓ Dol", command=lambda: self._knjizba_move_field(1)).pack(
                side="left", padx=(0, 4)
            )
            ttk.Button(btn_row, text="Preklopi vidno", command=self._knjizba_toggle_visible).pack(
                side="left", padx=(0, 4)
            )

        wrap_collapsible_labelframe(
            body,
            "Polja izbrane knjige (vrstni red = zgoraj navzdol)",
            _build_list_panel,
            self,
            "_knjizba_panel_list_collapsed",
            body_fill="both",
            body_expand=True,
        ).pack(fill="both", expand=True, pady=(0, 8))

        detail = ttk.LabelFrame(body, text="Izbrano polje", padding=8)
        detail.pack(fill="x", pady=(0, 8))
        ttk.Checkbutton(detail, text="Vidno v obrazcu", variable=self._knjizba_sel_visible).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=2
        )
        ttk.Label(detail, text="Oznaka (prazno = privzeto):").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(detail, textvariable=self._knjizba_sel_label, width=42).grid(
            row=1, column=1, sticky="ew", padx=(6, 0), pady=2
        )
        ttk.Label(detail, text="Vrstica (-1 = samodejno):").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Spinbox(detail, from_=-1, to=40, textvariable=self._knjizba_sel_row, width=8).grid(
            row=2, column=1, sticky="w", padx=(6, 0), pady=2
        )
        ttk.Label(detail, text="Stolpec (0 = levo, 1 = desno):").grid(row=3, column=0, sticky="w", pady=2)
        col_frm = ttk.Frame(detail)
        col_frm.grid(row=3, column=1, sticky="w", padx=(6, 0), pady=2)
        ttk.Combobox(
            col_frm,
            textvariable=self._knjizba_sel_col,
            values=("-1", "0", "1"),
            state="readonly",
            width=4,
        ).pack(side="left")
        ttk.Button(
            col_frm,
            text="← 0",
            width=4,
            command=lambda: self._knjizba_set_column(0),
        ).pack(side="left", padx=(6, 2))
        ttk.Button(
            col_frm,
            text="1 →",
            width=4,
            command=lambda: self._knjizba_set_column(1),
        ).pack(side="left")
        ttk.Label(detail, text="Širina vnosa (0 = privzeto):").grid(row=4, column=0, sticky="w", pady=2)
        ew_frm = ttk.Frame(detail)
        ew_frm.grid(row=4, column=1, sticky="w", padx=(6, 0), pady=2)
        ttk.Spinbox(ew_frm, from_=0, to=80, textvariable=self._knjizba_sel_entry_w, width=8).pack(
            side="left"
        )
        ttk.Button(
            ew_frm,
            text="−",
            width=3,
            command=lambda: self._knjizba_bump_int(self._knjizba_sel_entry_w, 0, 80, -2),
        ).pack(side="left", padx=(6, 2))
        ttk.Button(
            ew_frm,
            text="+",
            width=3,
            command=lambda: self._knjizba_bump_int(self._knjizba_sel_entry_w, 0, 80, 2),
        ).pack(side="left")
        ttk.Button(detail, text="Uporabi na polju", command=self._knjizba_apply_detail).grid(
            row=5, column=1, sticky="e", pady=(6, 0)
        )
        detail.columnconfigure(1, weight=1)

        ttk.Label(
            body,
            text=f"Shranjeno v: {KNJIZBA_FORM_FILE.name}",
            foreground="#666666",
        ).pack(anchor="w", pady=(0, 4))
        ttk.Button(body, text="Ponastavi privzeto postavitev knjige", command=self._reset_knjizba_form_defaults).pack(
            anchor="w"
        )

        self._refresh_knjizba_tree()
        self.after(50, self._knjizba_designer_refresh_safe)

    def _knjizba_designer_refresh_safe(self) -> None:
        if self._knjizba_designer is not None:
            try:
                self._knjizba_designer.refresh()
            except tk.TclError:
                pass

    def _save_knjizba_form_layout_ui(self) -> None:
        layout = self._collect_knjizba_form_layout()
        save_knjizba_form_layout_to_disk(layout)
        self._knjizba_working = copy.deepcopy(layout)

    def _reset_access_defaults(self) -> None:
        for key in ACCESS_OPTION_KEYS:
            if key in self._access_option_vars:
                self._access_option_vars[key].set(DEFAULT_ACCESS_OPTIONS[key])
        if "minimax_kirkpr_page" in self._access_url_vars:
            self._access_url_vars["minimax_kirkpr_page"].set(DEFAULT_MINIMAX_KIRKPR_PAGE_URL)
        if "append_organisation_id" in self._access_url_vars:
            self._access_url_vars["append_organisation_id"].set(
                bool(DEFAULT_ACCESS_URLS["append_organisation_id"])
            )
        for service in ACCESS_SERVICES:
            for flag in ACCESS_FLAGS:
                if service in self._access_vars and flag in self._access_vars[service]:
                    self._access_vars[service][flag].set(DEFAULT_ACCESS[service][flag])

    def _collect_access_urls(self) -> Dict[str, Any]:
        raw: Dict[str, Any] = {}
        if "minimax_kirkpr_page" in self._access_url_vars:
            raw["minimax_kirkpr_page"] = str(self._access_url_vars["minimax_kirkpr_page"].get()).strip()
        if "append_organisation_id" in self._access_url_vars:
            raw["append_organisation_id"] = bool(
                self._access_url_vars["append_organisation_id"].get()
            )
        return normalize_access_urls(raw)

    def _collect_access(self) -> Dict[str, Dict[str, bool]]:
        raw: Dict[str, Dict[str, bool]] = {}
        for service in ACCESS_SERVICES:
            raw[service] = {}
            for flag in ACCESS_FLAGS:
                raw[service][flag] = bool(self._access_vars[service][flag].get())
        return normalize_access_dict(raw)

    def _collect_access_options(self) -> Dict[str, bool]:
        raw = {key: bool(var.get()) for key, var in self._access_option_vars.items()}
        return normalize_access_options(raw)

    def _reset_border_defaults(self) -> None:
        for key in BORDER_INT_KEYS:
            if key in self._border_int_vars:
                self._border_int_vars[key].set(DEFAULT_BORDERS[key])
        for key in BORDER_COLOR_KEYS:
            if key in self._border_color_vars:
                self._border_color_vars[key].set(DEFAULT_BORDERS[key])

    def _pick_border_color(self, key: str) -> None:
        current = self._border_color_vars[key].get().strip()
        _rgb, hexval = colorchooser.askcolor(
            color=current or "#ffffff", parent=self, title=BORDER_LABELS_SL.get(key, key)
        )
        if hexval:
            self._border_color_vars[key].set(hexval.lower())

    def _sync_border_swatch(self, key: str) -> None:
        val = self._border_color_vars[key].get().strip()
        if val.startswith("#") and len(val) in (4, 7):
            try:
                self._border_swatches[key].configure(bg=val)
            except tk.TclError:
                pass

    def _reset_layout_defaults(self) -> None:
        for key in LAYOUT_KEYS:
            if key in self._layout_vars:
                self._layout_vars[key].set(DEFAULT_LAYOUT[key])

    def _pick_color(self, key: str) -> None:
        current = self._color_vars[key].get().strip()
        _rgb, hexval = colorchooser.askcolor(
            color=current or "#ffffff", parent=self, title=THEME_LABELS_SL.get(key, key)
        )
        if hexval:
            self._color_vars[key].set(hexval.lower())

    def _sync_swatch(self, key: str) -> None:
        val = self._color_vars[key].get().strip()
        if val.startswith("#") and len(val) in (4, 7):
            try:
                self._swatches[key].configure(bg=val)
            except tk.TclError:
                pass

    def _collect(self) -> Dict[str, Any]:
        colors = {}
        for key, var in self._color_vars.items():
            val = var.get().strip()
            if val.startswith("#"):
                colors[key] = val
        layout_raw = {}
        for key, var in self._layout_vars.items():
            layout_raw[key] = int(var.get())
        borders_raw: Dict[str, Any] = {}
        for key, var in self._border_color_vars.items():
            val = var.get().strip()
            if val.startswith("#"):
                borders_raw[key] = val
        for key, var in self._border_int_vars.items():
            borders_raw[key] = int(var.get())
        ui_raw = {key: bool(var.get()) for key, var in self._ui_option_vars.items()}
        return {
            "preset": "po meri",
            "font_family": self._font_family.get().strip() or "Segoe UI",
            "font_size": int(self._font_size.get()),
            "colors": {**DEFAULT_THEME["colors"], **colors},
            "layout": normalize_layout_dict(layout_raw),
            "borders": normalize_borders_dict(borders_raw),
            "ui": normalize_ui_dict(ui_raw),
        }

    def _refresh_main_window(self) -> None:
        self.app.apply_v2_theme()
        self.app.update_idletasks()

    def _apply_data(self, data: Dict[str, Any]) -> None:
        theme_data_to_class(data)
        self._refresh_main_window()
        self._working = copy.deepcopy(data)

    def _apply_preview(self) -> None:
        try:
            data = self._collect()
            access = self._collect_access()
            access_options = self._collect_access_options()
            access_urls = self._collect_access_urls()
            self._save_links_and_refresh_combo()
            self._save_file_compare_settings_ui()
            self._save_knjizba_form_layout_ui()
        except (TypeError, ValueError) as exc:
            messagebox.showerror("Napaka", str(exc), parent=self)
            return
        self._apply_data(data)
        self._access_working = copy.deepcopy(access)
        self._access_options_working = copy.deepcopy(access_options)
        self._access_urls_working = copy.deepcopy(access_urls)
        save_v2_access_to_disk(access, options=access_options, urls=access_urls)
        self._status_var.set(
            "Uporabljeno — dostop, povezave, primerjave datotek, videz in knjižba so aktivni."
        )

    def _save(self) -> None:
        try:
            data = self._collect()
            access = self._collect_access()
            access_options = self._collect_access_options()
            access_urls = self._collect_access_urls()
            links = self._collect_links()
            file_compare = self._collect_file_compare_settings()
            self._save_knjizba_form_layout_ui()
        except (TypeError, ValueError) as exc:
            messagebox.showerror("Napaka", str(exc), parent=self)
            return
        save_v2_theme_to_disk(data)
        save_v2_access_to_disk(access, options=access_options, urls=access_urls)
        save_edavki_links_to_disk(links)
        save_file_compare_settings_to_disk(file_compare)
        self._apply_data(data)
        self._access_working = copy.deepcopy(access)
        self._access_options_working = copy.deepcopy(access_options)
        self._access_urls_working = copy.deepcopy(access_urls)
        self._links_working = copy.deepcopy(links)
        self._file_compare_working = copy.deepcopy(file_compare)
        if hasattr(self.app, "_reload_edavki_links_config"):
            self.app._reload_edavki_links_config()
        if hasattr(self.app, "_rebuild_v21_file_compare_presets"):
            self.app._rebuild_v21_file_compare_presets()
        self._status_var.set("Shranjeno — glavno okno in postavitev knjižbe posodobljena.")

    def _save_close(self) -> None:
        try:
            data = self._collect()
            access = self._collect_access()
            access_options = self._collect_access_options()
            access_urls = self._collect_access_urls()
            links = self._collect_links()
            file_compare = self._collect_file_compare_settings()
            self._save_knjizba_form_layout_ui()
        except (TypeError, ValueError) as exc:
            messagebox.showerror("Napaka", str(exc), parent=self)
            return
        save_v2_theme_to_disk(data)
        save_v2_access_to_disk(access, options=access_options, urls=access_urls)
        save_edavki_links_to_disk(links)
        save_file_compare_settings_to_disk(file_compare)
        self._apply_data(data)
        if hasattr(self.app, "_reload_edavki_links_config"):
            self.app._reload_edavki_links_config()
        if hasattr(self.app, "_rebuild_v21_file_compare_presets"):
            self.app._rebuild_v21_file_compare_presets()
        self.destroy()


def open_settings_dialog(app: "AppV2") -> None:
    if getattr(app, "_v2_settings_dialog", None) is not None:
        try:
            if app._v2_settings_dialog.winfo_exists():
                app._v2_settings_dialog.lift()
                app._v2_settings_dialog.focus_force()
                return
        except tk.TclError:
            pass
    app._v2_settings_dialog = V2SettingsDialog(app)


def open_appearance_dialog(app: "AppV2") -> None:
    """Združljivost — isti dialog kot open_settings_dialog."""
    open_settings_dialog(app)
