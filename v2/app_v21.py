"""AppV2.1 — zavihki pogleda rezultatov, orodna vrstica kot 2.0."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import tkinter.messagebox as messagebox

import DavcnaBlagajna as core
from v2 import file_compare_settings
from v2.app import AppV2
from v2.menubar import setup_app_menubar
from v2.ui_build_v21 import build_ui_v21
from v2.version_journal import get_current_patch_version

AnalysisSnapshot = Tuple[
    Dict[Tuple[str, str], Dict[str, float]],
    Dict[Tuple[str, str, str], Dict[str, float]],
    core.DailyDocsMap,
    str,
]

KirkprSnapKey = Tuple[str, str]

V21_TAB_BLAGAJNA = 0
V21_TAB_KIRKPR = 1
V21_TAB_COMPARE = 2
V21_TAB_FILES_COMPARE = 3
V21_TAB_MINIMAX = 4

V21_KIRKPR_SUB_KIR = 0
V21_KIRKPR_SUB_KPR = 1
V21_KIRKPR_SRC_EDAVKI = 0
V21_KIRKPR_SRC_MINIMAX = 1


class AppV21(AppV2):
    UI_VERSION = "5.0"

    def __init__(self) -> None:
        self._v21_snap_blagajna: Optional[AnalysisSnapshot] = None
        self._v21_snap_kirkpr: Optional[AnalysisSnapshot] = None
        self._v21_kirkpr_snaps: Dict[KirkprSnapKey, Optional[AnalysisSnapshot]] = {}
        self._v21_view_tab_bar = None
        self._v21_view_nb = None
        self._v21_kirkpr_tab_bar = None
        self._v21_kirkpr_area = None
        self._v21_kirkpr_source_bar = None
        self._v21_kirkpr_sub_nb = None
        self._v21_kir_source_nb = None
        self._v21_kpr_source_nb = None
        self._v21_results_panel = None
        self._v21_page_tree = None
        self._v21_page_compare = None
        self._v21_page_files_compare = None
        self._v21_page_minimax = None
        self._v21_file_compare_presets_host = None
        self._v21_file_compare_hint_label = None
        self._v21_file_compare_choice_vars: Dict[int, Any] = {}
        self._v21_compare_host = None
        self._v21_compare_embed_active = False
        self._v21_compare_embed_use_files_host = False
        self._v21_restoring_view = False
        self._v21_active_view_tab = V21_TAB_BLAGAJNA
        self._v21_action_frm = None
        self._v21_btn_analyze_blagajna = None
        self._v21_btn_furs_blagajna = None
        self._v21_export_area = None
        self._v21_export_tab_bar = None
        self._v21_results_stack = None
        self._last_edavki_kirkpr_path = None
        self._last_minimax_kirkpr_path = None
        self._v21_kirkpr_snap_extra: Dict[KirkprSnapKey, Dict[str, Any]] = {}
        super().__init__()
        patch = get_current_patch_version()
        self.title(f"Davčna Blagajna {patch}")

    def _build_ui(self) -> None:
        setup_app_menubar(self, ui_version=self.UI_VERSION)
        build_ui_v21(self)
        self._rebuild_v21_file_compare_presets()

    def _rebuild_v21_file_compare_presets(self) -> None:
        host = getattr(self, "_v21_file_compare_presets_host", None)
        if host is None:
            return
        for child in host.winfo_children():
            child.destroy()
        self._v21_file_compare_choice_vars = {}
        definitions = file_compare_settings.load_file_compare_definitions_from_disk()
        for idx, definition in enumerate(definitions):
            if not bool(definition.get("enabled", True)):
                continue
            desc = (
                f"{idx + 1}) {definition.get('name', f'Primerjava {idx + 1}')}: "
                f"{file_compare_settings.describe_compare_side(definition.get('left', {}))} ↔ "
                f"{file_compare_settings.describe_compare_side(definition.get('right', {}))}"
            )
            var = core.tk.BooleanVar(value=bool(definition.get("selected", False)))
            self._v21_file_compare_choice_vars[idx] = var
            core.ttk.Checkbutton(host, text=desc, variable=var).pack(anchor="w", pady=1)
        hint = getattr(self, "_v21_file_compare_hint_label", None)
        if hint is not None:
            hint.configure(
                text=(
                    "Prednastavljeno: označi eno ali več shranjenih primerjav. "
                    "Uredi jih v Nastavitve → Primerjave datotek."
                )
            )

    def _bind_v21_view_tabs(self) -> None:
        if self._v21_view_tab_bar is None:
            return
        self._sync_v21_context_actions(V21_TAB_BLAGAJNA)
        self._on_v21_view_tab_changed()

    def _snapshot_current_analysis(self) -> AnalysisSnapshot:
        return (
            dict(self.monthly),
            dict(self.daily),
            copy.deepcopy(self.daily_docs),
            self._analysis_info_var.get(),
        )

    def _restore_analysis_snapshot(self, snap: Optional[AnalysisSnapshot]) -> None:
        self._v21_restoring_view = True
        try:
            if snap is None:
                self.monthly = {}
                self.daily = {}
                self.daily_docs = {}
                self._analysis_view_mode = "blagajna"
                self._kirkpr_export_ym = ("", "")
                self._kirkpr_meta = {}
                self._analysis_info_var.set(
                    "Vir podatkov: (ni naloženih podatkov — izberi mapo in zaženi analizo)"
                )
            else:
                monthly, daily, daily_docs, info = snap
                self.monthly = dict(monthly)
                self.daily = dict(daily)
                self.daily_docs = copy.deepcopy(daily_docs)
                self._analysis_info_var.set(info)
            self._sync_kirkpr_date_filter_ui()
            self._refresh_tree()
            self._refresh_analysis_source_info()
        finally:
            self._v21_restoring_view = False

    def _kirkpr_context(self) -> KirkprSnapKey:
        book = "KIR"
        source = "edavki"
        if self._v21_kirkpr_tab_bar is not None:
            if self._v21_kirkpr_tab_bar.active_index == V21_KIRKPR_SUB_KPR:
                book = "KPR"
        if (
            self._v21_kirkpr_source_bar is not None
            and self._v21_kirkpr_source_bar.active_index == V21_KIRKPR_SRC_MINIMAX
        ):
            source = "minimax"
        return book, source

    def _save_kirkpr_snapshot(self, book_u: str, source: str) -> None:
        book_u = (book_u or "KIR").strip().upper()
        src_key = (source or "edavki").strip().lower()
        self._v21_kirkpr_snaps[(book_u, src_key)] = self._snapshot_current_analysis()
        self._v21_kirkpr_snap_extra[(book_u, src_key)] = {
            "export_ym": tuple(self._kirkpr_export_ym),
            "meta": dict(self._kirkpr_meta),
            "date_filter": self.kirkpr_date_filter.get(),
        }

    def _load_kirkpr_both_books_from_file(
        self,
        file_path: Path,
        yyyy: str,
        mm: str,
        *,
        source: str,
    ) -> Dict[str, Dict[str, Any]]:
        """Iz ene ZIP/XML datoteke naloži KIR in KPR v ločena drevesa (posnetka)."""
        src_key = (source or "edavki").strip().lower()
        metas: Dict[str, Dict[str, Any]] = {}
        is_zip = file_path.suffix.lower() == ".zip"
        for book_u in ("KIR", "KPR"):
            if is_zip:
                meta = self._apply_kirkpr_zip_book(
                    file_path, yyyy, mm, book_u, source=src_key
                )
            else:
                meta = self._apply_kirkpr_xml_book(file_path, yyyy, mm, book_u)
            self._save_kirkpr_snapshot(book_u, src_key)
            metas[book_u] = meta
        return metas

    def _active_kirkpr_snapshot(self) -> Optional[AnalysisSnapshot]:
        return self._v21_kirkpr_snaps.get(self._kirkpr_context())

    def _sync_kirkpr_results_title(self) -> None:
        if self._v21_results_panel is None:
            return
        book, source = self._kirkpr_context()
        book_label = "KIR izdani računi" if book == "KIR" else "KPR prejeti računi"
        src_label = "eDavki" if source == "edavki" else "Minimax"
        self._v21_results_panel.configure(
            text=f"2. Drevo — {book_label} · {src_label} (leto → mesec → dan)"
        )

    def _show_v21_view_stack(self, idx: int) -> None:
        pages = (
            self._v21_page_tree,
            self._v21_page_compare,
            self._v21_page_files_compare,
            self._v21_page_minimax,
        )
        for page in pages:
            if page is not None:
                page.grid_remove()
        if idx in (V21_TAB_BLAGAJNA, V21_TAB_KIRKPR) and self._v21_page_tree is not None:
            self._v21_page_tree.grid(row=0, column=0, sticky="nsew")
        elif idx == V21_TAB_COMPARE and self._v21_page_compare is not None:
            self._v21_page_compare.grid(row=0, column=0, sticky="nsew")
        elif idx == V21_TAB_FILES_COMPARE and self._v21_page_files_compare is not None:
            self._v21_page_files_compare.grid(row=0, column=0, sticky="nsew")
        elif idx == V21_TAB_MINIMAX and self._v21_page_minimax is not None:
            self._v21_page_minimax.grid(row=0, column=0, sticky="nsew")

        if self._v21_kirkpr_area is not None:
            if idx == V21_TAB_KIRKPR:
                self._v21_kirkpr_area.grid(row=2, column=0, sticky="ew", pady=(2, 0))
            else:
                self._v21_kirkpr_area.grid_remove()

        if self._v21_export_area is not None:
            if idx == V21_TAB_BLAGAJNA:
                self._v21_export_area.grid(row=3, column=0, sticky="ew", pady=(4, 0))
            else:
                self._v21_export_area.grid_remove()

        if self._v21_results_stack is not None:
            stack_row = 4 if idx == V21_TAB_BLAGAJNA else 3
            self._v21_results_stack.grid(row=stack_row, column=0, sticky="nsew", pady=(4, 0))

    def _sync_v21_context_actions(self, idx: int) -> None:
        blagajna_btns = (self._v21_btn_furs_blagajna, self._v21_btn_analyze_blagajna)
        all_btns = blagajna_btns
        if all(btn is None for btn in all_btns):
            return
        for btn in all_btns:
            if btn is not None:
                btn.pack_forget()
        if idx == V21_TAB_BLAGAJNA:
            show = blagajna_btns
        else:
            show = ()
        for i, btn in enumerate(show):
            if btn is not None:
                btn.pack(side="left", padx=(0, 6) if i == 0 else (0, 0))

    def _restore_active_kirkpr_view(self) -> None:
        self._sync_kirkpr_results_title()
        ctx = self._kirkpr_context()
        extra = self._v21_kirkpr_snap_extra.get(ctx, {})
        self._analysis_view_mode = "kirkpr"
        self._kirkpr_export_ym = tuple(extra.get("export_ym", ("", "")))
        self._kirkpr_meta = dict(extra.get("meta", {}))
        date_f = extra.get("date_filter")
        if date_f:
            self.kirkpr_date_filter.set(str(date_f))
        self._restore_analysis_snapshot(self._active_kirkpr_snapshot())

    def _on_v21_kirkpr_source_tab_changed(self, _event: Any = None) -> None:
        if self._v21_restoring_view or self._v21_active_view_tab != V21_TAB_KIRKPR:
            return
        self._restore_active_kirkpr_view()

    def _on_v21_kirkpr_sub_tab_changed(self, _event: Any = None) -> None:
        if self._v21_restoring_view or self._v21_active_view_tab != V21_TAB_KIRKPR:
            return
        self._restore_active_kirkpr_view()

    def _on_v21_view_tab_changed(self, _event: Any = None) -> None:
        if self._v21_view_tab_bar is None or self._v21_restoring_view:
            return
        idx = self._v21_view_tab_bar.active_index
        self._v21_active_view_tab = idx
        self._show_v21_view_stack(idx)
        self._sync_v21_context_actions(idx)

        if idx == V21_TAB_BLAGAJNA:
            if self._v21_results_panel is not None:
                self._v21_results_panel.configure(
                    text="2. Drevo — Davčna blagajna (leto → mesec → dan → ZIP)"
                )
            self._analysis_view_mode = "blagajna"
            self._kirkpr_export_ym = ("", "")
            self._kirkpr_meta = {}
            self._restore_analysis_snapshot(self._v21_snap_blagajna)
        elif idx == V21_TAB_KIRKPR:
            self._restore_active_kirkpr_view()

    def _select_v21_view_tab(self, idx: int) -> None:
        if self._v21_view_tab_bar is None:
            return
        self._v21_view_tab_bar.select(idx, fire=False)
        self._on_v21_view_tab_changed()

    def _analyze(self) -> None:
        super()._analyze()
        self._v21_snap_blagajna = self._snapshot_current_analysis()
        self._select_v21_view_tab(V21_TAB_BLAGAJNA)

    def _active_kirkpr_source_or(self, default: str) -> str:
        return self._kirkpr_context()[1]

    def _uvozi_kirkpr(self) -> None:
        """Uvozi KIR in KPR iz iste datoteke — ločeni posnetki, zavihka KIR/KPR samo preklop pogleda."""
        _book, source = self._kirkpr_context()
        notify = core.get_access_options().get("show_action_result_dialogs", True)
        try:
            if source == "minimax":
                prepared = self._prepare_minimax_kirkpr_file()
                if prepared is None:
                    return
                file_path, yyyy, mm = prepared
                self._sync_output_dir_with_root()
                metas = self._load_kirkpr_both_books_from_file(
                    file_path, yyyy, mm, source="minimax"
                )
                file_label = self._display_path(file_path)
            else:
                prepared = self._prepare_kirkpr_zip()
                if prepared is None:
                    return
                zip_path, yyyy, mm = prepared
                self._sync_output_dir_with_root()
                metas = self._load_kirkpr_both_books_from_file(
                    zip_path, yyyy, mm, source="edavki"
                )
                file_label = self._display_path(zip_path)
        except (FileNotFoundError, ValueError) as exc:
            if notify:
                messagebox.showwarning("Uvozi podatke", str(exc))
            return

        self._sync_period_combos_from_ym(yyyy, mm)
        self._select_tree_month(yyyy, mm)
        self._select_v21_view_tab(V21_TAB_KIRKPR)
        self._restore_active_kirkpr_view()

        kir_rows = int(metas.get("KIR", {}).get("kir_rows", 0) or 0)
        kpr_rows = int(metas.get("KPR", {}).get("kpr_rows", 0) or 0)
        kir_docs = int(metas.get("KIR", {}).get("docs_total", 0) or 0)
        kpr_docs = int(metas.get("KPR", {}).get("docs_total", 0) or 0)
        src_label = "eDavki" if source == "edavki" else "Minimax"

        if kir_rows == 0 and kpr_rows == 0:
            if notify:
                messagebox.showwarning(
                    "Opozorilo",
                    f"Ni uporabnih podatkov KIR ali KPR ({src_label}).\n\nDatoteka: {file_label}",
                )
            return

        if notify:
            messagebox.showinfo(
                "Uvozi podatke",
                f"{src_label} · {yyyy}-{mm}\n"
                f"KIR: {kir_rows} vrstic, {kir_docs} dokumentov\n"
                f"KPR: {kpr_rows} vrstic, {kpr_docs} dokumentov\n\n"
                f"Zavihek KIR/KPR preklopi pogled med knjigama.\n\n"
                f"{file_label}",
            )

    def _analyze_kirkpr(self) -> None:
        """Združljivost z v2.0 — v 2.1 uporabi _uvozi_kirkpr."""
        self._uvozi_kirkpr()

    def _compare_kirkpr_edavki_minimax(
        self,
        edavki_path: Optional[Path] = None,
        minimax_path: Optional[Path] = None,
    ) -> None:
        self._select_v21_view_tab(V21_TAB_COMPARE)
        self._v21_compare_embed_active = True
        try:
            super()._compare_kirkpr_edavki_minimax(edavki_path, minimax_path)
        finally:
            self._v21_compare_embed_active = False

    def _compare_files(self) -> None:
        self._select_v21_view_tab(V21_TAB_FILES_COMPARE)
        self._v21_compare_embed_active = True
        self._v21_compare_embed_use_files_host = True
        try:
            super()._compare_files()
        finally:
            self._v21_compare_embed_active = False
            self._v21_compare_embed_use_files_host = False

    def _compare_files_presets(self) -> None:
        self._select_v21_view_tab(V21_TAB_FILES_COMPARE)
        self._v21_compare_embed_active = True
        self._v21_compare_embed_use_files_host = True
        try:
            super()._compare_files_presets()
        finally:
            self._v21_compare_embed_active = False
            self._v21_compare_embed_use_files_host = False
