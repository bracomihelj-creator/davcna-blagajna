# Primerjava kontrolnikov — 3.0.68 (Tk) ↔ 4.0.4 (WebView2)

**Datum:** 2026-11-16  
**Cilj:** zapreti luknje iz 4.0.3 (~85 %) do 100 % povezanih vedenj.

## API / vedenja 4.0.4

| Funkcija | Endpoint / pot | Status |
|---|---|---|
| Evidenca filter | `company_in_davcna_evidenca` + Ev. klik | **OK** |
| Neobd. preracun | `/api/neob` + `rebuild_aggregates` | **OK** |
| Filter dokumentov | `doc_filter` + `tree_month` | **OK** |
| ✓ označitev | `/api/tree/check` | **OK** |
| Sprazni | `/api/tree/clear` | **OK** |
| Detail panel | `/api/tree/detail` | **OK** |
| Dodaj nov zapis | `kirkpr_new_record` (Tk most) | **OK**/MOST |
| Seznam primerjav | `/api/compare_presets` (HTML) + zagon Tk | **OK**/MOST |

## Checkboxi

| Chk 3.0.68 | 4.0.4 | Delovanje |
|---|---|---|
| ZIP | `chkZip` | **OK** |
| Evidenca Davčnih blagajn | `chkEvidenca` + Ev. | **OK** |
| Vrednost Neobd.nabav | `chkNeob` → preracun | **OK** |
| DDV zavezanec | `chkDdv` | **OK** |
| ✓ mesec/dan | stolpec ✓ | **OK** |

## Sklep

Manjkajoča vedenja iz 4.0.3 so zaprta. Kompleksni urejevalniki ostanejo Tk most (hibrid).
