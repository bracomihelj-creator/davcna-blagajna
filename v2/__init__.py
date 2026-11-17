"""Davčna Blagajna 2.0 — izboljšan vmesnik nad obstoječo logiko v1."""

from __future__ import annotations

from typing import Any

__all__ = ["AppV2"]


def __getattr__(name: str) -> Any:
    if name == "AppV2":
        from v2.app import AppV2

        return AppV2
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
