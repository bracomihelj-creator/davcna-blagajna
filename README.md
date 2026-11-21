# Davčna Blagajna 5.1

Namizna aplikacija za davčno blagajno, KIR/KPR, primerjave in prenos v Minimax.
Videz: HTML + **pywebview / Edge WebView2** (5 pogledov: Blagajna, KIR/KPR,
Primerjaj KIRKPR, Primerjaj datoteke, Minimax). Poslovna logika je **ista kot v 3.0.68**
(`DavcnaBlagajna.py` + `v2/`), ki teče skrita v istem procesu (AppV21).

## Zagon

- `ZAZENI_5.1.bat` (s konzolo ob napaki) ali `DavcnaBlagajna.pyw` / `DavcnaBlagajna_5.1.pyw`
- Prva namestitev: `INSTALL.pyw` (preveri Python 3.10, pywebview, WebView2 Runtime, naredi bližnjico)
- Rollback: meni **Datoteka → Odpri Tk 3.0.68** ali `D:\PISARNA\Python\DavčnaBlagajna\Zagon_davcnaBlagajna_V3.bat`

## Struktura

| Pot | Namen |
|---|---|
| `DavcnaBlagajna.py` | jedro 3.0.68 (izračuni, FURS, KIR/KPR, Minimax API) — **ne spreminjaj brez DA** |
| `v2/` | AppV21 (Tk logika, nastavitve, Minimax WebView2 host, eDavki seja) |
| `host_webview.py` | pywebview okno + js_api Bridge na AppV21 |
| `tree_view.py` | pretvorba drevesa AppV21 v JSON za LOOK |
| `ui/` | `index.html`, `app.js`, `app.css` |
| `verzije/` | dnevnik verzij (JSON + TXT) |
| `docs/` | dokumentacija 5.0, zgodovina 4.0 in 3.0 |
| `tools/legacy/` | stari zaganjalniki (EXE, V3) in web_demo — samo za evidenco |
| `data/` | WebView2 profili, Minimax seja, videz (ni v gitu) |

## Odvisnosti

Python 3.10, `pywebview`, `selenium`, `openpyxl`, `pyodbc`, `websocket-client`,
`browser-cookie3`, `pywin32`. Microsoft Edge WebView2 Runtime. SQL Server (EvidencaFirm).

## Nastavitve in skrivnosti

`blagajna_minimax_settings.json` (Minimax OAuth / gesla), `blagajna_ui_settings.json`,
`blagajna_v2_access.json`, `DavcnaBlagajna_evidenca.json` so lokalne in **niso v gitu**.
Predloga: `blagajna_minimax_settings.example.json`, `blagajna_v2_access.example.json`.

## Pravila

Glej `.cursor/rules/` in `POROCILO.md`. Vsaka sprememba = svoj git commit.