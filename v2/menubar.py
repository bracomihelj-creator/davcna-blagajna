"""Zgornji meni — Verzija + Nastavitve."""

from __future__ import annotations

import tkinter as tk
from typing import TYPE_CHECKING

from v2.settings_menu import setup_settings_submenu
from v2.version_switch import add_version_menu

if TYPE_CHECKING:
    from v2.app import AppV2


def setup_app_menubar(app: "AppV2", *, ui_version: str) -> None:
    menubar = tk.Menu(app)
    app.config(menu=menubar)
    add_version_menu(menubar, app, current=ui_version)
    setup_settings_submenu(menubar, app)
