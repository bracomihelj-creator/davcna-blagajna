# -*- coding: utf-8 -*-
"""Prikaz drevesa za WebView2 — bere App (Tk drevo / monthly), ne lastno stanje."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from DavcnaBlagajna import (
    SUM_COLS,
    format_float,
    visible_sum_cols_for_analysis,
)


def _sum_dict(sums: Dict[str, float], cols: List[str]) -> Dict[str, float]:
    return {c: float(sums.get(c, 0.0)) for c in cols}


def _sum_formatted(sums: Dict[str, float], cols: List[str]) -> Dict[str, str]:
    return {c: format_float(sums.get(c, 0.0)) for c in cols}


def document_tree_label(doc: Any) -> str:
    doc_label = getattr(doc, "doc_id", None) or f"Vrstica {getattr(doc, 'source_row', '')}"
    doc_type = getattr(doc, "doc_type", None)
    if doc_type:
        doc_label = f"{doc_label} ({doc_type})"
    return doc_label


def visible_columns(monthly, daily, daily_docs) -> List[str]:
    return visible_sum_cols_for_analysis(monthly, daily, daily_docs)


def _struct_tag(tags: Any) -> str:
    for tag in tags or ():
        t = str(tag)
        if t == "grandtotal" or ":" in t:
            return t
    return ""


CHECKABLE_KINDS = ("month", "day", "year", "yearsum", "grandtotal")


def serialize_look_tree(app: Any, opened: Any = None) -> Dict[str, Any]:
    """HTML drevo iz App.monthly/daily — brez branja Tk Treeview za prikaz."""
    opened_ids = {str(x) for x in (opened or ())}
    monthly = getattr(app, "monthly", None) or {}
    daily = getattr(app, "daily", {}) or {}
    daily_docs = getattr(app, "daily_docs", {}) or {}
    try:
        monthly, daily, daily_docs = app._tree_view_data()
    except Exception:
        pass
    checked = getattr(app, "_tree_checked", set()) or set()
    tree = build_month_nodes(monthly, daily, daily_docs)
    cols = tree.get("sum_columns") or tree.get("value_columns") or []

    def mark(nid: str, kind: str) -> str:
        if kind not in CHECKABLE_KINDS:
            return ""
        return "☑" if nid in checked else "☐"

    def zip_nodes(yyyy: str, mm: str) -> List[Dict[str, Any]]:
        mm_norm = f"{int(mm):02d}"
        try:
            rows = app._calendar_month_zip_rows(yyyy, mm_norm)
        except Exception:
            return []
        out: List[Dict[str, Any]] = []
        for row in rows or []:
            name = str(row.get("name") or "")
            nid = f"zipfile:{yyyy}:{mm_norm}:{name}"
            enabled = bool(row.get("enabled"))
            label = name
            try:
                label = str(app._zip_row_label(row))
            except Exception:
                label = name
            out.append(
                {
                    "id": nid,
                    "kind": "zipfile",
                    "label": label,
                    "check": "☑" if enabled else "☐",
                    "checked": enabled,
                    "has_children": False,
                    "open": False,
                    "children": [],
                }
            )
        return out

    def enrich(node: Dict[str, Any], depth: int) -> Dict[str, Any]:
        nid = str(node.get("id") or "")
        kind = str(node.get("kind") or "row")
        kids = list(node.get("children") or [])
        if kind == "month" and nid in opened_ids:
            yyyy = str(node.get("yyyy") or "")
            mm = str(node.get("mm") or "")
            if yyyy and mm:
                kids = zip_nodes(yyyy, mm) + list(build_day_nodes(yyyy, mm, daily, daily_docs, cols))
        is_open = nid in opened_ids
        if kind == "year":
            is_open = nid in opened_ids
        has_children = bool(kids) or kind in ("year", "month", "day")
        if kind in ("yearsum", "grandtotal", "empty"):
            has_children = False
            is_open = False
        node["depth"] = depth
        node["open"] = is_open
        node["has_children"] = has_children
        node["check"] = node.get("check") or mark(nid, kind)
        node["checked"] = bool(node.get("checked")) or (nid in checked)
        if is_open and kids:
            node["children"] = [enrich(ch, depth + 1) for ch in kids]
        else:
            node["children"] = []
        return node

    tree["nodes"] = [enrich(n, 0) for n in (tree.get("nodes") or [])]
    return tree


def serialize_tk_tree(app: Any, *, opened_only: bool = True) -> Dict[str, Any]:
    """1:1 prikaz Tk Treeview (isti iid/tagi kot Sprazni / ✓).

    opened_only: zaprte veje brez otrok (kot Tk) — klik jih naloži prek _on_tree_open.
    """
    tree = getattr(app, "tree", None)
    monthly = getattr(app, "monthly", None) or {}
    if tree is None:
        return build_month_nodes(monthly, getattr(app, "daily", {}) or {}, getattr(app, "daily_docs", {}) or {})
    try:
        cols = [str(c) for c in (tree["columns"] or ())]
    except Exception:
        cols = []
    checked = getattr(app, "_tree_checked", set()) or set()

    def walk(parent: str, depth: int) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        try:
            children = tree.get_children(parent)
        except Exception:
            return out
        for iid in children:
            try:
                item = tree.item(iid)
            except Exception:
                continue
            tags = item.get("tags") or ()
            tag = _struct_tag(tags)
            kind = tag.split(":")[0] if tag else "row"
            values = ["" if v is None else str(v) for v in (item.get("values") or ())]
            mark = ""
            try:
                mark = app._tree_check_mark(iid)
            except Exception:
                mark = values[0] if values else ""
            node_id = tag or str(iid)
            is_open = bool(item.get("open"))
            raw_kids = []
            try:
                raw_kids = list(tree.get_children(str(iid)))
            except Exception:
                raw_kids = []
            has_children = bool(raw_kids) or kind in ("year", "month", "day")
            kids = walk(str(iid), depth + 1) if (is_open or not opened_only) else []
            node: Dict[str, Any] = {
                "id": node_id,
                "iid": str(iid),
                "kind": kind,
                "label": str(item.get("text") or node_id),
                "values": values,
                "check": mark,
                "checked": node_id in checked or mark == "☑",
                "open": is_open,
                "has_children": has_children,
                "depth": depth,
                "children": kids,
            }
            out.append(node)
        return out

    nodes = walk("", 0)
    if not nodes and monthly:
        return build_month_nodes(monthly, getattr(app, "daily", {}) or {}, getattr(app, "daily_docs", {}) or {})
    return {
        "columns": ["Obdobje"] + cols,
        "value_columns": cols,
        "sum_columns": [c for c in cols if c in SUM_COLS],
        "nodes": nodes,
        "stats": {
            "months": len(monthly),
            "days": len(getattr(app, "daily", {}) or {}),
            "documents": sum(len(v) for v in (getattr(app, "daily_docs", {}) or {}).values()),
        },
    }


def build_month_nodes(monthly, daily, daily_docs) -> Dict[str, Any]:
    cols = visible_columns(monthly, daily, daily_docs)
    by_year: Dict[str, List[Tuple[str, Dict[str, float]]]] = {}
    for (yyyy, mm), sums in monthly.items():
        by_year.setdefault(str(yyyy), []).append((str(mm), sums))
    grand_totals = {c: 0.0 for c in SUM_COLS}
    nodes: List[Dict[str, Any]] = []
    for yyyy in sorted(by_year.keys()):
        year_totals = {c: 0.0 for c in SUM_COLS}
        month_nodes: List[Dict[str, Any]] = []
        for mm, sums in sorted(by_year[yyyy], key=lambda x: x[0]):
            for c in SUM_COLS:
                year_totals[c] += float(sums.get(c, 0.0) or 0.0)
                grand_totals[c] += float(sums.get(c, 0.0) or 0.0)
            month_nodes.append(
                {
                    "id": f"month:{yyyy}:{mm}",
                    "kind": "month",
                    "label": f"{yyyy}-{mm}",
                    "yyyy": yyyy,
                    "mm": mm,
                    "sums": _sum_dict(sums, cols),
                    "formatted": _sum_formatted(sums, cols),
                    "has_children": True,
                    "children_loaded": False,
                    "children": [],
                }
            )
        nodes.append(
            {
                "id": f"year:{yyyy}",
                "kind": "year",
                "label": yyyy,
                "yyyy": yyyy,
                "children": month_nodes
                + [
                    {
                        "id": f"yearsum:{yyyy}",
                        "kind": "yearsum",
                        "label": f"Skupaj {yyyy}",
                        "yyyy": yyyy,
                        "sums": _sum_dict(year_totals, cols),
                        "formatted": _sum_formatted(year_totals, cols),
                    }
                ],
            }
        )
    if monthly:
        nodes.append(
            {
                "id": "grandtotal",
                "kind": "grandtotal",
                "label": "Skupaj vse",
                "sums": _sum_dict(grand_totals, cols),
                "formatted": _sum_formatted(grand_totals, cols),
            }
        )
    return {
        "columns": ["Leto", "Mesec", "Dan"] + cols,
        "sum_columns": cols,
        "value_columns": cols,
        "nodes": nodes,
        "stats": {
            "months": len(monthly),
            "days": len(daily or {}),
            "documents": sum(len(v) for v in (daily_docs or {}).values()),
        },
    }


def build_day_nodes(yyyy: str, mm: str, daily, daily_docs, cols: List[str]) -> List[Dict[str, Any]]:
    mm_norm = f"{int(mm):02d}"
    day_rows = sorted(
        [((y, m, d), sums) for (y, m, d), sums in daily.items() if y == yyyy and m == mm_norm],
        key=lambda kv: kv[0][2],
    )
    if not day_rows:
        return [{"id": f"empty:{yyyy}:{mm_norm}", "kind": "empty", "label": "(ni dnevnih podatkov)"}]
    out: List[Dict[str, Any]] = []
    for (_y, _m, dd), sums in day_rows:
        docs = (daily_docs or {}).get((yyyy, mm_norm, dd), [])
        doc_nodes = []
        for doc in sorted(docs, key=lambda d: (str(getattr(d, "doc_id", "")).lower(), getattr(d, "source_row", 0))):
            tag = str(getattr(doc, "source_row", "") or getattr(doc, "doc_id", ""))
            doc_nodes.append(
                {
                    "id": f"doc:{yyyy}:{mm_norm}:{dd}:{tag}",
                    "kind": "doc",
                    "label": document_tree_label(doc),
                    "sums": _sum_dict(getattr(doc, "sums", {}) or {}, cols),
                    "formatted": _sum_formatted(getattr(doc, "sums", {}) or {}, cols),
                }
            )
        out.append(
            {
                "id": f"day:{yyyy}:{mm_norm}:{dd}",
                "kind": "day",
                "label": f"{int(dd):02d}.{int(mm_norm)}.{yyyy}",
                "yyyy": yyyy,
                "mm": mm_norm,
                "dd": dd,
                "sums": _sum_dict(sums, cols),
                "formatted": _sum_formatted(sums, cols),
                "children": doc_nodes,
            }
        )
    return out
