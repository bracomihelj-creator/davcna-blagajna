"""Preveri Chrome remote-debugging port 9222 (eDavki / Blagajna)."""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

PORT = 9222


def port_listening(port: int = PORT) -> tuple[bool, str]:
    for host in ("127.0.0.1", "localhost"):
        url = f"http://{host}:{port}/json/version"
        try:
            with urllib.request.urlopen(url, timeout=3) as resp:
                body = resp.read(400).decode("utf-8", errors="replace")
                return True, f"{url}\n{body}"
        except (urllib.error.URLError, OSError) as exc:
            last = str(exc)
    return False, last


def devtools_active_port_file() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "User Data" / "DevToolsActivePort"


def chrome_process_info() -> dict:
    info: dict = {"count": 0, "debug_ports": [], "user_data_dirs": [], "shortest_cmd": ""}
    try:
        result = subprocess.run(
            ["wmic", "process", "where", "name='chrome.exe'", "get", "CommandLine"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception as exc:
        info["error"] = str(exc)
        return info
    text = result.stdout or ""
    info["count"] = text.lower().count("chrome.exe")
    info["debug_ports"] = sorted({int(m) for m in re.findall(r"--remote-debugging-port=(\d+)", text, re.I)})
    info["user_data_dirs"] = sorted(set(re.findall(r'--user-data-dir=([^\s"]+)', text, re.I)))[:5]
    lines = [ln.strip() for ln in text.splitlines() if "chrome.exe" in ln.lower()]
    if lines:
        lines.sort(key=len)
        info["shortest_cmd"] = lines[0][:500]
    return info


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true", help="Izhod 0/1 samo za bat (port OK / ne)")
    args = parser.parse_args()

    ok, detail = port_listening()
    proc = chrome_process_info()
    dt = devtools_active_port_file()
    dt_ok = dt.is_file()
    dt_text = dt.read_text(encoding="utf-8", errors="replace").strip() if dt_ok else ""

    if not args.quiet:
        if ok:
            print(f"LISTEN OK: {detail}")
        else:
            print(f"LISTEN FAIL: http://127.0.0.1:{PORT}/json/version -> {detail}")
        print(f"DevToolsActivePort: {'OK ' + dt_text if dt_ok else 'MANJKA (debugger ni aktiven)'}")
        print(f"chrome.exe count: {proc.get('count', 0)}")
        print(f"remote-debugging-port in cmdline: {proc.get('debug_ports') or 'NONE'}")
        print(f"user-data-dir samples: {proc.get('user_data_dirs') or 'DEFAULT_PROFILE'}")
        if proc.get("shortest_cmd"):
            print(f"shortest chrome cmdline: {proc['shortest_cmd']}")
        print()
        if ok:
            print("VERDICT: OK — Blagajna se lahko priklopi na tvoj Chrome.")
        elif proc.get("count", 0) > 0 and proc.get("debug_ports") and not ok:
            print(
                "VERDICT: NAPAKA — Chrome ima --remote-debugging-port, vendar port NE poslusa.\n"
                "         Na PRIVZETEM profilu to pogosto ne deluje (DevToolsActivePort manjka).\n"
                "         Resitev: ZAZENI_CHROME_EDAVKI_DEBUG.bat (profil BlagajnaFURS\\ChromeEdavki)."
            )
        elif proc.get("count", 0) > 0:
            print(
                "VERDICT: NAPAKA — Chrome tece BREZ debug porta.\n"
                "         Resitev: ZAZENI_CHROME_EDAVKI_DEBUG.bat (ločen eDavki profil)."
            )
        else:
            print("VERDICT: Chrome ne tece. Zazeni ZAZENI_CHROME_EDAVKI_DEBUG.bat.")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
