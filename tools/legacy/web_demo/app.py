"""Kratka interna spletna demo verzija Blagajna (FastAPI)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

WEB_DIR = Path(__file__).resolve().parent
ROOT = WEB_DIR.parent
MAIN_PY = ROOT / "DavcnaBlagajna.py"


def _load_core():
    spec = importlib.util.spec_from_file_location("blagajna_core", MAIN_PY)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Ne morem naložiti: {MAIN_PY}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["blagajna_core"] = mod
    spec.loader.exec_module(mod)
    return mod


core = _load_core()

from tree_data import build_day_nodes, build_month_nodes, visible_columns  # noqa: E402

app = FastAPI(title="Blagajna Web Demo", version="0.1.0")
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")
templates = Jinja2Templates(directory=WEB_DIR / "templates")


class AnalyzeRequest(BaseModel):
    root_path: str = Field(..., min_length=1)
    csv_name: str = "blagajne.csv"
    include_zips: bool = True


class AnalyzeState:
    monthly: Dict[Tuple[str, str], Dict[str, float]] = {}
    daily: Dict[Tuple[str, str, str], Dict[str, float]] = {}
    daily_docs: core.DailyDocsMap = {}
    visible_cols: List[str] = list(core.SUM_COLS)
    last_root: str = ""
    last_message: str = ""


state = AnalyzeState()


def _root_to_blagajna_dir(root_path: Path) -> Path:
    root_path = root_path.resolve()
    if root_path.name.lower() == "blagajna":
        root_path.mkdir(parents=True, exist_ok=True)
        return root_path
    target = root_path / "Blagajna"
    target.mkdir(parents=True, exist_ok=True)
    return target


def _filter_companies(companies: List[Dict[str, str]], q: str) -> List[Dict[str, str]]:
    needle = (q or "").strip().casefold()
    if not needle:
        return companies
    out: List[Dict[str, str]] = []
    for c in companies:
        hay = " ".join(
            str(c.get(k) or "")
            for k in ("Zšt", "NAZIV", "NASLOV", "DAVČNA", "Ime in priimek odg osebe", "DURS sifra", "Email")
        ).casefold()
        if needle in hay:
            out.append(c)
    return out


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_title": core.APP_TITLE,
            "durs_default": str(core.DURS_DEFAULT_PATH),
        },
    )


@app.get("/api/settings")
def api_settings() -> Dict[str, Any]:
    return {
        "durs_path": str(core.DURS_DEFAULT_PATH),
        "csv_name_default": "blagajne.csv",
        "demo_note": "Interna demo verzija — samo analiza CSV in prikaz drevesa.",
    }


@app.get("/api/companies")
def api_companies(
    q: str = Query("", description="Iskanje po firmah"),
    durs_path: Optional[str] = Query(None),
) -> Dict[str, Any]:
    path = Path(durs_path or core.DURS_DEFAULT_PATH).expanduser()
    try:
        companies = core.load_companies_from_durs_xlsx(path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"DURS datoteka ni najdena: {path}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    filtered = _filter_companies(companies, q)
    return {"total": len(companies), "count": len(filtered), "companies": filtered[:500]}


@app.post("/api/analyze")
def api_analyze(body: AnalyzeRequest) -> Dict[str, Any]:
    root = Path(body.root_path).expanduser().resolve()
    if not root.exists():
        raise HTTPException(status_code=400, detail=f"Mapa ne obstaja: {root}")

    blagajna = _root_to_blagajna_dir(root)
    source = core.resolve_analysis_data_root(blagajna)
    report = core.Report()
    csv_name = (body.csv_name or "blagajne.csv").strip() or "blagajne.csv"

    state.monthly = core.build_monthly_sums(source, csv_name, body.include_zips, report)
    state.daily = core.build_daily_sums(source, csv_name, body.include_zips, report)
    state.daily_docs = core.build_daily_docs(source, csv_name, body.include_zips, report)
    state.visible_cols = visible_columns(state.monthly, state.daily, state.daily_docs)
    state.last_root = str(source)

    warnings: List[str] = []
    if not state.monthly:
        warnings = core.format_analyze_warning_details(source, csv_name, report, include_zips=body.include_zips)
        state.last_message = "Ni najdenih uporabnih podatkov."
    else:
        state.last_message = (
            f"Analiza OK — {len(state.monthly)} mesecev, {len(state.daily)} dni, "
            f"{sum(len(v) for v in state.daily_docs.values())} dokumentov."
        )

    tree = build_month_nodes(state.monthly, state.daily, state.daily_docs)
    return {
        "ok": bool(state.monthly),
        "message": state.last_message,
        "source_root": str(source),
        "blagajna_dir": str(blagajna),
        "warnings": warnings,
        "tree": tree,
    }


@app.get("/api/tree")
def api_tree() -> Dict[str, Any]:
    if not state.monthly:
        return {"columns": ["Leto", "Mesec", "Dan"], "sum_columns": [], "nodes": [], "stats": {}}
    return build_month_nodes(state.monthly, state.daily, state.daily_docs)


@app.get("/api/tree/month/{yyyy}/{mm}")
def api_tree_month(yyyy: str, mm: str) -> Dict[str, Any]:
    if not state.monthly:
        raise HTTPException(status_code=400, detail="Najprej zaženi analizo.")
    cols = state.visible_cols or visible_columns(state.monthly, state.daily, state.daily_docs)
    children = build_day_nodes(yyyy, mm, state.daily, state.daily_docs, cols)
    return {"yyyy": yyyy, "mm": mm, "children": children}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="127.0.0.1", port=8765, reload=False)
