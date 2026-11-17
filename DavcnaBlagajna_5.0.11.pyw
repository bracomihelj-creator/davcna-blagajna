# -*- coding: utf-8 -*-
"""Zagon Davčna Blagajna 5.0.11 — isti vstop kot DavcnaBlagajna.pyw."""
from __future__ import annotations

import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "DavcnaBlagajna.pyw"), run_name="__main__")
