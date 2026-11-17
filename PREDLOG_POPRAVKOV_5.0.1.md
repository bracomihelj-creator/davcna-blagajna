# PREDLOG SPREMEMB — **5.0.1** (ZAHTEVA ODOBRITEV)

**Ne izvajaj, dokler uporabnik ne potrdi tega seznama.**

---

## 1. Številka in mapa

| | |
|---|---|
| Nova verzija | **5.0.1** |
| Nova mapa | `D:\PISARNA\Python\DavčnaBlagajna_5.0.1` |
| Osnova kopije | `D:\PISARNA\Python\DavčnaBlagajna` (**3.0.68**) |
| 3.0.68 | **nedotaknjena** |
| 4.0.x | **ne uporabljati** kot osnovo (hibrid) |

Zagon po izvedbi: `DavcnaBlagajna.pyw` + kopija `DavcnaBlagajna_5.0.1.pyw`, `INSTALL.pyw`, bližnjica.  
Rollback: `ZAZENI_DavcnaBlagajna_PY.bat` v mapi 3.0.68.

---

## 2. Seznam sprememb (po odobritvi)

1. Varnostna kopija 3.0.68 izvorov (brez brisanja SQL/JSON uporabnika).
2. Kopija potrebnih modulov 3.0.68 v mapo 5.0.1 (`DavcnaBlagajna.py`, `v2/*`, zagonske datoteke). **Ne** kopirati 4.0 `motor.py` / `tk_actions.py`.
3. Eno Python jedro: `AppV21` (ali `App`) **v istem procesu** kot pywebview.
4. Tk glavno okno `withdraw` — ni Tk LOOK.
5. HTML/CSS/JS: QUICK sidebar; **5 pogledov v levem panelu**; desno vsebina + drevo.
6. Bridge: JS kliče **iste** metode kot gumbi v `ui_build_v21.py` / `ui_build.py`.
7. Privzete poti 1:1 (`MINIMAX_TEMPLATE`, `_sync_output_dir_with_root`).
8. Dialogi (OAuth, konti, ZIP, nastavitve, primerjava) → HTML v istem oknu; datoteke Win32.
9. Namigi `#ffffe0`; verzija v naslovu **5.0.1**.
10. `.cursor/rules` za 5.0: eno stanje, brez mostu, 3.0.68 lock.
11. `INSTALL.pyw` (WebView2 Runtime, ne prepiše 3.0.68).
12. Po izvedbi: `CHANGELOG_5.0.1.md`, `TESTI_5.0.1.md`.

---

## 3. Ohranjene funkcije

Vse iz `FUNKCIONALNOSTI_5.0.1.md` — analiza, FURS, KIR/KPR, Excel, knjižbe, API, Minimax uvoz, primerjave, SQL firme, Ev., filter, ✓, Sprazni, Neobd., OAuth, konti.

Zaklenjeno: FURS 2.2.28 Chrome, KIR CDP :9222, Minimax WebView2 3.0.42.

---

## 4. Česa ni v obsegu

- Spremembe mape 3.0.68
- Selitev eDavki v WebView2
- Selenium
- Dvojni Motor / `tk_actions`
- Spremembe poslovnih formul v `DavcnaBlagajna.py` (razen nujnega adapterja za JSON prikaz)

---

## 5. Testni načrt (po izvedbi)

- [ ] Zagon/izhod 5.0.1; 3.0.68 še deluje
- [ ] Izbor firme 71 → Root in out_dir = `D:\Trops\71\Blagajna`; predloga = `KnjizbeInDDV.xlsx`
- [ ] Uvozi podatke = `_analyze` v istem App; drevo se ujema s 3.0.68
- [ ] FURS Blagajna: PakR URL + Od/do; ZIP cilj v status + odložišče (Win32)
- [ ] Knjižbe po dnevih: xlsx v out_dir, brez Permission denied
- [ ] Levi nav: 5 pogledov
- [ ] KIR/KPR prenosi/uvoz
- [ ] Primerjave
- [ ] Ni drugega python procesa AppV21 ob kliku gumba

---

## 6. Datoteke (nove v 5.0.1)

| Datoteka | Namen |
|---|---|
| `DavcnaBlagajna.py` | kopija 3.0.68 |
| `v2/*` | kopija 3.0.68 |
| `host_webview.py` / `DavcnaBlagajna.pyw` | pywebview + **isti** App |
| `ui/index.html`, `app.css`, `app.js` | LOOK + bridge |
| `INSTALL.pyw`, `ZAZENI_5.0.1.bat` | namestitev/zagon |
| pravilo `.mdc` | eno stanje |

---

## 7. Faza C — vprašanje

**Ali potrjuješ navedeni seznam sprememb za predlagano različico 5.0.1?**

Do izrecnega **DA** na ta seznam se koda ne spreminja.
