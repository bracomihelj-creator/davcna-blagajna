"""Zapri Chrome in znova zaženi z --remote-debugging-port (običajni profil)."""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

# reuse check from sibling module
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _check_chrome_debug import chrome_process_info, port_listening  # noqa: E402

DEFAULT_URL = "https://edavki.durs.si/"
DEFAULT_PORT = 9222


def edavki_chrome_profile_dir() -> Path:
    """Ločen profil za eDavki — debug port deluje (privzeti profil pogosto ne)."""
    p = Path(os.environ.get("LOCALAPPDATA", "")) / "BlagajnaFURS" / "ChromeEdavki"
    p.mkdir(parents=True, exist_ok=True)
    return p


def _find_chrome_exe() -> Path:
    for base in (
        os.environ.get("ProgramFiles", r"C:\Program Files"),
        os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
    ):
        p = Path(base) / "Google" / "Chrome" / "Application" / "chrome.exe"
        if p.is_file():
            return p
    raise FileNotFoundError("chrome.exe ni najden.")


def _kill_chrome_for_profile(profile_dir: Path, timeout_sec: float = 30.0) -> None:
    """Zapri le Chrome z našim eDavki profilom (običajni Chrome ostane odprt)."""
    needle = str(profile_dir.resolve()).lower()
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        try:
            result = subprocess.run(
                ["wmic", "process", "where", "name='chrome.exe'", "get", "ProcessId,CommandLine"],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            )
        except Exception:
            break
        pids: list[int] = []
        for line in (result.stdout or "").splitlines():
            low = line.lower()
            if "chrome.exe" not in low or needle not in low:
                continue
            parts = line.strip().split()
            if parts and parts[-1].isdigit():
                pids.append(int(parts[-1]))
        if not pids:
            return
        for pid in pids:
            subprocess.run(
                ["taskkill", "/F", "/PID", str(pid), "/T"],
                capture_output=True,
                check=False,
            )
        time.sleep(1.0)


def _start_chrome(chrome: Path, profile_dir: Path, port: int, url: str) -> subprocess.Popen:
    args = [
        str(chrome),
        f"--user-data-dir={profile_dir}",
        f"--remote-debugging-port={port}",
        "--remote-debugging-address=127.0.0.1",
        "--remote-allow-origins=*",
        "--no-first-run",
        "--no-default-browser-check",
        url,
    ]
    return subprocess.Popen(args, close_fds=True)


def _wait_port(port: int, timeout_sec: float = 60.0) -> bool:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        ok, _detail = port_listening(port)
        if ok:
            return True
        time.sleep(1.5)
    return False


def ensure_edavki_chrome_debug(
    *,
    port: int = DEFAULT_PORT,
    url: str = DEFAULT_URL,
    restart: bool = False,
    wait_sec: float = 60.0,
) -> bool:
    """Zaženi eDavki Chrome z debug portom, če še ne teče. Vrne True, ko port posluša."""
    ok_before, _ = port_listening(port)
    if ok_before and not restart:
        return True

    chrome = _find_chrome_exe()
    profile = edavki_chrome_profile_dir()
    if restart or ok_before:
        _kill_chrome_for_profile(profile)

    _start_chrome(chrome, profile, port, url)
    return _wait_port(port, timeout_sec=wait_sec)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument(
        "--restart",
        action="store_true",
        help="Znova zaženi eDavki Chrome (zapri le profil BlagajnaFURS/ChromeEdavki)",
    )
    parser.add_argument("--wait-sec", type=float, default=60.0)
    args = parser.parse_args()

    chrome = _find_chrome_exe()
    profile = edavki_chrome_profile_dir()
    print(f"Chrome: {chrome}")
    print(f"Profil eDavki: {profile}")
    print(f"Debug port: {args.port}")
    print(f"URL: {args.url}")
    print("(Tvoj obicajni Chrome lahko ostane odprt.)")

    if ensure_edavki_chrome_debug(
        port=args.port,
        url=args.url,
        restart=args.restart,
        wait_sec=args.wait_sec,
    ):
        print(f"OK — debug port {args.port} deluje.")
        print("Enkrat se prijavi v eDavke (certifikat) v NOVEM Chrome oknu, nato FURS Blagajna.")
        try:
            from _ensure_davcna_pyw import ensure_davcna_pyw_running

            ok_app, msg_app = ensure_davcna_pyw_running()
            print(f"Davčna Blagajna (.pyw): {msg_app}" + ("" if ok_app else " (napaka)"))
        except Exception as exc:
            print(f"Davčna Blagajna (.pyw): {exc}")
        return 0

    proc = chrome_process_info()
    dt = profile / "DevToolsActivePort"
    print()
    print(f"NAPAKA: Port {args.port} se po {int(args.wait_sec)} s ni odprl.")
    print(f"chrome.exe procesov (skupaj): {proc.get('count', 0)}")
    print(f"DevToolsActivePort v profilu: {'obstaja' if dt.is_file() else 'MANJKA'}")
    print()
    print("Poskusi rocno v PowerShell:")
    print(
        f'  & "{chrome}" --user-data-dir="{profile}" '
        f'--remote-debugging-port={args.port} --remote-allow-origins=* "{args.url}"'
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
