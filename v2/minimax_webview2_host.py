"""Standalone WebView2 host for Minimax Uvoz podatkov (Knjižbe in DDV).

Ločen od FURS Chrome in Chrome Minimax vtičnikov.
Profil: data/webview2/minimax_uvoz_profile (trajna seja; ni ista kot Chrome).
Če ni prijave: čakaj v oknu (~210 s), nato isti uvoz nadaljuje — brez drugega klika.
Pot: Vstopite → HARD firma → UvozPodatkov → KN potrdi → radio → IR/datum/opis → Excel → Uvozi.
Selektorji iz Hitri zajem 2026-10-08 / video uvoza.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
import sys
import threading
import time
import traceback
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
os.chdir(str(_ROOT))

MINIMAX_UVOZ_URL = "https://moj.minimax.si/SI/VA/WebUI/UvozPodatkov/UvozPodatkovCSV.aspx"
MINIMAX_ZACETEK_URL = "https://moj.minimax.si/SI/VA/WebUI/Zacetek/Zacetek.aspx"
MINIMAX_KNJIZENJE_URL = (
    "https://moj.minimax.si/SI/VA/WebUI/KnjizenjeIzdanegaRacuna/KnjizenjeIzdanegaRacuna.aspx"
)
VRSTA_ID = "2"
VRSTA_LABEL = "IR - Izdani račun"
TIP_LABEL = "Knjižbe in DDV"


def _http_json(url: str, timeout: float = 3.0) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _cdp_ws_connect(ws_url: str, timeout_sec: float = 10.0):
    """Odpri en CDP WebSocket (nodeId velja samo znotraj te seje)."""
    try:
        import websocket  # type: ignore
    except Exception as exc:
        raise RuntimeError(
            "Za priponko datoteke v WebView2 potrebuješ paket websocket-client "
            f"(pip install websocket-client). {exc}"
        ) from exc

    # Chromium zavrne WS brez --remote-allow-origins (403).
    try:
        return websocket.create_connection(
            ws_url, timeout=timeout_sec, suppress_origin=True
        )
    except TypeError:
        return websocket.create_connection(ws_url, timeout=timeout_sec)


def _cdp_ws_call(ws: Any, method: str, params: Optional[dict] = None, timeout_sec: float = 10.0) -> Any:
    """En CDP ukaz na že odprtem socketu."""
    msg_id = int(time.time() * 1000) % 1_000_000_000
    ws.send(json.dumps({"id": msg_id, "method": method, "params": params or {}}))
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        raw = ws.recv()
        data = json.loads(raw)
        if data.get("id") == msg_id:
            if "error" in data:
                raise RuntimeError(str(data["error"]))
            return data.get("result")
    raise TimeoutError(f"CDP timeout: {method}")


def _cdp_ws_send(ws_url: str, method: str, params: Optional[dict] = None, timeout_sec: float = 10.0) -> Any:
    """Enkratni CDP klic (nova seja) — za diagnostiko; priponka uporablja _cdp_set_file_input."""
    ws = _cdp_ws_connect(ws_url, timeout_sec=timeout_sec)
    try:
        return _cdp_ws_call(ws, method, params, timeout_sec=timeout_sec)
    finally:
        try:
            ws.close()
        except Exception:
            pass


def _webview2_cdp_args(port: int) -> str:
    """Argumenti Edge/WebView2 za CDP priponko datoteke."""
    p = int(port)
    return f"--remote-debugging-port={p} --remote-allow-origins=*"


def _cdp_list_pages(debug_port: int) -> tuple[list, str]:
    """Vrni (pages, error)."""
    try:
        pages = _http_json(f"http://127.0.0.1:{int(debug_port)}/json", timeout=2.0)
        return list(pages or []), ""
    except Exception as exc:
        return [], f"cdp_port:{exc}"


def _cdp_pick_ws(pages: list) -> str:
    for row in pages or []:
        u = str(row.get("url") or "")
        if "UvozPodatkov" in u or "minimax" in u.lower():
            ws = str(row.get("webSocketDebuggerUrl") or "").strip()
            if ws:
                return ws
    if pages:
        return str((pages[0] or {}).get("webSocketDebuggerUrl") or "").strip()
    return ""


def _cdp_set_file_input(
    debug_port: int,
    file_path: Path,
    *,
    selectors: Optional[list] = None,
    retries: int = 8,
    pause: float = 0.45,
) -> Dict[str, Any]:
    """CDP DOM.setFileInputFiles — VSA logika v ENI WebSocket seji (sicer nodeId pade)."""
    path = str(Path(file_path).resolve())
    if not Path(path).is_file():
        return {"ok": False, "how": "no_file", "detail": path}
    sels = list(
        selectors
        or [
            "#PPC_EPC_DC_FileUpload1",
            "input#PPC_EPC_DC_FileUpload1",
            "input[type=file][id*='FileUpload']",
            "input[type=file]",
        ]
    )
    last_err = ""
    for attempt in range(max(1, int(retries))):
        pages, perr = _cdp_list_pages(debug_port)
        if perr:
            last_err = perr
            time.sleep(pause)
            continue
        if not pages:
            last_err = "cdp_empty_targets"
            time.sleep(pause)
            continue
        ws_url = _cdp_pick_ws(pages)
        if not ws_url:
            last_err = "cdp_no_ws"
            time.sleep(pause)
            continue
        ws = None
        try:
            ws = _cdp_ws_connect(ws_url, timeout_sec=12.0)
            _cdp_ws_call(ws, "DOM.enable", {})
            doc = None
            for gd_params in ({"depth": -1, "pierce": True}, {"depth": 0}, {}):
                try:
                    doc = _cdp_ws_call(ws, "DOM.getDocument", gd_params)
                    if (doc or {}).get("root"):
                        break
                except Exception:
                    doc = None
            root_id = int(((doc or {}).get("root") or {}).get("nodeId") or 0)
            if not root_id:
                last_err = "cdp_no_root"
                time.sleep(pause)
                continue

            used_sel = ""
            set_ok = False
            for sel in sels:
                q = _cdp_ws_call(
                    ws, "DOM.querySelector", {"nodeId": root_id, "selector": sel}
                )
                nid = int((q or {}).get("nodeId") or 0)
                if not nid:
                    continue
                used_sel = sel
                backend_id = 0
                try:
                    desc = _cdp_ws_call(ws, "DOM.describeNode", {"nodeId": nid})
                    backend_id = int(
                        ((desc or {}).get("node") or {}).get("backendNodeId") or 0
                    )
                except Exception:
                    backend_id = 0
                # Poskusi oba načina v ISTI seji
                for params in (
                    ({"backendNodeId": backend_id, "files": [path]} if backend_id else None),
                    {"nodeId": nid, "files": [path]},
                ):
                    if not params:
                        continue
                    try:
                        _cdp_ws_call(ws, "DOM.setFileInputFiles", params)
                        set_ok = True
                        break
                    except Exception as exc:
                        last_err = f"cdp_set:{exc}"
                if set_ok:
                    break

            if set_ok:
                return {
                    "ok": True,
                    "how": "cdp_setFileInputFiles",
                    "selector": used_sel,
                    "attempt": attempt + 1,
                }
            if not used_sel:
                last_err = "cdp_no_file_input"
        except Exception as exc:
            last_err = f"cdp_exc:{exc}"
        finally:
            if ws is not None:
                try:
                    ws.close()
                except Exception:
                    pass
        time.sleep(pause)
    return {"ok": False, "how": last_err or "cdp_failed", "detail": f"port={debug_port}"}


def _clipboard_set_unicode(text: str) -> bool:
    """CF_UNICODETEXT v odložišče (Windows) — retry + PowerShell fallback."""
    if os.name != "nt":
        return False
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    CF_UNICODETEXT = 13
    GMEM_MOVEABLE = 0x0002
    for _ in range(6):
        try:
            if user32.OpenClipboard(0):
                try:
                    user32.EmptyClipboard()
                    data = (text + "\0").encode("utf-16-le")
                    h = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
                    if not h:
                        continue
                    ptr = kernel32.GlobalLock(h)
                    if not ptr:
                        kernel32.GlobalFree(h)
                        continue
                    ctypes.memmove(ptr, data, len(data))
                    kernel32.GlobalUnlock(h)
                    if user32.SetClipboardData(CF_UNICODETEXT, h):
                        return True
                    kernel32.GlobalFree(h)
                finally:
                    user32.CloseClipboard()
        except Exception:
            pass
        time.sleep(0.12)
    try:
        import subprocess

        # PowerShell Set-Clipboard (literal, escaped single quotes)
        safe = text.replace("'", "''")
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"Set-Clipboard -Value '{safe}'",
            ],
            check=False,
            capture_output=True,
            timeout=8,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0,
        )
        return True
    except Exception:
        return False


def _send_ctrl_v_enter() -> None:
    """Ctrl+V, Enter prek keybd_event."""
    if os.name != "nt":
        return
    user32 = ctypes.windll.user32
    KEYEVENTF_KEYUP = 0x0002
    VK_CONTROL = 0x11
    VK_V = 0x56
    VK_RETURN = 0x0D

    def _down(vk: int) -> None:
        user32.keybd_event(vk, 0, 0, 0)

    def _up(vk: int) -> None:
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)

    _down(VK_CONTROL)
    _down(VK_V)
    _up(VK_V)
    _up(VK_CONTROL)
    time.sleep(0.12)
    _down(VK_RETURN)
    _up(VK_RETURN)


def _find_open_dialog_hwnd() -> int:
    """Najdi HWND Windows Open/Odpri dialoga."""
    if os.name != "nt":
        return 0
    user32 = ctypes.windll.user32
    found = ctypes.c_void_p(0)
    titles = (
        "Open",
        "Odpri",
        "Izberi datoteko",
        "Izberite datoteko",
        "Select File",
        "File Upload",
    )

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def _enum(hwnd, _lparam):
        if not user32.IsWindowVisible(hwnd):
            return True
        buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf, 512)
        title = (buf.value or "").strip()
        if not title:
            return True
        cls = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cls, 256)
        is_dlg = (cls.value or "") == "#32770"
        for t in titles:
            if title == t or title.startswith(t) or t.lower() in title.lower():
                if is_dlg or True:
                    found.value = hwnd
                    return False
        return True

    user32.EnumWindows(_enum, 0)
    return int(found.value or 0)


def _dialog_set_filename(hwnd: int, path: str) -> bool:
    """WM_SETTEXT na Edit/ComboBoxEx v Open dialogu (brez odložišča)."""
    if os.name != "nt" or not hwnd:
        return False
    user32 = ctypes.windll.user32
    WM_SETTEXT = 0x000C
    edits: list[int] = []

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def _enum_child(ch, _lp):
        cls = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(ch, cls, 256)
        name = (cls.value or "").lower()
        if name in ("edit", "comboboxex32", "combobox"):
            edits.append(int(ch))
        return True

    user32.EnumChildWindows(hwnd, _enum_child, 0)
    if not edits:
        return False
    # Zadnji Edit je običajno polje »Ime datoteke«
    target = edits[-1]
    user32.SendMessageW(target, WM_SETTEXT, 0, path)
    return True


def _win_file_dialog_attach(file_path: Path, *, wait_dialog: float = 6.0) -> Dict[str, Any]:
    """Po kliku Izberite datoteko: v Open dialog vpiši pot + Enter."""
    path = str(Path(file_path).resolve())
    if not Path(path).is_file():
        return {"ok": False, "how": "no_file"}
    deadline = time.monotonic() + wait_dialog
    hwnd = 0
    while time.monotonic() < deadline:
        hwnd = _find_open_dialog_hwnd()
        if hwnd:
            break
        time.sleep(0.15)
    if not hwnd:
        return {"ok": False, "how": "no_open_dialog"}
    try:
        user32 = ctypes.windll.user32
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.25)
        if _dialog_set_filename(hwnd, path):
            time.sleep(0.1)
            # Enter potrdi Odpri
            VK_RETURN = 0x0D
            KEYEVENTF_KEYUP = 0x0002
            user32.keybd_event(VK_RETURN, 0, 0, 0)
            user32.keybd_event(VK_RETURN, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.4)
            return {"ok": True, "how": "win_dialog_settext", "hwnd": hwnd}
        # Fallback: odložišče + Ctrl+V Enter
        if _clipboard_set_unicode(path):
            _send_ctrl_v_enter()
            time.sleep(0.4)
            return {"ok": True, "how": "win_dialog_clipboard", "hwnd": hwnd}
        return {"ok": False, "how": "clipboard_failed", "hwnd": hwnd}
    except Exception as exc:
        return {"ok": False, "how": f"dialog_exc:{exc}"}


class Host:
    def __init__(
        self,
        ipc_dir: Path,
        profile_dir: Path,
        download_dir: Path,
        *,
        remote_debugging_port: int = 9333,
        start_url: str = MINIMAX_ZACETEK_URL,
    ):
        self.ipc_dir = ipc_dir
        self.profile_dir = profile_dir
        self.download_dir = download_dir
        self.remote_debugging_port = int(remote_debugging_port)
        self.start_url = start_url or MINIMAX_ZACETEK_URL
        self.commands_dir = ipc_dir / "commands"
        self.responses_dir = ipc_dir / "responses"
        self.state_file = ipc_dir / "state.json"
        self.events_file = ipc_dir / "events.jsonl"
        self.window = None
        self.ready = threading.Event()
        self.stop_event = threading.Event()
        self.hwnd = 0
        for p in (self.ipc_dir, self.profile_dir, self.download_dir, self.commands_dir, self.responses_dir):
            p.mkdir(parents=True, exist_ok=True)

    def emit(self, message: str, level: str = "INFO") -> None:
        item = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": str(message),
        }
        try:
            with self.events_file.open("a", encoding="utf-8") as f:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def write_state(self, **updates) -> None:
        state: Dict[str, Any] = {}
        try:
            if self.state_file.exists():
                state = json.loads(self.state_file.read_text(encoding="utf-8"))
        except Exception:
            state = {}
        state.update(updates)
        state["pid"] = os.getpid()
        state["remote_debugging_port"] = self.remote_debugging_port
        tmp = self.state_file.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            tmp.replace(self.state_file)
        except Exception:
            pass

    def _find_hwnd(self, title: str) -> int:
        if os.name != "nt":
            return 0
        try:
            return int(ctypes.windll.user32.FindWindowW(None, title) or 0)
        except Exception:
            return 0

    def before_show(self, window) -> None:
        self.window = window
        self.emit("native WebView2 control inicializiran.")

    def shown(self, window) -> None:
        self.window = window
        title = str(getattr(window, "title", "Davčna Blagajna — Minimax Uvoz WebView2"))
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline and not self.hwnd:
            self.hwnd = self._find_hwnd(title)
            if not self.hwnd:
                time.sleep(0.05)
        self.ready.set()
        self.write_state(
            ready=True,
            hwnd=self.hwnd,
            renderer="EdgeChromium / WebView2",
            profile=str(self.profile_dir),
            message="WebView2 pripravljen",
        )
        self.emit(f"WebView2 pripravljen; CDP :{self.remote_debugging_port}; profil={self.profile_dir}")
        threading.Thread(target=self.command_loop, daemon=True, name="WebView2IPC").start()

    def loaded(self, window) -> None:
        self.window = window

    def eval(self, script: str):
        if not self.window:
            raise RuntimeError("WebView2 okno še ni pripravljeno.")
        return self.window.evaluate_js(script)

    def wait_ready_state(self, timeout: float = 15.0) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                state = self.eval("document.readyState")
                if str(state) in ("interactive", "complete"):
                    return
            except Exception:
                pass
            time.sleep(0.15)

    def navigate(self, url: str) -> None:
        self.window.load_url(url)
        self.wait_ready_state(20)
        time.sleep(0.4)

    def snapshot(self) -> Dict[str, Any]:
        script = r"""
        (() => {
          const n = s => (s || '').normalize('NFD').replace(/[\u0300-\u036f]/g,'')
             .replace(/\s+/g,' ').trim().toUpperCase();
          const href = location.href || '';
          const path = location.pathname || '';
          const title = document.title || '';
          let org = '';
          for (const e of document.querySelectorAll(
            'ul.mm-menu > li > span.mm-header-dropdown > a, a[href*="ZacetekOrganizacije.aspx"]'
          )) {
            const t = (e.innerText || e.textContent || '').replace(/\s+/g, ' ').trim();
            if (t) { org = t; break; }
          }
          const body = (document.body?.innerText || '').slice(0, 12000);
          const bn = n(body);
          const hu = href.toUpperCase();
          const loginPage = /LOGIN|PRIJAVA|ACCOUNT|AUTH/i.test(href)
            || (bn.includes('PRIJAVA') && /LOGIN|ACCOUNT|AUTH/i.test(hu)
                && !/Zacetek\.aspx/i.test(path));
          const vstopite = /VSTOPITE(\s+V\s+PROGRAM)?/i.test(body)
            && !/Zacetek|UvozPodatkov|WebUI\/Zacetek/i.test(path);
          const onOrgList = /Zacetek\.aspx/i.test(path) && !/ZacetekOrganizacije/i.test(path);
          const alreadyWebUi = /Zacetek|UvozPodatkov|WebUI\//i.test(path) && !loginPage;
          return {
            url: href,
            path,
            title,
            organisation: org,
            login_page: Boolean(loginPage && !onOrgList && !alreadyWebUi),
            logged_in: !loginPage && !vstopite,
            needs_vstopite: Boolean(vstopite),
            on_org_list: Boolean(onOrgList),
            has_uvoz_form: Boolean(document.querySelector('#PPC_EPC_DC_I_Datum')),
            has_report: /POROCILO O UVOZU/i.test(bn)
              || Boolean(document.querySelector('#PPC_EPC_DC_A_PrikaziTemeljnico'))
          };
        })()
        """
        result = self.eval(script)
        return dict(result or {}) if isinstance(result, dict) else {}

    def try_fill_login(self, username: str, password: str) -> Dict[str, Any]:
        """Soft auto-fill prijave — SAMO login/auth polja, nikoli #F_Search / Moje org."""
        user = (username or "").strip()
        pwd = (password or "").strip()
        if not user or not pwd:
            return {"ok": False, "how": "no_credentials"}
        user_js = json.dumps(user)
        pwd_js = json.dumps(pwd)
        script = f"""
        (() => {{
          const user = {user_js};
          const pwd = {pwd_js};
          const path = location.pathname || '';
          const href = location.href || '';
          const onOrgList = /Zacetek\\.aspx/i.test(path) && !/ZacetekOrganizacije/i.test(path);
          const onWebUi = /Zacetek|UvozPodatkov|WebUI\\//i.test(path);
          const loginPage = /LOGIN|PRIJAVA|ACCOUNT|AUTH/i.test(href);
          if (onOrgList || (onWebUi && !loginPage)) {{
            return {{ ok: false, how: 'skip_already_in_app', href }};
          }}
          const visible = (el) => {{
            if (!el) return false;
            const r = el.getBoundingClientRect();
            const st = window.getComputedStyle(el);
            return r.width > 4 && r.height > 4
              && st.visibility !== 'hidden' && st.display !== 'none' && st.opacity !== '0';
          }};
          const isOrgSearch = (el) => {{
            if (!el) return true;
            const id = String(el.id || '').toLowerCase();
            const name = String(el.name || '').toLowerCase();
            const ph = String(el.getAttribute('placeholder') || '').toLowerCase();
            const cls = String(el.className || '').toLowerCase();
            const aria = String(el.getAttribute('aria-label') || '').toLowerCase();
            if (id === 'f_search' || id.includes('search') || id.includes('filter')) return true;
            if (name.includes('search') || name.includes('filter')) return true;
            if (/oišči|poisci|organizac|filtertextbox|filter/i.test(ph + ' ' + aria)) return true;
            if (cls.includes('filter') || cls.includes('search')) return true;
            try {{
              if (el.closest('#F_Search, .FilterTextBox, [id*="Search"], [class*="FilterText"]')) return true;
            }} catch (e) {{}}
            return false;
          }};
          const setVal = (el, v) => {{
            if (!el) return false;
            try {{ el.focus(); }} catch (e) {{}}
            try {{
              const desc = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
              if (desc && desc.set) desc.set.call(el, v); else el.value = v;
            }} catch (e) {{ el.value = v; }}
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
          }};
          const passEl = Array.from(document.querySelectorAll(
            "input[type='password'], input[autocomplete='current-password']"
          )).find(visible);
          if (!passEl && !loginPage) {{
            return {{ ok: false, how: 'not_login_page', href }};
          }}
          let email = Array.from(document.querySelectorAll(
            "input[type='email'], input[name='username'], input[name='Email'], "
            + "input[name='UserName'], input[autocomplete='username'], "
            + "input[id*='Email'], input[id*='User'], input[id*='Login']"
          )).find(el => visible(el) && !isOrgSearch(el));
          if (!email && passEl) {{
            const root = passEl.closest('form') || passEl.closest('.panel, .card, .modal, body') || document;
            email = Array.from(root.querySelectorAll(
              "input[type='text'], input:not([type]), input[type='email']"
            )).find(el => visible(el) && !isOrgSearch(el) && el !== passEl);
          }}
          if (!email) return {{ ok: false, how: 'no_email_field', href }};
          if (isOrgSearch(email)) return {{ ok: false, how: 'blocked_org_search', href }};
          setVal(email, user);
          if (passEl) setVal(passEl, pwd);
          const btns = Array.from(document.querySelectorAll(
            'button, input[type=submit], input[type=button], a[role=button], [role=button]'
          )).filter(visible);
          const hit = btns.find(el => {{
            const t = ((el.innerText || el.value || el.textContent || '') + '').trim();
            return /prijava|prijavi|login|sign\\s*in|naprej|nadaljuj/i.test(t);
          }});
          if (hit) {{
            try {{ hit.click(); }} catch (e) {{
              try {{
                hit.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}));
              }} catch (e2) {{}}
            }}
            return {{ ok: true, how: passEl ? 'filled_both_clicked' : 'filled_user_clicked', href }};
          }}
          return {{ ok: true, how: passEl ? 'filled_both' : 'filled_user', href }};
        }})()
        """
        try:
            result = self.eval(script)
            out = dict(result or {}) if isinstance(result, dict) else {"ok": False}
            if out.get("ok"):
                self.emit(f"auto-prijava: {out.get('how')}")
            return out
        except Exception as exc:
            return {"ok": False, "how": f"eval_error:{exc}"}

    def wait_until_logged_in(
        self,
        *,
        timeout: float = 210.0,
        login_username: str = "",
        login_password: str = "",
    ) -> Dict[str, Any]:
        """Ne prekini uvoza — počakaj prijavo v tem oknu, nato nadaljuj isti uvoz."""
        self.navigate(MINIMAX_ZACETEK_URL)
        time.sleep(0.4)
        self.pass_vstopite(timeout=8.0)
        snap = self.snapshot()
        if snap.get("on_org_list") or (snap.get("logged_in") and not snap.get("needs_vstopite")):
            return snap

        self.emit(
            "Čakam prijavo v tem oknu… "
            "(če je Minimax že v Chrome: Nastavitve → Odpri Minimax Chrome z debug, "
            "da lahko WebView2 prevzame sejo brez ponovne prijave)"
        )
        autofill_tried = False
        deadline = time.monotonic() + max(30.0, float(timeout))
        last_emit = 0.0
        while time.monotonic() < deadline:
            snap = self.snapshot()
            if snap.get("needs_vstopite"):
                self.pass_vstopite(timeout=8.0)
                snap = self.snapshot()
            if snap.get("on_org_list") or (snap.get("logged_in") and not snap.get("needs_vstopite")):
                self.emit("Prijava zaznana — nadaljujem uvoz.")
                return snap
            # Soft auto-fill SAMO na login/auth strani — nikoli na Moje organizacije
            if (
                not autofill_tried
                and login_username
                and login_password
                and snap.get("login_page")
                and not snap.get("on_org_list")
            ):
                autofill_tried = True
                self.try_fill_login(login_username, login_password)
                time.sleep(1.2)
            now = time.monotonic()
            if now - last_emit >= 12.0:
                left = max(0, int(deadline - now))
                self.emit(f"Čakam prijavo v tem oknu… še ~{left} s")
                last_emit = now
            time.sleep(0.9)

        raise RuntimeError(
            "WebView2 Minimax: prijava v predvidenem času ni bila zaznana.\n\n"
            "Prijavi se v odprtem WebView2 oknu (seja se shrani v\n"
            "data/webview2/minimax_uvoz_profile — ni ista kot Chrome),\n"
            "nato znova klikni Minimax spletni uvoz.\n\n"
            "Če si se že prijavil, pusti okno odprto in ponovi — uvoz bo nadaljeval."
        )

    def pass_vstopite(self, *, timeout: float = 12.0) -> Dict[str, Any]:
        """Peach landing »Vstopite v program« → WebUI (Moje org)."""
        script = r"""
        (() => {
          const txt = (el) => ((el && (el.innerText || el.textContent || el.value
            || el.getAttribute('aria-label') || el.getAttribute('title'))) || '')
            .replace(/\s+/g, ' ').trim();
          const visible = (el) => {
            if (!el) return false;
            const r = el.getBoundingClientRect();
            const st = window.getComputedStyle(el);
            return r.width > 8 && r.height > 8
              && st.visibility !== 'hidden' && st.display !== 'none' && st.opacity !== '0';
          };
          const fire = (el) => {
            if (!el) return false;
            try { el.scrollIntoView({ block: 'center' }); } catch (e) {}
            try { el.focus(); } catch (e) {}
            try { el.click(); return true; } catch (e) {}
            try {
              el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
              return true;
            } catch (e) { return false; }
          };
          const match = (s) => /vstopite(\s+v\s+program)?/i.test(s || '') || /vstop.*program/i.test(s || '');
          const nodes = Array.from(document.querySelectorAll(
            'a, button, input[type=button], input[type=submit], [role="button"], span, div'
          )).filter(visible);
          let hit = nodes.find(el => match(txt(el)));
          if (!hit) {
            hit = nodes.find(el => {
              const tag = (el.tagName || '').toLowerCase();
              const role = (el.getAttribute('role') || '').toLowerCase();
              if (!(tag === 'a' || tag === 'button' || tag === 'input' || role === 'button')) return false;
              const t = txt(el);
              return t.length >= 4 && t.length < 48 && /vstop/i.test(t);
            });
          }
          if (!hit) return { ok: false, reason: 'no_button', href: location.href };
          const clickable = hit.closest('a, button, [role="button"]') || hit;
          if (!fire(clickable)) return { ok: false, reason: 'click_failed', text: txt(clickable) };
          return { ok: true, text: txt(clickable), href: location.href };
        })()
        """
        snap = self.snapshot()
        if not snap.get("needs_vstopite"):
            return {"ok": True, "how": "not_needed"}
        self.emit("Vstopite v program → klik")
        deadline = time.monotonic() + timeout
        last: Dict[str, Any] = {}
        while time.monotonic() < deadline:
            last = dict(self.eval(script) or {})
            if last.get("ok"):
                time.sleep(1.2)
                self.wait_ready_state(15)
                snap2 = self.snapshot()
                if not snap2.get("needs_vstopite"):
                    return {"ok": True, "how": "clicked", "text": last.get("text")}
            time.sleep(0.4)
        return {"ok": False, "how": "timeout", "detail": last}

    def firm_active(self, *, organisation_name: str = "") -> Dict[str, Any]:
        """True če navbar/title kaže firmo (ZacetekOrganizacije / Uvoz), ne Moje org."""
        name_js = json.dumps((organisation_name or "").strip())
        script = f"""
        (() => {{
          const want = {name_js};
          const path = location.pathname || '';
          const title = document.title || '';
          const onOrgList = /Zacetek\\.aspx/i.test(path) && !/ZacetekOrganizacije/i.test(path);
          if (onOrgList) return {{ ok: false, org: '', path, title, reason: 'org_list' }};
          const pickText = (el) => ((el && (el.innerText || el.textContent)) || '').replace(/\\s+/g, ' ').trim();
          const candidates = [];
          const nav = document.querySelector('ul.mm-menu > li > span.mm-header-dropdown > a');
          if (nav) candidates.push(pickText(nav));
          document.querySelectorAll(
            'header a, header span, .mm-header a, .mm-header span, [class*="header"] a, nav a, h1, h2'
          ).forEach(el => {{
            const r = el.getBoundingClientRect();
            if (r.top < 140 && r.width > 20 && r.height > 8) {{
              const t = pickText(el);
              if (t && t.length >= 4 && t.length < 80
                  && !/^(nov|poslovanje|knjigovodstvo|banka|plače|šifranti|nabiralnik)/i.test(t)) {{
                candidates.push(t);
              }}
            }}
          }});
          const org = candidates.find(Boolean) || '';
          const hay = (org + ' ' + title).toLowerCase();
          let nameOk = !want;
          if (want) {{
            const w = want.toLowerCase();
            const parts = w.split(/[,.\\s]+/).filter(p => p.length >= 3).slice(0, 2);
            nameOk = hay.includes(w) || (parts.length > 0 && parts.every(p => hay.includes(p)));
          }}
          const inFirmUi = /ZacetekOrganizacije/i.test(path)
            || /UvozPodatkov/i.test(path)
            || (/WebUI/i.test(path) && !onOrgList && nameOk);
          return {{
            ok: Boolean(inFirmUi && nameOk),
            org: org || title,
            path,
            title,
            reason: nameOk ? 'ok' : 'name_mismatch'
          }};
        }})()
        """
        result = self.eval(script)
        return dict(result or {}) if isinstance(result, dict) else {"ok": False}

    def wait_firm_in_navbar(
        self, *, organisation_name: str = "", timeout: float = 18.0
    ) -> Dict[str, Any]:
        deadline = time.monotonic() + timeout
        last: Dict[str, Any] = {}
        while time.monotonic() < deadline:
            self.pass_vstopite(timeout=4.0)
            last = self.firm_active(organisation_name=organisation_name)
            if last.get("ok"):
                return last
            time.sleep(0.45)
        return {"ok": False, "reason": last.get("reason") or "timeout", "detail": last}

    def ensure_organisation(self, *, organisation_id: Optional[int], organisation_name: str = "") -> Dict[str, Any]:
        """HARD: Moje org → klik NAZIVA firme v seznamu (ne soft-skip).

        Počisti #F_Search, najdi vrstico (data-organizacijaid / naziv), scrollIntoView,
        klik samo na povezavo z besedilom naziva — nikoli zvezda/priljubljene.
        #F_Search samo kot zadnji fallback.
        """
        oid = int(organisation_id) if organisation_id else 0
        onm = (organisation_name or "").strip()
        already = self.firm_active(organisation_name=onm)
        if already.get("ok"):
            return {
                "ok": True,
                "how": "already",
                "organisation": already.get("org") or onm,
            }

        if not oid and not onm:
            return {"ok": False, "how": "no_target", "detail": "Manjka OrganisationId/naziv."}

        self.emit(f"HARD firma: {onm or oid}")
        self.navigate(MINIMAX_ZACETEK_URL)
        time.sleep(0.6)
        self.pass_vstopite(timeout=8.0)

        def _org_click_script(*, allow_search: bool) -> str:
            return f"""
        (() => {{
          const oid = {json.dumps(str(oid) if oid else "")};
          const allowSearch = {json.dumps(bool(allow_search))};
          const norm = (s) => String(s || '')
            .normalize('NFD').replace(/[\\u0300-\\u036f]/g, '')
            .replace(/đ/g, 'd').replace(/Đ/g, 'd')
            .replace(/\\s+/g, ' ').trim().toLowerCase();
          const onm = norm({json.dumps(onm)});
          const nameParts = onm.split(/[,.\\s]+/).filter(p => p.length >= 3).slice(0, 2);
          // Zadnji fallback: prva beseda firme (npr. "alfa") — NIKOLI e-pošta
          const searchQ = (nameParts[0] || onm || '').replace(/@.*/g, '').trim();
          const fire = (el) => {{
            try {{ el.click(); return true; }} catch (e) {{}}
            try {{
              el.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}));
              return true;
            }} catch (e) {{}}
            return false;
          }};
          const isStar = (el) => {{
            if (!el) return true;
            let n = el;
            for (let i = 0; i < 5 && n; i++, n = n.parentElement) {{
              const cls = ((n.className || '') + '').toString().toLowerCase();
              const title = ((n.getAttribute && (n.getAttribute('title') || n.getAttribute('aria-label'))) || '').toLowerCase();
              const href = ((n.getAttribute && (n.getAttribute('href') || n.getAttribute('onclick'))) || '').toLowerCase();
              if (/star|priljubl|favorite|favourite|icon-star|glyphicon-star|fa-star|zvezd/.test(cls + ' ' + title + ' ' + href)) return true;
            }}
            // Ikona brez besedila v prvem stolpcu = zvezda (priljubljene)
            const t = norm(el.textContent || '');
            if (t.length < 2) {{
              const td = el.closest('td, th');
              const tr = el.closest('tr');
              if (td && tr) {{
                const cells = Array.from(tr.children).filter(c => c.tagName === 'TD' || c.tagName === 'TH');
                if (cells[0] === td) return true;
              }}
            }}
            return false;
          }};
          const nameMatch = (t) => {{
            if (!t || t.length < 3) return false;
            if (!onm) return t.length >= 6;
            return t === onm || t.includes(onm) || (nameParts.length > 0 && nameParts.every(p => t.includes(p)));
          }};
          const orgLink = (root) => {{
            // SAMO povezava z vidnim nazivom firme — NIKOLI zvezda / prazen __doPostBack
            if (!root) return null;
            const scored = [];
            for (const a of Array.from(root.querySelectorAll('a'))) {{
              if (isStar(a)) continue;
              const t = norm(a.textContent || '');
              const href = (a.getAttribute('href') || '') + (a.getAttribute('onclick') || '');
              const cls = ((a.className || '') + '').toString().toLowerCase();
              const id = (a.id || '').toString();
              if (!t || t.length < 4) continue;
              if (/^(nastavit|dodaj|nova|novo|mobiln|nabiral)/i.test(t)) continue;
              if (/icon-settings|settings|star|priljubl|favorite|favourite/.test(cls)) continue;
              let score = 0;
              if (nameMatch(t)) score += 100;
              if (/organizacija-naziv/.test(cls)) score += 40;
              if (/LinkButton1/i.test(href) || /LinkButton1$/i.test(id)) score += 30;
              if (/__doPostBack|prijava/i.test(href)) score += 5;
              if (t.length < 6) score -= 40;
              if (score >= 100) scored.push({{ a, score, t }});
            }}
            scored.sort((x, y) => y.score - x.score);
            if (scored[0]) return scored[0].a;
            // Brez ujemanja naziva: najdaljša povezava v vrstici (ne ikona)
            const longOnes = Array.from(root.querySelectorAll('a')).filter(a => {{
              if (isStar(a)) return false;
              const t = norm(a.textContent || '');
              return t.length >= 8 && !/^(nastavit|dodaj)/i.test(t);
            }});
            longOnes.sort((a, b) => norm(b.textContent).length - norm(a.textContent).length);
            return longOnes[0] || null;
          }};
          const searchEl = () => document.querySelector(
            "#F_Search, input[placeholder*='oišči'], input[placeholder*='organizac'], input[type='search'], input[name*='Search']"
          );
          const setSearch = (val) => {{
            const search = searchEl();
            if (!search) return false;
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
            if (setter) setter.call(search, val); else search.value = val;
            search.dispatchEvent(new Event('input', {{ bubbles: true }}));
            search.dispatchEvent(new Event('keyup', {{ bubbles: true }}));
            search.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
          }};
          // Vedno počisti leftover filter pred skeniranjem seznama
          try {{
            const search = searchEl();
            if (search && String(search.value || '').trim()) setSearch('');
          }} catch (e) {{}}

          const findRow = () => {{
            if (oid) {{
              const byData = document.querySelector(
                'tr.prijava[data-organizacijaid="' + oid + '"], tr[data-organizacijaid="' + oid + '"], [data-organizacijaid="' + oid + '"]'
              );
              if (byData) return {{ row: byData, how: 'data-organizacijaid' }};
            }}
            if (onm && onm.length > 2) {{
              const rows = Array.from(document.querySelectorAll('tr.prijava, tr[data-organizacijaid], tr'));
              const row = rows.find(tr => {{
                if (!tr.getAttribute('data-organizacijaid') && !/prijava/i.test(tr.className || '')) {{
                  // samo vrstice seznama firm, ne celotna tabela UI
                  if (!tr.querySelector('a')) return false;
                }}
                const t = norm(tr.textContent);
                return t.includes(onm) || (nameParts.length && nameParts.every(p => t.includes(p)));
              }});
              if (row) return {{ row, how: 'name_row' }};
            }}
            return null;
          }};
          const clickFound = (found, howSuffix) => {{
            if (!found || !found.row) return null;
            try {{ found.row.scrollIntoView({{ block: 'center', inline: 'nearest' }}); }} catch (e) {{}}
            const l = orgLink(found.row);
            if (!l) return {{ ok: false, how: 'no_name_link', orgId: found.row.getAttribute('data-organizacijaid') || oid }};
            const clickedText = norm(l.innerText || l.textContent || '');
            // Zavrni klik, če besedilo ni naziv firme (sicer bi bila zvezda/ikona)
            if (onm && !nameMatch(clickedText) && clickedText.length < 8) {{
              return {{ ok: false, how: 'refused_non_name', text: clickedText }};
            }}
            if (l && fire(l)) {{
              return {{
                ok: true,
                how: (found.how || 'list') + (howSuffix || ''),
                orgId: found.row.getAttribute('data-organizacijaid') || oid,
                text: (l.innerText || '').trim(),
                usedSearch: !!howSuffix
              }};
            }}
            return null;
          }};

          // 1) Seznam na prvi strani — brez iskanja, brez zvezd
          let hit = clickFound(findRow(), '');
          if (hit && hit.ok) return hit;

          // 2) Zadnji fallback: filter #F_Search (samo če dovoljeno) — še vedno klik na NAZIV
          if (allowSearch && searchQ && !/@/.test(searchQ)) {{
            try {{ setSearch(searchQ); }} catch (e) {{}}
            hit = clickFound(findRow(), '+search');
            if (hit && hit.ok) return hit;
          }}

          const rows = document.querySelectorAll('[data-organizacijaid]');
          return {{
            ok: false,
            how: 'not_found',
            rows: rows.length,
            path: location.pathname || '',
            searchCleared: true,
            allowSearch: allowSearch,
            sample: Array.from(rows).slice(0, 8).map(r => r.getAttribute('data-organizacijaid'))
          }};
        }})()
        """

        deadline = time.monotonic() + 20
        search_after = time.monotonic() + 12  # ~12 s samo seznam + scroll, šele nato #F_Search
        last: Dict[str, Any] = {}
        while time.monotonic() < deadline:
            allow_search = time.monotonic() >= search_after
            last = dict(self.eval(_org_click_script(allow_search=allow_search)) or {})
            if last.get("ok"):
                self.emit(f"klik firme: {last.get('how')} → {last.get('text') or onm}")
                waited = self.wait_firm_in_navbar(organisation_name=onm, timeout=16.0)
                if waited.get("ok"):
                    return {
                        "ok": True,
                        "how": last.get("how"),
                        "organisation": waited.get("org") or last.get("text") or onm,
                    }
                return {
                    "ok": False,
                    "how": "no_navbar",
                    "detail": waited,
                    "clicked": last,
                }
            time.sleep(0.45)
        return {"ok": False, "how": last.get("how") or "timeout", "detail": last}

    def select_podatki_kn(self) -> Dict[str, Any]:
        """Hitri zajem korak 1: vidni Podatki mm-select → Knjižbe in DDV + skrito KN."""
        tip_js = json.dumps(TIP_LABEL)
        # Faza 1: odpri combo + vpiši vidno oznako (kot na sliki)
        open_script = f"""
        (() => {{
          const tipWant = {tip_js};
          const norm = (s) => String(s || '')
            .normalize('NFD').replace(/[\\u0300-\\u036f]/g, '')
            .replace(/\\s+/g, ' ').trim().toLowerCase();
          const tipN = norm(tipWant);
          const steps = [];
          const formReady = () => Boolean(
            document.querySelector('#PPC_EPC_DC_I_Datum')
            || document.querySelector('#PPC_EPC_DC_I_Moznosti_1')
          );
          const vp = document.querySelector('#PPC_EPC_DC_I_VrstaPrometa_h');
          const setNative = (el, val) => {{
            if (!el) return false;
            try {{
              const desc = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
              if (desc && desc.set) desc.set.call(el, val); else el.value = val;
            }} catch (e) {{ el.value = val; }}
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('keyup', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            return true;
          }};
          const findPodatki = () => {{
            const labels = Array.from(document.querySelectorAll('label, td, th, span, div, strong'));
            for (const lab of labels) {{
              const t = String(lab.innerText || lab.textContent || '').replace(/\\s+/g, ' ').trim();
              if (!/^podatki\\s*:?$/i.test(t)) continue;
              const row = lab.closest('tr, .form-group, .mm-form-group, .row, li, .col, div') || lab.parentElement;
              let inp = row && row.querySelector('input.mm-select-input, input[type=text], input:not([type=hidden])');
              if (!inp) {{
                let sib = lab.nextElementSibling;
                for (let i = 0; i < 5 && sib && !inp; i++, sib = sib.nextElementSibling) {{
                  if (sib.matches && sib.matches('input')) inp = sib;
                  else if (sib.querySelector) inp = sib.querySelector('input.mm-select-input, input[type=text]');
                }}
              }}
              if (inp) return inp;
            }}
            const byId = document.querySelector(
              "input[id*='VrstaPrometa']:not([type=hidden]), #PPC_EPC_DC_I_VrstaPrometa_i"
            );
            if (byId) return byId;
            const mms = Array.from(document.querySelectorAll('input.mm-select-input')).filter(el => {{
              const r = el.getBoundingClientRect();
              return r.width > 20 && r.height > 4;
            }});
            return mms.find(i => !(i.value || '').trim()) || mms[0] || null;
          }};
          const podatkiInp = findPodatki();
          const visible = podatkiInp ? String(podatkiInp.value || '').trim() : '';
          if (vp && String(vp.value || '').toUpperCase() === 'KN' && formReady()
              && /knjizbe/.test(norm(visible))) {{
            return {{ ok: true, steps: ['KN_already'], has_form: true, podatki: visible, phase: 'open' }};
          }}
          if (!podatkiInp) {{
            return {{ ok: false, steps: ['no_podatki_input'], has_form: formReady(), phase: 'open' }};
          }}
          try {{ podatkiInp.scrollIntoView({{ block: 'center' }}); }} catch (e) {{}}
          try {{ podatkiInp.focus(); }} catch (e) {{}}
          try {{ podatkiInp.click(); }} catch (e) {{}}
          const wrap = podatkiInp.closest('.input-group, .mm-select, .dropdown, td, div') || podatkiInp.parentElement;
          const btn = wrap && wrap.querySelector(
            'button, .mm-select-btn, .dropdown-toggle, span.caret, i.fa-caret-down, [class*=arrow]'
          );
          if (btn) {{ try {{ btn.click(); steps.push('KN_open'); }} catch (e) {{}} }}
          setNative(podatkiInp, tipWant);
          steps.push('KN_typed_visible');
          try {{
            podatkiInp.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'ArrowDown', bubbles: true }}));
          }} catch (e) {{}}
          return {{
            ok: true,
            steps,
            has_form: formReady(),
            podatki: String(podatkiInp.value || ''),
            phase: 'open',
            tipN
          }};
        }})()
        """
        # Faza 2: klik opcije iz seznama + skrito KN (enako kot _minimax_uvoz_select_podatki_kn_js)
        pick_script = f"""
        (() => {{
          const tipWant = {tip_js};
          const norm = (s) => String(s || '')
            .normalize('NFD').replace(/[\\u0300-\\u036f]/g, '')
            .replace(/\\s+/g, ' ').trim().toLowerCase();
          const tipN = norm(tipWant);
          const steps = [];
          const formReady = () => Boolean(
            document.querySelector('#PPC_EPC_DC_I_Datum')
            || document.querySelector('#PPC_EPC_DC_I_Moznosti_1')
          );
          const setNative = (el, val) => {{
            if (!el) return false;
            try {{
              const desc = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
              if (desc && desc.set) desc.set.call(el, val); else el.value = val;
            }} catch (e) {{ el.value = val; }}
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
            return true;
          }};
          const matchTip = (t) => {{
            const n = norm(t);
            if (!n || n.length > 80) return false;
            return n === tipN || n.includes('knjizbe in ddv')
              || (n.includes('knjizbe') && n.includes('ddv'));
          }};
          const fire = (el) => {{
            if (!el) return false;
            try {{ el.scrollIntoView({{ block: 'nearest' }}); }} catch (e) {{}}
            try {{ el.click(); return true; }} catch (e) {{}}
            try {{
              el.dispatchEvent(new MouseEvent('mousedown', {{ bubbles: true, cancelable: true, view: window }}));
              el.dispatchEvent(new MouseEvent('mouseup', {{ bubbles: true, cancelable: true, view: window }}));
              el.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}));
              return true;
            }} catch (e) {{ return false; }}
          }};
          let hit = null;
          const lists = Array.from(document.querySelectorAll(
            '.mm-select-dropdown, .mm-select-list, .dropdown-menu, ul[role=listbox], [class*=mm-select]'
          ));
          for (const list of lists) {{
            const r = list.getBoundingClientRect();
            if (r.width < 8 || r.height < 8) continue;
            hit = Array.from(list.querySelectorAll(
              'li, .mm-select-item, .dropdown-item, [role=option], a, div, span'
            )).find(el => {{
              const t = String(el.innerText || el.textContent || '').replace(/\\s+/g, ' ').trim();
              const er = el.getBoundingClientRect();
              return er.height > 4 && er.width > 20 && matchTip(t);
            }});
            if (hit) break;
          }}
          if (!hit) {{
            hit = Array.from(document.querySelectorAll(
              'li.mm-select-item, .mm-select-item, .dropdown-item, [role=option], li'
            )).find(el => {{
              const t = String(el.innerText || el.textContent || '').replace(/\\s+/g, ' ').trim();
              const er = el.getBoundingClientRect();
              return er.height > 4 && er.width > 40 && t.length < 60 && matchTip(t);
            }});
          }}
          if (hit && fire(hit)) {{
            steps.push('KN_opt');
            // Potrdi izbiro (Enter / blur) — šele nato se razširi radio
            try {{
              const inputs = Array.from(document.querySelectorAll('input.mm-select-input'));
              const inp = inputs.find(i => matchTip(String(i.value || ''))) || inputs[0];
              if (inp) {{
                inp.focus();
                inp.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
                inp.dispatchEvent(new KeyboardEvent('keyup', {{ key: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
                inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                inp.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                steps.push('KN_confirm');
              }}
            }} catch (e) {{}}
          }} else {{
            const inputs = Array.from(document.querySelectorAll('input.mm-select-input'));
            const inp = inputs.find(i => /podatk|promet/i.test(
              ((i.closest('.input-group,td,div') || i).previousElementSibling
                ? ((i.closest('.input-group,td,div') || i).previousElementSibling.innerText || '')
                : '') + ' ' + (i.id || '')
            )) || inputs[0];
            if (inp) {{
              setNative(inp, tipWant);
              try {{
                inp.dispatchEvent(new KeyboardEvent('keydown', {{ key: 'Enter', keyCode: 13, which: 13, bubbles: true }}));
                inp.dispatchEvent(new Event('change', {{ bubbles: true }}));
                inp.dispatchEvent(new Event('blur', {{ bubbles: true }}));
                steps.push('KN_enter');
              }} catch (e) {{ steps.push('KN_typed'); }}
            }}
          }}
          const vp = document.querySelector('#PPC_EPC_DC_I_VrstaPrometa_h');
          if (vp) {{ setNative(vp, 'KN'); steps.push('KN_h'); }}
          let podatkiVal = '';
          for (const inp of document.querySelectorAll('input.mm-select-input')) {{
            const v = String(inp.value || '').trim();
            if (matchTip(v)) {{ podatkiVal = v; break; }}
            if (!podatkiVal && v) podatkiVal = v;
          }}
          const formNow = formReady();
          const radio = document.querySelector('#PPC_EPC_DC_I_Moznosti_1');
          const radioReady = Boolean(radio);
          const visibleOk = matchTip(podatkiVal);
          return {{
            ok: formNow || radioReady || (visibleOk && steps.includes('KN_confirm')),
            steps,
            has_form: formNow || radioReady,
            radio_ready: radioReady,
            podatki: podatkiVal,
            vp: vp ? String(vp.value || '') : '',
            phase: 'pick',
            confirmed: steps.includes('KN_confirm') || steps.includes('KN_enter') || steps.includes('KN_opt')
          }};
        }})()
        """
        steps: list = []
        try:
            opened = dict(self.eval(open_script) or {})
        except Exception as exc:
            return {"ok": False, "how": f"open_error:{exc}", "steps": steps}
        steps.extend(list(opened.get("steps") or []))
        podatki_vis = str(opened.get("podatki") or "")
        if opened.get("steps") == ["KN_already"] or (
            opened.get("has_form") and "knji" in podatki_vis.casefold()
        ):
            return {
                "ok": True,
                "steps": steps or ["KN_already"],
                "has_form": True,
                "radio_ready": True,
                "podatki": podatki_vis or TIP_LABEL,
                "vp": "KN",
                "confirmed": True,
            }

        time.sleep(0.35)
        try:
            picked = dict(self.eval(pick_script) or {})
        except Exception as exc:
            return {"ok": False, "how": f"pick_error:{exc}", "steps": steps, "podatki": podatki_vis}
        steps.extend(list(picked.get("steps") or []))
        # Potrditev: kratka pavza, da Minimax razširi radio
        time.sleep(0.55)
        radio_chk = dict(
            self.eval(
                "(() => ({ radio: Boolean(document.querySelector('#PPC_EPC_DC_I_Moznosti_1')),"
                " datum: Boolean(document.querySelector('#PPC_EPC_DC_I_Datum')) }))()"
            )
            or {}
        )
        has_form = bool(
            picked.get("has_form") or radio_chk.get("radio") or radio_chk.get("datum")
        )
        out = {
            "ok": has_form or bool(picked.get("confirmed")),
            "steps": steps,
            "has_form": has_form,
            "radio_ready": bool(radio_chk.get("radio") or picked.get("radio_ready")),
            "podatki": picked.get("podatki") or podatki_vis or "",
            "vp": picked.get("vp") or "",
            "confirmed": bool(picked.get("confirmed")),
        }
        if out.get("ok") or out.get("has_form"):
            self.emit(
                f"Podatki KN: {', '.join(str(s) for s in steps) or 'OK'} → "
                f"{out.get('podatki') or TIP_LABEL}"
                + (" · potrjeno" if out.get("confirmed") else "")
            )
        return out

    def select_radio_uvoz(self) -> Dict[str, Any]:
        """Korak po KN: radio »Podatki naj se uvozijo« (#PPC_EPC_DC_I_Moznosti_1)."""
        script = r"""
        (() => {
          const radio = document.querySelector('#PPC_EPC_DC_I_Moznosti_1');
          if (!radio) return { ok: false, how: 'no_radio' };
          try { radio.scrollIntoView({ block: 'center' }); } catch (e) {}
          try { radio.focus(); } catch (e) {}
          radio.checked = true;
          try { radio.click(); } catch (e) {}
          radio.dispatchEvent(new Event('input', { bubbles: true }));
          radio.dispatchEvent(new Event('change', { bubbles: true }));
          // klik na label če obstaja
          try {
            const lab = document.querySelector("label[for='PPC_EPC_DC_I_Moznosti_1']");
            if (lab) lab.click();
          } catch (e) {}
          const fileBtn = Array.from(document.querySelectorAll('a, button, input, span, label')).find(el =>
            /izberite\s*datotek/i.test((el.innerText || el.textContent || el.value || '').trim())
          );
          return {
            ok: Boolean(radio.checked),
            how: 'radio_click',
            checked: Boolean(radio.checked),
            file_ui: Boolean(fileBtn || document.querySelector('#PPC_EPC_DC_FileUpload1'))
          };
        })()
        """
        result = dict(self.eval(script) or {})
        if result.get("ok"):
            self.emit("radio: Podatki naj se uvozijo")
        return result if result else {"ok": False, "how": "eval_fail"}

    def fill_fields_stepwise(self, *, date_sl: str, opis: str) -> Dict[str, Any]:
        """Po radiu: IR → Datum → Opis (ločeni JS koraki)."""
        steps: list = []
        set_native_js = (
            "const setNative=(el,val)=>{"
            "if(!el)return false;"
            "try{const d=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value');"
            "if(d&&d.set)d.set.call(el,val);else el.value=val;}"
            "catch(e){el.value=val;}"
            "el.dispatchEvent(new Event('input',{bubbles:true}));"
            "el.dispatchEvent(new Event('change',{bubbles:true}));"
            "el.dispatchEvent(new Event('blur',{bubbles:true}));"
            "return true;};"
        )

        # 1) Vrsta temeljnice IR
        ir_script = (
            "(()=>{"
            + set_native_js
            + f"const vrstaWant={json.dumps(VRSTA_LABEL)};"
            + "const steps=[];"
            + f"const vt=document.querySelector('#PPC_EPC_DC_I_VrstaTemeljniceID_h');"
            + f"if(vt){{setNative(vt,{json.dumps(VRSTA_ID)});steps.push('vrsta_h');}}"
            + "const vp=document.querySelector('#PPC_EPC_DC_I_VrstaPrometa_h');"
            + "if(vp){setNative(vp,'KN');steps.push('KN');}"
            + "try{for(const inp of document.querySelectorAll('input.mm-select-input')){"
            + "const wrap=inp.closest('.input-group')||inp.parentElement;"
            + "const label=(wrap&&wrap.previousElementSibling)"
            + "?(wrap.previousElementSibling.textContent||''):'';"
            + "const blob=(label+' '+(inp.getAttribute('aria-label')||'')"
            + "+' '+(inp.id||'')).toLowerCase();"
            + "if(!/temeljnic|vrsta/.test(blob))continue;"
            + "try{inp.focus();inp.click();}catch(e){}"
            + "setNative(inp,vrstaWant);"
            + "try{inp.dispatchEvent(new KeyboardEvent('keydown',"
            + "{key:'Enter',keyCode:13,which:13,bubbles:true}));}catch(e){}"
            + "const opts=Array.from(document.querySelectorAll("
            + "'li,.mm-select-item,[role=option],.dropdown-item'));"
            + "const hit=opts.find(el=>/izdani\\s*ra[cč]un|\\bir\\b/i.test("
            + "(el.innerText||'').trim()));"
            + "if(hit)try{hit.click();steps.push('vrsta_opt');}catch(e){}"
            + "steps.push('vrsta_ui');break;}}catch(e){}"
            + "return{ok:steps.length>0,steps,"
            + "vrsta_id:(document.querySelector('#PPC_EPC_DC_I_VrstaTemeljniceID_h')||{}).value||''};"
            + "})()"
        )
        ir = dict(self.eval(ir_script) or {})
        steps.extend(list(ir.get("steps") or []))
        time.sleep(0.35)

        # 2) Datum
        date_script = (
            "(()=>{"
            + set_native_js
            + f"const el=document.querySelector('#PPC_EPC_DC_I_Datum');"
            + f"const ok=setNative(el,{json.dumps(date_sl)});"
            + "return{ok,steps:ok?['datum']:[],date:el?el.value:''};"
            + "})()"
        )
        dres = dict(self.eval(date_script) or {})
        steps.extend(list(dres.get("steps") or []))
        time.sleep(0.25)

        # 3) Opis
        opis_script = (
            "(()=>{"
            + set_native_js
            + f"const el=document.querySelector('#PPC_EPC_DC_I_Opis');"
            + f"const ok=setNative(el,{json.dumps(opis)});"
            + "return{ok,steps:ok?['opis']:[],opis:el?el.value:''};"
            + "})()"
        )
        ores = dict(self.eval(opis_script) or {})
        steps.extend(list(ores.get("steps") or []))

        ok = bool(dres.get("ok") or ores.get("ok"))
        if ok:
            self.emit(f"polja: {', '.join(steps)}")
        return {
            "ok": ok,
            "steps": steps,
            "date": dres.get("date") or "",
            "opis": ores.get("opis") or "",
            "vrsta_id": ir.get("vrsta_id") or "",
        }

    def fill_form(self, *, date_sl: str, opis: str) -> Dict[str, Any]:
        """Združen fill (radio + polja) — raje uporabi select_radio_uvoz + fill_fields_stepwise."""
        radio = self.select_radio_uvoz()
        time.sleep(0.4)
        fields = self.fill_fields_stepwise(date_sl=date_sl, opis=opis)
        steps = []
        if radio.get("ok"):
            steps.append("uvoz")
        steps.extend(list(fields.get("steps") or []))
        return {
            "ok": bool(fields.get("ok") or radio.get("ok")),
            "steps": steps,
            "date": fields.get("date") or "",
            "opis": fields.get("opis") or "",
            "vrsta_id": fields.get("vrsta_id") or "",
            "reason": "" if (fields.get("ok") or radio.get("ok")) else "need_KN",
        }

    def click_file_picker(self) -> Dict[str, Any]:
        """Klik »Izberite datoteko« (vidni gumb; JS klik pogosto ne odpre native dialoga)."""
        script = r"""
        (() => {
          const file = document.querySelector(
            '#PPC_EPC_DC_FileUpload1, input[type=file][id*="FileUpload"], input[type=file]'
          );
          const labels = Array.from(document.querySelectorAll(
            'a, button, label, span, input[type=button], input[type=submit]'
          ));
          const btn = labels.find(el => {
            const t = (el.innerText || el.textContent || el.value || '').replace(/\s+/g, ' ').trim();
            return /izberite\s*datotek/i.test(t);
          });
          const fire = (el) => {
            if (!el) return false;
            try { el.scrollIntoView({ block: 'center' }); } catch (e) {}
            try { el.focus(); } catch (e) {}
            try { el.click(); return true; } catch (e) {}
            try {
              el.dispatchEvent(new MouseEvent('mousedown', { bubbles: true, cancelable: true, view: window }));
              el.dispatchEvent(new MouseEvent('mouseup', { bubbles: true, cancelable: true, view: window }));
              el.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
              return true;
            } catch (e) { return false; }
          };
          if (btn && fire(btn)) return { ok: true, how: 'izberite_datoteko', text: (btn.innerText || '').trim() };
          if (file && fire(file)) return { ok: true, how: 'file_input' };
          return { ok: false, how: 'no_picker', has_file: Boolean(file) };
        })()
        """
        result = self.eval(script)
        return dict(result or {}) if isinstance(result, dict) else {"ok": False}

    def _file_input_has_file(self) -> bool:
        try:
            r = self.eval(
                "(() => { const f=document.querySelector('#PPC_EPC_DC_FileUpload1, input[type=file]');"
                " return { ok: Boolean(f && f.files && f.files.length > 0),"
                " name: (f && f.files && f.files[0]) ? f.files[0].name : '' }; })()"
            )
            return bool((r or {}).get("ok"))
        except Exception:
            return False

    def attach_excel(self, xlsx: Path, *, port: int) -> Dict[str, Any]:
        """Korak Izberite datoteko: CDP (ista WS seja) ali Open dialog, nato Uvozi ločeno."""
        self.emit("Izberite datoteko: pripenjam Excel …")
        # 1) CDP najprej — JS klik file-inputa pogosto NE odpre Windows dialoga
        cdp = _cdp_set_file_input(port, xlsx)
        if cdp.get("ok"):
            time.sleep(0.25)
            try:
                self.eval(
                    "(() => { const f=document.querySelector('#PPC_EPC_DC_FileUpload1, input[type=file]');"
                    " if(f){ f.dispatchEvent(new Event('input',{bubbles:true}));"
                    " f.dispatchEvent(new Event('change',{bubbles:true})); } return {ok:true}; })()"
                )
            except Exception:
                pass
            self.emit(f"Izberite datoteko (CDP): {xlsx.name}")
            return {**cdp, "how": "izberite_datoteko_cdp"}

        # 2) Klik gumba + Windows Open dialog
        self.emit(f"CDP ({cdp.get('how')}) → klik Izberite datoteko + dialog …")
        clicked = self.click_file_picker()
        time.sleep(0.5)
        dlg = _win_file_dialog_attach(xlsx, wait_dialog=8.0) if clicked.get("ok") else {
            "ok": False,
            "how": "no_picker",
        }
        if dlg.get("ok"):
            time.sleep(0.3)
            try:
                self.eval(
                    "(() => { const f=document.querySelector('#PPC_EPC_DC_FileUpload1, input[type=file]');"
                    " if(f){ f.dispatchEvent(new Event('change',{bubbles:true})); } return {ok:true}; })()"
                )
            except Exception:
                pass
            self.emit(f"Izberite datoteko (dialog): {xlsx.name}")
            return {
                **dlg,
                "clicked_picker": True,
                "cdp": cdp,
                "how": "izberite_datoteko_dialog",
            }

        # 3) Še en CDP poskus po kliku (včasih input postane aktiven)
        cdp2 = _cdp_set_file_input(port, xlsx, retries=4)
        if cdp2.get("ok"):
            self.emit(f"Izberite datoteko (CDP po kliku): {xlsx.name}")
            return {**cdp2, "clicked_picker": bool(clicked.get("ok")), "dialog": dlg}

        return {
            "ok": False,
            "how": "attach_failed",
            "clicked_picker": bool(clicked.get("ok")),
            "cdp": cdp2 if cdp2.get("how") else cdp,
            "dialog": dlg,
            "detail": (
                f"CDP={((cdp2 or cdp).get('how'))}; "
                f"Dialog={dlg.get('how')}; "
                "Zapri star WebView2 in ponovi (CDP mora biti ena seja)."
            ),
        }

    def click_import(self) -> Dict[str, Any]:
        result = self.eval(
            "(() => { const b=document.querySelector('#PPC_EPC_DC_B_Import'); "
            "if(!b) return {ok:false}; b.click(); return {ok:true}; })()"
        )
        return dict(result or {}) if isinstance(result, dict) else {"ok": False}

    def read_report(self) -> Dict[str, Any]:
        script = r"""
        (() => {
          const showBtn = document.querySelector('#PPC_EPC_DC_A_PrikaziTemeljnico');
          const table = document.querySelector('table.mm-table');
          const rows = [];
          let errors = 0;
          if (table) {
            for (const tr of table.querySelectorAll('tr')) {
              const cells = Array.from(tr.querySelectorAll('th,td')).map(c => (c.innerText || '').trim());
              if (cells.length >= 4) {
                rows.push(cells);
                const label = (cells[0] || '').toLowerCase();
                if (/temeljnic|vrstica|ddv/.test(label)) {
                  const n = parseInt(String(cells[3] || '0').replace(/\D/g, ''), 10);
                  if (!isNaN(n)) errors += n;
                }
              }
            }
          }
          const body = (document.body && document.body.innerText) || '';
          const hasReport = /Poročilo o uvozu podatkov/i.test(body) || Boolean(showBtn);
          return { ok: hasReport, has_report: hasReport, errors, rows, show_temeljnica: Boolean(showBtn) };
        })()
        """
        result = self.eval(script)
        return dict(result or {}) if isinstance(result, dict) else {"ok": False}

    def click_show_temeljnica(self) -> Dict[str, Any]:
        result = self.eval(
            "(() => { const b=document.querySelector('#PPC_EPC_DC_A_PrikaziTemeljnico'); "
            "if(!b) return {ok:false}; b.click(); return {ok:true}; })()"
        )
        return dict(result or {}) if isinstance(result, dict) else {"ok": False}

    def import_knjizbe(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        xlsx = Path(str(payload.get("xlsx_path") or ""))
        date_sl = str(payload.get("date_sl") or "")
        opis = str(payload.get("opis") or "")
        click_import = bool(payload.get("click_import", True))
        open_temeljnica = bool(payload.get("open_temeljnica", True))
        org_id = payload.get("organisation_id")
        org_name = str(payload.get("organisation_name") or "").strip()
        port = int(payload.get("remote_debugging_port") or self.remote_debugging_port)

        if not xlsx.is_file():
            raise FileNotFoundError(f"Excel ne obstaja: {xlsx}")
        if not date_sl or not opis:
            raise ValueError("Manjkata date_sl ali opis.")

        login_username = str(payload.get("login_username") or "").strip()
        login_password = str(payload.get("login_password") or "").strip()

        def _in_app(s: Dict[str, Any]) -> bool:
            return bool(
                s.get("on_org_list")
                or s.get("organisation")
                or (s.get("logged_in") and not s.get("login_page") and not s.get("needs_vstopite"))
            )

        # 0) Če Chrome že ima Minimax sejo → prevzemi (brez ponovne prijave)
        self.pass_vstopite(timeout=5.0)
        snap = self.snapshot()
        synced = False
        if not _in_app(snap):
            try:
                from v2.chrome_session_sync import sync_service_into_webview2

                self.emit("Iščem aktivno Minimax sejo v Chrome…")
                sync = sync_service_into_webview2(
                    "minimax",
                    webview2_port=int(self.remote_debugging_port),
                    navigate_url=MINIMAX_ZACETEK_URL,
                    exclude_ports=(int(self.remote_debugging_port),),
                    log=lambda m: self.emit(m),
                )
                if sync.get("ok"):
                    synced = True
                    self.emit(
                        f"Prevzel sejo iz Chrome :{sync.get('source_port')} "
                        f"({sync.get('set')} piškotkov) — brez ponovne prijave"
                    )
                    # pywebview navigacija + Vstopite (peach) dokler nismo v WebUI
                    self.navigate(MINIMAX_ZACETEK_URL)
                    for _ in range(10):
                        self.pass_vstopite(timeout=4.0)
                        snap = self.snapshot()
                        if _in_app(snap):
                            break
                        time.sleep(0.45)
                else:
                    self.emit(
                        f"Chrome seja ni dosegljiva ({sync.get('how')}). "
                        "Če je Minimax odprt v navadnem Chrome brez debug, "
                        "uporabi Nastavitve → Odpri Minimax Chrome."
                    )
            except Exception as exc:
                self.emit(f"Chrome sync: {exc}", "WARN")

        # 1) Ročna prijava SAMO če sync ni pripeljal v WebUI
        self.pass_vstopite(timeout=8.0)
        snap = self.snapshot()
        if not _in_app(snap):
            if synced:
                self.emit("Seja iz Chrome je vstavljena, a WebUI še ni pripravljen — kratko čakam…")
                deadline = time.monotonic() + 25.0
                while time.monotonic() < deadline and not _in_app(snap):
                    self.pass_vstopite(timeout=4.0)
                    snap = self.snapshot()
                    if _in_app(snap):
                        break
                    time.sleep(0.6)
            if not _in_app(snap):
                snap = self.wait_until_logged_in(
                    timeout=210.0,
                    login_username=login_username,
                    login_password=login_password,
                )

        # 2) HARD firma — NE soft-skip na goli Uvoz brez seje firme
        org_sel = self.ensure_organisation(
            organisation_id=int(org_id) if org_id else None,
            organisation_name=org_name,
        )
        if not org_sel.get("ok"):
            raise RuntimeError(
                "Vstop v firmo ni uspel (Moje organizacije → naziv).\n"
                f"Cilj: {org_name or org_id or '?'}\n"
                f"Vzrok: {org_sel.get('how')}\n\n"
                "Na Moje organizacije klikni firmo (npr. ALFA GYM / "
                f"data-organizacijaid={org_id}), nato ponovi."
            )
        self.emit(f"firma v seji: {org_sel.get('organisation') or org_name}")

        # 3) Šele po potrjeni firimi → UvozPodatkovCSV (OrganisationId OK)
        url = MINIMAX_UVOZ_URL
        if org_id:
            url = f"{MINIMAX_UVOZ_URL}?OrganisationId={int(org_id)}"
        self.emit(f"odpiram uvoz (po firimi): {url}")
        self.navigate(url)
        time.sleep(0.5)
        self.pass_vstopite(timeout=6.0)
        firm_chk = self.firm_active(organisation_name=org_name)
        if not firm_chk.get("ok"):
            raise RuntimeError(
                "Po odprtju UvozPodatkov navbar ne kaže firme.\n"
                f"Pričakovano: {org_name or org_id}.\n"
                "Odpri firmo v WebView2 (Moje org → naziv), nato ponovi."
            )
        snap = self.snapshot()

        # 4a) Podatki → Knjižbe in DDV + potrdi (Enter) — šele nato radio
        kn_steps: list = []
        deadline = time.monotonic() + 28
        kn_ready = False
        while time.monotonic() < deadline:
            snap = self.snapshot()
            if snap.get("has_uvoz_form"):
                kn_ready = True
                kn_steps.append("KN_already_form")
                break
            sel = self.select_podatki_kn()
            kn_steps.extend(list(sel.get("steps") or []))
            if sel.get("has_form") or sel.get("radio_ready"):
                kn_ready = True
                time.sleep(0.7)
                break
            time.sleep(0.5)
        if not kn_ready:
            raise RuntimeError(
                "Podatki → Knjižbe in DDV (KN) ni uspelo potrditi.\n"
                "Ročno izberi KN v WebView2 oknu (potrdi v combo), nato ponovi."
            )
        self.emit(f"KN potrjen: {', '.join(str(s) for s in kn_steps) or 'OK'}")

        # 4b) Radio »Podatki naj se uvozijo«
        radio: Dict[str, Any] = {}
        deadline = time.monotonic() + 12
        while time.monotonic() < deadline:
            radio = self.select_radio_uvoz()
            if radio.get("ok"):
                break
            # KN morda še ni razširil forme
            self.select_podatki_kn()
            time.sleep(0.55)
        if not radio.get("ok"):
            raise RuntimeError(
                "Radio »Podatki naj se uvozijo« ni najden.\n"
                "Potrdi Knjižbe in DDV v combo Podatki, nato ponovi."
            )
        time.sleep(0.45)

        # 4c) IR → Datum → Opis (po korakih)
        filled: Dict[str, Any] = {}
        deadline = time.monotonic() + 16
        while time.monotonic() < deadline:
            filled = self.fill_fields_stepwise(date_sl=date_sl, opis=opis)
            if filled.get("ok"):
                break
            time.sleep(0.4)
        if not filled.get("ok"):
            raise RuntimeError("Obrazec Uvoz podatkov ni pripravljen (Datum/Opis/IR).")

        filled["steps"] = list(kn_steps) + ["uvoz"] + list(filled.get("steps") or [])
        self.emit(f"vpisano: {', '.join(filled.get('steps') or [])}")
        time.sleep(0.4)

        # 5) 1) Izberite datoteko → pot → 2) Uvozi podatke
        attached = self.attach_excel(xlsx, port=port)
        if not attached.get("ok"):
            raise RuntimeError(
                "Priponka Excela ni uspela (korak 1: Izberite datoteko).\n"
                f"Detail: {attached.get('detail') or attached.get('how')}\n"
                f"CDP: {((attached.get('cdp') or {}).get('how')) or '-'}\n"
                f"Dialog: {((attached.get('dialog') or {}).get('how')) or '-'}\n"
                f"Preveri --remote-allow-origins=* na CDP :{port}, "
                "websocket-client, ali zapri star WebView2 in ponovi."
            )
        self.emit(f"1) datoteka OK: {xlsx.name} ({attached.get('how')})")
        time.sleep(0.5)

        report: Dict[str, Any] = {}
        if click_import:
            self.emit("2) klik Uvozi podatke …")
            clicked = self.click_import()
            if not clicked.get("ok"):
                raise RuntimeError("Gumb Uvozi podatke ni najden (korak 2).")
            deadline = time.monotonic() + 60
            while time.monotonic() < deadline:
                report = self.read_report()
                if report.get("has_report"):
                    break
                time.sleep(0.5)
            if not report.get("has_report"):
                raise TimeoutError("Poročilo o uvozu se ni prikazalo.")
            errors = int(report.get("errors") or 0)
            if errors > 0:
                raise RuntimeError(f"Uvoz z napakami ({errors}).")
            if open_temeljnica and report.get("show_temeljnica"):
                self.click_show_temeljnica()
                report["opened_temeljnica"] = True
                self.emit("odprta temeljnica")

        return {
            "ok": True,
            "steps": list(filled.get("steps") or [])
            + (["datoteka", "uvozi"] if click_import else ["datoteka"]),
            "date": date_sl,
            "opis": opis,
            "file": xlsx.name,
            "organisation": firm_chk.get("org") or snap.get("organisation") or org_name,
            "report": report,
            "source": "WebView2",
        }

    def open_knjizenje(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Video OdpriKnjiženjeIRinIztržkov: HARD firma → Knjiženje IR/iztržkov → Najdi.

        Ne spreminja poteka import_knjizbe (3.0.42). Brez Chrome vtičnika.
        """
        org_id = payload.get("organisation_id")
        org_name = str(payload.get("organisation_name") or "").strip()
        date_from = str(payload.get("date_from") or "").strip()
        date_to = str(payload.get("date_to") or "").strip()
        opis = str(payload.get("opis") or "").strip()
        login_username = str(payload.get("login_username") or "").strip()
        login_password = str(payload.get("login_password") or "").strip()

        def _in_app(s: Dict[str, Any]) -> bool:
            return bool(
                s.get("on_org_list")
                or s.get("organisation")
                or (s.get("logged_in") and not s.get("login_page") and not s.get("needs_vstopite"))
            )

        self.pass_vstopite(timeout=5.0)
        snap = self.snapshot()
        if not _in_app(snap):
            try:
                from v2.chrome_session_sync import sync_service_into_webview2

                self.emit("Iščem aktivno Minimax sejo v Chrome…")
                sync = sync_service_into_webview2(
                    "minimax",
                    webview2_port=int(self.remote_debugging_port),
                    navigate_url=MINIMAX_ZACETEK_URL,
                    exclude_ports=(int(self.remote_debugging_port),),
                    log=lambda m: self.emit(m),
                )
                if sync.get("ok"):
                    self.emit(
                        f"Prevzel sejo iz Chrome :{sync.get('source_port')} "
                        f"({sync.get('set')} piškotkov)"
                    )
                    self.navigate(MINIMAX_ZACETEK_URL)
                    for _ in range(10):
                        self.pass_vstopite(timeout=4.0)
                        snap = self.snapshot()
                        if _in_app(snap):
                            break
                        time.sleep(0.45)
            except Exception as exc:
                self.emit(f"Chrome sync: {exc}", "WARN")

        self.pass_vstopite(timeout=8.0)
        snap = self.snapshot()
        if not _in_app(snap):
            snap = self.wait_until_logged_in(
                timeout=210.0,
                login_username=login_username,
                login_password=login_password,
            )

        # Video: Moje org → (Poišči) → klik naziva
        org_sel = self.ensure_organisation(
            organisation_id=int(org_id) if org_id else None,
            organisation_name=org_name,
        )
        if not org_sel.get("ok"):
            raise RuntimeError(
                "Vstop v firmo ni uspel (Moje organizacije → naziv).\n"
                f"Cilj: {org_name or org_id or '?'}\n"
                f"Vzrok: {org_sel.get('how')}"
            )
        self.emit(f"firma v seji: {org_sel.get('organisation') or org_name}")

        # Video: Knjigovodstvo → Knjiženje izdanih računov in iztržkov
        url = MINIMAX_KNJIZENJE_URL
        if org_id:
            url = f"{MINIMAX_KNJIZENJE_URL}?OrganisationId={int(org_id)}"
        self.emit(f"odpiram Knjiženje IR/iztržkov: {url}")
        self.navigate(url)
        time.sleep(0.7)
        self.pass_vstopite(timeout=6.0)

        # Video zaključek: Najdi (Od/Do opcijsko)
        najdi = self.eval(
            f"""
        (() => {{
          const setVal = (sel, v) => {{
            const el = document.querySelector(sel);
            if (!el) return false;
            el.focus();
            const setter = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;
            if (setter) setter.call(el, String(v || '')); else el.value = String(v || '');
            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
            el.dispatchEvent(new Event('blur', {{ bubbles: true }}));
            return true;
          }};
          const d0 = {json.dumps(date_from)};
          const d1 = {json.dumps(date_to)};
          const op = {json.dumps(opis)};
          const odOk = d0 ? setVal('#PPC_ctl04_ctl00_ctl01_I_DatumOd, input[id$="I_DatumOd"]', d0) : true;
          const doOk = d1 ? setVal('#PPC_ctl04_ctl00_ctl01_I_DatumDo, input[id$="I_DatumDo"]', d1) : true;
          if (op) setVal('#PPC_ctl04_ctl00_ctl01_I_Opis, input[id$="I_Opis"]', op);
          const btn = document.querySelector(
            '#PPC_ctl04_ctl00_B_Search, button#PPC_ctl04_ctl00_B_Search, button.button.search, button[id*="B_Search"]'
          ) || Array.from(document.querySelectorAll('button,a')).find(
            b => /^\\s*Najdi/i.test((b.textContent || '').trim())
          );
          let clicked = false;
          if (btn) {{
            try {{ btn.click(); clicked = true; }} catch (e) {{
              try {{
                btn.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true, view: window }}));
                clicked = true;
              }} catch (e2) {{}}
            }}
          }}
          const path = location.pathname || '';
          const onPage = /KnjizenjeIzdanegaRacuna/i.test(path);
          const tbl = document.querySelector('#TSearchFrame, table.mm-table');
          const rows = tbl ? tbl.querySelectorAll('tr').length : 0;
          return {{
            ok: !!(onPage && (clicked || (odOk && doOk))),
            onPage, clicked, odOk, doOk, rows,
            path, title: document.title || ''
          }};
        }})()
        """
        ) or {}
        if not najdi.get("ok"):
            # ponovi po kratkem čakanju (stran se še nalaga)
            time.sleep(1.0)
            najdi = self.eval(
                """
            (() => {
              const btn = document.querySelector(
                '#PPC_ctl04_ctl00_B_Search, button#PPC_ctl04_ctl00_B_Search, button[id*="B_Search"]'
              ) || Array.from(document.querySelectorAll('button,a')).find(
                b => /^\\s*Najdi/i.test((b.textContent || '').trim())
              );
              if (!btn) return { ok: false, how: 'no_najdi', path: location.pathname || '' };
              try { btn.click(); } catch (e) {
                btn.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
              }
              return { ok: true, clicked: true, path: location.pathname || '', how: 'najdi_retry' };
            })()
            """
            ) or {}
        self.emit(
            f"Najdi: {'OK' if najdi.get('ok') else 'FAIL'} | "
            f"rows={najdi.get('rows') or '?'} | {najdi.get('path') or ''}"
        )
        time.sleep(0.8)
        firm = self.firm_active(organisation_name=org_name)
        return {
            "ok": True,
            "steps": ["hard_firma", "knjizenje", "najdi"],
            "organisation": firm.get("org") or org_sel.get("organisation") or org_name,
            "date_from": date_from,
            "date_to": date_to,
            "najdi": najdi,
            "url": url,
            "source": "WebView2",
        }

    def handle(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if action == "diagnose":
            return self.snapshot()
        if action == "navigate_uvoz":
            url = str(payload.get("url") or MINIMAX_UVOZ_URL)
            self.navigate(url)
            return self.snapshot()
        if action == "reload":
            self.eval("location.reload(); true")
            self.wait_ready_state(15)
            return self.snapshot()
        if action == "import_knjizbe":
            return self.import_knjizbe(payload)
        if action == "open_knjizenje":
            return self.open_knjizenje(payload)
        if action == "shutdown":
            self.stop_event.set()
            try:
                self.window.destroy()
            except Exception:
                pass
            return {"stopped": True}
        raise ValueError(f"Neznan WebView2 ukaz: {action}")

    def respond(self, request_id: str, ok: bool, result=None, error: str = "") -> None:
        target = self.responses_dir / f"{request_id}.json"
        tmp = target.with_suffix(".tmp")
        data = {"ok": bool(ok), "result": result or {}, "error": error}
        tmp.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        tmp.replace(target)

    def command_loop(self) -> None:
        self.emit("IPC ukazna zanka pripravljena.")
        while not self.stop_event.is_set():
            for p in sorted(self.commands_dir.glob("*.json")):
                request_id = p.stem
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    request_id = str(data.get("id") or p.stem)
                    action = str(data.get("action") or "")
                    payload = dict(data.get("payload") or {})
                    p.unlink(missing_ok=True)
                    self.emit(f"ukaz: {action}")
                    result = self.handle(action, payload)
                    self.respond(request_id, True, result=result)
                except Exception as exc:
                    try:
                        p.unlink(missing_ok=True)
                    except Exception:
                        pass
                    self.emit(f"ukaz ni uspel: {exc}", "ERROR")
                    self.respond(str(request_id), False, error=str(exc))
            time.sleep(0.10)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ipc-dir", required=True)
    parser.add_argument("--profile-dir", required=True)
    parser.add_argument("--download-dir", required=True)
    parser.add_argument("--remote-debugging-port", type=int, default=9333)
    parser.add_argument("--start-url", default=MINIMAX_ZACETEK_URL)
    args = parser.parse_args()

    os.environ["WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS"] = _webview2_cdp_args(
        int(args.remote_debugging_port)
    )

    host = Host(
        Path(args.ipc_dir),
        Path(args.profile_dir),
        Path(args.download_dir),
        remote_debugging_port=int(args.remote_debugging_port),
        start_url=str(args.start_url),
    )
    title = f"Davčna Blagajna — Minimax Uvoz WebView2 [{os.getpid()}]"
    try:
        import webview

        webview.settings["ALLOW_DOWNLOADS"] = True
        webview.settings["OPEN_EXTERNAL_LINKS_IN_BROWSER"] = False
        webview.settings["OPEN_DEVTOOLS_IN_DEBUG"] = False
        window = webview.create_window(
            title,
            host.start_url,
            width=1180,
            height=760,
            resizable=True,
            min_size=(700, 480),
            confirm_close=False,
        )
        host.window = window
        window.events.before_show += host.before_show
        window.events.shown += host.shown
        window.events.loaded += host.loaded
        host.write_state(
            ready=False,
            hwnd=0,
            renderer="EdgeChromium / WebView2",
            message="Inicializacija WebView2",
        )
        webview.start(
            gui="edgechromium",
            debug=False,
            private_mode=False,
            storage_path=str(host.profile_dir),
        )
        return 0
    except Exception as exc:
        host.write_state(ready=False, hwnd=0, fatal=f"WebView2 ni mogoče zagnati: {exc}")
        host.emit("FATAL: " + str(exc), "ERROR")
        try:
            (host.ipc_dir / "host_error.log").write_text(traceback.format_exc(), encoding="utf-8")
        except Exception:
            pass
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
