# TESTI — Davčna Blagajna **4.0.1**

**Datum:** 2026-11-16

| Test | Rezultat | Opomba |
|---|---|---|
| Sintaksa `motor.py` / `host.py` / `tree_data` | **OK** | `py_compile` 2026-11-16 |
| Uvoz core 3.0.68 + `Motor.boot` | **OK** | version 4.0.1 / stable 3.0.68 |
| Seznam firm SQL | **OK** | `load_companies` → 132 firm |
| Zagon `.pyw` / WebView2 okno | NI ROČNO V TEJ SEJI | `ZAZENI_4.0.1.bat` |
| Analiza blagajne | NI ROČNO | enaka `build_monthly_sums` kot 3.0.68 |
| FURS Blagajna | NI ROČNO | kliče `_furs_pakrt_fill_in_user_chrome` |
| KIR/KPR CDP | NI ROČNO | `furs_kirkpr_cdp_fill_period` |
| Minimax WebView2 uvoz | NI ROČNO | zahteva Excel |
| Stabilna 3.0.68 še deluje | PRIČAKOVANO DA | mapa ni spremenjena |
| Installer | NI ROČNO | `INSTALL.pyw` |

**Ne trdimo 100 % runtime uspeha**, dokler zgornji ročni testi niso opravljeni.
