"""Ob zagonu Chrome debug: odpri DavcnaBlagajna.pyw, če app še ne teče."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

APP_DIR = Path(__file__).resolve().parent
PYW_NAME = "DavcnaBlagajna.pyw"
PYW_PATH = APP_DIR / PYW_NAME


def _pythonw() -> str:
    exe = Path(sys.executable)
    if os.name == "nt":
        candidate = exe.with_name("pythonw.exe")
        if candidate.exists():
            return str(candidate)
    return str(exe)


def is_davcna_blagajna_running() -> bool:
    """True, če že teče DavcnaBlagajna (.py / .pyw / pythonw)."""
    if os.name != "nt":
        return False
    # PowerShell: zanesljivejši od WMIC where z OR
    ps = (
        "Get-CimInstance Win32_Process -Filter \"Name='python.exe' OR Name='pythonw.exe'\" "
        "| Select-Object -ExpandProperty CommandLine"
    )
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception:
        return False
    for line in (result.stdout or "").splitlines():
        low = (
            line.lower()
            .replace("č", "c")
            .replace("ć", "c")
            .replace("š", "s")
            .replace("ž", "z")
        )
        if "blagajna" in low and ("davcna" in low or "davčna" in line.lower()):
            return True
    return False


def ensure_davcna_pyw_running(*, force: bool = False) -> Tuple[bool, str]:
    """Zaženi DavcnaBlagajna.pyw, če še ne teče. Vrne (ok, message)."""
    if not PYW_PATH.is_file():
        return False, f"Manjka {PYW_PATH}"
    if not force and is_davcna_blagajna_running():
        return True, "Davčna Blagajna že teče"
    try:
        creationflags = 0
        if os.name == "nt":
            creationflags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(
                subprocess, "CREATE_NEW_PROCESS_GROUP", 0
            )
        subprocess.Popen(
            [_pythonw(), str(PYW_PATH)],
            cwd=str(APP_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
            close_fds=True,
        )
        return True, f"Zagnan {PYW_NAME}"
    except Exception as exc:
        return False, str(exc)


def main() -> int:
    ok, msg = ensure_davcna_pyw_running()
    print(("OK" if ok else "NAPAKA") + f" — {msg}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
