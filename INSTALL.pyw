# -*- coding: utf-8 -*-
"""Namestitev Davčna Blagajna 5.1 — WebView2 LOOK (ne spreminja 3.0.68)."""
from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BAT = ROOT / "ZAZENI_5.1.bat"
APP = ROOT / "DavcnaBlagajna.pyw"
APP_COPY = ROOT / "DavcnaBlagajna_5.1.pyw"
CORE = ROOT / "DavcnaBlagajna.py"
HOST = ROOT / "host_webview.py"
UI = ROOT / "ui" / "index.html"
VERSION = "5.1.01"
SHORTCUT_NAME = "DavcnaBlagajna_5.1.lnk"
LEGACY = Path(r"D:\PISARNA\Python\DavčnaBlagajna")
MINIMAX_PROFILE = ROOT / "data" / "webview2" / "minimax_uvoz_profile"
LEGACY_MINIMAX_PROFILE = LEGACY / "data" / "webview2" / "minimax_uvoz_profile"


def _run(args: list) -> tuple[int, str]:
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=180)
        out = (p.stdout or "") + (p.stderr or "")
        return p.returncode, out.strip()
    except Exception as exc:
        return 1, str(exc)


def check_python() -> str:
    code, out = _run(["py", "-3.10", "-c", "import sys; print(sys.version)"])
    if code != 0:
        raise SystemExit("Python 3.10 ni najden (py -3.10).")
    return out.split("\n")[0]


def check_webview() -> str:
    code, _ = _run(["py", "-3.10", "-c", "import webview"])
    if code != 0:
        print("Namestitev pywebview …")
        c2, out2 = _run(["py", "-3.10", "-m", "pip", "install", "pywebview"])
        if c2 != 0:
            raise SystemExit("Namestitev pywebview ni uspela:\n" + out2)
        return "pywebview nameščen"
    return "pywebview že nameščen"


def check_webview2_runtime() -> str:
    import os

    pf86 = os.environ.get("PROGRAMFILES(X86)") or r"C:\Program Files (x86)"
    pf = os.environ.get("PROGRAMFILES") or r"C:\Program Files"
    roots = [
        Path(pf86) / "Microsoft" / "EdgeWebView" / "Application",
        Path(pf) / "Microsoft" / "EdgeWebView" / "Application",
    ]
    for p in roots:
        try:
            if p.is_dir() and any(p.iterdir()):
                return f"WebView2 Runtime: {p}"
        except OSError:
            continue
    print("Opozorilo: Microsoft Edge WebView2 Runtime ni najden. Namesti z https://developer.microsoft.com/microsoft-edge/webview2/")
    return "WebView2 Runtime: NI ZAZNAN (namesti Runtime)"


def check_standalone() -> str:
    missing = [str(p) for p in (CORE, HOST, UI, APP) if not p.is_file()]
    if missing:
        raise SystemExit("Manjkajo datoteke 5.1:\n" + "\n".join(missing))
    if not (ROOT / "v2" / "app_v21.py").is_file():
        raise SystemExit("Manjka v2/app_v21.py v mapi 5.1.")
    return f"samostojna 5.1: {ROOT}"


def ensure_minimax_session() -> str:
    """5.1 ima lastno Minimax WebView2 sejo v data/webview2 (ni v gitu).

    Če je še ni, jo enkrat kopira iz 3.0.68 (vir se samo bere), da ponovna prijava ni potrebna.
    """
    import shutil

    if MINIMAX_PROFILE.is_dir() and any(MINIMAX_PROFILE.iterdir()):
        return f"Minimax seja (5.1): {MINIMAX_PROFILE}"
    if LEGACY_MINIMAX_PROFILE.is_dir():
        MINIMAX_PROFILE.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(LEGACY_MINIMAX_PROFILE, MINIMAX_PROFILE, dirs_exist_ok=True)
        return f"Minimax seja kopirana iz 3.0.68 v {MINIMAX_PROFILE}"
    return "Minimax seja še ne obstaja — ob prvem spletnem uvozu se prijavi v oknu Minimax."


def _desktop_dir() -> Path:
    desktop = Path.home() / "Desktop"
    if not desktop.is_dir():
        desktop = Path.home() / "Namizje"
    return desktop


def desktop_shortcut() -> Path:
    desktop = _desktop_dir()
    lnk = desktop / SHORTCUT_NAME
    ps = (
        "$ws = New-Object -ComObject WScript.Shell; "
        f"$s = $ws.CreateShortcut('{str(lnk).replace(chr(39), chr(39)+chr(39))}'); "
        f"$s.TargetPath = '{str(BAT)}'; "
        f"$s.WorkingDirectory = '{str(ROOT)}'; "
        f"$s.Description = 'Davčna Blagajna {VERSION} (WebView2 LOOK, AppV21)'; "
        "$s.Save()"
    )
    _run(["powershell", "-NoProfile", "-Command", ps])
    return lnk


def main() -> None:
    print(f"Davčna Blagajna {VERSION} — namestitev (LOOK WebView2, isti AppV21)")
    print("Mapa:", ROOT)
    print("Python:", check_python())
    print(check_webview())
    print(check_webview2_runtime())
    print(check_standalone())
    print(ensure_minimax_session())
    if LEGACY.is_dir():
        print("Legacy 3.0.68 (nedotaknjena):", LEGACY)
    if not BAT.is_file():
        raise SystemExit("Manjka ZAZENI_5.1.bat.")
    if not APP_COPY.is_file():
        APP_COPY.write_text(APP.read_text(encoding="utf-8"), encoding="utf-8")
    lnk = desktop_shortcut()
    print("Bližnjica:", lnk)
    print("Zagon: DavcnaBlagajna.pyw  ali  ZAZENI_5.1.bat")
    print("Povrnitev: ZAZENI_DavcnaBlagajna_PY.bat v mapi 3.0.68")
    try:
        input("Enter za izhod …")
    except EOFError:
        pass


if __name__ == "__main__":
    main()
