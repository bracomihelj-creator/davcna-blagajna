# Zgodovina 3.0.x (DavčnaBlagajna, Tk) — zapis necommitanega dela

Stanje izvorne mape `D:\PISARNA\Python\DavčnaBlagajna` na dan 2026-11-21 (samo branje, mapa ni spremenjena).

Git v 3.0 ima samo 2 commita; zadnji je 3.0.13. Delo 3.0.14–3.0.68 ni bilo nikoli commitano.
Ta mapa ga hrani kot **zapis** (patch), da se ve, kaj se je spremenilo po 3.0.13.

**Pomembno:** `DavcnaBlagajna.py` in `v2/*` v 5.1 sta byte-identična stanju 3.0.68 na disku
(razen oznak serije/verzije in `v2/minimax_webview2*.py`), zato je vse to delo **že vsebovano v 5.1**.
Patchev ni treba uveljavljati.

## Commiti v 3.0
```
05d0f28 2026-10-09 10:52:49 +0200 braco Restore fast Minimax Uvoz open like 2.2.25 (3.0.11–3.0.13).
1f19fee 2026-10-09 00:43:29 +0200 braco Fix Minimax firm select via postback and add Chrome session status UX (3.0.09–3.0.10).
```

## Staged (glede na 3.0.13) — `3.0_staged_od_3.0.13.patch`
```
 DavcnaBlagajna.py                      | 624 ++++++++++++++++++++++++++++++++++++++++++++++++++++---------
 minimax_uvoz_config.json               |  11 ++
 v2/minimax_uvoz_config.py              |  44 +++++
 v2/minimax_webview2.py                 | 322 ++++++++++++++++++++++++++++++++
 v2/minimax_webview2_host.py            | 737 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 v2/ui_hints.py                         |   6 +-
 v2/version_journal.py                  | 169 +++++++++++++++++
 verzije/Davčna blagajna ver 3.0.14.txt |  16 ++
 verzije/Davčna blagajna ver 3.0.15.txt |  16 ++
 verzije/Davčna blagajna ver 3.0.16.txt |  19 ++
 verzije/Davčna blagajna ver 3.0.17.txt |  18 ++
 verzije/Davčna blagajna ver 3.0.18.txt |  16 ++
 verzije/Davčna blagajna ver 3.0.19.txt |  16 ++
 verzije/Davčna blagajna ver 3.0.20.txt |  16 ++
 verzije/Davčna blagajna ver 3.0.21.txt |  15 ++
 verzije/Davčna blagajna ver 3.0.22.txt |  20 ++
 verzije/davcna_blagajna_verzije.json   | 118 +++++++++++-
 17 files changed, 2095 insertions(+), 88 deletions(-)
```

## Unstaged (staged → 3.0.68) — `3.0_unstaged_do_3.0.68.patch`
```
 DavcnaBlagajna.py                    | 2398 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-------------
 minimax_uvoz_config.json             |    2 +-
 v2/minimax_uvoz_config.py            |   11 +-
 v2/minimax_webview2.py               |   45 +-
 v2/minimax_webview2_host.py          | 1833 ++++++++++++++++++++++++++++++++++++++++++++++++--------
 v2/ui_build.py                       |  417 +++++++------
 v2/ui_hints.py                       |   38 +-
 verzije/davcna_blagajna_verzije.json |  605 ++++++++++++++++++-
 8 files changed, 4510 insertions(+), 839 deletions(-)
```

## Stanje datotek v 3.0 (git status; ?? = nikoli v gitu)
```
MM DavcnaBlagajna.py
AM minimax_uvoz_config.json
AM v2/minimax_uvoz_config.py
AM v2/minimax_webview2.py
AM v2/minimax_webview2_host.py
 M v2/ui_build.py
MM v2/ui_hints.py
A  v2/version_journal.py
A  "verzije/Davčna blagajna ver 3.0.14.txt"
A  "verzije/Davčna blagajna ver 3.0.15.txt"
A  "verzije/Davčna blagajna ver 3.0.16.txt"
A  "verzije/Davčna blagajna ver 3.0.17.txt"
A  "verzije/Davčna blagajna ver 3.0.18.txt"
A  "verzije/Davčna blagajna ver 3.0.19.txt"
A  "verzije/Davčna blagajna ver 3.0.20.txt"
A  "verzije/Davčna blagajna ver 3.0.21.txt"
A  "verzije/Davčna blagajna ver 3.0.22.txt"
MM verzije/davcna_blagajna_verzije.json
?? .cursor/
?? ANALIZA_4.0.1.md
?? Arhiv/
?? BlagajnaMinimax.spec
?? DavcnaBlagajna.pyw
?? DavcnaBlagajna.spec
?? DavcnaBlagajna_evidenca.json
?? DavcnaBlagajna_v2_1.py
?? FUNKCIONALNOSTI_4.0.1.md
?? PREDLOG_POPRAVKOV_4.0.1.md
?? UI_MIGRACIJA_4.0.1.md
?? ZAZENI_BLAGAJNA_EXE.bat
?? ZAZENI_CHROME_EDAVKI_DEBUG.bat
?? ZAZENI_CHROME_MINIMAX_DEBUG.bat
?? ZAZENI_DavcnaBlagajna_PY.bat
?? ZGRADI_DAVCNA_BLAGAJNA.bat
?? Zagon_davcnaBlagajna_V3.bat
?? __pycache__/
?? _check_chrome_debug.py
?? _ensure_davcna_pyw.py
?? _start_chrome_edavki_debug.py
?? _start_chrome_minimax_debug.py
?? blagajna_edavki_links.json
?? blagajna_error.log
?? blagajna_kirkpr_knjizba_form.json
?? blagajna_minimax_settings.example.json
?? blagajna_minimax_settings.json
?? blagajna_ui_settings.json
?? blagajna_v2_access.json
?? blagajna_v2_file_compare.json
?? blagajna_v2_theme.json
?? data/
?? dist/
?? list_minimax_payment_methods.py
?? v2/__init__.py
?? v2/__pycache__/
?? v2/access_settings.py
?? v2/app.py
?? v2/app_v21.py
?? v2/browser_inapp.py
?? v2/chrome_session_sync.py
?? v2/collapsible.py
?? v2/companies_sql.py
?? v2/date_picker.py
?? v2/edavki_links_settings.py
?? v2/file_compare_settings.py
?? v2/filtered_combobox.py
?? v2/kirkpr_editor.py
?? v2/kirkpr_knjizba_form_layout.py
?? v2/knjizba_form_designer.py
?? v2/menubar.py
?? v2/portal_bridge.py
?? v2/tab_bar.py
?? v2/theme.py
?? v2/tooltip.py
?? v2/version_history_ui.py
?? v2/version_switch.py
?? "verzije/Davčna blagajna ver 2.1.01.txt"
?? "verzije/Davčna blagajna ver 2.1.02.txt"
?? "verzije/Davčna blagajna ver 2.1.03.txt"
?? "verzije/Davčna blagajna ver 2.1.04.txt"
?? "verzije/Davčna blagajna ver 2.1.05.txt"
?? "verzije/Davčna blagajna ver 2.1.06.txt"
?? "verzije/Davčna blagajna ver 2.1.08.txt"
?? "verzije/Davčna blagajna ver 2.1.09.txt"
?? "verzije/Davčna blagajna ver 2.1.10.txt"
?? "verzije/Davčna blagajna ver 2.1.11.txt"
?? "verzije/Davčna blagajna ver 2.1.12.txt"
?? "verzije/Davčna blagajna ver 2.1.13.txt"
?? "verzije/Davčna blagajna ver 2.1.14.txt"
?? "verzije/Davčna blagajna ver 2.1.15.txt"
?? "verzije/Davčna blagajna ver 2.1.16.txt"
?? "verzije/Davčna blagajna ver 2.1.17.txt"
?? "verzije/Davčna blagajna ver 2.1.18.txt"
?? "verzije/Davčna blagajna ver 2.1.19.txt"
?? "verzije/Davčna blagajna ver 2.1.20.txt"
?? "verzije/Davčna blagajna ver 2.1.21.txt"
?? "verzije/Davčna blagajna ver 2.1.22.txt"
?? "verzije/Davčna blagajna ver 2.1.23.txt"
?? "verzije/Davčna blagajna ver 2.1.24.txt"
?? "verzije/Davčna blagajna ver 2.1.25.txt"
?? "verzije/Davčna blagajna ver 2.1.26.txt"
?? "verzije/Davčna blagajna ver 2.1.27.txt"
?? "verzije/Davčna blagajna ver 2.1.28.txt"
?? "verzije/Davčna blagajna ver 2.1.29.txt"
?? "verzije/Davčna blagajna ver 2.1.30.txt"
?? "verzije/Davčna blagajna ver 2.1.31.txt"
?? "verzije/Davčna blagajna ver 2.1.32.txt"
?? "verzije/Davčna blagajna ver 2.1.33.txt"
?? "verzije/Davčna blagajna ver 2.1.34.txt"
?? "verzije/Davčna blagajna ver 2.1.35.txt"
?? "verzije/Davčna blagajna ver 2.1.36.txt"
?? "verzije/Davčna blagajna ver 2.1.37.txt"
?? "verzije/Davčna blagajna ver 2.1.38.txt"
?? "verzije/Davčna blagajna ver 2.1.39.txt"
?? "verzije/Davčna blagajna ver 2.1.40.txt"
?? "verzije/Davčna blagajna ver 2.1.41.txt"
?? "verzije/Davčna blagajna ver 2.1.42.txt"
?? "verzije/Davčna blagajna ver 2.1.43.txt"
?? "verzije/Davčna blagajna ver 2.1.44.txt"
?? "verzije/Davčna blagajna ver 2.1.45.txt"
?? "verzije/Davčna blagajna ver 2.1.46.txt"
?? "verzije/Davčna blagajna ver 2.1.47.txt"
?? "verzije/Davčna blagajna ver 2.1.48.txt"
?? "verzije/Davčna blagajna ver 2.1.49.txt"
?? "verzije/Davčna blagajna ver 2.1.50.txt"
?? "verzije/Davčna blagajna ver 2.1.59.txt"
?? "verzije/Davčna blagajna ver 2.1.60.txt"
?? "verzije/Davčna blagajna ver 2.1.61.txt"
?? "verzije/Davčna blagajna ver 2.1.62.txt"
?? "verzije/Davčna blagajna ver 2.1.63.txt"
?? "verzije/Davčna blagajna ver 2.1.64.txt"
?? "verzije/Davčna blagajna ver 2.1.65.txt"
?? "verzije/Davčna blagajna ver 2.1.66.txt"
?? "verzije/Davčna blagajna ver 2.1.67.txt"
?? "verzije/Davčna blagajna ver 2.1.68.txt"
?? "verzije/Davčna blagajna ver 2.1.69.txt"
?? "verzije/Davčna blagajna ver 2.1.70.txt"
?? "verzije/Davčna blagajna ver 2.1.71.txt"
?? "verzije/Davčna blagajna ver 2.1.72.txt"
?? "verzije/Davčna blagajna ver 2.1.73.txt"
?? "verzije/Davčna blagajna ver 2.1.74.txt"
?? "verzije/Davčna blagajna ver 2.1.77.txt"
?? "verzije/Davčna blagajna ver 2.1.78.txt"
?? "verzije/Davčna blagajna ver 2.1.79.txt"
?? "verzije/Davčna blagajna ver 2.1.80.txt"
?? "verzije/Davčna blagajna ver 2.1.81.txt"
?? "verzije/Davčna blagajna ver 2.1.82.txt"
?? "verzije/Davčna blagajna ver 2.2.01.txt"
?? "verzije/Davčna blagajna ver 2.2.02.txt"
?? "verzije/Davčna blagajna ver 2.2.03.txt"
?? "verzije/Davčna blagajna ver 2.2.04.txt"
?? "verzije/Davčna blagajna ver 2.2.05.txt"
?? "verzije/Davčna blagajna ver 2.2.06.txt"
?? "verzije/Davčna blagajna ver 2.2.07.txt"
?? "verzije/Davčna blagajna ver 2.2.08.txt"
?? "verzije/Davčna blagajna ver 2.2.09.txt"
?? "verzije/Davčna blagajna ver 2.2.10.txt"
?? "verzije/Davčna blagajna ver 2.2.11.txt"
?? "verzije/Davčna blagajna ver 2.2.12.txt"
?? "verzije/Davčna blagajna ver 2.2.13.txt"
?? "verzije/Davčna blagajna ver 2.2.14.txt"
?? "verzije/Davčna blagajna ver 2.2.15.txt"
?? "verzije/Davčna blagajna ver 2.2.16.txt"
?? "verzije/Davčna blagajna ver 2.2.17.txt"
?? "verzije/Davčna blagajna ver 2.2.18.txt"
?? "verzije/Davčna blagajna ver 2.2.19.txt"
?? "verzije/Davčna blagajna ver 2.2.20.txt"
?? "verzije/Davčna blagajna ver 2.2.21.txt"
?? "verzije/Davčna blagajna ver 2.2.22.txt"
?? "verzije/Davčna blagajna ver 2.2.23.txt"
?? "verzije/Davčna blagajna ver 2.2.24.txt"
?? "verzije/Davčna blagajna ver 2.2.25.txt"
?? "verzije/Davčna blagajna ver 2.2.26.txt"
?? "verzije/Davčna blagajna ver 2.2.27.txt"
?? "verzije/Davčna blagajna ver 2.2.28.txt"
?? "verzije/Davčna blagajna ver 2.2.29.txt"
?? "verzije/Davčna blagajna ver 3.0.01.txt"
?? "verzije/Davčna blagajna ver 3.0.02.txt"
?? "verzije/Davčna blagajna ver 3.0.03.txt"
?? "verzije/Davčna blagajna ver 3.0.04.txt"
?? "verzije/Davčna blagajna ver 3.0.05.txt"
?? "verzije/Davčna blagajna ver 3.0.06.txt"
?? "verzije/Davčna blagajna ver 3.0.07.txt"
?? "verzije/Davčna blagajna ver 3.0.08.txt"
?? "verzije/Davčna blagajna ver 3.0.23.txt"
?? "verzije/Davčna blagajna ver 3.0.24.txt"
?? "verzije/Davčna blagajna ver 3.0.25.txt"
?? "verzije/Davčna blagajna ver 3.0.26.txt"
?? "verzije/Davčna blagajna ver 3.0.27.txt"
?? "verzije/Davčna blagajna ver 3.0.28.txt"
?? "verzije/Davčna blagajna ver 3.0.29.txt"
?? "verzije/Davčna blagajna ver 3.0.30.txt"
?? "verzije/Davčna blagajna ver 3.0.31.txt"
?? "verzije/Davčna blagajna ver 3.0.32.txt"
?? "verzije/Davčna blagajna ver 3.0.33.txt"
?? "verzije/Davčna blagajna ver 3.0.34.txt"
?? "verzije/Davčna blagajna ver 3.0.35.txt"
?? "verzije/Davčna blagajna ver 3.0.36.txt"
?? "verzije/Davčna blagajna ver 3.0.37.txt"
?? "verzije/Davčna blagajna ver 3.0.38.txt"
?? "verzije/Davčna blagajna ver 3.0.39.txt"
?? "verzije/Davčna blagajna ver 3.0.40.txt"
?? "verzije/Davčna blagajna ver 3.0.41.txt"
?? "verzije/Davčna blagajna ver 3.0.42.txt"
?? "verzije/Davčna blagajna ver 3.0.43.txt"
?? "verzije/Davčna blagajna ver 3.0.44.txt"
?? "verzije/Davčna blagajna ver 3.0.45.txt"
?? "verzije/Davčna blagajna ver 3.0.46.txt"
?? "verzije/Davčna blagajna ver 3.0.47.txt"
?? "verzije/Davčna blagajna ver 3.0.48.txt"
?? "verzije/Davčna blagajna ver 3.0.49.txt"
?? "verzije/Davčna blagajna ver 3.0.50.txt"
?? "verzije/Davčna blagajna ver 3.0.51.txt"
?? "verzije/Davčna blagajna ver 3.0.52.txt"
?? "verzije/Davčna blagajna ver 3.0.53.txt"
?? "verzije/Davčna blagajna ver 3.0.54.txt"
?? "verzije/Davčna blagajna ver 3.0.55.txt"
?? "verzije/Davčna blagajna ver 3.0.56.txt"
?? "verzije/Davčna blagajna ver 3.0.57.txt"
?? "verzije/Davčna blagajna ver 3.0.58.txt"
?? "verzije/Davčna blagajna ver 3.0.59.txt"
?? "verzije/Davčna blagajna ver 3.0.60.txt"
?? "verzije/Davčna blagajna ver 3.0.61.txt"
?? "verzije/Davčna blagajna ver 3.0.62.txt"
?? "verzije/Davčna blagajna ver 3.0.63.txt"
?? "verzije/Davčna blagajna ver 3.0.64.txt"
?? "verzije/Davčna blagajna ver 3.0.65.txt"
?? "verzije/Davčna blagajna ver 3.0.66.txt"
?? "verzije/Davčna blagajna ver 3.0.67.txt"
?? "verzije/Davčna blagajna ver 3.0.68.txt"
?? web_demo/
```

Dnevnik verzij 2.1.01–3.0.68 (168 TXT + JSON) je v 5.1 že v `verzije/`.
Ni preneseno (namenoma): `Arhiv/` (2.2.29), `dist/` (EXE + kopija gesel), `data/` (WebView2 profili,
`_napaka_frames` zaslonske slike), `blagajna_error.log`, `blagajna_minimax_settings.json` (gesla).