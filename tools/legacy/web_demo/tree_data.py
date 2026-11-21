"""JSON dreveso rezultatov — enaka struktura kot desktop _refresh_tree / _load_days_for_month."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from blagajna_core import (
    SUM_COLS,
    CompareDailyDocument,
    DailyDocsMap,
    format_float,
    visible_sum_cols_for_analysis,
)


def _sum_dict(sums: Dict[str, float], cols: List[str]) -> Dict[str, float]:
    return {c: float(sums.get(c, 0.0)) for c in cols}


def _sum_formatted(sums: Dict[str, float], cols: List[str]) -> Dict[str, str]:
    return {c: format_float(sums.get(c, 0.0)) for c in cols}


def document_tree_label(doc: CompareDailyDocument) -> str:
    doc_label = doc.doc_id or f"Vrstica {doc.source_row}"
    if doc.doc_type:
        doc_label = f"{doc_label} ({doc.doc_type})"
    return doc_label


def visible_columns(
    monthly: Dict[Tuple[str, str], Dict[str, float]],
    daily: Dict[Tuple[str, str, str], Dict[str, float]],
    daily_docs: DailyDocsMap,
) -> List[str]:
    return visible_sum_cols_for_analysis(monthly, daily, daily_docs)


def build_month_nodes(
    monthly: Dict[Tuple[str, str], Dict[str, float]],
    daily: Dict[Tuple[str, str, str], Dict[str, float]],
    daily_docs: DailyDocsMap,
) -> Dict[str, Any]:
    cols = visible_columns(monthly, daily, daily_docs)
    by_year: Dict[str, List[Tuple[str, Dict[str, float]]]] = {}
    for (yyyy, mm), sums in monthly.items():
        by_year.setdefault(yyyy, []).append((mm, sums))

    grand_totals = {c: 0.0 for c in SUM_COLS}
    nodes: List[Dict[str, Any]] = []

    for yyyy in sorted(by_year.keys()):
        year_totals = {c: 0.0 for c in SUM_COLS}
        month_nodes: List[Dict[str, Any]] = []
        for mm, sums in sorted(by_year[yyyy], key=lambda x: x[0]):
            for c in SUM_COLS:
                year_totals[c] += sums[c]
                grand_totals[c] += sums[c]
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
        "nodes": nodes,
        "stats": {
            "months": len(monthly),
            "days": len(daily),
            "documents": sum(len(v) for v in daily_docs.values()),
        },
    }


def build_day_nodes(
    yyyy: str,
    mm: str,
    daily: Dict[Tuple[str, str, str], Dict[str, float]],
    daily_docs: DailyDocsMap,
    cols: List[str],
) -> List[Dict[str, Any]]:
    mm_norm = f"{int(mm):02d}"
    day_rows = sorted(
        [((y, m, d), sums) for (y, m, d), sums in daily.items() if y == yyyy and m == mm_norm],
        key=lambda kv: kv[0][2],
    )
    if not day_rows:
        return [
            {
                "id": f"empty:{yyyy}:{mm_norm}",
                "kind": "empty",
                "label": "(ni dnevnih podatkov)",
                "yyyy": yyyy,
                "mm": mm_norm,
            }
        ]

    out: List[Dict[str, Any]] = []
    for (_y, _m, dd), sums in day_rows:
        day_key = (yyyy, mm_norm, dd)
        docs = daily_docs.get(day_key, [])
        doc_nodes: List[Dict[str, Any]] = []
        for doc in sorted(docs, key=lambda d: (d.doc_id.lower(), d.source_row)):
            doc_tag_key = str(doc.source_row) if doc.source_row else doc.doc_id
            doc_nodes.append(
                {
                    "id": f"doc:{yyyy}:{mm_norm}:{dd}:{doc_tag_key}",
                    "kind": "doc",
                    "label": document_tree_label(doc),
                    "yyyy": yyyy,
                    "mm": mm_norm,
                    "dd": dd,
                    "sums": _sum_dict(doc.sums, cols),
                    "formatted": _sum_formatted(doc.sums, cols),
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
