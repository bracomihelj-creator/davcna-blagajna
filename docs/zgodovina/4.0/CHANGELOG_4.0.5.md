# CHANGELOG — 4.0.5

## 4.0.5 — 2026-11-17

**DA:** 100 % migracija razen LOOK.

- **FURS Blagajna:** 1:1 z `_open_furs_and_optional_month_location` — DURS → `furs_pakr_page_url` → Od/do (zaklenjeno 2.2.28). Odpravlja »Manjka URL DPR PakR«.
- **Evidenca / Prenos KIR/KPR:** ista AppV21 metoda (`furs_kirkpr_open`).
- **Minimax spletni uvoz:** vedno prek iste AppV21 poti (brez okrnjenega stubа).
- **Pravilo:** `.cursor/rules/davcna-blagajna-4.0-100pct-vedenje.mdc` — LOOK drugačen, vedenje enako.
