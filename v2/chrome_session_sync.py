"""Prenos seje (piškotki + storage) iz že odprtega Chrome CDP v WebView2 / drug CDP.

Avtomatizem: poišče aktiven Chrome, kjer je odprt Minimax / eDavki / eVem / AJPES,
in skopira sejo. Ne zaganja Chrome, ne ubija profilov, ne uporablja vtičnikov.
Če Chrome ni na voljo → tiho spodleti (klicatelj nadaljuje z lastnim profilom).
"""
from __future__ import annotations

import json
import time
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

LogFn = Callable[[str], None]

# Trajna shramba seje (piškotki) — WebView2 / app jo uporabi tudi ko Chrome ni odprt
_APP_ROOT = Path(__file__).resolve().parent.parent
SESSION_CACHE_DIR = _APP_ROOT / "data" / "webview2" / "session_cache"


@dataclass(frozen=True)
class ServiceSpec:
    key: str
    label: str
    domains: Tuple[str, ...]
    origins: Tuple[str, ...]
    preferred_ports: Tuple[int, ...]


SERVICES: Dict[str, ServiceSpec] = {
    "minimax": ServiceSpec(
        key="minimax",
        label="Minimax",
        domains=("minimax.si", "moj.minimax.si"),
        origins=("https://moj.minimax.si",),
        preferred_ports=(9223, 9222),
    ),
    "edavki": ServiceSpec(
        key="edavki",
        label="eDavki",
        domains=("edavki.durs.si", "durs.si"),
        origins=("https://edavki.durs.si",),
        preferred_ports=(9222, 9223),
    ),
    "evem": ServiceSpec(
        key="evem",
        label="eVEM",
        domains=("evem.gov.si", "e-vem.gov.si", "spot.gov.si"),
        origins=("https://evem.gov.si", "https://spot.gov.si"),
        preferred_ports=(9222, 9223),
    ),
    "ajpes": ServiceSpec(
        key="ajpes",
        label="AJPES",
        domains=("ajpes.si",),
        origins=("https://www.ajpes.si", "https://ajpes.si"),
        preferred_ports=(9222, 9223),
    ),
}

# Pogosti lokalni debug porte (Chrome profili). Kratek seznam — hiter soft-fail.
_SCAN_PORTS: Tuple[int, ...] = (9222, 9223, 9224, 9225, 9333)


@dataclass
class SessionBundle:
    ok: bool
    service: str = ""
    how: str = ""
    host: str = "127.0.0.1"
    port: int = 0
    cookies: List[Dict[str, Any]] = field(default_factory=list)
    local_storage: Dict[str, str] = field(default_factory=dict)
    session_storage: Dict[str, str] = field(default_factory=dict)
    page_url: str = ""

    @property
    def cookie_count(self) -> int:
        return len(self.cookies)


def _http_json(url: str, timeout: float = 2.0) -> Any:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def _cdp_connect(ws_url: str, timeout_sec: float = 10.0):
    try:
        import websocket  # type: ignore
    except Exception as exc:
        raise RuntimeError(f"Manjka websocket-client: {exc}") from exc
    try:
        return websocket.create_connection(
            ws_url, timeout=timeout_sec, suppress_origin=True
        )
    except TypeError:
        return websocket.create_connection(ws_url, timeout=timeout_sec)


def _cdp_call(ws: Any, method: str, params: Optional[dict] = None, timeout_sec: float = 10.0) -> Any:
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


def _list_pages(host: str, port: int) -> List[Dict[str, Any]]:
    try:
        pages = _http_json(f"http://{host}:{int(port)}/json", timeout=0.6)
        return list(pages or []) if isinstance(pages, list) else []
    except Exception:
        return []


def _domain_match(url_or_domain: str, domains: Sequence[str]) -> bool:
    s = (url_or_domain or "").lower()
    return any(d.lower() in s for d in domains)


def discover_cdp_endpoints(
    *,
    preferred_ports: Sequence[int] = (),
    exclude_ports: Sequence[int] = (),
    host: str = "127.0.0.1",
) -> List[Tuple[str, int]]:
    """Najdi žive CDP endpointe (ne zaganja brskalnikov)."""
    exclude = {int(p) for p in exclude_ports}
    ordered: List[int] = []
    for p in list(preferred_ports) + list(_SCAN_PORTS):
        pi = int(p)
        if pi in exclude or pi in ordered:
            continue
        ordered.append(pi)
    found: List[Tuple[str, int]] = []
    for port in ordered:
        pages = _list_pages(host, port)
        if pages:
            found.append((host, port))
    return found


def find_active_service_endpoint(
    service: str,
    *,
    exclude_ports: Sequence[int] = (),
    host: str = "127.0.0.1",
) -> Optional[Tuple[str, int, List[Dict[str, Any]]]]:
    """Vrni (host, port, pages) kjer je aktiven zavihek za storitev."""
    spec = SERVICES.get((service or "").strip().lower())
    if not spec:
        return None
    endpoints = discover_cdp_endpoints(
        preferred_ports=spec.preferred_ports,
        exclude_ports=exclude_ports,
        host=host,
    )
    # 1) Najprej endpointe z zavihkom te storitve
    for h, port in endpoints:
        pages = _list_pages(h, port)
        if not pages:
            continue
        for row in pages:
            url = str(row.get("url") or "")
            title = str(row.get("title") or "")
            if _domain_match(url, spec.domains) or _domain_match(title, spec.domains):
                return h, port, pages
    # 2) Preferred port (npr. ChromeMinimax :9223) tudi brez ujemanja URL —
    #    getAllCookies bo še vedno našel piškotke, če je profil prijavljen
    for h, port in endpoints:
        if int(port) in {int(p) for p in spec.preferred_ports}:
            pages = _list_pages(h, port)
            if pages:
                return h, port, pages
    return None


def _pick_ws(pages: List[Dict[str, Any]], domains: Sequence[str]) -> Tuple[str, str]:
    """(ws_url, page_url)."""
    for row in pages or []:
        url = str(row.get("url") or "")
        if _domain_match(url, domains):
            ws = str(row.get("webSocketDebuggerUrl") or "").strip()
            if ws:
                return ws, url
    for row in pages or []:
        if str(row.get("type") or "page") not in ("", "page"):
            continue
        ws = str(row.get("webSocketDebuggerUrl") or "").strip()
        if ws:
            return ws, str(row.get("url") or "")
    return "", ""


def _cookie_for_domains(cookie: dict, domains: Sequence[str]) -> Optional[dict]:
    if not isinstance(cookie, dict):
        return None
    name = str(cookie.get("name") or "").strip()
    if not name:
        return None
    domain = str(cookie.get("domain") or "").strip()
    if domain and not _domain_match(domain, domains):
        return None
    param: Dict[str, Any] = {
        "name": name,
        "value": str(cookie.get("value") or ""),
        "path": str(cookie.get("path") or "/"),
    }
    if domain:
        param["domain"] = domain
    if "secure" in cookie:
        param["secure"] = bool(cookie.get("secure"))
    if "httpOnly" in cookie:
        param["httpOnly"] = bool(cookie.get("httpOnly"))
    same = cookie.get("sameSite")
    if same in ("Strict", "Lax", "None"):
        param["sameSite"] = same
    exp = cookie.get("expires")
    if exp is not None:
        try:
            exp_f = float(exp)
            if exp_f > 0:
                param["expires"] = exp_f
        except (TypeError, ValueError):
            pass
    return param


def export_session_from_chrome(
    service: str,
    *,
    exclude_ports: Sequence[int] = (),
    host: str = "127.0.0.1",
    log: Optional[LogFn] = None,
) -> SessionBundle:
    """Iz aktivnega Chrome za storitev izvozi piškotke + storage. Ne zaganja Chrome."""
    log = log or (lambda _m: None)
    key = (service or "").strip().lower()
    spec = SERVICES.get(key)
    if not spec:
        return SessionBundle(ok=False, service=key, how="neznana_storitev")

    found = find_active_service_endpoint(key, exclude_ports=exclude_ports, host=host)
    if not found:
        # Poskusi preferred porte tudi brez ujemanja URL — samo če getAllCookies najde domeno
        for port in spec.preferred_ports:
            if int(port) in {int(p) for p in exclude_ports}:
                continue
            pages = _list_pages(host, int(port))
            if pages:
                found = (host, int(port), pages)
                break
    if not found:
        log(f"chrome_session_sync | {spec.label}: ni aktivnega Chrome CDP")
        return SessionBundle(ok=False, service=key, how="ni_aktivnega_chrome")

    h, port, pages = found
    ws, page_url = _pick_ws(pages, spec.domains)
    if not ws:
        return SessionBundle(ok=False, service=key, how="brez_ws", host=h, port=port)

    sock = _cdp_connect(ws, timeout_sec=12.0)
    try:
        _cdp_call(sock, "Network.enable", {}, timeout_sec=5.0)
        all_ck = _cdp_call(sock, "Network.getAllCookies", {}, timeout_sec=10.0) or {}
        raw = list(all_ck.get("cookies") or [])
        cookies = []
        for c in raw:
            p = _cookie_for_domains(c if isinstance(c, dict) else {}, spec.domains)
            if p:
                # ohrani surove CDP atribute za setCookies
                cookies.append(c if isinstance(c, dict) else p)

        local_storage: Dict[str, str] = {}
        session_storage: Dict[str, str] = {}
        if _domain_match(page_url, spec.domains):
            try:
                _cdp_call(sock, "Runtime.enable", {}, timeout_sec=3.0)
                got = _cdp_call(
                    sock,
                    "Runtime.evaluate",
                    {
                        "expression": """
(() => {
  const dump = (store) => {
    const o = {};
    try {
      for (let i = 0; i < store.length; i++) {
        const k = store.key(i);
        if (k != null) o[String(k)] = String(store.getItem(k) ?? '');
      }
    } catch (e) {}
    return o;
  };
  return { localStorage: dump(localStorage), sessionStorage: dump(sessionStorage) };
})()
""",
                        "returnByValue": True,
                    },
                    timeout_sec=8.0,
                ) or {}
                val = (got.get("result") or {}).get("value") if isinstance(got, dict) else None
                if isinstance(val, dict):
                    local_storage = {
                        str(k): str(v) for k, v in dict(val.get("localStorage") or {}).items()
                    }
                    session_storage = {
                        str(k): str(v) for k, v in dict(val.get("sessionStorage") or {}).items()
                    }
            except Exception as exc:
                log(f"chrome_session_sync | storage: {exc}")

        ok = bool(cookies)
        how = f"chrome:{h}:{port}" + (f"|pages:{page_url[:80]}" if page_url else "")
        log(
            f"chrome_session_sync | {spec.label}: "
            f"{'OK' if ok else 'prazno'} cookies={len(cookies)} "
            f"ls={len(local_storage)} ss={len(session_storage)} | {how}"
        )
        return SessionBundle(
            ok=ok,
            service=key,
            how=how,
            host=h,
            port=port,
            cookies=cookies,
            local_storage=local_storage,
            session_storage=session_storage,
            page_url=page_url,
        )
    finally:
        try:
            sock.close()
        except Exception:
            pass


def _to_set_cookie_params(cookies: Sequence[dict], domains: Sequence[str], fallback_url: str) -> List[dict]:
    out: List[dict] = []
    base = fallback_url if fallback_url.endswith("/") else (fallback_url + "/" if fallback_url else "")
    for c in cookies:
        p = _cookie_for_domains(c if isinstance(c, dict) else {}, domains)
        if not p:
            continue
        # CDP setCookie zanesljivejši z url + domain
        if base:
            p["url"] = base
        out.append(p)
    return out


def inject_session_into_cdp(
    target_port: int,
    bundle: SessionBundle,
    *,
    host: str = "127.0.0.1",
    navigate_url: str = "",
    log: Optional[LogFn] = None,
) -> Dict[str, Any]:
    """Vstavi piškotke (+ storage prek Runtime) v ciljni CDP (npr. WebView2 :9333)."""
    log = log or (lambda _m: None)
    if not bundle.ok or not bundle.cookies:
        return {"ok": False, "how": bundle.how or "prazna_seja", "set": 0}

    spec = SERVICES.get(bundle.service)
    if not spec:
        return {"ok": False, "how": "neznana_storitev", "set": 0}

    origin = (navigate_url or (spec.origins[0] if spec.origins else "")).rstrip("/")
    fallback_url = origin + "/" if origin else ""

    pages = _list_pages(host, int(target_port))
    ws, _cur = _pick_ws(pages, spec.domains)
    if not ws and pages:
        ws = str((pages[0] or {}).get("webSocketDebuggerUrl") or "").strip()
    if not ws:
        return {"ok": False, "how": f"target_cdp_ni:{target_port}", "set": 0}

    params = _to_set_cookie_params(bundle.cookies, spec.domains, fallback_url)
    if not params:
        return {"ok": False, "how": "ni_parametrov", "set": 0}

    sock = _cdp_connect(ws, timeout_sec=12.0)
    set_n = 0
    try:
        _cdp_call(sock, "Network.enable", {}, timeout_sec=5.0)
        if origin:
            try:
                _cdp_call(sock, "Page.enable", {}, timeout_sec=3.0)
                _cdp_call(sock, "Page.navigate", {"url": origin + "/"}, timeout_sec=15.0)
                time.sleep(0.5)
            except Exception as exc:
                log(f"chrome_session_sync | navigate origin: {exc}")
        try:
            _cdp_call(sock, "Network.setCookies", {"cookies": params}, timeout_sec=12.0)
            set_n = len(params)
        except Exception:
            for p in params:
                try:
                    _cdp_call(sock, "Network.setCookie", p, timeout_sec=5.0)
                    set_n += 1
                except Exception:
                    pass

        # Osveži stran z novimi piškotki (sicer ostane login)
        target = navigate_url or (origin + "/" if origin else "")
        if target:
            try:
                _cdp_call(sock, "Page.navigate", {"url": target}, timeout_sec=15.0)
                time.sleep(0.8)
            except Exception as exc:
                log(f"chrome_session_sync | navigate after cookies: {exc}")

        ls = bundle.local_storage or {}
        ss = bundle.session_storage or {}
        if ls or ss:
            try:
                _cdp_call(
                    sock,
                    "Runtime.evaluate",
                    {
                        "expression": f"""
(() => {{
  const ls = {json.dumps(ls, ensure_ascii=False)};
  const ss = {json.dumps(ss, ensure_ascii=False)};
  try {{ Object.keys(ls).forEach(k => localStorage.setItem(k, String(ls[k]))); }} catch (e) {{}}
  try {{ Object.keys(ss).forEach(k => sessionStorage.setItem(k, String(ss[k]))); }} catch (e) {{}}
  return true;
}})()
""",
                        "returnByValue": True,
                    },
                    timeout_sec=8.0,
                )
            except Exception as exc:
                log(f"chrome_session_sync | inject storage: {exc}")
            if target:
                try:
                    _cdp_call(sock, "Page.reload", {"ignoreCache": False}, timeout_sec=10.0)
                    time.sleep(0.6)
                except Exception:
                    pass
    finally:
        try:
            sock.close()
        except Exception:
            pass

    log(f"chrome_session_sync | vstavljeno v :{target_port} set={set_n} ({bundle.how})")
    return {
        "ok": set_n > 0,
        "how": bundle.how,
        "set": set_n,
        "service": bundle.service,
        "source_port": bundle.port,
        "localStorage": len(bundle.local_storage),
        "sessionStorage": len(bundle.session_storage),
    }


def cache_path(service: str) -> Path:
    SESSION_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return SESSION_CACHE_DIR / f"{(service or '').strip().lower()}.json"


def save_session_cache(bundle: SessionBundle) -> Optional[Path]:
    """Shrani sejo na disk (avtomatski spomin za WebView2)."""
    if not bundle.ok or not bundle.cookies:
        return None
    path = cache_path(bundle.service)
    payload = {
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "service": bundle.service,
        "how": bundle.how,
        "host": bundle.host,
        "port": bundle.port,
        "page_url": bundle.page_url,
        "cookies": bundle.cookies,
        "localStorage": bundle.local_storage,
        "sessionStorage": bundle.session_storage,
    }
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)
    return path


def load_session_cache(service: str) -> SessionBundle:
    """Naloži shranjeno sejo (če obstaja)."""
    key = (service or "").strip().lower()
    path = cache_path(key)
    if not path.is_file():
        return SessionBundle(ok=False, service=key, how="ni_cache")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        cookies = list(data.get("cookies") or [])
        if not cookies:
            return SessionBundle(ok=False, service=key, how="cache_prazna")
        return SessionBundle(
            ok=True,
            service=key,
            how=f"cache:{path.name}",
            host=str(data.get("host") or ""),
            port=int(data.get("port") or 0),
            cookies=cookies,
            local_storage={
                str(k): str(v) for k, v in dict(data.get("localStorage") or {}).items()
            },
            session_storage={
                str(k): str(v) for k, v in dict(data.get("sessionStorage") or {}).items()
            },
            page_url=str(data.get("page_url") or ""),
        )
    except Exception as exc:
        return SessionBundle(ok=False, service=key, how=f"cache_napaka:{exc}")


def sync_all_from_chrome(
    *,
    exclude_ports: Sequence[int] = (),
    services: Optional[Sequence[str]] = None,
    log: Optional[LogFn] = None,
) -> Dict[str, Any]:
    """Iz aktivnega Chrome izvozi Minimax/eDavki/eVEM/AJPES in shrani v cache.

    Ne zaganja Chrome. Vrne povzetek po storitvi.
    """
    log = log or (lambda _m: None)
    keys = [str(s).lower() for s in (services or list(SERVICES.keys()))]
    summary: Dict[str, Any] = {"ok": False, "services": {}, "saved": 0}
    saved = 0
    for key in keys:
        if key not in SERVICES:
            summary["services"][key] = {"ok": False, "how": "neznana"}
            continue
        bundle = export_session_from_chrome(
            key, exclude_ports=exclude_ports, log=log
        )
        if bundle.ok:
            path = save_session_cache(bundle)
            if path:
                saved += 1
            summary["services"][key] = {
                "ok": True,
                "cookies": bundle.cookie_count,
                "port": bundle.port,
                "how": bundle.how,
                "cache": str(path) if path else "",
            }
            log(
                f"chrome_session_sync | shranjeno {SERVICES[key].label}: "
                f"{bundle.cookie_count} piškotkov → cache"
            )
        else:
            # Obdrži star cache; samo označi da Chrome ni dal sveže seje
            cached = load_session_cache(key)
            summary["services"][key] = {
                "ok": False,
                "how": bundle.how,
                "cache_ok": cached.ok,
                "cache_cookies": cached.cookie_count if cached.ok else 0,
            }
    summary["saved"] = saved
    summary["ok"] = saved > 0
    return summary


def sync_service_into_webview2(
    service: str,
    *,
    webview2_port: int,
    navigate_url: str = "",
    exclude_ports: Optional[Sequence[int]] = None,
    log: Optional[LogFn] = None,
    use_cache: bool = True,
) -> Dict[str, Any]:
    """Mehak sync: Chrome (če aktiven) → cache → WebView2 CDP.

    Ne zaganja Chrome. Če ni seje → {ok: False}.
    """
    log = log or (lambda _m: None)
    excl = list(exclude_ports or [])
    excl.append(int(webview2_port))
    bundle = export_session_from_chrome(
        service, exclude_ports=excl, log=log
    )
    if bundle.ok:
        save_session_cache(bundle)
    elif use_cache:
        bundle = load_session_cache(service)
        if bundle.ok:
            log(f"chrome_session_sync | {service}: uporaba shranjene seje (cache)")
    if not bundle.ok:
        return {"ok": False, "how": bundle.how, "set": 0, "service": service}
    result = inject_session_into_cdp(
        int(webview2_port),
        bundle,
        navigate_url=navigate_url,
        log=log,
    )
    result["service"] = service
    return result
