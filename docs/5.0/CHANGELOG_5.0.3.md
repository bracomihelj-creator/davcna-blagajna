# CHANGELOG — Davčna Blagajna 5.0.3

**Datum:** 2026-11-17

## Zakaj

Po API (firma 09) se je odprlo okno, ki je izgledalo kot nov Edge, in zahtevalo prijavo v Minimax. V 3.0.68 seja ostane.

Log 5.0.2: `Chrome sync: No module named 'v2'` — host proces nima korena na `sys.path`, zato ne prevzame Chrome/WebView2 seje. Profil uvoza je bil v mapi 5.0 (kopija), ne živa 3.0.68 seja.

## Izvedeno

- `PYTHONPATH` + `sys.path` za `minimax_webview2_host.py` → `import v2.chrome_session_sync` deluje.
- Minimax WebView2 profil = **isti** kot 3.0.68 (`data\webview2\minimax_uvoz_profile` v mapi 3.0.68).
- Glavni LOOK WebView2: `OPEN_EXTERNAL_LINKS_IN_BROWSER=False` (ne odpira Microsoft Edge).

## Chk / query / prijava (primerjava z 3.0.68)

| 3.0.68 | 5.0.3 |
|---|---|
| Išči firme (`company_search`) | levo, debounce 250 ms → `_render_companies` |
| Ev. chk + filter evidence | `chkEvidenca` → `_on_evidenca_filter_toggle` |
| ZIP chk | `include_zips` pred `_analyze` |
| Neobd.nabav chk | `_on_show_neobdavcljive_toggle` |
| ✓ drevo | `_toggle_tree_check` |
| Filter dokumentov + Enter | `_apply_doc_filter` |
| OAuth prijava | password grant, **brez brskalnika** |
| Po API Knjiženje | WebView2 host, **ne** nov Edge |
