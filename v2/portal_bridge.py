"""Portal most — bistvo pristopa (vzorec QUICK_eNDM PortalRouter).

Namen: Davčna Blagajna NE gradi lastne sejne logike (kopiranje kukijev).
Kliče usmerjevalnik iz QUICK_eNDM — privzeto trajni WebView2 (pywebview).
QUICK Chrome Bridge vtičnik je IZKLOPLJEN (chrome_bridge_enabled=False).

  1) WebView2 profil (minimax / edavki / ajpes / spot=eVEM);
  2) Chrome CDP samo če usmerjevalnik še najde aktivni debug (brez vtičnika).

Predpostavka (2026-10-11): seje so VEDNO prijavljene (minimax, edavki, ajpes, eVEM).

Plače / eNDM SQL / KIRKPR niso del tega mosta — playbooki ostanejo v svojih app
(npr. QUICK_eNDM). Tukaj je samo izbira motorja in odpiranje portala.

Zaklenjene poti (nespremenjene): FURS PakR 2.2.28, Minimax KN uvoz 3.0.42.
eDavki/Halcom prednostno Chrome; WebView2 edavki samo rezervna prijava.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Callable, Dict, Optional

ENDM_ROOT = Path(r"D:\PISARNA\Python\QUICK_eNDM")

PORTALS = ("minimax", "edavki", "ajpes", "spot")

_router: Any = None
_import_error: str = ""


def _ensure_endm_on_path() -> None:
    root = str(ENDM_ROOT.resolve())
    if root not in sys.path:
        sys.path.insert(0, root)


def endm_available() -> bool:
    return ENDM_ROOT.is_dir() and (ENDM_ROOT / "portal_router.py").is_file()


def get_import_error() -> str:
    return _import_error


def get_portal_router() -> Any:
    """Singleton PortalRouter iz QUICK_eNDM (QuickWebViewProfiles + BrowserBridge)."""
    global _router, _import_error
    if _router is not None:
        return _router
    if not endm_available():
        _import_error = f"QUICK_eNDM ni na {ENDM_ROOT}"
        raise RuntimeError(_import_error)
    _ensure_endm_on_path()
    try:
        from browser_bridge import BrowserBridge  # type: ignore
        from config_service import load_config  # type: ignore
        from portal_router import PortalRouter  # type: ignore
        from quick_webview_profiles import QuickWebViewProfiles  # type: ignore
    except Exception as exc:
        _import_error = f"Uvoz QUICK_eNDM modulov: {exc}"
        raise RuntimeError(_import_error) from exc

    try:
        cfg = load_config(ENDM_ROOT)
        try:
            # Davčna Blagajna: pywebview + WebView2, ne QUICK Chrome Bridge vtičnik
            cfg.chrome_bridge_enabled = False
        except Exception:
            pass
    except Exception:
        from types import SimpleNamespace

        cfg = SimpleNamespace(
            chrome_bridge_enabled=False,
            spot_portal_url="https://spot.gov.si/mojspot",
        )

    web_profiles = QuickWebViewProfiles(ENDM_ROOT)
    browser = BrowserBridge(cfg, ENDM_ROOT)
    _router = PortalRouter(web_profiles, browser)
    _import_error = ""
    return _router


def normalize_portal(portal: str) -> str:
    name = str(portal or "").strip().lower()
    if name == "evem":
        return "spot"
    return name


def resolve_portal(
    portal: str = "minimax",
    log: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """Odločitev motorja za portal: chrome | webview (+ stanje)."""
    log = log or (lambda _m: None)
    portal = normalize_portal(portal)
    router = get_portal_router()
    decision = dict(router.resolve(portal, log=log) or {})
    engine = str(decision.get("engine") or "webview")
    if engine == "chrome":
        label = "Chrome — aktivni portal"
    else:
        label = f"WebView2 — trajni profil »{portal}«"
    decision["portal"] = portal
    decision["engine_label"] = label
    return decision


def open_portal(
    portal: str,
    url: str = "",
    log: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """Odpri portal: aktivni Chrome če ustreza, sicer WebView2 profil."""
    log = log or (lambda _m: None)
    portal = normalize_portal(portal)
    router = get_portal_router()
    result = dict(router.open_portal(portal, url=str(url or ""), log=log) or {})
    result["portal"] = portal
    if "engine_label" not in result:
        eng = str(result.get("engine") or "")
        if "chrome" in eng.lower():
            result["engine_label"] = "Chrome — aktivni portal"
        else:
            result["engine_label"] = f"WebView2 — trajni profil »{portal}«"
    return result


def active_chrome(log: Optional[Callable[[str], None]] = None) -> Dict[str, Any]:
    """Kaj je trenutno aktivni Chrome portal (če sploh)."""
    log = log or (lambda _m: None)
    router = get_portal_router()
    info = dict(router.active_chrome() or {})
    if info.get("active"):
        log(f"Portal most: aktivni Chrome = {info.get('portal') or '?'}")
    return info


def webview_profiles_status() -> Dict[str, Dict[str, Any]]:
    """Stanje štirih trajnih WebView2 profilov."""
    router = get_portal_router()
    try:
        return dict(router.web_profiles.status_all() or {})
    except Exception:
        return {}


def engine_status_text(decision: Optional[Dict[str, Any]] = None) -> str:
    d = decision or {}
    if d.get("login_required"):
        return "login_required (WebView2)"
    engine = str(d.get("engine") or "")
    if engine == "chrome" or "chrome" in engine.lower():
        return "Chrome"
    if engine == "webview" or "webview" in engine.lower():
        return "WebView2"
    return engine or "?"


def status_summary(
    portals: tuple[str, ...] = PORTALS,
    log: Optional[Callable[[str], None]] = None,
) -> Dict[str, Any]:
    """Kratek pregled: za vsak portal chrome vs webview (brez playbookov)."""
    log = log or (lambda _m: None)
    active = active_chrome(log=log)
    out: Dict[str, Any] = {
        "active_chrome": active,
        "portals": {},
        "endm_root": str(ENDM_ROOT),
    }
    for name in portals:
        try:
            d = resolve_portal(name, log=log)
            out["portals"][name] = {
                "engine": d.get("engine"),
                "engine_label": d.get("engine_label"),
            }
        except Exception as exc:
            out["portals"][name] = {"engine": "", "error": str(exc)}
    return out
