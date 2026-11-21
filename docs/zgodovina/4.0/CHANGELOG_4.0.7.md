# CHANGELOG — 4.0.7

## 4.0.7 — 2026-11-17

**1:1 uskladitev stanja poti z 3.0.68**

- Predloga: vedno `D:\Trops\MiniMax\KnjizbeInDDV.xlsx` če je prazna/mapa (odpravlja Permission denied pri knjižbah).
- Ob izboru firme: `out_dir` = Root Blagajna (kot `_sync_output_dir_with_root`).
- `tk_actions`: ne povozi praznih poti; preveri da je predloga datoteka.
- `context_payload` / boot: `_ensure_paths_like_308()` pred vsako akcijo.
