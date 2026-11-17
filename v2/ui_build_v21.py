"""Gradnja vmesnika 2.1 — orodna vrstica kot 2.0, zavihki preklapljajo pogled rezultatov."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

import DavcnaBlagajna as core
from v2 import ui_hints as H
from v2.tab_bar import TabBar
from v2.theme import V2Theme, v2_muted
from v2.version_journal import get_current_patch_version
from v2.collapsible import wrap_collapsible_frame, wrap_collapsible_labelframe
from v2.ui_build import (
    _build_company_panel,
    _build_export_workflow_panel,
    _build_main_vertical_split,
    _build_minimax_quick_bar,
    _build_results_panel,
    _build_toolbar,
    _mk_btn,
    _tip,
)


def _bind_panel_wheel(canvas: tk.Canvas) -> None:
    def _on_wheel(event: tk.Event) -> None:
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind(_event: tk.Event) -> None:
        canvas.bind_all("<MouseWheel>", _on_wheel)

    def _unbind(_event: tk.Event) -> None:
        canvas.unbind_all("<MouseWheel>")

    canvas.bind("<Enter>", _bind)
    canvas.bind("<Leave>", _unbind)


def _make_scroll_host(parent: ttk.Frame) -> tuple[tk.Canvas, ttk.Frame]:
    """Canvas + notranji okvir z drsnikoma (kot pri nastavitvah)."""
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    canvas = tk.Canvas(parent, highlightthickness=0, borderwidth=0)
    vsb = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    hsb = ttk.Scrollbar(parent, orient="horizontal", command=canvas.xview)
    canvas.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    inner = ttk.Frame(canvas)
    window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

    def _on_inner_configure(_event: tk.Event) -> None:
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(event: tk.Event) -> None:
        canvas.itemconfigure(window_id, width=max(event.width, inner.winfo_reqwidth()))

    inner.bind("<Configure>", _on_inner_configure)
    canvas.bind("<Configure>", _on_canvas_configure)
    _bind_panel_wheel(canvas)
    return canvas, inner


def build_ui_v21(app: core.App) -> None:
    app._setup_ui_styles()

    shell = ttk.Frame(app)
    shell.pack(fill="both", expand=True)

    _build_header_v21(app, shell)
    _build_toolbar(
        app,
        shell,
        include_period=False,
        include_minimax=False,
        include_analyze=False,
        include_furs=False,
        include_compare=False,
    )

    work = _build_main_vertical_split(app, shell, include_export_tabs=False)
    work.rowconfigure(0, weight=1)
    work.columnconfigure(0, weight=1)

    _build_main_panels_v21(app, work)
    _build_footer_v21(app, shell)

    app._setup_tree_columns()
    app._setup_company_columns()

    if hasattr(app, "_bind_v21_view_tabs"):
        app._bind_v21_view_tabs()


def _build_header_v21(app: core.App, parent: ttk.Frame) -> None:
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

    patch = get_current_patch_version()

    app.register_v2_chrome_label(
        tk.Label(
            title_row,
            text=patch,
            bg=V2Theme.BADGE_BG,
            fg=V2Theme.BADGE_FG,
            padx=10,
            pady=2,
        ),
        "badge",
    ).pack(side="left", padx=(10, 0))

    app.register_v2_chrome_label(
        tk.Label(
            left,
            text="Zgoraj: pogled → uvoz → izvoz → drevo  ·  spodaj: pot & Minimax nastavitve",
            bg=V2Theme.HEADER_BG,
            fg=V2Theme.HEADER_MUTED,
        ),
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


def _build_kirkpr_source_panel(app: core.App, parent: ttk.Frame) -> TabBar:
    """Podzavihka eDavki / Minimax z gumbi v vsakem zavihku."""
    wrap = ttk.Frame(parent)
    wrap.pack(fill="x")

    content = ttk.Frame(wrap)
    content.pack(fill="x")
    content.columnconfigure(0, weight=1)

    edavki_frm = ttk.Frame(content, padding=(0, 4, 0, 2))
    minimax_frm = ttk.Frame(content, padding=(0, 4, 0, 2))
    edavki_frm.grid(row=0, column=0, sticky="ew")
    minimax_frm.grid(row=0, column=0, sticky="ew")

    ed_bar = ttk.Frame(edavki_frm)
    ed_bar.pack(fill="x")
    btn_prenos_ed = app._accent_button(
        ed_bar,
        text="Prenos KIR/KPR eDavki",
        command=app._safe_call(
            app._open_furs_kir_kpr_and_optional_month_location,
            "_open_furs_kir_kpr_and_optional_month_location",
        ),
    )
    btn_prenos_ed.pack(side="left", padx=(0, 6))
    btn_uvozi_ed = app._accent_button(
        ed_bar,
        text="Uvozi podatke",
        command=app._safe_call(app._uvozi_kirkpr, "_uvozi_kirkpr"),
    )
    btn_uvozi_ed.pack(side="left")
    _tip(btn_uvozi_ed, H.IMPORT_KIRKPR)
    _tip(btn_prenos_ed, H.PRENOS_EDAVKI)

    mm_bar = ttk.Frame(minimax_frm)
    mm_bar.pack(fill="x")
    btn_prenos_mm = app._accent_button(
        mm_bar,
        text="Prenos KIR/KPR minimax",
        command=app._safe_call(app._prenos_minimax_kirkpr, "_prenos_minimax_kirkpr"),
    )
    btn_prenos_mm.pack(side="left", padx=(0, 6))
    btn_uvozi_mm = app._accent_button(
        mm_bar,
        text="Uvozi podatke",
        command=app._safe_call(app._uvozi_kirkpr, "_uvozi_kirkpr"),
    )
    btn_uvozi_mm.pack(side="left")
    _tip(btn_uvozi_mm, H.IMPORT_KIRKPR)
    _tip(btn_prenos_mm, H.PRENOS_MINIMAX)

    def _show_source(idx: int) -> None:
        if idx == 0:
            edavki_frm.grid()
            minimax_frm.grid_remove()
        else:
            minimax_frm.grid()
            edavki_frm.grid_remove()
        if hasattr(app, "_on_v21_kirkpr_source_tab_changed"):
            app._on_v21_kirkpr_source_tab_changed()

    bar = TabBar(wrap, ("eDavki", "Minimax"), _show_source, compact=True)
    bar.pack(fill="x", before=content)
    minimax_frm.grid_remove()
    return bar


def _build_main_panels_v21(app: core.App, parent: ttk.Frame) -> None:
    main = ttk.Frame(parent, padding=(0, 6, 0, 4))
    main.pack(fill="both", expand=True)
    main.rowconfigure(0, weight=1)
    main.columnconfigure(0, weight=1)

    hpaned = ttk.Panedwindow(main, orient="horizontal")
    hpaned.grid(row=0, column=0, sticky="nsew")

    left_host = ttk.Frame(hpaned)
    right_host = ttk.Frame(hpaned)
    hpaned.add(left_host, weight=1)
    hpaned.add(right_host, weight=3)

    _build_company_panel(app, left_host, include_period=True)

    right_host.rowconfigure(0, weight=1)
    right_host.columnconfigure(0, weight=1)

    right_col = ttk.Frame(right_host)
    right_col.grid(row=0, column=0, sticky="nsew")
    right_col.rowconfigure(4, weight=1)
    right_col.columnconfigure(0, weight=1)

    def _build_mm_body(body: ttk.Frame) -> None:
        bar = _build_minimax_quick_bar(app, body)
        bar.pack(fill="x")

    mm_outer = wrap_collapsible_frame(
        right_col,
        "Minimax — Org ID / OAuth",
        _build_mm_body,
        app,
        "_v21_mm_bar_collapsed",
        collapsed_default=True,
    )
    mm_outer.grid(row=0, column=0, sticky="ew", pady=(0, 4))

    view_hdr = ttk.Frame(right_col)
    view_hdr.grid(row=1, column=0, sticky="ew", pady=(0, 2))
    v2_muted(view_hdr, text="Pogled analize:").pack(side="left", padx=(0, 8))

    view_labels = (
        "Blagajna",
        "KIR/KPR",
        "Primerjaj KIRKPR",
        "Primerjaj datoteke",
        "Minimax",
    )

    def _on_view_tab(idx: int) -> None:
        if hasattr(app, "_on_v21_view_tab_changed"):
            app._on_v21_view_tab_changed()

    app._v21_view_tab_bar = TabBar(view_hdr, view_labels, _on_view_tab)
    app._v21_view_tab_bar.pack(side="left", fill="x", expand=True)
    if hasattr(app, "register_v2_tab_bar"):
        app.register_v2_tab_bar(app._v21_view_tab_bar)
    app._v21_view_nb = None

    def _build_kirkpr_body(body: ttk.Frame) -> None:
        def _on_kirkpr_book(idx: int) -> None:
            if hasattr(app, "_on_v21_kirkpr_sub_tab_changed"):
                app._on_v21_kirkpr_sub_tab_changed()

        app._v21_kirkpr_tab_bar = TabBar(
            body,
            ("KIR", "KPR"),
            _on_kirkpr_book,
            compact=True,
        )
        app._v21_kirkpr_tab_bar.pack(fill="x", pady=(0, 4))
        if hasattr(app, "register_v2_tab_bar"):
            app.register_v2_tab_bar(app._v21_kirkpr_tab_bar)

        app._v21_kirkpr_source_bar = _build_kirkpr_source_panel(app, body)
        if hasattr(app, "register_v2_tab_bar"):
            app.register_v2_tab_bar(app._v21_kirkpr_source_bar)

    app._v21_kirkpr_area = wrap_collapsible_labelframe(
        right_col,
        "1. Uvoz — KIR/KPR (eDavki ali Minimax)",
        _build_kirkpr_body,
        app,
        "_v21_kirkpr_collapsed",
        collapsed_default=False,
    )
    app._v21_kirkpr_area.grid(row=2, column=0, sticky="ew", pady=(2, 0))
    app._v21_kirkpr_area.grid_remove()
    app._v21_kirkpr_sub_nb = None
    app._v21_kir_source_nb = None
    app._v21_kpr_source_nb = None

    def _build_export_body(body: ttk.Frame) -> None:
        app._v21_export_tab_bar = _build_export_workflow_panel(app, body, titled=False)
        if hasattr(app, "register_v2_tab_bar"):
            app.register_v2_tab_bar(app._v21_export_tab_bar)

    app._v21_export_area = wrap_collapsible_frame(
        right_col,
        "Izvoz — Excel · knjižbe · Minimax API",
        _build_export_body,
        app,
        "_v21_export_collapsed",
        collapsed_default=False,
    )
    app._v21_export_area.grid(row=3, column=0, sticky="ew", pady=(4, 0))

    stack = ttk.Frame(right_col)
    app._v21_results_stack = stack
    stack.grid(row=4, column=0, sticky="nsew", pady=(4, 0))
    stack.rowconfigure(0, weight=1)
    stack.columnconfigure(0, weight=1)

    app._v21_page_tree = ttk.Frame(stack)
    app._v21_page_compare = ttk.Frame(stack)
    app._v21_page_files_compare = ttk.Frame(stack)
    app._v21_page_minimax = ttk.Frame(stack)
    for page in (
        app._v21_page_tree,
        app._v21_page_compare,
        app._v21_page_files_compare,
        app._v21_page_minimax,
    ):
        page.rowconfigure(0, weight=1)
        page.columnconfigure(0, weight=1)

    app._v21_results_panel = _build_results_panel(
        app,
        app._v21_page_tree,
        title="2. Drevo — Davčna blagajna (leto → mesec → dan → ZIP)",
        contextual_tab_actions=True,
        grid_column=0,
    )
    app._v21_page_tree.grid(row=0, column=0, sticky="nsew")

    _build_compare_page_v21(app, app._v21_page_compare)
    _build_files_compare_page_v21(app, app._v21_page_files_compare)
    _build_minimax_page_v21(app, app._v21_page_minimax)


def _build_compare_page_v21(app: core.App, parent: ttk.Frame) -> None:
    scroll_host = ttk.Frame(parent)
    scroll_host.grid(row=0, column=0, sticky="nsew")
    _canvas, body = _make_scroll_host(scroll_host)

    v2_muted(
        body,
        text="Primerjava eDavki KIR/KPR ↔ Minimax XML (izvoz iz Evidence KIRKPR).",
        wraplength=900,
        justify="left",
    ).pack(anchor="w", padx=4, pady=(8, 4))

    app._v21_compare_host = ttk.Frame(body)
    app._v21_compare_host.pack(fill="both", expand=True, padx=4, pady=(0, 8))


def _build_files_compare_page_v21(app: core.App, parent: ttk.Frame) -> None:
    parent.rowconfigure(1, weight=1)
    parent.columnconfigure(0, weight=1)

    top = ttk.Frame(parent)
    top.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 0))

    cmp_bar = ttk.Frame(top)
    cmp_bar.pack(fill="x")
    app._v21_btn_compare_files = _mk_btn(
        cmp_bar,
        text="Primerjaj datoteki (ročno)",
        command=app._safe_call(app._compare_files, "_compare_files"),
        hint=H.COMPARE_FILES,
        accent=False,
        app=app,
    )
    _mk_btn(
        cmp_bar,
        text="Primerjaj",
        command=app._safe_call(app._compare_files_presets, "_compare_files_presets"),
        hint="Zaženi označene primerjave za izbrano obdobje.",
        accent=True,
        app=app,
    ).pack(side="left", padx=(8, 0))

    presets = ttk.LabelFrame(top, text="Primerjaj", padding=(6, 3))
    presets.pack(fill="x", pady=(4, 0))

    app._v21_file_compare_presets_host = ttk.Frame(presets)
    app._v21_file_compare_presets_host.pack(fill="x")

    app._v21_file_compare_hint_label = v2_muted(
        top,
        text="Prednastavljeno: označi shranjene primerjave.",
        wraplength=900,
        justify="left",
    )
    app._v21_file_compare_hint_label.pack(anchor="w", pady=(2, 0))

    app._v21_files_compare_host = ttk.Frame(parent)
    app._v21_files_compare_host.grid(row=1, column=0, sticky="nsew", padx=4, pady=(4, 8))
    app._v21_files_compare_host.rowconfigure(0, weight=0)
    app._v21_files_compare_host.rowconfigure(1, weight=1)
    app._v21_files_compare_host.columnconfigure(0, weight=1)


def _build_minimax_page_v21(app: core.App, parent: ttk.Frame) -> None:
    scroll_host = ttk.Frame(parent)
    scroll_host.grid(row=0, column=0, sticky="nsew")
    _canvas, body = _make_scroll_host(scroll_host)

    v2_muted(
        body,
        text="Minimax pogled — nastavitve dokumenta so v spodnjem panelu «Minimax nastavitve».",
        wraplength=900,
        justify="center",
    ).pack(expand=True, pady=40)


def _build_footer_v21(app: core.App, parent: ttk.Frame) -> None:
    foot = tk.Frame(parent, bg=V2Theme.FOOTER_BG, height=28)
    foot.pack(fill="x")
    foot.pack_propagate(False)
    app.register_v2_chrome_frame(foot, footer=True)
    patch = get_current_patch_version()
    app.register_v2_chrome_label(
        tk.Label(
            foot,
            text=f"Davčna Blagajna {patch} · pogled · uvoz · izvoz · Verzija → Zgodovina sprememb",
            bg=V2Theme.FOOTER_BG,
            fg=V2Theme.FOOTER_FG,
        ),
        "footer",
    ).pack(side="left", padx=12, pady=4)
