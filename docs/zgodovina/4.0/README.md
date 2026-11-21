# Zgodovina 4.0.x (DavčnaBlagajna_4.0.1)

Prvi poskus prenosa na WebView2 (4.0.1–4.0.7, 16.–17. 11. 2026).
Arhitektura: `host.py` (lokalni HTTP strežnik + pywebview) + `motor.py` + `tk_actions.py`
(vsaka Tk akcija v ločenem procesu). V 5.x je nadomeščena z enim procesom
(`host_webview.py`, js_api Bridge na isti AppV21).

Tu so samo dokumenti (CHANGELOG, TESTI, POROČILA, analize, README 4.0.1) in
Cursor pravila 4.0 (`cursor_rules/`). Koda 4.0 (`host.py`, `motor.py`, `tk_actions.py`,
`tree_data*.py`) NI prenesena — v 5.1 jo nadomešča `host_webview.py` / `tree_view.py`.
Iz 4.0 sta v 5.1 prenesena: gumb »Odpri Tk 3.0.68« (rollback) in nastavitev gostote.

Izvorna mapa ostane nedotaknjena: `D:\PISARNA\Python\DavčnaBlagajna_4.0.1`.