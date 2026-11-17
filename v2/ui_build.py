"""Gradnja vmesnika 2.0 — enaka funkcionalnost kot v1, drugačen razpored."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

import DavcnaBlagajna as core
from v2 import ui_hints as H
from v2.collapsible import wrap_collapsible_labelframe
from v2.theme import V2Layout, V2Theme, bind_notebook_active_tab_style, v2_info, v2_muted
from v2.tooltip import attach_tooltip


def _reg_layout(app: core.App, key: str, widget: tk.Misc) -> None:
    if hasattr(app, "register_layout_widget"):
        app.register_layout_widget(key, widget)


def _layout_muted(app: core.App, parent: tk.Misc, text: str, **kwargs: Any) -> ttk.Label:
    wraplength = kwargs.pop("wraplength", V2Layout.help_wraplength)
    lbl = v2_muted(parent, text=text, wraplength=wraplength, **kwargs)
    _reg_layout(app, "help_wraplength", lbl)
    return lbl


def _tip(widget: tk.Misc, text: str) -> None:
    attach_tooltip(widget, text)


def _mk_btn(
    parent: tk.Misc,
    *,
    text: str,
    command,
    hint: str,
    side: str = "left",
    padx=(0, 0),
    width=None,
    accent: bool = False,
    app: core.App | None = None,
) -> ttk.Button:
    kwargs = {"text": text, "command": command}
    if width is not None:
        kwargs["width"] = width
    if accent:
        btn = app._accent_button(parent, **kwargs)  # type: ignore[union-attr]
    else:
        btn = ttk.Button(parent, **kwargs)
    btn.pack(side=side, padx=padx)
    _tip(btn, hint)
    return btn


def build_ui_v2(app: core.App) -> None:
    app._setup_ui_styles()

    shell = ttk.Frame(app)
    shell.pack(fill="both", expand=True)

    _build_header(app, shell)
    _build_toolbar(app, shell)

    work = _build_main_vertical_split(app, shell)
    _build_main_panels(app, work)
    _build_footer(app, shell)

    app._setup_tree_columns()
    app._setup_company_columns()


def _build_header(app: core.App, parent: ttk.Frame) -> None:
    hdr = tk.Frame(parent, bg=V2Theme.HEADER_BG, height=72)
    hdr.pack(fill="x")
    hdr.pack_propagate(False)
    app.register_v2_chrome_frame(hdr)

    left = tk.Frame(hdr, bg=V2Theme.HEADER_BG)
    left.pack(side="left", fill="y", padx=(16, 8), pady=10)
    app.register_v2_chrome_frame(left)

    title_row = tk.Frame(left, bg=V2Theme.HEADER_BG)
    title_row.pack(anchor="w")
    app.register_v2_chrome_frame(title_row)

    app.register_v2_chrome_label(
        tk.Label(title_row, text="Davčna Blagajna", bg=V2Theme.HEADER_BG, fg=V2Theme.HEADER_FG),
        "header_title",
    ).pack(side="left")

    app.register_v2_chrome_label(
        tk.Label(
            title_row,
            text="2.0",
            bg=V2Theme.BADGE_BG,
            fg=V2Theme.BADGE_FG,
            padx=10,
            pady=2,
        ),
        "badge",
    ).pack(side="left", padx=(10, 0))

    app.register_v2_chrome_label(
        tk.Label(left, text=V2Theme.APP_SUBTITLE, bg=V2Theme.HEADER_BG, fg=V2Theme.HEADER_MUTED),
        "header_muted",
    ).pack(anchor="w", pady=(4, 0))

    right = tk.Frame(hdr, bg=V2Theme.HEADER_BG)
    right.pack(side="right", fill="y", padx=16, pady=10)
    app.register_v2_chrome_frame(right)

    app.register_v2_chrome_label(
        tk.Label(
            right,
            textvariable=app.minimax_status,
            bg=V2Theme.HEADER_BG,
            fg=V2Theme.HEADER_ACCENT_FG,
            anchor="e",
        ),
        "header_accent",
    ).pack(anchor="e")

    app.register_v2_chrome_label(
        tk.Label(
            right,
            textvariable=app.selected_company_label,
            bg=V2Theme.HEADER_BG,
            fg=V2Theme.HEADER_FG,
            anchor="e",
        ),
        "header_company",
    ).pack(anchor="e", pady=(4, 0))


def _build_period_controls(app: core.App, parent: tk.Misc, *, title: str = "Obdobje") -> ttk.Labelframe:
    period = ttk.Labelframe(parent, text=title, padding=6)
    prow = ttk.Frame(period)
    prow.pack(fill="x")

    ttk.Label(prow, text="Leto:", width=5).pack(side="left")
    year_cb = app._yellow_combobox(
        prow,
        textvariable=app.period_year,
        values=app._period_year_combo_values(),
        state="readonly",
        width=6,
    )
    year_cb.pack(side="left", padx=(0, 8))
    app._period_year_cb = year_cb
    year_cb.bind(
        "<<ComboboxSelected>>",
        app._safe_call(app._on_period_combo_changed, "_on_period_combo_changed"),
    )

    ttk.Label(prow, text="Mesec:", width=6).pack(side="left")
    month_cb = app._yellow_combobox(
        prow,
        textvariable=app.period_month,
        values=list(core.PERIOD_MONTH_COMBO_VALUES),
        state="readonly",
        width=4,
    )
    month_cb.pack(side="left", padx=(0, 4))
    month_cb.bind(
        "<<ComboboxSelected>>",
        app._safe_call(app._on_period_combo_changed, "_on_period_combo_changed"),
    )
    return period


def _build_minimax_quick_bar(app: core.App, parent: tk.Misc) -> ttk.Labelframe:
    quick = ttk.Labelframe(parent, text="Minimax", padding=6)
    qrow = ttk.Frame(quick)
    qrow.pack(fill="x")
    ttk.Label(qrow, text="Org ID:", width=6).pack(side="left", padx=(0, 4))
    org_entry = app._yellow_entry(qrow, textvariable=app.minimax_org_id, width=10, state="readonly")
    org_entry.pack(side="left", padx=(0, 8))
    _mk_btn(
        qrow,
        text="OAuth…",
        command=app._safe_call(app._open_oauth_settings_dialog, "_open_oauth_settings_dialog"),
        hint=H.OAUTH,
        padx=(0, 4),
    )
    return quick


def _build_main_vertical_split(
    app: core.App,
    parent: ttk.Frame,
    *,
    include_export_tabs: bool = True,
) -> ttk.Frame:
    """Zgornji del + spodnji panel z gumboma − / + za skrčitev."""
    outer = ttk.Frame(parent)
    outer.pack(fill="both", expand=True, padx=10, pady=(4, 0))
    paned = ttk.Panedwindow(outer, orient="vertical")
    paned.pack(fill="both", expand=True)

    work = ttk.Frame(paned)
    settings_outer = ttk.Frame(paned)
    paned.add(work, weight=5)
    paned.add(settings_outer, weight=2)

    toggle = ttk.Frame(settings_outer)
    toggle.pack(fill="x", padx=2, pady=(2, 0))
    toggle_label = (
        "Pot & datoteke · Minimax nastavitve"
        if not include_export_tabs
        else "Pot & datoteke · Minimax · Excel · API"
    )
    v2_muted(toggle, text=toggle_label).pack(side="left", padx=4)

    body = ttk.Frame(settings_outer)
    body.pack(fill="both", expand=True)

    app._v2_main_paned = paned
    app._v2_settings_body = body
    app._v2_settings_collapsed = False
    app._v2_settings_sash_saved: int | None = None

    def _set_collapsed(collapsed: bool) -> None:
        app._v2_settings_collapsed = collapsed
        paned.update_idletasks()
        total_h = max(paned.winfo_height(), 120)
        if collapsed:
            if app._v2_settings_sash_saved is None:
                app._v2_settings_sash_saved = paned.sashpos(0)
            body.pack_forget()
            toggle.update_idletasks()
            paned.sashpos(0, max(40, total_h - toggle.winfo_reqheight() - 6))
        else:
            body.pack(fill="both", expand=True)
            paned.update_idletasks()
            saved = app._v2_settings_sash_saved
            if saved is not None and 80 < saved < total_h - 80:
                paned.sashpos(0, saved)
            else:
                paned.sashpos(0, int(total_h * 0.68))

    ttk.Button(toggle, text="−", width=3, command=lambda: _set_collapsed(True)).pack(side="right", padx=(2, 0))
    ttk.Button(toggle, text="+", width=3, command=lambda: _set_collapsed(False)).pack(side="right")

    _build_settings_notebook(app, body, include_export_tabs=include_export_tabs)

    def _init_sash(_event: tk.Event | None = None) -> None:
        if getattr(app, "_v2_settings_collapsed", False):
            return
        paned.update_idletasks()
        h = paned.winfo_height()
        if h > 100 and paned.sashpos(0) < 50:
            paned.sashpos(0, int(h * 0.68))

    paned.bind("<Map>", _init_sash, add="+")
    return work


def _build_toolbar(
    app: core.App,
    parent: ttk.Frame,
    *,
    include_period: bool = True,
    include_minimax: bool = True,
    include_analyze: bool = True,
    include_furs: bool = True,
    include_compare: bool = True,
) -> None:
    bar = ttk.Frame(parent, style="V2.Toolbar.TFrame", padding=(10, 8, 10, 4))
    packed = False

    if include_period:
        period_title = "Obdobje & analiza" if include_analyze else "Obdobje"
        period = _build_period_controls(app, bar, title=period_title)
        period.pack(side="left", fill="y", padx=(0, 8))
        packed = True

    if include_period and include_analyze:
        prow = ttk.Frame(period)
        prow.pack(fill="x", pady=(6, 0))
        _mk_btn(
            prow,
            text="Analiziraj Davčno blagajno",
            command=app._safe_call(app._analyze, "_analyze"),
            hint=H.ANALYZE_BLAGAJNA,
            padx=(0, 6),
            accent=True,
            app=app,
        )
        _mk_btn(
            prow,
            text="Analiziraj KIRKPR",
            command=app._safe_call(app._analyze_kirkpr, "_analyze_kirkpr"),
            hint=H.ANALYZE_KIRKPR,
            padx=(0, 6),
            accent=True,
            app=app,
        )
        packed = True

    if include_compare:
        _mk_btn(
            bar,
            text="Primerjaj datoteki",
            command=app._safe_call(app._compare_files, "_compare_files"),
            hint=H.COMPARE_FILES,
            padx=(0, 6),
        )
        packed = True

    if include_furs:
        furs = ttk.Labelframe(bar, text="eDavki / FURS", padding=6)
        furs.pack(side="left", fill="y", padx=(0, 8))
        packed = True

        frow = ttk.Frame(furs)
        frow.pack(fill="x")
        _mk_btn(
            frow,
            text="FURS Blagajna",
            command=app._safe_call(
                app._open_furs_and_optional_month_location,
                "_open_furs_and_optional_month_location",
            ),
            hint=H.FURS_BLAGAJNA,
            padx=(0, 6),
            accent=True,
            app=app,
        )
        _mk_btn(
            frow,
            text="Evidenca KIR/KPR",
            command=app._safe_call(
                app._open_furs_kir_kpr_and_optional_month_location,
                "_open_furs_kir_kpr_and_optional_month_location",
            ),
            hint=H.EVIDENCA_KIRKPR,
            accent=True,
            app=app,
        )

    if include_minimax:
        quick = _build_minimax_quick_bar(app, bar)
        quick.pack(side="right", fill="y")
        packed = True

    if packed:
        bar.pack(fill="x")


def _build_company_panel(app: core.App, parent: ttk.Frame, *, include_period: bool = False) -> ttk.Labelframe:
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)
    left = ttk.Labelframe(parent, text="Firme (SQL EvidencaFirm)", padding=8)
    left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
    tree_row = 6 if include_period else 5
    left.rowconfigure(tree_row, weight=1)
    left.columnconfigure(0, weight=1)

    row = 0
    if include_period:
        period_frm = _build_period_controls(app, left, title="Obdobje")
        period_frm.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        row += 1

    search_frm = ttk.Frame(left)
    search_frm.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 6))
    row += 1
    ttk.Label(search_frm, text="Išči:", width=5).pack(side="left")
    app._yellow_entry(search_frm, textvariable=app.company_search, width=22).pack(side="left", padx=(0, 4))
    _mk_btn(
        search_frm,
        text="✕",
        width=3,
        command=lambda: app.company_search.set(""),
        hint=H.COMPANY_SEARCH_CLEAR,
    )
    app.company_search.trace_add("write", lambda *_: app._render_companies())

    src_frm = ttk.Frame(left)
    src_frm.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 6))
    row += 1
    ttk.Label(src_frm, text="Vir:", width=7).pack(side="left")
    ttk.Label(src_frm, textvariable=app.companies_source_label, foreground=V2Theme.MUTED).pack(
        side="left", padx=(0, 4), fill="x", expand=True
    )
    _mk_btn(
        src_frm,
        text="Osveži",
        command=app._safe_call(app._load_companies, "_load_companies"),
        hint=H.LOAD_COMPANIES,
        padx=(4, 0),
    )

    ev_frm = ttk.Frame(left)
    ev_frm.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 4))
    row += 1
    ev_cb = ttk.Checkbutton(
        ev_frm,
        text="Evidenca Davčnih blagajn",
        variable=app.filter_evidenca_davcnih,
        command=app._safe_call(app._on_evidenca_filter_toggle, "_on_evidenca_filter_toggle"),
    )
    ev_cb.pack(side="left")
    _tip(ev_cb, H.FILTER_EVIDENCA)
    app._evidenca_count_label = ttk.Label(ev_frm, text="", foreground=V2Theme.MUTED)
    app._evidenca_count_label.pack(side="left", padx=(8, 0))

    links_frm = ttk.Frame(left)
    links_frm.grid(row=row, column=0, columnspan=2, sticky="ew", pady=(0, 6))
    row += 1
    ttk.Label(links_frm, text="eDavki:", width=7).pack(side="left")
    app._edavki_link_cb = app._yellow_combobox(
        links_frm,
        textvariable=app._edavki_link_var,
        width=34,
        state="readonly",
    )
    app._edavki_link_cb.pack(side="left", padx=(0, 4), fill="x", expand=True)
    _mk_btn(
        links_frm,
        text="Odpri",
        command=app._safe_call(app._open_edavki_link_combo, "_open_edavki_link_combo"),
        hint="Odpri izbrano povezavo v Chrome (DURS izbrane firme). Nastavitve → Povezave.",
        padx=(0, 0),
        accent=True,
        app=app,
    )
    if hasattr(app, "_reload_edavki_links_config"):
        app._reload_edavki_links_config(on_startup=True)

    v2_muted(left, text="Klikni firmo za izbor. Ev. = evidenca davčnih blagajn.").grid(
        row=row, column=0, sticky="w", pady=(0, 6)
    )
    row += 1

    app.company_tree = ttk.Treeview(left, show="headings", selectmode="browse")
    app.company_tree.bind(
        "<<TreeviewSelect>>",
        app._safe_call(app._on_company_select, "_on_company_select"),
    )
    app.company_tree.bind(
        "<Button-1>",
        app._safe_call(app._on_company_tree_click, "_on_company_tree_click"),
        add="+",
    )
    c_vsb = ttk.Scrollbar(left, orient="vertical", command=app.company_tree.yview)
    c_hsb = ttk.Scrollbar(left, orient="horizontal", command=app.company_tree.xview)
    app.company_tree.configure(yscrollcommand=c_vsb.set, xscrollcommand=c_hsb.set)
    app.company_tree.grid(row=row, column=0, sticky="nsew")
    c_vsb.grid(row=row, column=1, sticky="ns")
    c_hsb.grid(row=row + 1, column=0, sticky="ew")
    return left


def _build_results_panel(
    app: core.App,
    parent: ttk.Frame,
    *,
    title: str = "Rezultati (leto → mesec → dan → ZIP)",
    include_analyze_buttons: bool = False,
    contextual_tab_actions: bool = False,
    grid_column: int = 1,
) -> ttk.Labelframe:
    """Drevo + Podrobnosti izbire kot ločena panela +/− (skrči / razširi)."""
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(grid_column, weight=1)
    host = ttk.Frame(parent)
    host.grid(row=0, column=grid_column, sticky="nsew")
    host.rowconfigure(0, weight=1)
    host.rowconfigure(1, weight=0)
    host.columnconfigure(0, weight=1)

    def _build_tree_body(body: ttk.Frame) -> None:
        body.rowconfigure(2, weight=1)
        body.columnconfigure(0, weight=1)

        rtb = ttk.Frame(body)
        rtb.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        if contextual_tab_actions:
            action_frm = ttk.Frame(rtb)
            action_frm.pack(side="left", padx=(0, 12))
            app._v21_action_frm = action_frm
            app._v21_btn_furs_blagajna = app._accent_button(
                action_frm,
                text="FURS Blagajna",
                command=app._safe_call(
                    app._open_furs_and_optional_month_location,
                    "_open_furs_and_optional_month_location",
                ),
            )
            app._v21_btn_analyze_blagajna = app._accent_button(
                action_frm,
                text="Uvozi podatke",
                command=app._safe_call(app._analyze, "_analyze"),
            )
            for btn, hint in (
                (app._v21_btn_furs_blagajna, H.FURS_BLAGAJNA),
                (app._v21_btn_analyze_blagajna, H.IMPORT_BLAGAJNA),
            ):
                _tip(btn, hint)
        elif include_analyze_buttons:
            _mk_btn(
                rtb,
                text="Analiziraj Davčno blagajno",
                command=app._safe_call(app._analyze, "_analyze"),
                hint=H.ANALYZE_BLAGAJNA,
                padx=(0, 6),
                accent=True,
                app=app,
            )
            _mk_btn(
                rtb,
                text="Analiziraj KIR/KPR",
                command=app._safe_call(app._analyze_kirkpr, "_analyze_kirkpr"),
                hint=H.ANALYZE_KIRKPR,
                padx=(0, 12),
                accent=True,
                app=app,
            )
        filter_frm = ttk.Frame(rtb)
        filter_frm.pack(side="left", fill="x", expand=True)
        ttk.Label(filter_frm, text="Filter (Zap. št. / P3):").pack(side="left")
        filter_entry = ttk.Entry(filter_frm, textvariable=app.doc_filter, width=24)
        filter_entry.pack(side="left", padx=(4, 4))
        _tip(filter_entry, H.DOC_FILTER_ENTRY)
        filter_entry.bind("<Return>", app._safe_call(app._apply_doc_filter, "_apply_doc_filter"))
        _mk_btn(
            filter_frm,
            text="Filtriraj",
            command=app._safe_call(app._apply_doc_filter, "_apply_doc_filter"),
            hint=H.FILTER_APPLY,
            padx=(0, 4),
        )
        _mk_btn(
            filter_frm,
            text="Počisti filter",
            command=app._safe_call(app._clear_doc_filter, "_clear_doc_filter"),
            hint=H.FILTER_CLEAR,
            padx=(0, 8),
        )
        v2_muted(filter_frm, text="delni niz ali blag* / *97846").pack(side="left", padx=(0, 8))
        neob_cb = ttk.Checkbutton(
            filter_frm,
            text="Vrednost Neobd.nabav",
            variable=app.show_neobdavcljive,
            command=app._safe_call(app._on_show_neobdavcljive_toggle, "_on_show_neobdavcljive_toggle"),
        )
        neob_cb.pack(side="left", padx=(0, 8))
        _tip(neob_cb, H.SHOW_NEOBD)
        _mk_btn(
            rtb,
            text="Dodaj nov zapis",
            command=app._safe_call(app._open_kirkpr_new_record_editor, "_open_kirkpr_new_record_editor"),
            hint="Ročno odpri Minimax API knjižbo za nov zapis (KIR/KPR). Izberi dan v drevesu.",
            side="right",
            padx=(0, 8),
        )
        _mk_btn(
            rtb,
            text="Razširi",
            command=app._safe_call(app._tree_expand_all, "_tree_expand_all"),
            hint=H.TREE_EXPAND,
            side="right",
            padx=(0, 4),
        )
        _mk_btn(
            rtb,
            text="Skrči",
            command=app._safe_call(app._tree_collapse_all, "_tree_collapse_all"),
            hint=H.TREE_COLLAPSE,
            side="right",
            padx=(0, 8),
        )
        _mk_btn(
            rtb,
            text="Sprazni",
            command=app._safe_call(app._tree_clear_selected_result_row, "_tree_clear_selected_result_row"),
            hint=H.TREE_CLEAR_ROW,
            side="right",
            accent=True,
            app=app,
        )
        v2_muted(rtb, text="Izbriši izbrano vrstico (Delete ali gumb Sprazni).").pack(
            side="right", padx=(0, 10)
        )

        info_frm = ttk.Frame(body)
        info_frm.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 4))
        v2_info(info_frm, textvariable=app._analysis_info_var, wraplength=920, justify="left").pack(
            anchor="w"
        )
        ttk.Label(
            info_frm,
            textvariable=app._tree_checked_sum_var,
            foreground=V2Theme.MUTED,
            wraplength=920,
            justify="left",
        ).pack(anchor="w", pady=(2, 0))
        v2_muted(
            info_frm,
            text="Klikni ✓ za označitev meseca/dneva (seštevek spodaj). Izvoz/Shrani upošteva označene vrstice, sicer izbrano v drevesu.",
            wraplength=920,
            justify="left",
        ).pack(anchor="w", pady=(2, 0))

        app._tree_sel_tag = "tree_sel_active"
        app._tree_styled_iid = None
        tree_style = ttk.Style(app)
        tree_style.map(
            "Treeview",
            foreground=[("selected", V2Theme.TREE_SEL_FG)],
            background=[("selected", V2Theme.TREE_SEL_BG)],
        )

        app.tree = ttk.Treeview(body, show="tree headings")
        app.tree.tag_configure(
            app._tree_sel_tag,
            foreground=V2Theme.TREE_ACTIVE_TAG,
            font=("Segoe UI", 9, "bold"),
        )
        app.tree.tag_configure("zip_disabled", foreground=V2Theme.TREE_ZIP_DISABLED)
        app.tree.tag_configure(
            "kirkpr_date_outside",
            foreground="#cc0000",
            background="#ffe8e8",
        )
        app.tree.bind("<Double-1>", app._safe_call(app._on_tree_double_click, "_on_tree_double_click"))
        app.tree.bind(
            "<Delete>",
            app._safe_call(app._tree_clear_selected_result_row, "_tree_clear_selected_result_row"),
        )
        app.tree.bind("<<TreeviewOpen>>", app._safe_call(app._on_tree_open, "_on_tree_open"))
        app.tree.bind("<<TreeviewSelect>>", app._safe_call(app._on_tree_select, "_on_tree_select"))
        app.tree.bind(
            "<Button-1>",
            app._safe_call(app._on_tree_cell_click, "_on_tree_cell_click"),
            add="+",
        )
        vsb = ttk.Scrollbar(body, orient="vertical", command=app.tree.yview)
        hsb = ttk.Scrollbar(body, orient="horizontal", command=app.tree.xview)
        app.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        app.tree.grid(row=2, column=0, sticky="nsew")
        vsb.grid(row=2, column=1, sticky="ns")
        hsb.grid(row=3, column=0, sticky="ew")

    def _build_detail_body(body: ttk.Frame) -> None:
        body.columnconfigure(0, weight=1)
        app._selection_detail_title = tk.StringVar(value="(ni izbire)")
        ttk.Label(body, textvariable=app._selection_detail_title).grid(
            row=0, column=0, sticky="w", pady=(0, 4)
        )
        app._selection_detail_tree = ttk.Treeview(
            body,
            columns=("Znesek",),
            show="tree headings",
            height=4,
        )
        app._selection_detail_tree.heading("#0", text="Stolpec")
        app._selection_detail_tree.column("#0", width=280, anchor="w", stretch=True)
        app._selection_detail_tree.heading("Znesek", text="Znesek")
        app._selection_detail_tree.column("Znesek", width=120, anchor="e", stretch=False)
        d_vsb = ttk.Scrollbar(body, orient="vertical", command=app._selection_detail_tree.yview)
        app._selection_detail_tree.configure(yscrollcommand=d_vsb.set)
        app._selection_detail_tree.grid(row=1, column=0, sticky="nsew")
        d_vsb.grid(row=1, column=1, sticky="ns")

    tree_outer = wrap_collapsible_labelframe(
        host,
        title,
        _build_tree_body,
        app,
        "_v21_tree_panel_collapsed",
        collapsed_default=False,
        padding=8,
        body_fill="both",
        body_expand=True,
        lf_fill="both",
        lf_expand=True,
        collapse_hint=H.PANEL_TREE_COLLAPSE,
        expand_hint=H.PANEL_TREE_EXPAND,
    )
    tree_outer.grid(row=0, column=0, sticky="nsew")

    detail_outer = wrap_collapsible_labelframe(
        host,
        "Podrobnosti izbire",
        _build_detail_body,
        app,
        "_v21_detail_panel_collapsed",
        collapsed_default=False,
        padding=4,
        body_fill="x",
        body_expand=False,
        lf_fill="x",
        lf_expand=False,
        collapse_hint=H.PANEL_DETAIL_COLLAPSE,
        expand_hint=H.PANEL_DETAIL_EXPAND,
    )
    detail_outer.grid(row=1, column=0, sticky="ew", pady=(6, 0))

    app._v21_tree_panel_outer = tree_outer
    app._v21_detail_panel_outer = detail_outer
    right = getattr(tree_outer, "labelframe", None)
    if right is None:
        # fallback (ne bi smelo)
        right = tree_outer  # type: ignore[assignment]
    return right  # type: ignore[return-value]


def _build_main_panels(app: core.App, parent: ttk.Frame) -> None:
    main = ttk.Frame(parent, padding=(0, 6, 0, 4))
    main.pack(fill="both", expand=True)
    main.columnconfigure(0, weight=0, minsize=420)
    main.columnconfigure(1, weight=1)
    main.rowconfigure(0, weight=1)

    _build_company_panel(app, main)
    _build_results_panel(app, main)


def _build_settings_notebook(
    app: core.App,
    parent: ttk.Frame,
    *,
    include_export_tabs: bool = True,
) -> None:
    nb = ttk.Notebook(parent)
    nb.pack(fill="both", expand=True, padx=0, pady=(0, 4))

    tab_paths = ttk.Frame(nb, padding=8)
    tab_minimax = ttk.Frame(nb, padding=8)

    nb.add(tab_paths, text="Pot & datoteke")
    nb.add(tab_minimax, text="Minimax nastavitve")
    if include_export_tabs:
        tab_excel = ttk.Frame(nb, padding=8)
        tab_izvoz = ttk.Frame(nb, padding=8)
        nb.add(tab_excel, text="Excel & knjižbe")
        nb.add(tab_izvoz, text="Izvoz v Minimax API")
    bind_notebook_active_tab_style(nb)
    if hasattr(app, "register_v2_notebook"):
        app.register_v2_notebook(nb)

    _build_tab_paths(app, tab_paths)
    _build_tab_minimax(app, tab_minimax)
    if include_export_tabs:
        _build_tab_excel(app, tab_excel)
        _build_tab_izvoz(app, tab_izvoz)


def _build_export_workflow_panel(app: core.App, parent: ttk.Frame, *, titled: bool = True):
    """Korak 3: izvoz v Excel / knjižbe / Minimax API (nad drevesom rezultatov)."""
    from v2.tab_bar import TabBar

    if titled:
        wrap = ttk.Labelframe(
            parent, text="Izvoz — Excel · knjižbe · Minimax API", padding=(6, 4, 6, 2)
        )
    else:
        wrap = ttk.Frame(parent, padding=(0, 2, 0, 0))
    wrap.pack(fill="x", expand=False)

    content = ttk.Frame(wrap)
    content.pack(fill="x")
    content.columnconfigure(0, weight=1)

    excel_frm = ttk.Frame(content, padding=(0, 2, 0, 0))
    api_frm = ttk.Frame(content, padding=(0, 2, 0, 0))
    excel_frm.grid(row=0, column=0, sticky="ew")
    api_frm.grid(row=0, column=0, sticky="ew")

    _build_tab_excel(app, excel_frm)
    _build_tab_izvoz(app, api_frm)

    def _show_export(idx: int) -> None:
        if idx == 0:
            excel_frm.grid()
            api_frm.grid_remove()
        else:
            api_frm.grid()
            excel_frm.grid_remove()

    bar = TabBar(wrap, ("Excel & knjižbe", "Izvoz v Minimax API"), _show_export, compact=True)
    bar.pack(fill="x", before=content)
    api_frm.grid_remove()
    return bar


def _build_tab_paths(app: core.App, parent: ttk.Frame) -> None:
    r1 = ttk.Frame(parent)
    r1.pack(fill="x", pady=2)
    ttk.Label(r1, text="Root:", width=6).pack(side="left")
    root_ent = app._yellow_entry(r1, textvariable=app.root_dir, width=V2Layout.root_width)
    root_ent.pack(side="left", padx=4)
    _reg_layout(app, "root_width", root_ent)
    _mk_btn(
        r1,
        text="…",
        width=3,
        command=app._safe_call(app._pick_root, "_pick_root"),
        hint=H.PICK_ROOT,
    )
    zip_cb = ttk.Checkbutton(r1, text="ZIP", variable=app.include_zips)
    zip_cb.pack(side="left", padx=(8, 4))
    _tip(zip_cb, H.ZIP_PACKAGES)
    _mk_btn(
        r1,
        text="ZIP paketi…",
        command=app._safe_call(app._open_zip_packages_dialog, "_open_zip_packages_dialog"),
        hint=H.ZIP_PACKAGES,
        padx=(0, 8),
    )

    r1b = ttk.Frame(parent)
    r1b.pack(fill="x", pady=2)
    ttk.Label(r1b, text="Shranjevanje:", width=11).pack(side="left")
    out_ent = app._yellow_entry(r1b, textvariable=app.out_dir, width=V2Layout.out_dir_width)
    out_ent.pack(side="left", padx=4)
    _reg_layout(app, "out_dir_width", out_ent)
    _mk_btn(
        r1b,
        text="…",
        width=3,
        command=app._safe_call(app._pick_out, "_pick_out"),
        hint=H.PICK_OUT,
        padx=(0, 8),
    )
    ttk.Label(r1b, text="Datoteka:", width=8).pack(side="left")
    file_ent = app._yellow_entry(r1b, textvariable=app.out_file, width=V2Layout.out_file_width)
    file_ent.pack(side="left", padx=2)
    _reg_layout(app, "out_file_width", file_ent)
    ttk.Label(r1b, text="Sheet:", width=5).pack(side="left", padx=(4, 0))
    sheet_ent = app._yellow_entry(r1b, textvariable=app.sheet_name, width=V2Layout.sheet_width)
    sheet_ent.pack(side="left", padx=2)
    _reg_layout(app, "sheet_width", sheet_ent)
    ttk.Label(r1b, text="CSV:", width=4).pack(side="left")
    csv_ent = app._yellow_entry(r1b, textvariable=app.csv_name, width=V2Layout.csv_width)
    csv_ent.pack(side="left", padx=2)
    _reg_layout(app, "csv_width", csv_ent)

    _layout_muted(
        app,
        parent,
        text="Root = …\\Blagajna (ustvari se ob izbiri firme). Analiza bere YYYY-MM mape/ZIP v mapi firme.",
        justify="left",
    ).pack(anchor="w", pady=(8, 0))


def _build_tab_minimax(app: core.App, parent: ttk.Frame) -> None:
    r2 = ttk.Frame(parent)
    r2.pack(fill="x", pady=2)
    ttk.Label(r2, text="DocumentType:", width=12).pack(side="left")
    doc_cb = app._yellow_combobox(
        r2,
        textvariable=app.minimax_document_type,
        values=core.MINIMAX_DOCUMENT_TYPE_OPTIONS,
        state="readonly",
        width=V2Layout.document_type_width,
    )
    doc_cb.pack(side="left", padx=(0, 4))
    _reg_layout(app, "document_type_width", doc_cb)
    app._minimax_document_type_cb = doc_cb
    doc_cb.bind(
        "<<ComboboxSelected>>",
        lambda _e: app._sync_minimax_document_type_display(save=True),
        add="+",
    )

    r2hint = ttk.Frame(parent)
    r2hint.pack(fill="x", pady=(0, 2))
    try:
        _r2_bg = ttk.Style().lookup("TFrame", "background") or V2Theme.PANEL_BG
    except tk.TclError:
        _r2_bg = V2Theme.PANEL_BG
    hint_lbl = tk.Label(
        r2hint,
        textvariable=app.minimax_document_type_hint,
        fg=V2Theme.ACCENT_TEXT,
        bg=_r2_bg,
        anchor="w",
        wraplength=V2Layout.help_wraplength,
        justify="left",
    )
    if hasattr(app, "register_v2_hint_label"):
        app.register_v2_hint_label(hint_lbl)
    else:
        hint_lbl.configure(font=V2Theme.ui_font(bold=True))
    hint_lbl.pack(side="left", anchor="w")
    _reg_layout(app, "help_wraplength", hint_lbl)

    r2b = ttk.Frame(parent)
    r2b.pack(fill="x", pady=(0, 4))
    _layout_muted(app, r2b, text=core.MINIMAX_DOCUMENT_TYPE_HELP, justify="left").pack(
        side="left", anchor="w"
    )

    r2c = ttk.Frame(parent)
    r2c.pack(fill="x", pady=(0, 4))
    ddv_cb = ttk.Checkbutton(
        r2c,
        text="Podjetje je zavezanec za DDV (API pošlje IssuedInvoicePostingTaxes)",
        variable=app.minimax_ddv_zavezanec,
        command=app._safe_call(app._on_ddv_zavezanec_toggle, "_on_ddv_zavezanec_toggle"),
    )
    ddv_cb.pack(side="left", anchor="w")
    _tip(
        ddv_cb,
        "Vklopi, če firma pošilja davčne vrstice v Minimax API.\n"
        "Iz SQL seznama firm (OddajaDdv): Mesečni/Tromesečni = kljukica, Ni zavezanec = brez.\n"
        "Ob vsaki izbiri firme se checkbox uskladi iz tega seznama.",
    )

    r3 = ttk.Frame(parent)
    r3.pack(fill="x", pady=2)
    ttk.Label(r3, text="Način plačila:", width=13).pack(side="left")
    pm_cb = app._yellow_combobox(
        r3,
        textvariable=app.minimax_payment_method_label,
        values=list(app._minimax_payment_method_label_to_id.keys()),
        state="readonly",
        width=V2Layout.payment_method_width,
    )
    pm_cb.pack(side="left", padx=4)
    _reg_layout(app, "payment_method_width", pm_cb)
    app._minimax_payment_method_cb = pm_cb
    app.minimax_payment_method_label.trace_add("write", app._sync_minimax_payment_method_from_label)
    pm_cb.bind("<<ComboboxSelected>>", lambda _e: app._on_minimax_payment_method_selected())
    app._bind_combobox_konti_opener(pm_cb, "_open_kontiranje_placila_editor")
    ttk.Button(
        r3,
        text="Konti…",
        width=7,
        command=app._safe_call(app._open_kontiranje_placila_editor, "_open_kontiranje_placila_editor"),
    ).pack(side="left", padx=(0, 4))
    ttk.Button(
        r3,
        text="↻",
        width=3,
        command=app._safe_call(app._refresh_minimax_payment_methods, "_refresh_minimax_payment_methods"),
    ).pack(side="left", padx=(0, 12))

    r4 = ttk.Frame(parent)
    r4.pack(fill="x", pady=2)
    ttk.Label(r4, text="Vrsta prodaje:", width=13).pack(side="left")
    vrsta_cb = app._yellow_combobox(
        r4,
        textvariable=app.vrsta_prodaje,
        values=core.VRSTA_PRODAJE_LABELS,
        state="readonly",
        width=V2Layout.vrsta_prodaje_width,
    )
    vrsta_cb.pack(side="left", padx=4)
    _reg_layout(app, "vrsta_prodaje_width", vrsta_cb)
    app._vrsta_prodaje_cb = vrsta_cb
    app._bind_combobox_konti_opener(vrsta_cb, "_open_kontiranje_prihodkov_editor")
    _mk_btn(
        r4,
        text="Konti…",
        width=7,
        command=app._safe_call(app._open_kontiranje_prihodkov_editor, "_open_kontiranje_prihodkov_editor"),
        hint=H.KONTI,
        padx=(4, 0),
    )


def _build_tab_excel(app: core.App, parent: ttk.Frame) -> None:
    row = ttk.Frame(parent)
    row.pack(fill="x", pady=4)
    _mk_btn(
        row,
        text="Shrani v Excel",
        command=app._safe_call(app._save, "_save"),
        hint=H.SAVE_EXCEL,
    )
    _mk_btn(
        row,
        text="Izvoz podatkov v excel",
        command=app._safe_call(app._export_analysis_to_excel, "_export_analysis_to_excel"),
        hint=H.EXPORT_ANALYSIS_EXCEL,
        padx=6,
    )
    _mk_btn(
        row,
        text="Knjižbe DDV po mesecih",
        command=app._safe_call(app._copy_to_knjizbe, "_copy_to_knjizbe"),
        hint=H.KNJIZBE_MONTH,
        padx=6,
    )
    _mk_btn(
        row,
        text="Knjižbe DDV po dnevih",
        command=app._safe_call(app._copy_daily_to_knjizbe, "_copy_daily_to_knjizbe"),
        hint=H.KNJIZBE_DAILY,
        padx=6,
        accent=True,
        app=app,
    )
    _mk_btn(
        row,
        text="Minimax spletni uvoz",
        command=app._safe_call(app._open_minimax_web_uvoz_browser, "_open_minimax_web_uvoz_browser"),
        hint=H.MINIMAX_WEB_UVOZ,
        padx=6,
    )

    tpl = ttk.Frame(parent)
    tpl.pack(fill="x", pady=4)
    ttk.Label(tpl, text="Predloga knjižb:", width=14).pack(side="left")
    tpl_ent = app._yellow_entry(tpl, textvariable=app.template_path, width=V2Layout.template_width)
    tpl_ent.pack(side="left", padx=2)
    _reg_layout(app, "template_width", tpl_ent)
    _mk_btn(
        tpl,
        text="…",
        width=3,
        command=app._safe_call(app._pick_template, "_pick_template"),
        hint=H.PICK_TEMPLATE,
        padx=4,
    )


def _build_tab_izvoz(app: core.App, parent: ttk.Frame) -> None:
    row = ttk.Frame(parent)
    row.pack(fill="x", pady=4)
    _mk_btn(
        row,
        text="Pošlji mesečne podatke v Minimax API",
        command=app._safe_call(app._send_month_file_to_minimax_api, "_send_month_file_to_minimax_api"),
        hint=H.SEND_MONTH_API,
    )
    _mk_btn(
        row,
        text="Pošlji dnevne podatke v Minimax API",
        command=app._safe_call(app._send_daily_to_minimax_api, "_send_daily_to_minimax_api"),
        hint=H.SEND_DAILY_API,
        padx=6,
        accent=True,
        app=app,
    )
    _layout_muted(
        app,
        parent,
        text=(
            "Dnevni: API če je mogoč (OAuth/token); WebView2 samo če API ni mogoč. "
            "Mesečni gumb = Minimax API (OAuth + Org ID). "
            "Portal most: aktivni Chrome portal, sicer trajni WebView2 profil "
            "(v2/portal_bridge → QUICK_eNDM)."
        ),
        justify="left",
    ).pack(anchor="w", pady=(8, 0))


def _build_footer(app: core.App, parent: ttk.Frame) -> None:
    foot = tk.Frame(parent, bg=V2Theme.FOOTER_BG, height=28)
    foot.pack(fill="x")
    foot.pack_propagate(False)
    if hasattr(app, "register_v2_chrome_frame"):
        app.register_v2_chrome_frame(foot, footer=True)
    app.register_v2_chrome_label(
        tk.Label(
            foot,
            text="Davčna Blagajna 2.0 · v1 ostane na voljo (DavcnaBlagajna.py)",
            bg=V2Theme.FOOTER_BG,
            fg=V2Theme.FOOTER_FG,
        ),
        "footer",
    ).pack(side="left", padx=12, pady=4)
