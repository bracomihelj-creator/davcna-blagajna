# TESTI — 4.0.4

## Avtomatski smoke (2026-11-16)

| Test | Rezultat |
|---|---|
| `APP_VERSION` | **4.0.4** |
| SQL firme | 132 / Ev. **10** |
| Filter Evidenca | **10 / 132** |
| compare_presets | OK (4) |
| tree_clear brez izbire | zavrnjeno (pričakovano) |
| py_compile motor/host/tk_actions | OK |
| HTTP boot/companies/select/analyze/neob/compare | OK |
| Analiza obdobje ≠ podatki | sporočilo + `available_months` |
| Analiza 2026-09 + ✓ + detail + Sprazni | preverjeno v teku |

## Ročno (priporočeno)

1. Zagon `DavcnaBlagajna.pyw` — naslov 4.0.4  
2. chk Evidenca → ~10 firm; klik Ev. ☑/☐  
3. Uvozi podatke za mesec, ki obstaja → drevo  
4. ✓ na mesecu → vrstica Označeno  
5. Klik vrstice → detail desno  
6. Sprazni → vrstica izgine  
7. Neobd. → osvežitev seštevkov  
8. Filtriraj dokument → po Razširi manj docs  
9. Dodaj nov zapis / Primerjaj → Tk dialog  
