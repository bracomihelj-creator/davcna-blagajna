"""Urejanje KIR/KPR vrstic — Minimax API knjižba."""

from __future__ import annotations

import threading
from typing import Any, Dict, List, Optional

import tkinter as tk
from tkinter import messagebox, ttk

import DavcnaBlagajna as core
from v2.filtered_combobox import attach_filtered_combobox
from v2.date_picker import SlDatePicker
from v2.kirkpr_knjizba_form_layout import (
    KPR_FIELD_KEY_TO_SUM_COL,
    knjizba_form_grid_positions,
    load_knjizba_form_layout_from_disk,
    resolve_knjizba_form_fields,
)


class KirkprMinimaxKnjizbaDialog(tk.Toplevel):
    """KIR/KPR: popravek in pošiljanje knjižbe v Minimax API."""

    def __init__(
        self,
        master: Any,
        *,
        book: str,
        source_row: Optional[int],
        doc_sums: Dict[str, float],
        yyyy: str,
        mm: str,
        dd: str,
        kirkpr_fields: Optional[Dict[str, str]] = None,
        doc_id: str = "",
        match_id: str = "",
    ) -> None:
        super().__init__(master)
        self._app = master
        self._book = (book or "KIR").strip().upper()
        self._is_kpr = self._book == "KPR"
        self._source_row = int(source_row) if source_row is not None else None
        self._yyyy, self._mm, self._dd = yyyy, mm, dd
        self._doc_sums = dict(doc_sums)
        self._kirkpr_fields = dict(kirkpr_fields or {})
        self._doc_id = (doc_id or "").strip()
        self._match_id = (match_id or "").strip()
        self._api_vars: Dict[str, tk.StringVar] = {}
        self._date_pickers: Dict[str, SlDatePicker] = {}
        self._label_to_code: Dict[str, str] = {}
        self._customer_label_to_id: Dict[str, str] = {}
        self._all_account_labels: List[str] = []
        self._all_customer_labels: List[str] = []
        self._customers_raw: List[Dict[str, Any]] = []
        self._customers_fb = False
        self._form_layout = load_knjizba_form_layout_from_disk()
        self._load_token = 0

        row_label = f" vrstica {self._source_row}" if self._source_row is not None else " — nov zapis"
        api_label = "ReceivedInvoice" if self._is_kpr else "IssuedInvoicePosting"
        self.title(f"Minimax knjižba — {self._book}{row_label}")
        self.transient(master)
        self.grab_set()
        w = int(self._form_layout.get("dialog_width") or 720)
        h = int(self._form_layout.get("dialog_height") or 640)
        self.geometry(f"{w}x{h}")
        self.minsize(480, 360)

        frm = ttk.Frame(self, padding=10)
        frm.pack(fill="both", expand=True)
        hint = (
            "Prejeti računi (KPR): polja P2/P4/P8–P21, API ReceivedInvoice. "
            if self._is_kpr
            else "Izdani računi (KIR): tip dokumenta, prihodki, API IssuedInvoicePosting. "
        )
        ttk.Label(
            frm,
            text=(
                f"{hint}"
                f"Zneski: 1.111,11. Postavitev: Nastavitve → Minimax knjižba ({self._book})."
            ),
            wraplength=max(400, w - 80),
        ).pack(anchor="w", pady=(0, 8))

        self._status_var = tk.StringVar(value="Nalagam podatke iz Minimax API …")
        ttk.Label(frm, textvariable=self._status_var, foreground="#444444").pack(
            anchor="w", pady=(0, 6)
        )

        self._form_host = ttk.Frame(frm)
        self._form_host.pack(fill="both", expand=True)

        btn_frm = ttk.Frame(frm)
        btn_frm.pack(fill="x", pady=(10, 0))
        self._btn_send = ttk.Button(
            btn_frm, text="Pošlji v Minimax API", command=self._send_api, state="disabled"
        )
        self._btn_send.pack(side="right")
        ttk.Button(btn_frm, text="Zapri", command=self.destroy).pack(side="right", padx=(0, 8))

        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.lift()
        self.focus_force()
        self._load_token += 1
        token = self._load_token
        self.after(10, lambda: self._begin_load(doc_sums, token))

    def _begin_load(self, doc_sums: Dict[str, float], token: int) -> None:
        if not self._alive() or token != self._load_token:
            return
        if self._is_kpr:
            try:
                tpl = self._app._build_kpr_minimax_knjizba_template_context(
                    self._yyyy,
                    self._mm,
                    self._dd,
                    doc_sums,
                    source_row=self._source_row,
                    kirkpr_fields=self._kirkpr_fields,
                )
                if self._alive() and token == self._load_token:
                    self._apply_loaded_context(tpl)
                    self._status_var.set(
                        "Obrazec iz evidence — nalagam podatke iz Minimax API …"
                    )
            except Exception as exc:
                core.log_error("KirkprMinimaxKnjizbaDialog._begin_load template", exc)
        self._start_load_context(doc_sums, token)

    def _start_load_context(self, doc_sums: Dict[str, float], token: int) -> None:
        if not self._alive() or token != self._load_token:
            return
        self.config(cursor="watch")
        if not self._form_host.winfo_children():
            self._status_var.set(
                "Nalagam podatke iz Minimax API … (počakajte, okno ostane odzivno)"
            )
        self.update_idletasks()

        def progress(msg: str) -> None:
            def ui() -> None:
                if self._alive() and token == self._load_token:
                    self._status_var.set(msg)
            self.after(0, ui)

        def work() -> None:
            err: Optional[BaseException] = None
            ctx: Optional[Dict[str, Any]] = None
            try:
                ctx = self._app._load_kirkpr_minimax_knjizba_context(
                    self._yyyy,
                    self._mm,
                    self._dd,
                    doc_sums,
                    book=self._book,
                    source_row=self._source_row,
                    kirkpr_fields=self._kirkpr_fields,
                    doc_id=self._doc_id,
                    match_id=self._match_id,
                    progress_cb=progress,
                )
            except BaseException as exc:
                err = exc
                core.log_error("KirkprMinimaxKnjizbaDialog._load_context", exc)

            def ui() -> None:
                if not self._alive() or token != self._load_token:
                    return
                self.config(cursor="")
                if err is not None:
                    messagebox.showerror("Minimax API", str(err), parent=self)
                    self.destroy()
                    return
                if ctx is not None:
                    self._apply_loaded_context(ctx)

            self.after(0, ui)

        threading.Thread(target=work, daemon=True).start()

    def _apply_loaded_context(self, ctx: Dict[str, Any]) -> None:
        self._label_to_code = dict(ctx.get("label_to_code") or {})
        self._customer_label_to_id = dict(ctx.get("label_to_customer_id") or {})
        self._all_account_labels = list(ctx.get("account_labels") or [])
        self._all_customer_labels = list(ctx.get("customer_labels") or [])
        self._customers_raw = list(ctx.get("customers") or [])
        self._customers_fb = bool(ctx.get("customers_fallback"))
        defaults = dict(ctx.get("defaults") or {})
        payload = ctx.get("payload") or {}
        accounts = ctx.get("accounts") or []
        accounts_fb = bool(ctx.get("accounts_fallback"))
        org_id = ctx.get("organisation_id")

        for child in self._form_host.winfo_children():
            child.destroy()
        self._date_pickers.clear()

        self._build_api_form(self._form_host, defaults, payload, accounts, accounts_fb, org_id)
        self._btn_send.configure(state="normal")

        acc_note = (
            f"Naloženih kont iz API: {len(accounts)} (org {org_id})."
            if accounts
            else "Konta iz API niso na voljo — vpiši kodo konta ročno."
            if accounts_fb
            else "Konta iz API niso na voljo."
        )
        api_source = str(ctx.get("api_source") or "template")
        matched_id = ctx.get("matched_minimax_id")
        if api_source in {"issuedinvoiceposting", "receivedinvoice"} and matched_id:
            acc_note = (
                f"Naloženo iz Minimax API ({api_source} ID {matched_id}). "
                f"{acc_note}"
            )
        elif self._is_kpr:
            jh = dict(ctx.get("journal_hints") or {})
            if jh.get("posted") and api_source == "template":
                acc_note = "Status Potrjen (iz knjiženja v temeljnici). " + acc_note
            if jh.get("konto") or jh.get("vezni_dokument"):
                parts = []
                if jh.get("konto"):
                    parts.append(f"konto {jh['konto']}")
                if jh.get("vezni_dokument"):
                    parts.append(f"vezni {jh['vezni_dokument']}")
                acc_note = f"Iz knjiženja (temeljnica): {', '.join(parts)}. " + acc_note
            elif self._source_row is not None:
                acc_note = (
                    "V Minimaxu ni bil najden ujemajoč zapis — prikazana je predloga. "
                    + acc_note
                )
        elif self._source_row is not None:
            acc_note = (
                "V Minimaxu ni bil najden ujemajoč zapis — prikazana je predloga. "
                + acc_note
            )
        self._status_var.set(acc_note)

    def _alive(self) -> bool:
        try:
            return bool(self.winfo_exists())
        except tk.TclError:
            return False

    def _build_api_form(
        self,
        parent: ttk.Frame,
        defaults: Dict[str, str],
        payload: Dict[str, Any],
        accounts: List[Dict[str, Any]],
        accounts_fb: bool,
        org_id: Any,
    ) -> None:
        layout = self._form_layout
        label_w = int(layout.get("label_width") or 22)
        entry_w = int(layout.get("entry_width") or 48)
        columns = int(layout.get("columns") or 1)
        dialog_w = int(layout.get("dialog_width") or 720)
        show_field_hints = columns < 2

        scroll_wrap = ttk.Frame(parent)
        scroll_wrap.pack(fill="both", expand=True)
        scroll_wrap.rowconfigure(0, weight=1)
        scroll_wrap.columnconfigure(0, weight=1)

        canvas = tk.Canvas(scroll_wrap, highlightthickness=0)
        vsb = ttk.Scrollbar(scroll_wrap, orient="vertical", command=canvas.yview)
        hsb = ttk.Scrollbar(scroll_wrap, orient="horizontal", command=canvas.xview)
        canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        inner = ttk.Frame(canvas)
        inner_win = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_inner_configure(_event: tk.Event) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event: tk.Event) -> None:
            canvas.itemconfigure(inner_win, height=event.height)

        inner.bind("<Configure>", _on_inner_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        def _on_mousewheel(event: tk.Event) -> None:
            if getattr(event, "num", None) == 5 or (getattr(event, "delta", 0) or 0) < 0:
                canvas.yview_scroll(1, "units")
            elif getattr(event, "num", None) == 4 or (getattr(event, "delta", 0) or 0) > 0:
                canvas.yview_scroll(-1, "units")

        def _on_shift_wheel(event: tk.Event) -> None:
            if getattr(event, "num", None) == 5 or (getattr(event, "delta", 0) or 0) < 0:
                canvas.xview_scroll(1, "units")
            elif getattr(event, "num", None) == 4 or (getattr(event, "delta", 0) or 0) > 0:
                canvas.xview_scroll(-1, "units")

        for widget in (canvas, inner, scroll_wrap):
            widget.bind("<MouseWheel>", _on_mousewheel)
            widget.bind("<Shift-MouseWheel>", _on_shift_wheel)
            widget.bind("<Button-4>", _on_mousewheel)
            widget.bind("<Button-5>", _on_mousewheel)

        doc_type = str(defaults.get("document_type") or "")
        if self._is_kpr:
            show_due = True
            show_tx = False
            show_customer = True
            show_invoice_date = True
        else:
            show_due = bool(payload.get("DateDue")) or doc_type in {"IRS", "AVA"}
            show_tx = bool(defaults.get("datum_transakcije")) or doc_type in {"IRS", "AVA"}
            show_customer = bool(defaults.get("stranka_id")) or core.minimax_document_type_customer_required(
                doc_type
            )
            show_invoice_date = False

        field_defs = resolve_knjizba_form_fields(
            layout,
            book=self._book,
            show_due=show_due,
            show_tx=show_tx,
            show_customer=show_customer,
            show_invoice_date=show_invoice_date,
        )
        positions = knjizba_form_grid_positions(field_defs, columns=columns)

        self._api_vars = {}
        max_row = 0
        for (field, (grid_row, grid_col)) in zip(field_defs, positions):
            key = field["key"]
            label = field["label"]
            kind = field["kind"]
            field_entry_w = int(field.get("entry_width") or 0)
            if field_entry_w <= 0:
                field_entry_w = entry_w
            max_row = max(max_row, grid_row + (2 if kind in ("konto", "customer") else 1))

            ttk.Label(inner, text=f"{label}:", width=label_w).grid(
                row=grid_row, column=grid_col, sticky="w", pady=2, padx=(0, 2)
            )
            var = tk.StringVar(value=str(defaults.get(key, "") or ""))
            self._api_vars[key] = var

            if kind == "konto":
                labels = list(self._label_to_code.keys())
                konto_val = str(defaults.get("konto_label") or defaults.get("konto") or "")
                if konto_val and labels and konto_val not in labels:
                    mapped = core.konto_combo_label_for_code(konto_val, self._label_to_code)
                    if mapped:
                        konto_val = mapped
                var.set(konto_val)
                widget = ttk.Combobox(
                    inner,
                    textvariable=var,
                    values=labels,
                    width=field_entry_w,
                )
                widget.grid(row=grid_row, column=grid_col + 1, sticky="ew", pady=2, padx=(4, 8))
                attach_filtered_combobox(
                    widget,
                    self._all_account_labels or labels,
                    mode="konto",
                    label_to_code=self._label_to_code,
                )
                if show_field_hints:
                    hint_row = grid_row + 1
                    hint = ttk.Label(
                        inner,
                        text=f"API konta (org {org_id}): {len(accounts)} — tipkaj npr. 41 za filter"
                        + (" — brez pravice Pregled kontov" if accounts_fb and not accounts else ""),
                        foreground="#666666",
                    )
                    hint.grid(row=hint_row, column=grid_col + 1, sticky="w", padx=(4, 8))
                    max_row = max(max_row, hint_row + 1)
            elif kind == "customer":
                labels = list(self._customer_label_to_id.keys())
                label_key = f"{key}_label"
                cust_val = str(defaults.get(label_key) or defaults.get(key) or "")
                if cust_val and cust_val.isdigit():
                    cust_val = core.customer_combo_label_for_id(
                        cust_val,
                        self._customer_label_to_id,
                        self._customers_raw,
                    )
                elif cust_val and labels and cust_val not in labels:
                    for lbl, cid in self._customer_label_to_id.items():
                        if cid == cust_val:
                            cust_val = lbl
                            break
                var.set(cust_val)
                widget = ttk.Combobox(
                    inner,
                    textvariable=var,
                    values=labels,
                    width=field_entry_w,
                )
                widget.grid(row=grid_row, column=grid_col + 1, sticky="ew", pady=2, padx=(4, 8))
                attach_filtered_combobox(
                    widget,
                    self._all_customer_labels or labels,
                    mode="customer",
                )
                if show_field_hints:
                    hint_row = grid_row + 1
                    n_cust = len(labels)
                    hint = ttk.Label(
                        inner,
                        text=f"API stranke/dobavitelji (org {org_id}): {n_cust} — tipkaj za filter (npr. qui)"
                        + (
                            " — brez pravice Pregled strank"
                            if self._customers_fb and not n_cust
                            else ""
                        ),
                        foreground="#666666",
                    )
                    hint.grid(row=hint_row, column=grid_col + 1, sticky="w", padx=(4, 8))
                    max_row = max(max_row, hint_row + 1)
            elif kind == "date_picker":
                picker = SlDatePicker(inner, textvariable=var)
                picker.grid(row=grid_row, column=grid_col + 1, sticky="w", pady=2, padx=(4, 8))
                self._date_pickers[key] = picker
            elif kind == "document_type":
                values = core.minimax_document_type_combobox_values()
                init = core.minimax_document_type_label_for_api(doc_type or var.get())
                if init not in values and values:
                    init = values[0]
                var.set(init)
                widget = ttk.Combobox(
                    inner,
                    textvariable=var,
                    values=values,
                    width=field_entry_w,
                    state="readonly",
                )
                widget.grid(row=grid_row, column=grid_col + 1, sticky="ew", pady=2, padx=(4, 8))
            elif kind == "status_kir":
                values = core.minimax_issued_status_combobox_values()
                init = core.minimax_issued_invoice_posting_status_label(var.get())
                if init not in values and values:
                    init = values[0]
                var.set(init)
                widget = ttk.Combobox(
                    inner,
                    textvariable=var,
                    values=values,
                    width=field_entry_w,
                    state="readonly",
                )
                widget.grid(row=grid_row, column=grid_col + 1, sticky="ew", pady=2, padx=(4, 8))
            elif kind == "status_kpr":
                values = core.minimax_received_status_combobox_values()
                init = core.minimax_received_invoice_status_label(var.get())
                if init not in values and values:
                    init = values[0]
                var.set(init)
                widget = ttk.Combobox(
                    inner,
                    textvariable=var,
                    values=values,
                    width=field_entry_w,
                    state="readonly",
                )
                widget.grid(row=grid_row, column=grid_col + 1, sticky="ew", pady=2, padx=(4, 8))
            else:
                widget = ttk.Entry(inner, textvariable=var, width=field_entry_w)
                widget.grid(row=grid_row, column=grid_col + 1, sticky="ew", pady=2, padx=(4, 8))

        if columns >= 2:
            for c in (1, 3):
                inner.columnconfigure(c, weight=1)
        else:
            inner.columnconfigure(1, weight=1)

        if layout.get("show_api_summary", True):
            self._build_api_summary(inner, payload, max_row, columns, dialog_w)

    def _build_api_summary(
        self,
        inner: ttk.Frame,
        payload: Dict[str, Any],
        max_row: int,
        columns: int,
        dialog_w: int,
    ) -> None:
        lines: List[str] = []
        if self._is_kpr:
            amt = payload.get("InvoiceAmount")
            if amt is not None:
                lines.append(f"Znesek računa: {core.format_amount_sl(float(amt or 0))}")
            cust = payload.get("Customer")
            if isinstance(cust, dict) and cust.get("ID") is not None:
                lines.append(f"Dobavitelj ID: {cust.get('ID')}")
        else:
            taxes = payload.get("IssuedInvoicePostingTaxes") or []
            pays = payload.get("IssuedInvoicePostingPaymentMethods") or []
            for tax in taxes:
                pct = tax.get("TaxPercentage")
                base = tax.get("TaxBase")
                amt = tax.get("TaxAmount")
                vat_acc = tax.get("VatAccountingType")
                lines.append(
                    f"DDV {pct}%: osnova {core.format_amount_sl(float(base or 0))}, "
                    f"davek {core.format_amount_sl(float(amt or 0))}, tip {vat_acc}"
                )
            for pay in pays:
                amt = pay.get("Amount")
                pm = pay.get("PaymentMethod") or {}
                pm_id = pm.get("ID") if isinstance(pm, dict) else pm
                lines.append(
                    f"Plačilo: {core.format_amount_sl(float(amt or 0))}"
                    + (f" (način ID {pm_id})" if pm_id else "")
                )
        if lines:
            extra = ttk.LabelFrame(inner, text="Podrobnosti iz API predloge", padding=6)
            extra.grid(
                row=max_row + 1,
                column=0,
                columnspan=4 if columns >= 2 else 2,
                sticky="ew",
                pady=(10, 0),
            )
            ttk.Label(extra, text="\n".join(lines), justify="left", wraplength=max(400, dialog_w - 80)).pack(
                anchor="w"
            )

    def _parse_amount_field(self, key: str) -> float:
        if key not in self._api_vars:
            return 0.0
        return core.parse_amount(self._api_vars[key].get())

    def _collect_sums_kir(self) -> Dict[str, float]:
        sums = core._zero_sum_cols()
        if "vrednost" in self._api_vars:
            sums["Vrednost računa"] = self._parse_amount_field("vrednost")
        if "osnova22" in self._api_vars:
            sums["Davčna osnova (22%)"] = self._parse_amount_field("osnova22")
        if "davek22" in self._api_vars:
            sums["Davek (22%)"] = self._parse_amount_field("davek22")
        if "osnova95" in self._api_vars:
            sums["Davčna osnova (9,5%)"] = self._parse_amount_field("osnova95")
        if "davek95" in self._api_vars:
            sums["Davek (9,5%)"] = self._parse_amount_field("davek95")
        if "neobdavcljive" in self._api_vars:
            sums[core.NEOBDAVCLJIVE_DISPLAY_COL] = self._parse_amount_field("neobdavcljive")
        if "oproscene" in self._api_vars:
            sums["Vrednost oproščenih dobav"] = self._parse_amount_field("oproscene")
        if not sums.get("Vrednost računa"):
            sums["Vrednost računa"] = self._doc_sums.get("Vrednost računa", 0.0)
        return sums

    def _collect_sums_kpr(self) -> Dict[str, float]:
        sums = core._zero_kpr_sum_cols()
        for key, col in KPR_FIELD_KEY_TO_SUM_COL.items():
            if key in self._api_vars:
                sums[col] = self._parse_amount_field(key)
        if "vrednost" in self._api_vars:
            sums["Vrednost računa"] = self._parse_amount_field("vrednost")
        elif not sums.get("Vrednost računa"):
            sums["Vrednost računa"] = self._doc_sums.get("Vrednost računa", 0.0)
        return sums

    def _collect_sums(self) -> Dict[str, float]:
        if self._is_kpr:
            return self._collect_sums_kpr()
        return self._collect_sums_kir()

    def _var_get(self, key: str, default: str = "") -> str:
        var = self._api_vars.get(key)
        return var.get() if var is not None else default

    def _send_api(self) -> None:
        status_raw = self._var_get("status")
        if self._is_kpr:
            status = core.parse_minimax_received_status(status_raw)
            st_listine = self._var_get("st_listine")
            vezni = self._var_get("vezni_dokument")
            opis = core.build_kpr_minimax_notes_text(
                st_listine,
                vezni,
                fallback=self._var_get("opis"),
            )
            customer_raw = self._var_get("dobavitelj_id")
            customer_id = core.minimax_customer_match_by_query(
                self._customers_raw,
                customer_raw,
                self._customer_label_to_id,
            )
        else:
            status = core.parse_minimax_issued_status(status_raw)
            opis = self._var_get("opis")
            st_listine = ""
            vezni = ""
            customer_id = core.parse_customer_combo_value(self._var_get("stranka_id"))
        doc_type = (
            core.parse_minimax_document_type_api(self._var_get("document_type"))
            if not self._is_kpr
            else ""
        )
        sums = self._collect_sums()
        datum = self._var_get("datum")
        konto = core.parse_konto_combo_value(self._var_get("konto"))
        date_due = self._var_get("datum_zapadlosti")
        date_tx = self._var_get("datum_transakcije")
        datum_racuna = self._var_get("datum_racuna")
        sklic = self._var_get("sklic")
        label = "Prejeti račun" if self._is_kpr else "Knjižba"

        self._btn_send.configure(state="disabled")
        self.config(cursor="watch")
        self._status_var.set("Pošiljam v Minimax API …")

        def work() -> None:
            err: Optional[BaseException] = None
            loc: Any = None
            try:
                loc = self._app._post_kirkpr_doc_minimax_api(
                    self._yyyy,
                    self._mm,
                    self._dd,
                    sums,
                    book=self._book,
                    datum=datum,
                    opis=opis,
                    konto=konto,
                    date_due=date_due,
                    date_transaction=date_tx,
                    datum_racuna=datum_racuna,
                    sklic=sklic,
                    customer_id=customer_id,
                    document_type=doc_type,
                    status=status,
                    st_listine=st_listine,
                    vezni_dokument=vezni,
                )
            except BaseException as exc:
                err = exc
                core.log_error("KirkprMinimaxKnjizbaDialog._send_api", exc)

            def ui() -> None:
                if not self._alive():
                    return
                self.config(cursor="")
                self._btn_send.configure(state="normal")
                if err is not None:
                    messagebox.showerror("Minimax API", str(err), parent=self)
                    self._status_var.set(f"Napaka: {err}")
                    return
                messagebox.showinfo("Minimax API", f"{label} ustvarjen.\n{loc}", parent=self)
                self.destroy()

            self.after(0, ui)

        threading.Thread(target=work, daemon=True).start()
