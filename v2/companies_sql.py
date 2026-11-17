"""Firme iz SQL EvidencaFirm (dbo.Clients) — linija 3.0.xx."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from v2.edavki_links_settings import resolve_sql_connection_string


STATUS_AKTIVNO = "Aktivno"


def _cell(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _company_from_sql_row(row: Any) -> Dict[str, str]:
    """Preslika vrstico dbo.Clients v format Davčne Blagajne (COMPANY_COLS_UI + oddaja DDV)."""
    zst = row[0]
    sod = _cell(row[1]) or STATUS_AKTIVNO
    kratko = _cell(row[2])
    dolgo = _cell(row[3])
    naslov = _cell(row[4])
    davcna = _cell(row[5])
    odg = _cell(row[6])
    oddaja = _cell(row[7])
    durs = _cell(row[8])
    email = _cell(row[9])
    org_id = _cell(row[10])
    naziv = kratko or dolgo
    return {
        "Zšt": str(int(zst)) if zst is not None else "",
        "Sodelovanje": sod,
        "NAZIV": naziv,
        "NASLOV": naslov,
        "DAVČNA": davcna,
        "Ime in priimek odg osebe": odg,
        "oddaja DDV": oddaja,
        "DURS sifra": durs,
        "Email": email,
        "Org_ID": org_id,
        "Kratko ime": kratko,
        "Dolgo": dolgo,
    }


def load_companies_from_evidenca_sql(
    connection_string: str = "",
    *,
    include_prekinitev: bool = False,
) -> List[Dict[str, str]]:
    """
    Naloži firme iz dbo.Clients (EvidencaFirm).
    Privzeto samo aktivno sodelovanje.
    """
    cs = (connection_string or "").strip() or resolve_sql_connection_string()
    if not cs:
        raise RuntimeError(
            "Manjka SQL povezava do Evidence firm.\n"
            "Nastavi sql_config_path (../EvidencaFirm/config.json) v blagajna_edavki_links.json "
            "ali sql_connection_string."
        )
    try:
        import pyodbc  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError("Za SQL uvoz namesti pyodbc (pip install pyodbc).") from exc

    conn = pyodbc.connect(cs, timeout=15)
    try:
        cur = conn.cursor()
        sql = """
            SELECT
                Zst,
                Sodelovanje,
                KratkoIme,
                Dolgo,
                Naslov,
                Davcna,
                OdgOseba,
                OddajaDdv,
                DursSifra,
                Email,
                OrgId
            FROM dbo.Clients
        """
        if include_prekinitev:
            sql += " ORDER BY Zst"
            cur.execute(sql)
        else:
            sql += " WHERE Sodelovanje = ? OR Sodelovanje IS NULL OR LTRIM(RTRIM(Sodelovanje)) = N'' ORDER BY Zst"
            cur.execute(sql, (STATUS_AKTIVNO,))
        out: List[Dict[str, str]] = []
        for row in cur.fetchall():
            rec = _company_from_sql_row(row)
            if not rec.get("DAVČNA") and not rec.get("NAZIV"):
                continue
            if not rec.get("DAVČNA"):
                continue
            out.append(rec)
        return out
    finally:
        conn.close()


def sql_source_label(connection_string: str = "") -> str:
    """Kratka oznaka vira za UI."""
    cs = (connection_string or "").strip() or resolve_sql_connection_string()
    if not cs:
        return "SQL (ni povezave)"
    # Poskusi izluščiti Database=
    import re

    m = re.search(r"Database=([^;]+)", cs, re.I)
    db = (m.group(1).strip() if m else "EvidencaFirm") or "EvidencaFirm"
    return f"SQL · {db} · dbo.Clients"
