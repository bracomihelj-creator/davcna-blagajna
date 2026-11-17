"""Vizualna tema Davčna Blagajna 2.0 — prilagodljive barve in fonti."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import tkinter as tk
from tkinter import ttk

V2_THEME_FILE = Path(__file__).resolve().parent.parent / "blagajna_v2_theme.json"

THEME_COLOR_KEYS: Tuple[str, ...] = (
    "WINDOW_BG",
    "PANEL_BG",
    "HEADER_BG",
    "HEADER_FG",
    "HEADER_MUTED",
    "FOOTER_BG",
    "FOOTER_FG",
    "TEXT",
    "MUTED",
    "BORDER",
    "ACCENT",
    "ACCENT_DIM",
    "ACCENT_FG",
    "ACCENT_TEXT",
    "ENTRY_BG",
    "ENTRY_FG",
    "TREE_SEL_FG",
    "TREE_SEL_BG",
    "TREE_ACTIVE_TAG",
    "BADGE_BG",
    "BADGE_FG",
    "HEADER_ACCENT_FG",
)

THEME_LABELS_SL: Dict[str, str] = {
    "WINDOW_BG": "Ozadje okna (rob)",
    "PANEL_BG": "Ozadje panelov",
    "HEADER_BG": "Glava — ozadje",
    "HEADER_FG": "Glava — besedilo",
    "HEADER_MUTED": "Glava — pomožno besedilo",
    "FOOTER_BG": "Noga — ozadje",
    "FOOTER_FG": "Noga — besedilo",
    "TEXT": "Besedilo",
    "MUTED": "Blago besedilo",
    "BORDER": "Obrobe",
    "ACCENT": "Poudarek / gumbi",
    "ACCENT_DIM": "Poudarek (temnejši)",
    "ACCENT_FG": "Besedilo na gumbih",
    "ACCENT_TEXT": "Naslovi / poudarki",
    "ENTRY_BG": "Rumena polja — ozadje",
    "ENTRY_FG": "Rumena polja — besedilo",
    "TREE_SEL_FG": "Drevo — izbrano besedilo",
    "TREE_SEL_BG": "Drevo — izbrano ozadje",
    "TREE_ACTIVE_TAG": "Drevo — aktivna vrstica",
    "BADGE_BG": "Značka 2.0 — ozadje",
    "BADGE_FG": "Značka 2.0 — besedilo",
    "HEADER_ACCENT_FG": "Status Minimax (glava)",
}

DEFAULT_THEME: Dict[str, Any] = {
    "preset": "privzeta",
    "font_family": "Segoe UI",
    "font_size": 9,
    "colors": {
        "WINDOW_BG": "#0f172a",
        "PANEL_BG": "#f8fafc",
        "HEADER_BG": "#1e293b",
        "HEADER_FG": "#f1f5f9",
        "HEADER_MUTED": "#94a3b8",
        "FOOTER_BG": "#1e293b",
        "FOOTER_FG": "#94a3b8",
        "TEXT": "#1e293b",
        "MUTED": "#64748b",
        "BORDER": "#cbd5e1",
        "ACCENT": "#0ea5e9",
        "ACCENT_DIM": "#0284c7",
        "ACCENT_FG": "#ffffff",
        "ACCENT_TEXT": "#0369a1",
        "ENTRY_BG": "#fef9c3",
        "ENTRY_FG": "#1e293b",
        "ENTRY_DISABLED": "#e2e8f0",
        "TREE_SEL_FG": "#0369a1",
        "TREE_SEL_BG": "#e0f2fe",
        "TREE_ZIP_DISABLED": "#94a3b8",
        "TREE_ACTIVE_TAG": "#0284c7",
        "BADGE_BG": "#6366f1",
        "BADGE_FG": "#ffffff",
        "HEADER_ACCENT_FG": "#7dd3fc",
    },
}

THEME_PRESETS: Dict[str, Dict[str, Any]] = {
    "privzeta": DEFAULT_THEME,
    "temna": {
        "preset": "temna",
        "font_family": "Segoe UI",
        "font_size": 9,
        "colors": {
            **DEFAULT_THEME["colors"],
            "WINDOW_BG": "#020617",
            "PANEL_BG": "#1e293b",
            "HEADER_BG": "#0f172a",
            "TEXT": "#e2e8f0",
            "MUTED": "#94a3b8",
            "BORDER": "#334155",
            "ACCENT": "#38bdf8",
            "ACCENT_DIM": "#0ea5e9",
            "ACCENT_TEXT": "#7dd3fc",
            "ENTRY_BG": "#422006",
            "ENTRY_FG": "#fef3c7",
        },
    },
    "svetla": {
        "preset": "svetla",
        "font_family": "Segoe UI",
        "font_size": 9,
        "colors": {
            **DEFAULT_THEME["colors"],
            "WINDOW_BG": "#e2e8f0",
            "PANEL_BG": "#ffffff",
            "HEADER_BG": "#334155",
            "ACCENT": "#2563eb",
            "ACCENT_DIM": "#1d4ed8",
            "ACCENT_TEXT": "#1e40af",
            "ENTRY_BG": "#ffff99",
        },
    },
    "klasicna": {
        "preset": "klasicna",
        "font_family": "Segoe UI",
        "font_size": 9,
        "colors": {
            **DEFAULT_THEME["colors"],
            "WINDOW_BG": "#d4d4d4",
            "PANEL_BG": "#f0f0f0",
            "HEADER_BG": "#4a4a4a",
            "ACCENT": "#cc0000",
            "ACCENT_DIM": "#a30000",
            "ACCENT_TEXT": "#1a4a7a",
            "ENTRY_BG": "#ffff99",
            "TREE_SEL_FG": "#cc0000",
            "TREE_SEL_BG": "#fff0f0",
            "TREE_ACTIVE_TAG": "#cc0000",
        },
    },
}

FONT_FAMILIES: Tuple[str, ...] = ("Segoe UI", "Tahoma", "Calibri", "Arial", "Verdana")

DEFAULT_LAYOUT: Dict[str, int] = {
    "root_width": 28,
    "out_dir_width": 28,
    "document_type_width": 6,
    "payment_method_width": 45,
    "vrsta_prodaje_width": 45,
    "template_width": 45,
    "out_file_width": 14,
    "sheet_width": 8,
    "csv_width": 8,
    "help_wraplength": 480,
}

LAYOUT_KEYS: Tuple[str, ...] = tuple(DEFAULT_LAYOUT.keys())

LAYOUT_LABELS_SL: Dict[str, str] = {
    "root_width": "Root — širina",
    "out_dir_width": "Shranjevanje — širina",
    "document_type_width": "DocumentType (combo)",
    "payment_method_width": "Način plačila (combo)",
    "vrsta_prodaje_width": "Vrsta prodaje (combo)",
    "template_width": "Predloga knjižb — širina",
    "out_file_width": "Datoteka (Excel) — širina",
    "sheet_width": "Sheet — širina",
    "csv_width": "CSV — širina",
    "help_wraplength": "Pomožno besedilo — prelom (px)",
}

DEFAULT_BORDERS: Dict[str, Any] = {
    "tab_inactive_bg": "#e2e8f0",
    "tab_active_bg": "#f8fafc",
    "tab_active_fg": "#dc2626",
    "tab_active_underline_px": 3,
    "tab_border_px": 0,
    "tab_border_color": "#cbd5e1",
    "panel_border_px": 1,
    "panel_border_color": "#cbd5e1",
    "separator_px": 1,
    "separator_color": "#cbd5e1",
}

BORDER_COLOR_KEYS: Tuple[str, ...] = (
    "tab_inactive_bg",
    "tab_active_bg",
    "tab_active_fg",
    "tab_border_color",
    "panel_border_color",
    "separator_color",
)

BORDER_INT_KEYS: Tuple[str, ...] = (
    "tab_active_underline_px",
    "tab_border_px",
    "panel_border_px",
    "separator_px",
)

BORDER_KEYS: Tuple[str, ...] = BORDER_COLOR_KEYS + BORDER_INT_KEYS

BORDER_LABELS_SL: Dict[str, str] = {
    "tab_inactive_bg": "Zavihek neaktiven — ozadje",
    "tab_active_bg": "Zavihek aktiven — ozadje",
    "tab_active_fg": "Zavihek aktiven — barva besedila",
    "tab_active_underline_px": "Zavihek aktiven — debelina črte (px)",
    "tab_border_px": "Zavihek — debelina obrobe (px)",
    "tab_border_color": "Zavihek — barva obrobe",
    "panel_border_px": "Panel (okvir) — debelina obrobe (px)",
    "panel_border_color": "Panel — barva obrobe",
    "separator_px": "Ločilna črta — debelina (px)",
    "separator_color": "Ločilna črta — barva",
}

DEFAULT_UI: Dict[str, bool] = {
    "double_click_open_folder": True,
    "double_click_kirkpr_open_editor": True,
}

UI_OPTION_KEYS: Tuple[str, ...] = (
    "double_click_open_folder",
    "double_click_kirkpr_open_editor",
)

UI_OPTION_LABELS_SL: Dict[str, str] = {
    "double_click_open_folder": "Dvojni klik na mesec v drevesu Blagajna odpre mapo ali ZIP",
    "double_click_kirkpr_open_editor": (
        "Dvojni klik na dokument v drevesu KIR/KPR odpre Minimax API knjižbo"
    ),
}

# Stare ključe iz prejšnjih različic JSON
_LAYOUT_LEGACY_MAP: Dict[str, Tuple[str, ...]] = {
    "path_width": ("root_width", "out_dir_width"),
    "combo_width": ("payment_method_width", "vrsta_prodaje_width"),
    "file_width": ("out_file_width",),
    "short_width": ("sheet_width", "csv_width"),
}


def normalize_layout_dict(layout: Optional[Dict[str, Any]]) -> Dict[str, int]:
    out = copy.deepcopy(DEFAULT_LAYOUT)
    if not layout:
        return out
    for legacy, targets in _LAYOUT_LEGACY_MAP.items():
        if legacy in layout:
            try:
                val = int(layout[legacy])
            except (TypeError, ValueError):
                continue
            for target in targets:
                out[target] = val
    for key in LAYOUT_KEYS:
        if key in layout:
            try:
                out[key] = int(layout[key])
            except (TypeError, ValueError):
                pass
    return out


class V2Theme:
    """Trenutna tema — atributi se posodabljajo iz JSON / menija."""

    APP_TITLE = "Davčna Blagajna 2.0"
    APP_SUBTITLE = "Mesečni seštevki · firme · Minimax · FURS"

    FONT_FAMILY = "Segoe UI"
    FONT_SIZE = 9

    WINDOW_BG = "#0f172a"
    PANEL_BG = "#f8fafc"
    HEADER_BG = "#1e293b"
    HEADER_FG = "#f1f5f9"
    HEADER_MUTED = "#94a3b8"
    FOOTER_BG = "#1e293b"
    FOOTER_FG = "#94a3b8"
    HEADER_ACCENT_FG = "#7dd3fc"

    TEXT = "#1e293b"
    MUTED = "#64748b"
    BORDER = "#cbd5e1"

    ACCENT = "#0ea5e9"
    ACCENT_DIM = "#0284c7"
    ACCENT_FG = "#ffffff"
    ACCENT_TEXT = "#0369a1"

    ENTRY_BG = "#fef9c3"
    ENTRY_FG = "#1e293b"
    ENTRY_DISABLED = "#e2e8f0"

    TREE_SEL_FG = "#0369a1"
    TREE_SEL_BG = "#e0f2fe"
    TREE_ZIP_DISABLED = "#94a3b8"
    TREE_ACTIVE_TAG = "#0284c7"

    BADGE_BG = "#6366f1"
    BADGE_FG = "#ffffff"

    @classmethod
    def ui_font(cls, *, size_delta: int = 0, bold: bool = False) -> Tuple[str, int, str]:
        weight = "bold" if bold else "normal"
        return (cls.FONT_FAMILY, max(7, cls.FONT_SIZE + size_delta), weight)

    @classmethod
    def BTN_ACCENT_FONT(cls) -> Tuple[str, int, str]:
        return cls.ui_font(bold=True)

    @classmethod
    def BTN_PRIMARY_FONT(cls) -> Tuple[str, int, str]:
        return cls.ui_font(bold=True)


class V2Layout:
    """Širine polj v spodnjem panelu — iz JSON / menija Nastavitve."""

    root_width = 28
    out_dir_width = 28
    document_type_width = 6
    payment_method_width = 45
    vrsta_prodaje_width = 45
    template_width = 45
    out_file_width = 14
    sheet_width = 8
    csv_width = 8
    help_wraplength = 480


class V2Borders:
    """Obrobe zavihkov, panelov in črt — iz JSON / menija Nastavitve."""

    tab_inactive_bg = "#e2e8f0"
    tab_active_bg = "#f8fafc"
    tab_active_fg = "#dc2626"
    tab_active_underline_px = 3
    tab_border_px = 0
    tab_border_color = "#cbd5e1"
    panel_border_px = 1
    panel_border_color = "#cbd5e1"
    separator_px = 1
    separator_color = "#cbd5e1"


class V2Ui:
    """Vedenje vmesnika — iz JSON / menija Nastavitve."""

    double_click_open_folder = True
    double_click_kirkpr_open_editor = True


def normalize_ui_dict(ui: Optional[Dict[str, Any]]) -> Dict[str, bool]:
    out = copy.deepcopy(DEFAULT_UI)
    if not ui:
        return out
    for key in UI_OPTION_KEYS:
        if key in ui:
            out[key] = bool(ui[key])
    return out


def ui_data_to_class(data: Dict[str, Any]) -> None:
    ui = normalize_ui_dict(data.get("ui") if isinstance(data.get("ui"), dict) else None)
    for key, val in ui.items():
        setattr(V2Ui, key, val)


def normalize_borders_dict(borders: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    out = copy.deepcopy(DEFAULT_BORDERS)
    if not borders:
        return out
    for key in BORDER_COLOR_KEYS:
        if key in borders and isinstance(borders[key], str) and borders[key].startswith("#"):
            out[key] = borders[key]
    for key in BORDER_INT_KEYS:
        if key in borders:
            try:
                out[key] = int(borders[key])
            except (TypeError, ValueError):
                pass
    out["tab_active_underline_px"] = max(1, min(12, int(out["tab_active_underline_px"])))
    out["tab_border_px"] = max(0, min(8, int(out["tab_border_px"])))
    out["panel_border_px"] = max(0, min(8, int(out["panel_border_px"])))
    out["separator_px"] = max(1, min(12, int(out["separator_px"])))
    return out


def borders_data_to_class(data: Dict[str, Any]) -> None:
    borders = normalize_borders_dict(data.get("borders") if isinstance(data.get("borders"), dict) else None)
    for key, val in borders.items():
        setattr(V2Borders, key, val)


def layout_data_to_class(data: Dict[str, Any]) -> None:
    layout = normalize_layout_dict(data.get("layout") if isinstance(data.get("layout"), dict) else None)
    for key in LAYOUT_KEYS:
        val = layout[key]
        if key == "help_wraplength":
            val = max(200, min(1200, val))
        else:
            val = max(4, min(120, val))
        setattr(V2Layout, key, val)


def theme_data_to_class(data: Dict[str, Any]) -> None:
    colors = data.get("colors") if isinstance(data.get("colors"), dict) else {}
    V2Theme.FONT_FAMILY = str(data.get("font_family") or "Segoe UI")
    try:
        V2Theme.FONT_SIZE = max(7, min(16, int(data.get("font_size") or 9)))
    except (TypeError, ValueError):
        V2Theme.FONT_SIZE = 9
    for key, val in colors.items():
        if hasattr(V2Theme, key) and isinstance(val, str) and val.startswith("#"):
            setattr(V2Theme, key, val)
    layout_data_to_class(data)
    borders_data_to_class(data)
    ui_data_to_class(data)


def class_to_theme_data(*, preset: str = "po meri") -> Dict[str, Any]:
    colors = {k: getattr(V2Theme, k) for k in DEFAULT_THEME["colors"]}
    layout = {k: int(getattr(V2Layout, k)) for k in LAYOUT_KEYS}
    borders = {k: getattr(V2Borders, k) for k in BORDER_KEYS}
    ui = {k: bool(getattr(V2Ui, k)) for k in UI_OPTION_KEYS}
    return {
        "preset": preset,
        "font_family": V2Theme.FONT_FAMILY,
        "font_size": V2Theme.FONT_SIZE,
        "colors": colors,
        "layout": layout,
        "borders": borders,
        "ui": ui,
    }


def load_v2_theme_from_disk() -> Dict[str, Any]:
    if not V2_THEME_FILE.exists():
        data = copy.deepcopy(DEFAULT_THEME)
        data["layout"] = copy.deepcopy(DEFAULT_LAYOUT)
        data["borders"] = copy.deepcopy(DEFAULT_BORDERS)
        data["ui"] = copy.deepcopy(DEFAULT_UI)
        theme_data_to_class(data)
        return data
    try:
        raw = json.loads(V2_THEME_FILE.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError("theme root must be object")
        merged = copy.deepcopy(DEFAULT_THEME)
        merged["layout"] = copy.deepcopy(DEFAULT_LAYOUT)
        merged["borders"] = copy.deepcopy(DEFAULT_BORDERS)
        merged["ui"] = copy.deepcopy(DEFAULT_UI)
        merged["preset"] = str(raw.get("preset") or merged["preset"])
        merged["font_family"] = str(raw.get("font_family") or merged["font_family"])
        merged["font_size"] = raw.get("font_size", merged["font_size"])
        if isinstance(raw.get("colors"), dict):
            merged["colors"].update({k: v for k, v in raw["colors"].items() if isinstance(v, str)})
        if isinstance(raw.get("layout"), dict):
            merged["layout"] = normalize_layout_dict(raw["layout"])
        if isinstance(raw.get("borders"), dict):
            merged["borders"] = normalize_borders_dict(raw["borders"])
        if isinstance(raw.get("ui"), dict):
            merged["ui"] = normalize_ui_dict(raw["ui"])
        theme_data_to_class(merged)
        return merged
    except Exception:
        data = copy.deepcopy(DEFAULT_THEME)
        data["layout"] = copy.deepcopy(DEFAULT_LAYOUT)
        data["borders"] = copy.deepcopy(DEFAULT_BORDERS)
        data["ui"] = copy.deepcopy(DEFAULT_UI)
        theme_data_to_class(data)
        return data


def save_v2_theme_to_disk(data: Optional[Dict[str, Any]] = None) -> None:
    payload = data if data is not None else class_to_theme_data()
    V2_THEME_FILE.parent.mkdir(parents=True, exist_ok=True)
    V2_THEME_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def apply_preset(preset_key: str) -> Dict[str, Any]:
    base = THEME_PRESETS.get(preset_key, DEFAULT_THEME)
    data = copy.deepcopy(base)
    data["layout"] = copy.deepcopy(DEFAULT_LAYOUT)
    data["borders"] = copy.deepcopy(DEFAULT_BORDERS)
    data["ui"] = copy.deepcopy(DEFAULT_UI)
    theme_data_to_class(data)
    return data


def get_ui_option(key: str, default: Optional[bool] = None) -> bool:
    if key in UI_OPTION_KEYS:
        return bool(getattr(V2Ui, key, DEFAULT_UI.get(key, False)))
    if default is not None:
        return default
    return bool(DEFAULT_UI.get(key, False))


def apply_v2_ttk_styles(root: tk.Misc) -> None:
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    bg = V2Theme.PANEL_BG
    fg = V2Theme.TEXT
    base_font = V2Theme.ui_font()

    style.configure(".", background=bg, foreground=fg, font=base_font)
    style.configure("TFrame", background=bg)
    style.configure("V2.Header.TFrame", background=V2Theme.HEADER_BG)
    style.configure("V2.Footer.TFrame", background=V2Theme.FOOTER_BG)
    style.configure("V2.Toolbar.TFrame", background=bg)
    style.configure(
        "TLabelframe",
        background=bg,
        foreground=V2Theme.ACCENT_TEXT,
        bordercolor=V2Borders.panel_border_color,
        borderwidth=int(V2Borders.panel_border_px),
        relief="solid" if int(V2Borders.panel_border_px) > 0 else "flat",
    )
    style.configure(
        "TLabelframe.Label",
        background=bg,
        foreground=V2Theme.ACCENT_TEXT,
        font=V2Theme.ui_font(bold=True),
    )
    tab_active_fg = V2Borders.tab_active_fg
    tab_inactive_bg = V2Borders.tab_inactive_bg
    tab_active_bg = V2Borders.tab_active_bg
    nb_tab = "V2.Tab.TNotebook.Tab"
    nb_tab_active = "V2.ActiveTab.TNotebook.Tab"
    try:
        tab_layout = style.layout("TNotebook.Tab")
        if tab_layout:
            style.layout(nb_tab, tab_layout)
            style.layout(nb_tab_active, tab_layout)
    except tk.TclError:
        pass

    style.configure("TNotebook", background=bg, borderwidth=0, tabmargins=[2, 4, 2, 0])
    style.configure(
        nb_tab,
        background=tab_inactive_bg,
        foreground=V2Theme.TEXT,
        padding=[12, 6],
        font=base_font,
    )
    style.configure(
        nb_tab_active,
        background=tab_active_bg,
        foreground=tab_active_fg,
        padding=[12, 6],
        font=V2Theme.ui_font(bold=True),
    )
    style.map(
        nb_tab,
        background=[("selected", tab_inactive_bg), ("active", "#cbd5e1")],
        foreground=[("selected", V2Theme.TEXT), ("!selected", V2Theme.TEXT)],
    )
    style.map(
        nb_tab_active,
        background=[("selected", tab_active_bg), ("active", tab_active_bg)],
        foreground=[("selected", tab_active_fg), ("!selected", tab_active_fg)],
    )
    style.configure(
        "TNotebook.Tab",
        background=tab_inactive_bg,
        foreground=V2Theme.TEXT,
        padding=[12, 6],
        font=base_font,
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", tab_active_bg), ("active", "#cbd5e1")],
        foreground=[("selected", V2Theme.TEXT)],
    )
    style.configure(
        "TButton",
        background="#e2e8f0",
        foreground=fg,
        bordercolor=V2Theme.BORDER,
        focusthickness=1,
        padding=(8, 4),
        font=base_font,
    )
    style.map("TButton", background=[("active", "#cbd5e1"), ("pressed", "#94a3b8")])
    style.configure(
        "V2.Accent.TButton",
        background=V2Theme.ACCENT,
        foreground=V2Theme.ACCENT_FG,
        font=V2Theme.ui_font(bold=True),
        bordercolor=V2Theme.ACCENT_DIM,
        padding=(10, 5),
    )
    style.map(
        "V2.Accent.TButton",
        background=[("active", V2Theme.ACCENT_DIM), ("pressed", "#0369a1")],
        foreground=[("disabled", "#cbd5e1")],
    )
    style.configure(
        "Treeview",
        background="#ffffff",
        fieldbackground="#ffffff",
        foreground=fg,
        rowheight=max(22, V2Theme.FONT_SIZE + 14),
        bordercolor=V2Borders.panel_border_color,
        font=base_font,
    )
    style.configure(
        "Treeview.Heading",
        background=tab_inactive_bg,
        foreground=V2Theme.ACCENT_TEXT,
        font=V2Theme.ui_font(bold=True),
        relief="flat",
    )
    style.map(
        "Treeview",
        background=[("selected", V2Theme.TREE_SEL_BG)],
        foreground=[("selected", V2Theme.TREE_SEL_FG)],
    )
    style.configure(
        "Yellow.TCombobox",
        fieldbackground=V2Theme.ENTRY_BG,
        background=V2Theme.ENTRY_BG,
        selectbackground=V2Theme.ENTRY_BG,
        selectforeground=V2Theme.ENTRY_FG,
        foreground=V2Theme.ENTRY_FG,
        font=base_font,
    )
    style.map(
        "Yellow.TCombobox",
        fieldbackground=[("readonly", V2Theme.ENTRY_BG), ("disabled", V2Theme.ENTRY_DISABLED)],
        background=[("readonly", V2Theme.ENTRY_BG), ("disabled", V2Theme.ENTRY_DISABLED)],
        foreground=[("readonly", V2Theme.ENTRY_FG), ("disabled", V2Theme.MUTED)],
        selectbackground=[("readonly", V2Theme.ENTRY_BG), ("disabled", V2Theme.ENTRY_DISABLED)],
        selectforeground=[("readonly", V2Theme.ENTRY_FG), ("disabled", V2Theme.MUTED)],
    )
    style.configure("TEntry", fieldbackground="#ffffff", foreground=fg, font=base_font)
    style.configure("TCheckbutton", background=bg, foreground=fg, font=base_font)
    style.configure("TRadiobutton", background=bg, foreground=fg, font=base_font)
    style.configure("TLabel", background=bg, foreground=fg, font=base_font)
    style.configure("TScrollbar", background=tab_inactive_bg, troughcolor=bg, bordercolor=V2Borders.panel_border_color)


def v2_separator(parent: tk.Misc, **kwargs: Any) -> tk.Frame:
    """Vodoravna ločilna črta z debelino in barvo iz nastavitev obrob."""
    px = max(1, int(V2Borders.separator_px))
    frm = tk.Frame(
        parent,
        height=px,
        bg=V2Borders.separator_color,
        highlightthickness=0,
        bd=0,
        **kwargs,
    )
    frm.pack_propagate(False)
    return frm


def v2_muted(parent: tk.Widget, text: str, **kwargs: Any) -> ttk.Label:
    return ttk.Label(parent, text=text, foreground=V2Theme.MUTED, **kwargs)


def v2_info(parent: tk.Widget, textvariable: tk.StringVar, **kwargs: Any) -> ttk.Label:
    return ttk.Label(parent, textvariable=textvariable, foreground=V2Theme.ACCENT_TEXT, **kwargs)


V2_NB_TAB = "V2.Tab.TNotebook.Tab"
V2_NB_TAB_ACTIVE = "V2.ActiveTab.TNotebook.Tab"


def refresh_notebook_active_tab(nb: ttk.Notebook) -> None:
    """Aktivni zavihek: krepko + rdeče."""
    try:
        current = nb.index(nb.select())
        count = nb.index("end")
    except tk.TclError:
        return

    def _apply() -> None:
        try:
            cur = nb.index(nb.select())
            for i in range(nb.index("end")):
                nb.tab(i, style=V2_NB_TAB_ACTIVE if i == cur else V2_NB_TAB)
        except tk.TclError:
            pass

    try:
        for i in range(count):
            nb.tab(i, style=V2_NB_TAB_ACTIVE if i == current else V2_NB_TAB)
    except tk.TclError:
        pass
    try:
        nb.winfo_toplevel().after_idle(_apply)
    except tk.TclError:
        _apply()


def bind_notebook_active_tab_style(nb: ttk.Notebook) -> None:
    """Poveži osveževanje stila ob menjavi zavihka."""
    refresh_notebook_active_tab(nb)

    def _on_change(_event: tk.Event) -> None:
        refresh_notebook_active_tab(nb)

    nb.bind("<<NotebookTabChanged>>", _on_change, add="+")
    try:
        nb.bind("<ButtonRelease-1>", _on_change, add="+")
    except tk.TclError:
        pass
