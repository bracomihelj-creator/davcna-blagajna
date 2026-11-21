# -*- coding: utf-8 -*-
"""Davčna Blagajna 5.1.00 — LOOK WebView2, stanje = isti AppV21 proces (brez Tk oken)."""
from __future__ import annotations

import ctypes
import json
import os
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(str(ROOT))

APP_VERSION = "5.1.00"
APP_TITLE = f"Davčna Blagajna {APP_VERSION}"
UI = ROOT / "ui"
PROFILE = ROOT / "data" / "webview2_profile"
APPEARANCE_FILE = ROOT / "data" / "appearance.json"
DEFAULT_APPEARANCE = {"theme": "light", "look": "t5", "accent": "#4f46e5", "radius": 12, "font_size": 13, "density": "normal"}
# Rollback (iz 4.0 »Odpri legacy 3.0.68«): nespremenjena Tk 3.0.68 v sosednji mapi — samo zaganjalnik.
LEGACY_TK_ROOT = Path(os.environ.get("DAVCNA_BLAGAJNA_LEGACY_ROOT") or r"D:\PISARNA\Python\DavčnaBlagajna")

VIEWS = ("Blagajna", "KIR/KPR", "Primerjaj KIRKPR", "Primerjaj datoteke", "Minimax")

ALLOWED_INVOKE = {
    "_analyze",
    "_open_furs_and_optional_month_location",
    "_open_furs_kir_kpr_and_optional_month_location",
    "_prenos_minimax_kirkpr",
    "_uvozi_kirkpr",
    "_analyze_kirkpr",
    "_compare_files",
    "_compare_files_presets",
    "_open_oauth_settings_dialog",
    "_open_kontiranje_placila_editor",
    "_open_kontiranje_prihodkov_editor",
    "_refresh_minimax_payment_methods",
    "_save",
    "_export_analysis_to_excel",
    "_copy_to_knjizbe",
    "_copy_daily_to_knjizbe",
    "_open_minimax_web_uvoz_browser",
    "_send_month_file_to_minimax_api",
    "_send_daily_to_minimax_api",
    "_pick_template",
    "_pick_root",
    "_pick_out",
    "_open_zip_packages_dialog",
    "_open_kirkpr_new_record_editor",
    "_apply_doc_filter",
    "_clear_doc_filter",
    "_on_show_neobdavcljive_toggle",
    "_on_kirkpr_date_filter_changed",
    "_tree_expand_all",
    "_tree_collapse_all",
    "_tree_clear_selected_result_row",
    "_load_companies",
    "_on_evidenca_filter_toggle",
    "_open_edavki_link_combo",
}

INVOKE_MSG = {
    "_analyze": "Analiziraj: uvoz končan.",
    "_on_evidenca_filter_toggle": "Filter evidence posodobljen.",
    "_load_companies": "Seznam firm osvežen.",
    "_on_show_neobdavcljive_toggle": "Prikaz neobdavčljivih posodobljen.",
    "_apply_doc_filter": "Filter dokumentov uporabljen.",
    "_clear_doc_filter": "Filter dokumentov počiščen.",
    "_tree_expand_all": "Drevo razširjeno.",
    "_tree_collapse_all": "Drevo skrčeno.",
    "_tree_clear_selected_result_row": "Vrstica odstranjena.",
    "_uvozi_kirkpr": "KIR/KPR uvožen.",
    "_send_daily_to_minimax_api": "Oddaja Excel (spletni uvoz) — ni prek API.",
    "_send_month_file_to_minimax_api": "Oddaja Excel (spletni uvoz) — ni prek API.",
    "_open_minimax_web_uvoz_browser": "Oddaja Excel (spletni uvoz) — ni prek API.",
}

NO_TREE_INVOKE = {
    "_on_evidenca_filter_toggle",
    "_load_companies",
    "_open_edavki_link_combo",
    "_open_oauth_settings_dialog",
    "_open_kontiranje_placila_editor",
    "_open_kontiranje_prihodkov_editor",
    "_open_zip_packages_dialog",
    "_open_kirkpr_new_record_editor",
    "_pick_template",
    "_pick_root",
    "_pick_out",
}

LOOK_TK_INVOKE = {
    "_open_oauth_settings_dialog": "oauth",
    "_open_zip_packages_dialog": "zip",
    "_open_kontiranje_placila_editor": "konti_pay",
    "_open_kontiranje_prihodkov_editor": "konti_vrsta",
    "_open_kirkpr_new_record_editor": "kirkpr",
}

OAUTH_FIELDS = (
    ("minimax_api_base", "Minimax API URL", False),
    ("minimax_scope", "Scope", False),
    ("minimax_client_id", "Client ID", False),
    ("minimax_client_secret", "Client secret", True),
    ("minimax_api_username", "API username", False),
    ("minimax_api_password", "API password", True),
    ("minimax_web_username", "Web username (uvoz; prazno=API)", False),
    ("minimax_web_password", "Web password (uvoz; prazno=API)", True),
    ("minimax_org_id", "Org ID", False),
    ("minimax_customer_id", "Customer ID (IRS/IRI/AVA)", False),
    ("minimax_payment_method_code", "Način plačila (koda; prazno=Gotovina)", False),
    ("minimax_vat_accounting_type_s", "DDV tip S", False),
    ("minimax_vat_accounting_type_z", "DDV tip Z", False),
    ("minimax_vat_accounting_type_n", "DDV tip N", False),
    ("minimax_vat_rate_22_search", "VAT rate lookup 22%", False),
    ("minimax_vat_rate_95_search", "VAT rate lookup 9,5%", False),
    ("minimax_vat_rate_0_search", "VAT rate lookup 0%", False),
)


def _sv(app: Any, name: str, default: str = "") -> str:
    var = getattr(app, name, None)
    if var is None:
        return default
    try:
        return str(var.get() or default)
    except Exception:
        return default


def _set_sv(app: Any, name: str, value: Any) -> None:
    var = getattr(app, name, None)
    if var is None:
        return
    try:
        var.set(value)
    except Exception:
        pass


def _clipboard_set_unicode(text: str) -> bool:
    if os.name != "nt":
        return False
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002
    for _ in range(6):
        try:
            if user32.OpenClipboard(0):
                try:
                    user32.EmptyClipboard()
                    data = (str(text) + "\0").encode("utf-16-le")
                    h = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
                    if not h:
                        continue
                    ptr = kernel32.GlobalLock(h)
                    if not ptr:
                        kernel32.GlobalFree(h)
                        continue
                    ctypes.memmove(ptr, data, len(data))
                    kernel32.GlobalUnlock(h)
                    if user32.SetClipboardData(CF_UNICODETEXT, h):
                        return True
                    kernel32.GlobalFree(h)
                finally:
                    user32.CloseClipboard()
        except Exception:
            pass
        time.sleep(0.12)
    try:
        import subprocess

        safe = str(text).replace("'", "''")
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", f"Set-Clipboard -Value '{safe}'"],
            capture_output=True,
            timeout=8,
        )
        return True
    except Exception:
        return False


def _patch_clipboard(app: Any) -> None:
    orig = getattr(app, "_set_clipboard_text", None)

    def _win32(text: str) -> None:
        if _clipboard_set_unicode(text):
            return
        if callable(orig):
            try:
                orig(text)
            except Exception:
                pass

    app._set_clipboard_text = _win32  # type: ignore[method-assign]


def _patch_look_window(app: Any) -> None:
    """LOOK: Tk ostane skrit — po API nikoli deiconify."""

    def _keep_hidden(_event: Any = None) -> None:
        try:
            app.withdraw()
            app.attributes("-alpha", 0)
        except Exception:
            pass

    def _restore() -> None:
        _keep_hidden()

    def _snap() -> None:
        _keep_hidden()

    app._restore_main_window_after_api = _restore  # type: ignore[method-assign]
    app._snapshot_main_window = _snap  # type: ignore[method-assign]
    app.deiconify = lambda *a, **k: _keep_hidden()  # type: ignore[method-assign]
    app.wm_deiconify = lambda *a, **k: _keep_hidden()  # type: ignore[method-assign]
    app.lift = lambda *a, **k: None  # type: ignore[method-assign]
    app.focus_force = lambda *a, **k: None  # type: ignore[method-assign]
    try:
        app.bind("<Map>", _keep_hidden)
    except Exception:
        pass
    _keep_hidden()


class _LookDialogs:
    """LOOK nima Tk oken — messagebox gre v statusno vrstico."""

    def __init__(self) -> None:
        self.title = ""
        self.msg = ""
        self.kind = ""

    def clear(self) -> None:
        self.title = ""
        self.msg = ""
        self.kind = ""

    def _cap(self, kind: str, title: Any, message: Any) -> None:
        self.kind = kind
        self.title = str(title or "")
        self.msg = str(message or "")

    def showinfo(self, title: Any = "", message: Any = "", **_kw: Any) -> str:
        self._cap("info", title, message)
        return "ok"

    def showwarning(self, title: Any = "", message: Any = "", **_kw: Any) -> str:
        self._cap("warning", title, message)
        return "ok"

    def showerror(self, title: Any = "", message: Any = "", **_kw: Any) -> str:
        self._cap("error", title, message)
        return "ok"

    def askyesno(self, title: Any = "", message: Any = "", **_kw: Any) -> bool:
        self._cap("ask", title, message)
        return True

    def askokcancel(self, title: Any = "", message: Any = "", **_kw: Any) -> bool:
        self._cap("ask", title, message)
        return True

    def look_msg(self) -> str:
        if not self.title and not self.msg:
            return ""
        first = (self.msg.split("\n") or [""])[0].strip()
        if "uspeh" in self.title.lower() and "api" in self.title.lower():
            return first or "Oddaja prek API. Odprto Knjiženje."
        if "spletni uvoz" in self.title.lower() or "spletni uvoz" in self.msg.lower():
            extra = first
            base = "Oddaja Excel (spletni uvoz) — ni prek API."
            if extra and extra.casefold() not in base.casefold():
                return f"{base} {extra}"
            return base
        if self.kind == "error":
            return (f"{self.title}: {first}" if first else self.title).strip(": ")
        return first or self.title


LOOK_DIALOGS = _LookDialogs()


def _folder_has_blagajna_data(app: Any) -> bool:
    """True, če v mapi Blagajna že so YYYY-MM mape ali ZIP."""
    from DavcnaBlagajna import data_root_has_month_sources, resolve_analysis_data_root

    raw = _sv(app, "root_dir")
    if not raw:
        return False
    try:
        root = app._to_path(raw)
    except Exception:
        root = Path(raw)
    try:
        source = resolve_analysis_data_root(root)
    except Exception:
        source = root
    try:
        return bool(data_root_has_month_sources(source))
    except Exception:
        return False

PRENOS_INVOKE = {
    "_send_daily_to_minimax_api",
    "_send_month_file_to_minimax_api",
    "_open_minimax_web_uvoz_browser",
}


def _look_prenos_status(app: Any, nm: str, look: str) -> Dict[str, Any]:
    """LOOK pasica: API uspeh ali jasno Oddaja Excel, če ni API."""
    title = (LOOK_DIALOGS.title or "").casefold()
    body = (LOOK_DIALOGS.msg or look or "").casefold()
    kind = LOOK_DIALOGS.kind
    if "uspeh" in title and "api" in title:
        return {
            "ok": True,
            "channel": "api",
            "msg": look or "Oddaja prek API. Odprto Knjiženje.",
        }
    api_possible = False
    try:
        api_possible = bool(app._minimax_api_send_possible())
    except Exception:
        api_possible = False
    excel = (
        nm == "_open_minimax_web_uvoz_browser"
        or "spletni uvoz" in title
        or "spletni uvoz" in body
        or (nm in PRENOS_INVOKE and not api_possible)
        or (kind == "error" and "api" in title)
    )
    if excel:
        extra = (look or "").split("\n")[0].strip()
        msg = "Oddaja Excel (spletni uvoz) — ni prek API."
        if extra and extra.casefold() not in msg.casefold():
            msg = f"{msg} {extra}"
        return {
            "ok": kind not in ("error", "warning"),
            "channel": "excel",
            "msg": msg,
        }
    return {
        "ok": kind != "error",
        "channel": "api" if api_possible else "excel",
        "msg": look or INVOKE_MSG.get(nm, "Končano."),
    }


def _win_browse_folder(title: str = "Izberi mapo") -> str:
    """Windows izbor mape — ni Tk okna."""
    try:
        from ctypes import wintypes

        class BROWSEINFO(ctypes.Structure):
            _fields_ = [
                ("hwndOwner", wintypes.HWND),
                ("pidlRoot", ctypes.c_void_p),
                ("pszDisplayName", ctypes.c_wchar_p),
                ("lpszTitle", ctypes.c_wchar_p),
                ("ulFlags", wintypes.UINT),
                ("lpfn", ctypes.c_void_p),
                ("lParam", ctypes.c_long),
                ("iImage", ctypes.c_int),
            ]

        shell32 = ctypes.windll.shell32
        ole32 = ctypes.windll.ole32
        buf = ctypes.create_unicode_buffer(260)
        bi = BROWSEINFO()
        bi.lpszTitle = title
        bi.ulFlags = 0x0001 | 0x0040
        pidl = shell32.SHBrowseForFolderW(ctypes.byref(bi))
        if not pidl:
            return ""
        ok = shell32.SHGetPathFromIDListW(pidl, buf)
        ole32.CoTaskMemFree(pidl)
        return buf.value if ok else ""
    except Exception:
        return ""


def _win_open_file(title: str = "Izberi datoteko") -> str:
    """Windows izbor datoteke — ni Tk okna."""
    try:
        from ctypes import wintypes

        class OPENFILENAME(ctypes.Structure):
            _fields_ = [
                ("lStructSize", wintypes.DWORD),
                ("hwndOwner", wintypes.HWND),
                ("hInstance", wintypes.HINSTANCE),
                ("lpstrFilter", ctypes.c_wchar_p),
                ("lpstrCustomFilter", ctypes.c_wchar_p),
                ("nMaxCustFilter", wintypes.DWORD),
                ("nFilterIndex", wintypes.DWORD),
                ("lpstrFile", ctypes.c_wchar_p),
                ("nMaxFile", wintypes.DWORD),
                ("lpstrFileTitle", ctypes.c_wchar_p),
                ("nMaxFileTitle", wintypes.DWORD),
                ("lpstrInitialDir", ctypes.c_wchar_p),
                ("lpstrTitle", ctypes.c_wchar_p),
                ("Flags", wintypes.DWORD),
                ("nFileOffset", wintypes.WORD),
                ("nFileExtension", wintypes.WORD),
                ("lpstrDefExt", ctypes.c_wchar_p),
                ("lCustData", ctypes.c_void_p),
                ("lpfnHook", ctypes.c_void_p),
                ("lpTemplateName", ctypes.c_wchar_p),
                ("pvReserved", ctypes.c_void_p),
                ("dwReserved", wintypes.DWORD),
                ("FlagsEx", wintypes.DWORD),
            ]

        OFN_PATHMUSTEXIST = 0x00000800
        OFN_FILEMUSTEXIST = 0x00001000
        OFN_EXPLORER = 0x00080000
        buf = ctypes.create_unicode_buffer(32768)
        ofn = OPENFILENAME()
        ofn.lStructSize = ctypes.sizeof(OPENFILENAME)
        ofn.lpstrFile = ctypes.cast(buf, ctypes.c_wchar_p)
        ofn.nMaxFile = len(buf)
        ofn.lpstrTitle = title
        ofn.lpstrFilter = "Vse datoteke\0*.*\0"
        ofn.nFilterIndex = 1
        ofn.Flags = OFN_EXPLORER | OFN_PATHMUSTEXIST | OFN_FILEMUSTEXIST
        if ctypes.windll.comdlg32.GetOpenFileNameW(ctypes.byref(ofn)):
            return buf.value or ""
        return ""
    except Exception:
        return ""


def _install_no_tk_dialogs() -> None:
    """LOOK: ni Tk messagebox, Toplevel, filedialog, colorchooser."""
    import tkinter as tk
    import tkinter.messagebox as tmb
    from tkinter import colorchooser, filedialog, simpledialog

    def _show(title: Any = None, message: Any = None, _icon: Any = None, _type: Any = None, **_options: Any) -> str:
        LOOK_DIALOGS._cap("info", title, message)
        typ = str(_type or "").lower()
        if "yesno" in typ or "okcancel" in typ:
            return "yes"
        return "ok"

    tmb._show = _show  # type: ignore[method-assign]
    tmb.showinfo = LOOK_DIALOGS.showinfo  # type: ignore[method-assign]
    tmb.showwarning = LOOK_DIALOGS.showwarning  # type: ignore[method-assign]
    tmb.showerror = LOOK_DIALOGS.showerror  # type: ignore[method-assign]
    tmb.askyesno = LOOK_DIALOGS.askyesno  # type: ignore[method-assign]
    tmb.askokcancel = LOOK_DIALOGS.askokcancel  # type: ignore[method-assign]
    tmb.askyesnocancel = LOOK_DIALOGS.askyesno  # type: ignore[method-assign]
    tmb.askretrycancel = LOOK_DIALOGS.askokcancel  # type: ignore[method-assign]
    tmb.askquestion = LOOK_DIALOGS.askyesno  # type: ignore[method-assign]

    orig_tl = tk.Toplevel

    class _LookToplevel(orig_tl):  # type: ignore[valid-type,misc]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            super().__init__(*args, **kwargs)
            self._look_hide()
            try:
                self.bind("<Map>", lambda _e: self._look_hide())
            except Exception:
                pass

        def _look_hide(self) -> None:
            try:
                orig_tl.withdraw(self)
            except Exception:
                pass
            try:
                orig_tl.attributes(self, "-alpha", 0)
            except Exception:
                pass

        def deiconify(self, *a: Any, **k: Any) -> None:
            self._look_hide()

        def wm_deiconify(self, *a: Any, **k: Any) -> None:
            self._look_hide()

        def lift(self, *a: Any, **k: Any) -> None:
            return None

        def focus_force(self, *a: Any, **k: Any) -> None:
            return None

        def grab_set(self, *a: Any, **k: Any) -> None:
            return None

        def grab_set_global(self, *a: Any, **k: Any) -> None:
            return None

    tk.Toplevel = _LookToplevel  # type: ignore[misc]
    filedialog.askdirectory = lambda *a, **k: _win_browse_folder(str(k.get("title") or "Izberi mapo"))  # type: ignore[method-assign]
    filedialog.askopenfilename = lambda *a, **k: _win_open_file(str(k.get("title") or "Izberi datoteko"))  # type: ignore[method-assign]
    filedialog.asksaveasfilename = lambda *a, **k: _win_open_file(str(k.get("title") or "Shrani datoteko"))  # type: ignore[method-assign]
    filedialog.askopenfilenames = lambda *a, **k: ()  # type: ignore[method-assign]
    simpledialog.askstring = lambda *a, **k: None  # type: ignore[method-assign]
    simpledialog.askinteger = lambda *a, **k: None  # type: ignore[method-assign]
    simpledialog.askfloat = lambda *a, **k: None  # type: ignore[method-assign]
    colorchooser.askcolor = lambda *a, **k: (None, None)  # type: ignore[method-assign]


def _find_iid_by_tag(app: Any, node_id: str) -> Optional[str]:
    tree = getattr(app, "tree", None)
    if tree is None or not node_id:
        return None

    def walk(parent: str = "") -> Optional[str]:
        for iid in tree.get_children(parent):
            tags = tree.item(iid, "tags") or ()
            if node_id in tags or (tags and str(tags[0]) == node_id) or str(iid) == node_id:
                return str(iid)
            found = walk(str(iid))
            if found:
                return found
        return None

    return walk()


def _look_detail(app: Any, node_id: str) -> Dict[str, Any]:
    """Analitični podatki za panel Izbrano (isti zneski kot 3.0.68)."""
    from DavcnaBlagajna import (
        SUM_COLS,
        _rollup_sum_col_for_tree,
        _tree_sums_with_debet_vr,
        _zero_sum_cols,
        format_float,
        sum_col_is_nonzero,
    )

    nid = str(node_id or "").strip()
    empty = {"detail_title": "(ni izbire)", "detail_rows": []}
    if not nid:
        return empty
    parts = nid.split(":")
    kind = parts[0] if parts else ""
    try:
        monthly, daily, daily_docs = app._tree_view_data()
    except Exception:
        monthly = getattr(app, "monthly", None) or {}
        daily = getattr(app, "daily", {}) or {}
        daily_docs = getattr(app, "daily_docs", {}) or {}
    title = nid
    sums = _zero_sum_cols()
    extra: List[Dict[str, str]] = []
    try:
        if kind == "day" and len(parts) >= 4:
            yyyy, mm, dd = parts[1], f"{int(parts[2]):02d}", f"{int(parts[3]):02d}"
            title = f"Dan {dd}.{mm}.{yyyy}"
            raw = daily.get((yyyy, mm, dd)) or daily.get((yyyy, mm, str(int(parts[3])))) or _zero_sum_cols()
            sums = _tree_sums_with_debet_vr(raw)
        elif kind == "month" and len(parts) >= 3:
            yyyy, mm = parts[1], f"{int(parts[2]):02d}"
            title = f"Mesec {yyyy}-{mm}"
            sums = _tree_sums_with_debet_vr(monthly.get((yyyy, mm), _zero_sum_cols()))
        elif kind == "doc" and len(parts) >= 5:
            yyyy, mm, dd, doc_key = parts[1], f"{int(parts[2]):02d}", f"{int(parts[3]):02d}", parts[4]
            docs = daily_docs.get((yyyy, mm, dd), []) or []
            doc = next(
                (d for d in docs if str(getattr(d, "source_row", "")) == doc_key or str(getattr(d, "doc_id", "")) == doc_key),
                None,
            )
            if doc is not None:
                title = f"Dokument: {getattr(doc, 'doc_id', doc_key)}"
                sums = _tree_sums_with_debet_vr(getattr(doc, "sums", {}) or {})
                fields = getattr(doc, "kirkpr_fields", None) or {}
                for tag in sorted(fields.keys(), key=lambda t: int(str(t)[1:]) if str(t)[1:].isdigit() else 0):
                    extra.append({"label": str(tag), "value": str(fields[tag])})
            else:
                title = "Dokument"
        elif kind == "yearsum" and len(parts) >= 2:
            yyyy = parts[1]
            title = f"Skupaj leto {yyyy}"
            for (y, _m), s in monthly.items():
                if str(y) == yyyy:
                    for c in SUM_COLS:
                        sums[c] = float(sums.get(c, 0.0)) + float(_rollup_sum_col_for_tree(c, s))
        elif kind == "year" and len(parts) >= 2:
            yyyy = parts[1]
            title = f"Leto {yyyy}"
            for (y, _m), s in monthly.items():
                if str(y) == yyyy:
                    for c in SUM_COLS:
                        sums[c] = float(sums.get(c, 0.0)) + float(_rollup_sum_col_for_tree(c, s))
        elif kind == "grandtotal":
            title = "Skupaj vse"
            for s in monthly.values():
                for c in SUM_COLS:
                    sums[c] = float(sums.get(c, 0.0)) + float(_rollup_sum_col_for_tree(c, s))
        elif kind == "zipfile" and len(parts) >= 4:
            yyyy, mm, name = parts[1], f"{int(parts[2]):02d}", ":".join(parts[3:])
            title = f"ZIP {name}"
            try:
                loaded_n, loaded_vr = app._month_stats_from_loaded_docs(yyyy, mm, name)
                sums = _zero_sum_cols()
                sums["Vrednost računa"] = float(loaded_vr or 0.0)
                extra.append({"label": "Dokumentov (naloženo)", "value": str(loaded_n)})
            except Exception:
                pass
    except Exception:
        pass
    rows = extra + [
        {"label": str(c), "value": format_float(val)}
        for c, val in sums.items()
        if sum_col_is_nonzero(float(val or 0.0))
    ]
    return {"detail_title": title, "detail_rows": rows}


def _normalize_appearance(data: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(DEFAULT_APPEARANCE)
    out.update(data or {})
    out["theme"] = "dark" if str(out.get("theme") or "").strip().lower() == "dark" else "light"
    out["look"] = "t4" if str(out.get("look") or "").strip().lower() == "t4" else "t5"
    dens = str(out.get("density") or "normal").strip().lower()
    out["density"] = dens if dens in ("compact", "comfortable") else "normal"
    return out


def _load_appearance() -> Dict[str, Any]:
    data = dict(DEFAULT_APPEARANCE)
    try:
        if APPEARANCE_FILE.is_file():
            raw = json.loads(APPEARANCE_FILE.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                data.update(raw)
    except Exception:
        pass
    return _normalize_appearance(data)


def _save_appearance(data: Dict[str, Any]) -> Dict[str, Any]:
    merged = _normalize_appearance(data or {})
    APPEARANCE_FILE.parent.mkdir(parents=True, exist_ok=True)
    APPEARANCE_FILE.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return merged


class Bridge:
    """js_api — LOOK je HTML; klici gredo na isti AppV21 (skriti motor, ni Tk okna)."""

    def __init__(self, app: Any) -> None:
        self.app = app
        self._tree_opened: set = set()

    def _call_tk(self, fn: Callable[[], Any], timeout: float = 300.0) -> Any:
        box: Dict[str, Any] = {}
        done = threading.Event()

        def run() -> None:
            try:
                box["v"] = fn()
            except Exception as exc:
                box["e"] = exc
            finally:
                done.set()

        try:
            self.app.after(0, run)
        except Exception:
            return fn()
        if not done.wait(timeout):
            raise TimeoutError("Tk klic je potekel.")
        if "e" in box:
            raise box["e"]
        return box.get("v")

    def ping(self) -> Dict[str, Any]:
        return {"ok": True, "version": APP_VERSION}

    def _auto_import_folder_unlocked(self, *, force: bool = False) -> str:
        """Če v mapi Blagajna so CSV/ZIP, poženi isti _analyze kot gumb Analiziraj."""
        app = self.app
        if not getattr(app, "selected_company", None):
            return ""
        monthly = getattr(app, "monthly", None) or {}
        if monthly and not force:
            return ""
        if not _folder_has_blagajna_data(app):
            return ""
        app._session_restore_silent = True
        try:
            app._analyze()
        except Exception as exc:
            return f"V mapi so datoteke, uvoz ni uspel: {exc}"
        finally:
            app._session_restore_silent = False
        n = len(getattr(app, "monthly", {}) or {})
        if not n:
            return "V mapi so datoteke, za izbrano obdobje ni vrstic."
        y = _sv(app, "period_year")
        m = _sv(app, "period_month")
        self._tree_opened.clear()
        if y:
            self._tree_opened.add(f"year:{y}")
        if y and m:
            try:
                self._tree_opened.add(f"month:{y}:{int(m):02d}")
            except Exception:
                self._tree_opened.add(f"month:{y}:{m}")
        for key in (getattr(app, "monthly", {}) or {}):
            if not isinstance(key, (tuple, list)) or len(key) < 2:
                continue
            self._tree_opened.add(f"year:{key[0]}")
            self._tree_opened.add(f"month:{key[0]}:{key[1]}")
        return f"Analiziraj: uvoženo iz mape ({n} mesecev)."

    def import_if_folder_has_data(self, force: Any = False) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            msg = self._auto_import_folder_unlocked(force=bool(force))
            snap = self._snapshot_unlocked(include_tree=True)
            snap["ok"] = True
            snap["force_tree"] = True
            snap["msg"] = msg or "V mapi ni CSV/ZIP za samodejni uvoz."
            return snap

        return self._call_tk(work)

    def boot(self) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            imported = self._auto_import_folder_unlocked()
            snap = self._snapshot_unlocked(include_tree=True)
            snap["ok"] = True
            if imported:
                snap["msg"] = imported
                snap["force_tree"] = True
            snap["views"] = list(VIEWS)
            snap["appearance"] = _load_appearance()
            try:
                import DavcnaBlagajna as core

                snap["doc_types"] = list(core.minimax_document_type_combobox_values())
                snap["vrsta_labels"] = list(core.VRSTA_PRODAJE_LABELS)
            except Exception:
                snap["doc_types"] = []
                snap["vrsta_labels"] = []
            try:
                from v2.edavki_links_settings import combo_labels, load_edavki_links_from_disk

                snap["edavki_links"] = list(combo_labels(load_edavki_links_from_disk()))
            except Exception:
                snap["edavki_links"] = []
            snap["edavki_link"] = _sv(self.app, "_edavki_link_var")
            try:
                snap["years"] = list(self.app._period_year_combo_values())
            except Exception:
                snap["years"] = []
            return snap

        return self._call_tk(work)

    def snapshot(self) -> Dict[str, Any]:
        return self._call_tk(self._snapshot_unlocked)

    def _snapshot_unlocked(self, include_tree: bool = True) -> Dict[str, Any]:
        app = self.app
        tree: Dict[str, Any] = {"columns": [], "value_columns": [], "sum_columns": [], "nodes": []}
        if include_tree:
            from tree_view import serialize_look_tree

            tree = serialize_look_tree(app, self._tree_opened)
        checked: List[str] = []
        try:
            checked = sorted(str(x) for x in (getattr(app, "_tree_checked", set()) or set()))
        except Exception:
            pass
        sel = getattr(app, "selected_company", None) or {}
        y = _sv(app, "period_year")
        m = _sv(app, "period_month")
        root_path = _sv(app, "root_dir")
        zip_hint = ""
        try:
            if root_path and y and m:
                zip_hint = str(Path(root_path) / f"{int(y):04d}-{int(m):02d}.zip")
        except Exception:
            zip_hint = ""
        selenium_auto = False
        try:
            import DavcnaBlagajna as core

            selenium_auto = bool(core.get_access_options().get("selenium_auto", False))
        except Exception:
            selenium_auto = False
        view_idx = int(getattr(app, "_v21_active_view_tab", 0) or 0)
        kirkpr_book = 0
        kirkpr_source = 0
        try:
            if getattr(app, "_v21_kirkpr_tab_bar", None) is not None:
                kirkpr_book = int(app._v21_kirkpr_tab_bar.active_index)
            if getattr(app, "_v21_kirkpr_source_bar", None) is not None:
                kirkpr_source = int(app._v21_kirkpr_source_bar.active_index)
        except Exception:
            pass
        return {
            "version": APP_VERSION,
            "title": APP_TITLE,
            "year": y,
            "month": m,
            "root_path": root_path,
            "out_dir": _sv(app, "out_dir"),
            "out_file": _sv(app, "out_file"),
            "sheet_name": _sv(app, "sheet_name"),
            "csv_name": _sv(app, "csv_name"),
            "template_path": _sv(app, "template_path"),
            "include_zips": bool(getattr(app, "include_zips", None) and app.include_zips.get()),
            "show_neob": bool(getattr(app, "show_neobdavcljive", None) and app.show_neobdavcljive.get()),
            "filter_evidenca": bool(
                getattr(app, "filter_evidenca_davcnih", None) and app.filter_evidenca_davcnih.get()
            ),
            "ddv_zavezanec": bool(
                getattr(app, "minimax_ddv_zavezanec", None) and app.minimax_ddv_zavezanec.get()
            ),
            "doc_filter": _sv(app, "doc_filter"),
            "company_search": _sv(app, "company_search"),
            "minimax_status": _sv(app, "minimax_status"),
            "company_label": _sv(app, "selected_company_label"),
            "analysis_info": _sv(app, "_analysis_info_var"),
            "checked_sum": _sv(app, "_tree_checked_sum_var"),
            "org_id": str(sel.get("Org_ID") or _sv(app, "minimax_org_id")),
            "zst": str(sel.get("Zšt") or ""),
            "source": _sv(app, "companies_source_label"),
            "doc_type": _sv(app, "minimax_document_type"),
            "vrsta_prodaje": _sv(app, "vrsta_prodaje"),
            "pay": _sv(app, "payment_method_label"),
            "edavki_link": _sv(app, "_edavki_link_var"),
            "kirkpr_date_filter": _sv(app, "kirkpr_date_filter"),
            "furs_zip": zip_hint,
            "selenium_auto": selenium_auto,
            "view_idx": view_idx,
            "kirkpr_book": kirkpr_book,
            "kirkpr_source": kirkpr_source,
            "tree": tree,
            "checked": checked,
        }

    def companies(self, q: str = "") -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            app = self.app
            if q is not None:
                _set_sv(app, "company_search", str(q))
            try:
                app._render_companies()
            except Exception:
                pass
            rows = list(getattr(app, "companies_all", []) or [])
            needle = (q or _sv(app, "company_search") or "").strip().casefold()
            ev_only = bool(
                getattr(app, "filter_evidenca_davcnih", None) and app.filter_evidenca_davcnih.get()
            )
            out: List[Dict[str, str]] = []
            ev_n = 0
            for c in rows:
                mark = "☐"
                try:
                    mark = app._company_evidenca_checkbox(c)
                except Exception:
                    pass
                in_ev = mark == "☑"
                if in_ev:
                    ev_n += 1
                if ev_only and not in_ev:
                    continue
                if needle:
                    hay = " ".join(
                        str(c.get(k) or "")
                        for k in ("Zšt", "NAZIV", "DAVČNA", "DURS sifra", "Email", "NASLOV", "Org_ID")
                    ).casefold()
                    if needle not in hay:
                        continue
                row = dict(c)
                row["Ev."] = mark
                out.append(row)
            return {
                "ok": True,
                "companies": out[:800],
                "count": len(out),
                "total": len(rows),
                "evidenca_count": ev_n,
                "source": _sv(app, "companies_source_label"),
            }

        return self._call_tk(work)

    def select_company(self, zst: str) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            zst_s = str(zst or "").strip()
            company = next(
                (
                    c
                    for c in (getattr(self.app, "companies_all", []) or [])
                    if str(c.get("Zšt", "")).strip() == zst_s
                ),
                None,
            )
            if not company:
                return {"ok": False, "msg": f"Firma Zšt={zst_s} ni v seznamu."}
            self.app._apply_selected_company(dict(company))
            self.app._saved_company_zst = zst_s
            try:
                self.app._save_ui_settings_to_disk()
            except Exception:
                pass
            imported = self._auto_import_folder_unlocked()
            self._tree_opened.clear()
            y = _sv(self.app, "period_year")
            m = _sv(self.app, "period_month")
            mm = ""
            try:
                mm = f"{int(m):02d}" if m else ""
            except Exception:
                mm = str(m or "")
            if y:
                self._tree_opened.add(f"year:{y}")
            if y and mm:
                self._tree_opened.add(f"month:{y}:{mm}")
            for key in (getattr(self.app, "monthly", {}) or {}):
                if not isinstance(key, (tuple, list)) or len(key) < 2:
                    continue
                yy, mo = str(key[0]), str(key[1])
                self._tree_opened.add(f"year:{yy}")
                if not mm or str(mo).zfill(2) == mm or str(mo) == str(m):
                    self._tree_opened.add(f"month:{yy}:{mo}")
            snap = self._snapshot_unlocked(include_tree=True)
            snap["ok"] = True
            snap["force_tree"] = True
            if imported:
                snap["msg"] = imported
            elif getattr(self.app, "monthly", None):
                snap["msg"] = f"Izbrana firma Zšt {zst_s} (analiza v pomnilniku)."
            else:
                snap["msg"] = (
                    f"Izbrana firma Zšt {zst_s}. V mapi ni CSV/ZIP — po FURS klikni Analiziraj."
                )
            snap["label"] = snap.get("company_label")
            return snap

        return self._call_tk(work)

    def set_period(self, year: Any, month: Any) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            _set_sv(self.app, "period_year", str(int(year)))
            _set_sv(self.app, "period_month", f"{int(month):02d}")
            try:
                self.app._save_ui_settings_to_disk()
            except Exception:
                pass
            return {"ok": True, "year": _sv(self.app, "period_year"), "month": _sv(self.app, "period_month")}

        return self._call_tk(work)

    def set_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            mapping = {
                "csv_name": "csv_name",
                "out_dir": "out_dir",
                "out_file": "out_file",
                "sheet_name": "sheet_name",
                "template_path": "template_path",
                "root_dir": "root_dir",
                "doc_filter": "doc_filter",
                "minimax_document_type": "minimax_document_type",
                "vrsta_prodaje": "vrsta_prodaje",
                "payment_method_label": "payment_method_label",
                "kirkpr_date_filter": "kirkpr_date_filter",
            }
            payload = data or {}
            for src, attr in mapping.items():
                if src in payload:
                    val = payload[src]
                    if src == "template_path" and not str(val or "").strip():
                        continue
                    _set_sv(self.app, attr, val)
            if "include_zips" in payload and hasattr(self.app, "include_zips"):
                self.app.include_zips.set(bool(payload["include_zips"]))
            if "show_neob" in payload and hasattr(self.app, "show_neobdavcljive"):
                self.app.show_neobdavcljive.set(bool(payload["show_neob"]))
            if "ddv_zavezanec" in payload and hasattr(self.app, "minimax_ddv_zavezanec"):
                self.app.minimax_ddv_zavezanec.set(bool(payload["ddv_zavezanec"]))
            if "filter_evidenca" in payload and hasattr(self.app, "filter_evidenca_davcnih"):
                self.app.filter_evidenca_davcnih.set(bool(payload["filter_evidenca"]))
            if "edavki_link" in payload:
                _set_sv(self.app, "_edavki_link_var", payload["edavki_link"])
            return {"ok": True, **self._snapshot_unlocked(include_tree=False)}

        return self._call_tk(work)

    def set_view(self, idx: int) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            i = int(idx)
            try:
                self.app._select_v21_view_tab(i)
            except Exception as exc:
                return {"ok": False, "msg": str(exc)}
            snap = self._snapshot_unlocked()
            snap["ok"] = True
            snap["view_idx"] = i
            snap["msg"] = f"Pogled: {VIEWS[i] if 0 <= i < len(VIEWS) else i}"
            return snap

        return self._call_tk(work)

    def set_kirkpr_book(self, idx: int) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            bar = getattr(self.app, "_v21_kirkpr_tab_bar", None)
            if bar is not None:
                bar.select(int(idx), fire=True)
            return {"ok": True, **self._snapshot_unlocked()}

        return self._call_tk(work)

    def set_kirkpr_source(self, idx: int) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            bar = getattr(self.app, "_v21_kirkpr_source_bar", None)
            if bar is not None:
                bar.select(int(idx), fire=True)
            return {"ok": True, **self._snapshot_unlocked()}

        return self._call_tk(work)

    def tree_month(self, yyyy: str, mm: str) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            from tree_view import serialize_tk_tree

            iid = _find_iid_by_tag(self.app, f"month:{yyyy}:{mm}")
            if iid:
                try:
                    self.app.tree.item(iid, open=True)
                    self.app.tree.see(iid)
                except Exception:
                    pass
            tree = serialize_tk_tree(self.app)
            children = []
            for year in tree.get("nodes") or []:
                for ch in year.get("children") or []:
                    if ch.get("id") == f"month:{yyyy}:{mm}":
                        children = ch.get("children") or []
            return {"ok": True, "children": children, "tree": tree}

        return self._call_tk(work)

    def toggle_check(self, node_id: str, iid: str = "") -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            nid = str(node_id or "").strip()
            kind = nid.split(":")[0] if nid else ""
            found = str(iid or "").strip() or _find_iid_by_tag(self.app, nid)
            if kind == "zipfile" and found:
                try:
                    self.app._toggle_zip_from_tree(found)
                except Exception:
                    pass
            s = getattr(self.app, "_tree_checked", None)
            if s is None:
                self.app._tree_checked = set()
                s = self.app._tree_checked
            if kind in ("month", "day", "year", "yearsum", "grandtotal"):
                if nid in s:
                    s.discard(nid)
                else:
                    s.add(nid)
                if found:
                    try:
                        vals = list(self.app.tree.item(found, "values") or ())
                        if vals:
                            vals[0] = "☑" if nid in s else "☐"
                            self.app.tree.item(found, values=vals)
                    except Exception:
                        pass
                try:
                    self.app._refresh_checked_sum_label()
                except Exception:
                    pass
            on = nid in (getattr(self.app, "_tree_checked", set()) or set())
            if kind == "zipfile" and found:
                try:
                    on = self.app._tree_check_mark(found) == "☑"
                except Exception:
                    pass
            return {
                "ok": True,
                "id": nid,
                "iid": found,
                "on": on,
                "check": "☑" if on else "☐",
                "checked": sorted(str(x) for x in (getattr(self.app, "_tree_checked", set()) or set())),
                "checked_sum": _sv(self.app, "_tree_checked_sum_var"),
            }

        return self._call_tk(work)

    def tree_toggle(self, node_id: str, iid: str = "") -> Dict[str, Any]:
        """HTML razširi/skrči — podatki iz monthly/daily, ne iz Tk Treeview."""
        def work() -> Dict[str, Any]:
            from tree_view import serialize_look_tree

            nid = str(node_id or "").strip()
            opened = nid not in self._tree_opened
            if opened:
                self._tree_opened.add(nid)
            else:
                self._tree_opened.discard(nid)
            kind, yyyy, mm = "", "", ""
            parts = nid.split(":")
            if parts:
                kind = parts[0]
            if kind in ("month", "day") and len(parts) >= 3:
                yyyy, mm = parts[1], parts[2]
                try:
                    self.app._sync_period_combos_from_ym(yyyy, mm)
                except Exception:
                    pass
            try:
                self.app._refresh_selection_detail_form()
            except Exception:
                pass
            out = {
                "ok": True,
                "id": nid,
                "iid": str(iid or ""),
                "open": opened,
                "tree": serialize_look_tree(self.app, self._tree_opened),
                "checked_sum": _sv(self.app, "_tree_checked_sum_var"),
                "year": _sv(self.app, "period_year"),
                "month": _sv(self.app, "period_month"),
            }
            out.update(_look_detail(self.app, nid))
            return out

        return self._call_tk(work)

    def select_tree(self, node_id: str, iid: str = "") -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            nid = str(node_id or "").strip()
            parts = nid.split(":")
            if parts and parts[0] in ("month", "day") and len(parts) >= 3:
                try:
                    self.app._sync_period_combos_from_ym(parts[1], parts[2])
                except Exception:
                    pass
            try:
                self.app._refresh_selection_detail_form()
            except Exception:
                pass
            out = {"ok": True, "id": nid, "iid": str(iid or "")}
            out.update(_look_detail(self.app, nid))
            return out

        return self._call_tk(work)

    def tree_reset_selection(self) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            self.app._tree_styled_iid = None
            try:
                self.app.tree.selection_remove(self.app.tree.selection())
            except Exception:
                pass
            try:
                self.app._refresh_selection_detail_form()
            except Exception:
                pass
            return {"ok": True, "msg": "Izbor ponastavljen.", "detail_title": "(ni izbire)", "detail_rows": []}

        return self._call_tk(work)

    def _look_panel_unlocked(self, panel: str) -> Dict[str, Any]:
        snap = self._snapshot_unlocked(include_tree=False)
        snap["ok"] = True
        snap["look_panel"] = panel
        if panel == "oauth":
            snap["oauth_fields"] = [
                {
                    "key": key,
                    "label": label,
                    "secret": secret,
                    "value": _sv(self.app, key),
                }
                for key, label, secret in OAUTH_FIELDS
            ]
            snap["minimax_document_type"] = _sv(self.app, "minimax_document_type")
            try:
                snap["minimax_ddv_zavezanec"] = bool(self.app.minimax_ddv_zavezanec.get())
            except Exception:
                snap["minimax_ddv_zavezanec"] = False
            snap["msg"] = "OAuth / Minimax (LOOK)."
            return snap
        if panel == "zip":
            from DavcnaBlagajna import (
                default_zip_enabled_map,
                format_float,
                infer_blagajna_context_year,
                scan_blagajna_zips,
            )

            zip_var = getattr(self.app, "include_zips", None)
            zip_on = True
            try:
                if zip_var is not None:
                    zip_on = bool(zip_var.get())
            except Exception:
                zip_on = True
            if not zip_on:
                snap["zip_rows"] = []
                snap["msg"] = "Vklopi checkbox ZIP, nato izberi pakete."
                return snap
            try:
                self.app._ensure_zip_selection_loaded()
            except Exception:
                pass
            root = self.app._analysis_source_root(self.app._to_path(_sv(self.app, "root_dir")))
            csv_name = (_sv(self.app, "csv_name") or "blagajne.csv").strip() or "blagajne.csv"
            ctx_year = infer_blagajna_context_year(root)
            probes = scan_blagajna_zips(root, csv_name, context_yyyy=ctx_year)
            saved = dict(getattr(self.app, "_zip_enabled", {}) or {})
            enabled = default_zip_enabled_map(probes, saved)
            rows = []
            for p in probes:
                rows.append(
                    {
                        "name": p.name,
                        "label": p.package_label,
                        "docs": p.doc_count if p.ok else 0,
                        "value": format_float(p.vrednost_racuna) if p.ok else "—",
                        "ok": bool(p.ok),
                        "enabled": bool(enabled.get(p.name, False)),
                    }
                )
            snap["zip_rows"] = rows
            snap["msg"] = "ZIP paketi (LOOK)."
            return snap
        if panel in ("konti_pay", "konti_vrsta"):
            from DavcnaBlagajna import get_kontiranje_placila, get_kontiranje_prihodkov

            rows = get_kontiranje_placila() if panel == "konti_pay" else get_kontiranje_prihodkov()
            snap["konti_rows"] = [dict(r) for r in rows]
            snap["konti_mode"] = panel
            snap["msg"] = "Kontiranje (LOOK)."
            return snap
        snap["msg"] = "Dodaj KIR/KPR zapis: najprej uvozi KIR/KPR in označi dan v drevesu. Tk editor je odstranjen."
        return snap

    def invoke(self, name: str) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            nm = str(name or "").strip()
            if nm not in ALLOWED_INVOKE:
                return {"ok": False, "msg": f"Ni dovoljen klic: {nm}"}
            if nm in LOOK_TK_INVOKE:
                return self._look_panel_unlocked(LOOK_TK_INVOKE[nm])
            fn = getattr(self.app, nm, None)
            if not callable(fn):
                return {"ok": False, "msg": f"Metoda ni na voljo: {nm}"}
            wrapped = self.app._safe_call(fn, nm)
            LOOK_DIALOGS.clear()
            wrapped()
            if nm == "_tree_collapse_all":
                self._tree_opened.clear()
            elif nm in ("_analyze", "_uvozi_kirkpr"):
                self._tree_opened.clear()
                y = _sv(self.app, "period_year")
                m = _sv(self.app, "period_month")
                mm = ""
                try:
                    mm = f"{int(m):02d}" if m else ""
                except Exception:
                    mm = str(m or "")
                if y:
                    self._tree_opened.add(f"year:{y}")
                if y and mm:
                    self._tree_opened.add(f"month:{y}:{mm}")
                    self._tree_opened.add(f"month:{y}:{m}")
                for key in (getattr(self.app, "monthly", {}) or {}):
                    if not isinstance(key, (tuple, list)) or len(key) < 2:
                        continue
                    yy, mo = str(key[0]), str(key[1])
                    self._tree_opened.add(f"year:{yy}")
                    if not mm or str(mo).zfill(2) == mm or str(mo) == str(m):
                        self._tree_opened.add(f"month:{yy}:{mo}")
            elif nm == "_tree_expand_all":
                monthly = getattr(self.app, "monthly", {}) or {}
                daily = getattr(self.app, "daily", {}) or {}
                opened = set()
                for (yyyy, mm) in monthly:
                    opened.add(f"year:{yyyy}")
                    opened.add(f"month:{yyyy}:{mm}")
                for (yyyy, mm, dd) in daily:
                    opened.add(f"year:{yyyy}")
                    opened.add(f"month:{yyyy}:{mm}")
                    opened.add(f"day:{yyyy}:{mm}:{dd}")
                self._tree_opened = opened
            snap = self._snapshot_unlocked(include_tree=nm not in NO_TREE_INVOKE)
            look = LOOK_DIALOGS.look_msg()
            if nm in PRENOS_INVOKE:
                prenos = _look_prenos_status(self.app, nm, look)
                snap["ok"] = prenos["ok"]
                snap["msg"] = prenos["msg"]
                snap["channel"] = prenos["channel"]
            elif LOOK_DIALOGS.kind == "error":
                snap["ok"] = False
                snap["msg"] = look or INVOKE_MSG.get(nm, "Napaka.")
            else:
                snap["ok"] = True
                snap["msg"] = look or INVOKE_MSG.get(nm, "Končano.")
            return snap

        return self._call_tk(work, timeout=600.0)

    def toggle_evidenca(self, zst: str) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            company = next(
                (
                    c
                    for c in (getattr(self.app, "companies_all", []) or [])
                    if str(c.get("Zšt", "")).strip() == str(zst).strip()
                ),
                None,
            )
            if not company:
                return {"ok": False, "msg": "Firma ni v seznamu."}
            if self.app._is_company_in_davcna_evidenca(company):
                self.app._remove_company_from_davcna_evidenca(company)
                msg = "Odstranjeno iz evidence."
            else:
                self.app._add_company_to_davcna_evidenca(company)
                msg = "Dodano v evidenco."
            if self.app.filter_evidenca_davcnih.get():
                self.app._render_companies()
            payload = {
                "ok": True,
                "msg": msg,
            }
            q = _sv(self.app, "company_search")
            rows = list(getattr(self.app, "companies_all", []) or [])
            needle = q.strip().casefold()
            ev_only = bool(self.app.filter_evidenca_davcnih.get())
            out_rows: List[Dict[str, str]] = []
            ev_n = 0
            for c in rows:
                mark = self.app._company_evidenca_checkbox(c)
                in_ev = mark == "☑"
                if in_ev:
                    ev_n += 1
                if ev_only and not in_ev:
                    continue
                if needle:
                    hay = " ".join(
                        str(c.get(k) or "")
                        for k in ("Zšt", "NAZIV", "DAVČNA", "DURS sifra", "Email", "NASLOV", "Org_ID")
                    ).casefold()
                    if needle not in hay:
                        continue
                row = dict(c)
                row["Ev."] = mark
                out_rows.append(row)
            payload.update(
                {
                    "companies": out_rows[:800],
                    "count": len(out_rows),
                    "total": len(rows),
                    "evidenca_count": ev_n,
                    "source": _sv(self.app, "companies_source_label"),
                }
            )
            return payload

        return self._call_tk(work)

    def compare_presets(self) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            from v2 import file_compare_settings

            defs = file_compare_settings.load_file_compare_definitions_from_disk()
            out = []
            for idx, definition in enumerate(defs):
                if not bool(definition.get("enabled", True)):
                    continue
                var = getattr(self.app, "_v21_file_compare_choice_vars", {}).get(idx)
                selected = bool(var.get()) if var is not None else bool(definition.get("selected", False))
                out.append(
                    {
                        "idx": idx,
                        "name": definition.get("name", f"Primerjava {idx + 1}"),
                        "desc": (
                            f"{file_compare_settings.describe_compare_side(definition.get('left', {}))} ↔ "
                            f"{file_compare_settings.describe_compare_side(definition.get('right', {}))}"
                        ),
                        "selected": selected,
                    }
                )
            return {"ok": True, "presets": out}

        return self._call_tk(work)

    def set_preset(self, idx: int, selected: bool) -> Dict[str, Any]:
        def work() -> Dict[str, Any]:
            var = getattr(self.app, "_v21_file_compare_choice_vars", {}).get(int(idx))
            if var is not None:
                var.set(bool(selected))
            return {"ok": True}

        return self._call_tk(work)

    def appearance(self, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if data:
            saved = _save_appearance(data)
        else:
            saved = _load_appearance()
        return {"ok": True, "appearance": saved}

    def open_settings(self) -> Dict[str, Any]:
        return {"ok": True, "look_panel": "videz", "msg": "Videz LOOK — Tk dialog je odstranjen."}

    def open_legacy_tk(self) -> Dict[str, Any]:
        """Rollback: zažene NESPREMENJENO Tk 3.0.68 iz mape 3.0.68 (samo zaganjalnik, ne deli stanja)."""
        import shutil
        import subprocess

        root = LEGACY_TK_ROOT
        target = root / "DavcnaBlagajna.pyw"
        if not target.is_file():
            target = root / "DavcnaBlagajna_v2_1.py"
        if not target.is_file():
            return {"ok": False, "msg": f"Tk 3.0.68 ni najdena: {root}"}
        pyw = shutil.which("pyw")
        if pyw:
            args = [pyw, "-3.10", str(target)]
        else:
            pythonw = Path(sys.executable).with_name("pythonw.exe")
            args = [str(pythonw if pythonw.is_file() else sys.executable), str(target)]
        try:
            subprocess.Popen(
                args,
                cwd=str(root),
                close_fds=True,
                creationflags=getattr(subprocess, "DETACHED_PROCESS", 0),
            )
            return {"ok": True, "msg": f"Zagon Tk 3.0.68: {target}"}
        except Exception as exc:
            return {"ok": False, "msg": f"Zagon Tk 3.0.68 ni uspel: {exc}"}

    def open_history(self) -> Dict[str, Any]:
        from v2.version_journal import get_current_patch_version, list_version_entries

        versions: List[Dict[str, Any]] = []
        for entry in list_version_entries()[:80]:
            versions.append(
                {
                    "id": str(entry.get("id") or ""),
                    "date": str(entry.get("date") or ""),
                    "title": str(entry.get("title") or ""),
                    "changes": str(entry.get("changes") or ""),
                }
            )
        return {
            "ok": True,
            "look_panel": "history",
            "current": get_current_patch_version(),
            "versions": versions,
            "msg": "Zgodovina verzij (LOOK).",
        }

    def look_save(self, panel: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = dict(data or {})

        def work() -> Dict[str, Any]:
            name = str(panel or "").strip()
            if name == "oauth":
                for key, _label, _secret in OAUTH_FIELDS:
                    if key in payload:
                        _set_sv(self.app, key, payload.get(key) or "")
                if "minimax_document_type" in payload:
                    _set_sv(self.app, "minimax_document_type", payload.get("minimax_document_type") or "")
                if "minimax_ddv_zavezanec" in payload:
                    try:
                        self.app.minimax_ddv_zavezanec.set(bool(payload.get("minimax_ddv_zavezanec")))
                    except Exception:
                        pass
                self.app._save_minimax_settings_to_disk(show_message=False)
                self.app._update_minimax_status("nastavitve shranjene")
                snap = self._snapshot_unlocked(include_tree=False)
                snap["ok"] = True
                snap["msg"] = "OAuth / Minimax shranjeno."
                return snap
            if name == "oauth_login":
                self.app._oauth_login_minimax()
                snap = self._snapshot_unlocked(include_tree=False)
                snap["ok"] = True
                snap["msg"] = LOOK_DIALOGS.look_msg() or "OAuth prijava."
                return snap
            if name == "zip":
                enabled = payload.get("enabled") or {}
                if isinstance(enabled, dict):
                    self.app._zip_enabled = {str(k): bool(v) for k, v in enabled.items()}
                    self.app._save_zip_selection_settings()
                snap = self._snapshot_unlocked(include_tree=False)
                snap["ok"] = True
                snap["msg"] = "ZIP paketi shranjeni."
                return snap
            if name in ("konti_pay", "konti_vrsta"):
                from DavcnaBlagajna import set_kontiranje_placila, set_kontiranje_prihodkov

                rows = payload.get("rows") or []
                if name == "konti_pay":
                    set_kontiranje_placila(rows)
                else:
                    set_kontiranje_prihodkov(rows)
                self.app._on_kontiranje_saved()
                snap = self._snapshot_unlocked(include_tree=False)
                snap["ok"] = True
                snap["msg"] = "Kontiranje shranjeno."
                return snap
            return {"ok": False, "msg": f"Neznan LOOK panel: {name}"}

        return self._call_tk(work)

    def close_window(self) -> None:
        try:
            import webview

            for w in webview.windows:
                w.destroy()
        except Exception:
            pass
        try:
            self.app.after(0, self.app.destroy)
        except Exception:
            pass


def _start_appv21() -> Any:
    """AppV21 + Tk mainloop na lastni niti (WebView2 zasede glavno STA)."""
    holder: Dict[str, Any] = {}
    ready = threading.Event()
    error: List[BaseException] = []

    def tk_main() -> None:
        try:
            try:
                import pythoncom

                pythoncom.CoInitialize()
            except Exception:
                pass
            from v2.app_v21 import AppV21
            from v2.version_journal import get_current_patch_version

            import DavcnaBlagajna as core

            core.log_info(f"PROGRAM START 5.1.00 ({get_current_patch_version()}) WebView2 LOOK")
            _install_no_tk_dialogs()
            app = AppV21()
            _patch_clipboard(app)
            try:
                app.withdraw()
                app.attributes("-alpha", 0)
                try:
                    app.attributes("-toolwindow", True)
                except Exception:
                    pass
            except Exception:
                pass
            _patch_look_window(app)
            app._restore_session_analyze = lambda: None  # type: ignore[method-assign]
            app._warmup_chrome_sessions_cache = lambda: None  # type: ignore[method-assign]
            try:
                app.update_idletasks()
            except Exception:
                pass
            holder["app"] = app
            ready.set()
            app.mainloop()
        except BaseException as exc:
            error.append(exc)
            ready.set()

    threading.Thread(target=tk_main, daemon=True, name="appv21-5").start()
    if not ready.wait(120):
        raise SystemExit("AppV21 se ni zagnal v 120 s.")
    if error:
        raise error[0]
    app = holder.get("app")
    if app is None:
        raise SystemExit("AppV21 ni na voljo.")
    return app


EXIT_GRACE_S = 3.0
_normal_exit = threading.Event()


def _shutdown_after_close(app: Any) -> None:
    """Po zaprtju glavnega okna: shrani stanje UI, ustavi Tk in zapri proces.

    pywebview 6.2.1 (WinForms) po zaprtju okna včasih ne vrne iz webview.start(),
    zato je proces ostal v ozadju. Tu: shrani blagajna_ui_settings.json (kot Tk
    zapiranje), ustavi Tk zanko, splakni dnevnik; če proces po EXIT_GRACE_S še teče,
    ga varnostno končaj z os._exit(0). Podatkov in izračunov ne spreminja.
    """
    done = threading.Event()

    def on_tk() -> None:
        try:
            save = getattr(app, "_save_ui_settings_to_disk", None)
            if callable(save):
                save()
        except Exception:
            pass
        try:
            app.quit()
        except Exception:
            pass
        done.set()

    try:
        app.after(0, on_tk)
        done.wait(5.0)
    except Exception:
        pass
    try:
        import logging

        logging.shutdown()
    except Exception:
        pass
    for stream in (sys.stdout, sys.stderr):
        try:
            if stream:
                stream.flush()
        except Exception:
            pass
    if not _normal_exit.wait(EXIT_GRACE_S):
        os._exit(0)


def _install_exit_on_close(window: Any, app: Any) -> None:
    def on_closed(*_a: Any) -> None:
        threading.Thread(
            target=_shutdown_after_close, args=(app,), daemon=True, name="exit-on-close"
        ).start()

    try:
        window.events.closed += on_closed
    except Exception:
        pass


def desktop() -> None:
    if sys.platform != "win32":
        raise SystemExit("Namizni zagon je namenjen Windows 10/11.")
    try:
        import webview
    except ImportError as exc:
        raise SystemExit("Manjka pywebview. Namesti: py -3.10 -m pip install pywebview") from exc

    _install_no_tk_dialogs()
    app = _start_appv21()
    PROFILE.mkdir(parents=True, exist_ok=True)
    bridge = Bridge(app)
    index = (UI / "index.html").resolve()
    if not index.is_file():
        try:
            app.after(0, app.destroy)
        except Exception:
            pass
        raise SystemExit(f"Manjka UI: {index}")
    try:
        webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = False
        webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
    except Exception:
        pass
    window = webview.create_window(
        APP_TITLE,
        index.as_uri(),
        js_api=bridge,
        width=1480,
        height=940,
        min_size=(1100, 720),
        background_color="#f4f7fc",
        text_select=True,
    )
    _install_exit_on_close(window, app)
    try:
        webview.start(gui="edgechromium", private_mode=False, storage_path=str(PROFILE))
    finally:
        try:
            app.after(0, app.quit)
        except Exception:
            pass
        try:
            app.after(0, app.destroy)
        except Exception:
            pass
        _normal_exit.set()


if __name__ == "__main__":
    desktop()
