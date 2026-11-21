# TESTI — Davčna Blagajna 5.0.1

**Datum:** 2026-11-17  
**Ne trdi 100 % delovanja, dokler uporabnik ne preveri tokov na svojih podatkih.**

## Avtomatsko (ta seja)

| Test | Rezultat |
|---|---|
| `py_compile` host_webview.py, tree_view.py, DavcnaBlagajna.pyw, INSTALL.pyw | OK |
| `import tree_view` + pywebview | OK |
| `get_current_patch_version()` v mapi 5.0.1 | 5.0.1 |
| `get_current` v mapi 3.0.68 | 3.0.68 (nespremenjeno) |
| Obstoj `ui/index.html`, `app.css`, `app.js` | da |
| 3.0.68 mapa ni spremenjena (razen morebitnega `.mdc` pravila) | namenoma |
| Ni `motor.py` / `tk_actions.py` v 5.0.1 | namenoma |

## Ročno (uporabnik)

- [ ] Zagon `ZAZENI_5.0.1.bat` / `DavcnaBlagajna.pyw`; izhod
- [ ] 3.0.68 še deluje (`ZAZENI_DavcnaBlagajna_PY.bat` v stari mapi)
- [ ] Levi nav: 5 pogledov (Blagajna / KIR/KPR / Primerjaj KIRKPR / Primerjaj datoteke / Minimax)
- [ ] Izbor firme 71 → Root in out_dir = `D:\Trops\71\Blagajna`; predloga = `KnjizbeInDDV.xlsx`
- [ ] Uvozi podatke = `_analyze` v istem procesu; drevo se ujema s 3.0.68
- [ ] FURS Blagajna: PakR URL + Od/do; ZIP cilj v status vrstici; odložišče Win32
- [ ] Knjižbe po dnevih: xlsx v out_dir, brez Permission denied
- [ ] KIR/KPR prenosi/uvoz (eDavki Chrome :9222, Minimax)
- [ ] Primerjave prednastavitev
- [ ] Ev. kljukica, filter evidence, eDavki Odpri
- [ ] Ni drugega python procesa AppV21 ob kliku gumba
- [ ] Minimax spletni uvoz odpre obstoječi WebView2 host 3.0.42

## Omejitve te seje

- GUI ni kliknjen od konca do konca v tej seji (ni nadomestek za tvoj preizkus).
- Dialogi nastavitev / OAuth / konti / ZIP ostanejo Tk Toplevel iz 3.0.68 (pomožna okna, ne glavni LOOK).
- Tk okno obstaja skrito (StringVar + Treeview = isto stanje); ni vidno kot glavni UI.
