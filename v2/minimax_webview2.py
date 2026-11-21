"""Controller for dedicated Minimax Uvoz WebView2 helper (Chrome-free)."""
from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Callable, Dict, Optional


class WebView2Unavailable(RuntimeError):
    pass


class MinimaxUvozWebView2Controller:
    """Embeddable / standalone WebView2 process for Minimax Knjižbe in DDV uvoz."""

    def __init__(self, root_dir: Path):
        self.root_dir = Path(root_dir)
        self.helper = self.root_dir / "v2" / "minimax_webview2_host.py"
        # 5.1: lastna trajna seja v mapi aplikacije (relativno na skript), ne več iz mape 3.0.68.
        # Sejo 3.0.68 kopira INSTALL.pyw (enkratno, samo branje iz 3.0.68), da ponovna prijava ni potrebna.
        self.profile_dir = self.root_dir / "data" / "webview2" / "minimax_uvoz_profile"
        self.ipc_dir = self.root_dir / "data" / "webview2" / "ipc_uvoz"
        self.download_dir = self.root_dir / "data" / "webview2" / "downloads"
        self.commands_dir = self.ipc_dir / "commands"
        self.responses_dir = self.ipc_dir / "responses"
        self.state_file = self.ipc_dir / "state.json"
        self.events_file = self.ipc_dir / "events.jsonl"
        self.process: Optional[subprocess.Popen] = None
        self.hwnd = 0
        self.parent_hwnd = 0
        self._adopted_pid = 0
        self._event_offset = 0
        self._last_state: Dict[str, Any] = {}
        for p in (self.profile_dir, self.download_dir, self.commands_dir, self.responses_dir):
            p.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def supported() -> bool:
        return os.name == "nt"

    @staticmethod
    def _pid_alive(pid: int) -> bool:
        if int(pid or 0) <= 0:
            return False
        try:
            kernel = ctypes.windll.kernel32
            handle = kernel.OpenProcess(0x1000, False, int(pid))
            if handle:
                kernel.CloseHandle(handle)
                return True
        except Exception:
            pass
        try:
            os.kill(int(pid), 0)
            return True
        except OSError:
            return False

    def _adopt_from_state(self) -> bool:
        state = self.read_state()
        pid = int(state.get("pid") or 0)
        hwnd = int(state.get("hwnd") or 0)
        if not pid or not self._pid_alive(pid):
            self._adopted_pid = 0
            return False
        self._adopted_pid = pid
        self.hwnd = hwnd
        self._last_state = state
        return True

    def _host_alive(self) -> bool:
        if self.process is not None and self.process.poll() is None:
            return True
        if self._adopted_pid and self._pid_alive(self._adopted_pid):
            return True
        return self._adopt_from_state()

    def is_running(self) -> bool:
        if self.process and self.process.poll() is None and self.hwnd:
            return True
        return self._adopt_from_state()

    def _bring_to_front(self) -> None:
        hwnd = int(self.hwnd or 0)
        if not hwnd:
            return
        try:
            user32 = ctypes.windll.user32
            user32.ShowWindow(hwnd, 9)
            user32.SetForegroundWindow(hwnd)
        except Exception:
            pass

    def _pythonw(self) -> str:
        exe = Path(sys.executable)
        if os.name == "nt":
            candidate = exe.with_name("pythonw.exe")
            if candidate.exists():
                return str(candidate)
        return str(exe)

    def _clear_ipc(self) -> None:
        """Počisti samo IPC ukaze/odgovore — NIKOLI ne briše profila/piškotkov."""
        try:
            self.state_file.unlink(missing_ok=True)
        except Exception:
            pass
        for folder in (self.commands_dir, self.responses_dir):
            try:
                for p in folder.glob("*.json"):
                    p.unlink(missing_ok=True)
            except Exception:
                pass
        try:
            self.events_file.parent.mkdir(parents=True, exist_ok=True)
            self.events_file.write_text("", encoding="utf-8")
        except Exception:
            pass
        self._event_offset = 0

    def start(
        self,
        log: Optional[Callable[[str], None]] = None,
        timeout: float = 25.0,
        *,
        remote_debugging_port: int = 9333,
        start_url: str = "",
    ) -> Dict[str, Any]:
        log = log or (lambda _m: None)
        if not self.supported():
            raise WebView2Unavailable("WebView2 je podprt samo v Windows.")
        if self.is_running():
            log("WebView2: že odprt Minimax — nadaljujem v istem oknu.")
            self._bring_to_front()
            return dict(self._last_state)
        if not self.helper.exists():
            raise WebView2Unavailable(f"Manjka WebView2 modul: {self.helper}")

        if self.process and self.process.poll() is not None:
            self.process = None
            self.hwnd = 0
        # Samo IPC; profil (minimax_uvoz_profile) ostane — cookies med zagoni trajajo.
        self._clear_ipc()
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            self._pythonw(),
            str(self.helper),
            "--ipc-dir",
            str(self.ipc_dir),
            "--profile-dir",
            str(self.profile_dir),
            "--download-dir",
            str(self.download_dir),
            "--remote-debugging-port",
            str(int(remote_debugging_port)),
        ]
        if start_url:
            cmd.extend(["--start-url", start_url])

        log("WebView2: zaganjam Minimax uvoz brskalnik …")
        creationflags = 0
        if os.name == "nt":
            creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        env = os.environ.copy()
        env["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = (
            f"--remote-debugging-port={int(remote_debugging_port)} "
            f"--remote-allow-origins=*"
        )
        # Host teče kot v2/minimax_webview2_host.py → sys.path sicer nima korena (import v2 pade).
        env["PYTHONPATH"] = str(self.root_dir) + os.pathsep + str(env.get("PYTHONPATH") or "")
        self.process = subprocess.Popen(
            cmd,
            cwd=str(self.root_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
            env=env,
        )

        deadline = time.monotonic() + timeout
        last_error = ""
        while time.monotonic() < deadline:
            self._drain_events(log)
            if self.process.poll() is not None:
                raise WebView2Unavailable(
                    f"WebView2 proces se je končal (koda {self.process.returncode}). {last_error}".strip()
                )
            state = self.read_state()
            if state:
                self._last_state = state
                if state.get("fatal"):
                    raise WebView2Unavailable(str(state.get("fatal")))
                hwnd = int(state.get("hwnd") or 0)
                if state.get("ready") and hwnd:
                    self.hwnd = hwnd
                    log(
                        f"WebView2 pripravljen · renderer {state.get('renderer', 'EdgeChromium')} · "
                        f"CDP :{remote_debugging_port}"
                    )
                    return state
                last_error = str(state.get("message") or "")
            time.sleep(0.12)
        raise WebView2Unavailable(
            "WebView2 se v predvidenem času ni inicializiral. Preveri WebView2 Runtime in pywebview."
        )

    def read_state(self) -> Dict[str, Any]:
        try:
            if not self.state_file.exists():
                return {}
            return json.loads(self.state_file.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def _drain_events(self, log: Callable[[str], None]) -> None:
        try:
            if not self.events_file.exists():
                return
            with self.events_file.open("r", encoding="utf-8", errors="replace") as f:
                f.seek(self._event_offset)
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        item = json.loads(line)
                        msg = str(item.get("message") or "")
                    except Exception:
                        msg = line
                    if msg:
                        log("WebView2: " + msg)
                self._event_offset = f.tell()
        except Exception:
            pass

    def send(
        self,
        action: str,
        payload: Optional[Dict[str, Any]] = None,
        timeout: float = 90.0,
        log: Optional[Callable[[str], None]] = None,
        *,
        remote_debugging_port: int = 9333,
        start_url: str = "",
    ) -> Dict[str, Any]:
        log = log or (lambda _m: None)
        self.start(
            log=log,
            remote_debugging_port=remote_debugging_port,
            start_url=start_url,
        )
        request_id = uuid.uuid4().hex
        cmd_path = self.commands_dir / f"{request_id}.json"
        response_path = self.responses_dir / f"{request_id}.json"
        data = {"id": request_id, "action": action, "payload": payload or {}}
        tmp = cmd_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        tmp.replace(cmd_path)
        log(f"ukaz {action} poslan.")

        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self._drain_events(log)
            if not self._host_alive():
                raise WebView2Unavailable("WebView2 proces se je med izvajanjem končal.")
            if response_path.exists():
                try:
                    response = json.loads(response_path.read_text(encoding="utf-8"))
                finally:
                    try:
                        response_path.unlink(missing_ok=True)
                    except Exception:
                        pass
                if not response.get("ok"):
                    raise RuntimeError(str(response.get("error") or f"WebView2 ukaz {action} ni uspel."))
                return dict(response.get("result") or {})
            time.sleep(0.12)
        raise TimeoutError(f"WebView2 ukaz »{action}« se {timeout:.0f} s ni zaključil.")

    def import_knjizbe(
        self,
        *,
        xlsx_path: Path,
        date_sl: str,
        opis: str,
        organisation_id: Optional[int] = None,
        organisation_name: str = "",
        click_import: bool = True,
        open_temeljnica: bool = True,
        remote_debugging_port: int = 9333,
        start_url: str = "",
        login_username: str = "",
        login_password: str = "",
        log: Optional[Callable[[str], None]] = None,
    ) -> Dict[str, Any]:
        # ~210 s čakanje prijave + HARD firma + KN/IR/Excel
        return self.send(
            "import_knjizbe",
            {
                "xlsx_path": str(Path(xlsx_path).resolve()),
                "date_sl": date_sl,
                "opis": opis,
                "organisation_id": organisation_id,
                "organisation_name": organisation_name or "",
                "click_import": bool(click_import),
                "open_temeljnica": bool(open_temeljnica),
                "remote_debugging_port": int(remote_debugging_port),
                "login_username": (login_username or "").strip(),
                "login_password": (login_password or "").strip(),
            },
            timeout=320.0,
            log=log,
            remote_debugging_port=remote_debugging_port,
            start_url=start_url,
        )

    def open_knjizenje(
        self,
        *,
        organisation_id: Optional[int] = None,
        organisation_name: str = "",
        date_from: str = "",
        date_to: str = "",
        opis: str = "",
        remote_debugging_port: int = 9333,
        start_url: str = "",
        login_username: str = "",
        login_password: str = "",
        log: Optional[Callable[[str], None]] = None,
    ) -> Dict[str, Any]:
        """Video: HARD firma → Knjiženje IR/iztržkov → Najdi (po API pregled)."""
        zacetek = "https://moj.minimax.si/SI/VA/WebUI/Zacetek/Zacetek.aspx"
        return self.send(
            "open_knjizenje",
            {
                "organisation_id": organisation_id,
                "organisation_name": organisation_name or "",
                "date_from": date_from or "",
                "date_to": date_to or "",
                "opis": (opis or "").strip(),
                "login_username": (login_username or "").strip(),
                "login_password": (login_password or "").strip(),
            },
            timeout=280.0,
            log=log,
            remote_debugging_port=remote_debugging_port,
            start_url=start_url or zacetek,
        )

    def embed(self, parent_hwnd: int, width: int, height: int) -> None:
        if not self.supported() or not self.hwnd:
            return
        user32 = ctypes.windll.user32
        hwnd = int(self.hwnd)
        parent = int(parent_hwnd)
        if not parent:
            return
        GWL_STYLE = -16
        WS_CHILD = 0x40000000
        WS_VISIBLE = 0x10000000
        WS_CAPTION = 0x00C00000
        WS_THICKFRAME = 0x00040000
        WS_MINIMIZEBOX = 0x00020000
        WS_MAXIMIZEBOX = 0x00010000
        WS_SYSMENU = 0x00080000
        get_style = getattr(user32, "GetWindowLongPtrW", user32.GetWindowLongW)
        set_style = getattr(user32, "SetWindowLongPtrW", user32.SetWindowLongW)
        style = int(get_style(hwnd, GWL_STYLE))
        style &= ~(WS_CAPTION | WS_THICKFRAME | WS_MINIMIZEBOX | WS_MAXIMIZEBOX | WS_SYSMENU)
        style |= WS_CHILD | WS_VISIBLE
        user32.SetParent(hwnd, parent)
        set_style(hwnd, GWL_STYLE, style)
        self.parent_hwnd = parent
        self.resize(width, height)
        user32.ShowWindow(hwnd, 5)

    def resize(self, width: int, height: int) -> None:
        if not self.supported() or not self.hwnd or not self.parent_hwnd:
            return
        try:
            ctypes.windll.user32.MoveWindow(
                int(self.hwnd), 0, 0, max(50, int(width)), max(50, int(height)), True
            )
        except Exception:
            pass

    def show(self) -> None:
        if self.supported() and self.hwnd:
            try:
                ctypes.windll.user32.ShowWindow(int(self.hwnd), 5)
            except Exception:
                pass

    def hide(self) -> None:
        if self.supported() and self.hwnd:
            try:
                ctypes.windll.user32.ShowWindow(int(self.hwnd), 0)
            except Exception:
                pass

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            try:
                self.send("shutdown", {}, timeout=3)
            except Exception:
                try:
                    self.process.terminate()
                except Exception:
                    pass
        self.process = None
        self.hwnd = 0
        self.parent_hwnd = 0
