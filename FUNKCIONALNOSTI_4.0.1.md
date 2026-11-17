# FUNKCIONALNOSTI — Davčna Blagajna · inventar za **4.0.1**

**Osnova:** produkcijska koda 3.0.68 (PREVERJENO)  
**UI osnova inventarja:** `v2/ui_build_v21.py` + `v2/ui_build.py` + `v2/ui_hints.py` + meniji  
**Status:** inventar iz kode — ne pomeni, da je vsaka pot v tej seji ročno kliknjena (NI PREVERJENO runtime).

---

## 1. Okna in pogledi

| ID | Okno / pogled | Tip | Vir | Status |
|---|---|---|---|---|
| W1 | Glavno okno AppV2 / AppV21 | `tk.Tk` | `v2/app.py`, `v2/app_v21.py` | PREVERJENO |
| W2 | Primerjava datotek — razlike | `Toplevel` | `DavcnaBlagajna.py` | PREVERJENO |
| W3 | Kontiranje — načini plačila / prihodki | `Toplevel` | `KontiranjeEditorDialog` | PREVERJENO |
| W4 | ZIP paketi — FURS blagajna | `Toplevel` | `ZipPackagesDialog` | PREVERJENO |
| W5 | Nastavi OAuth / Minimax | `Toplevel` | `_open_oauth_settings_dialog` | PREVERJENO |
| W6 | Minimax WebView2 host (uvoz/Knjiženje) | ločen proces pywebview | `v2/minimax_webview2*.py` | PREVERJENO — **ohraniti** |
| W7 | Nastavitve (tema, dostop, eDavki, primerjave, knjižba forma) | meni / dialogi | `v2/settings_menu.py` | PREVERJENO |
| W8 | Zgodovina verzij | dialog | `v2/version_history_ui.py` | PREVERJENO |

---

## 2. Glavna postavitev (v2.1)

```
[Header: naslov + badge verzije + Minimax status + firma]
[Orodna vrstica — v v2.1 večinoma prazna / skrita klasika]
[H-Paned]
  Levo: Firme (SQL) + obdobje Leto/Mesec
  Desno:
    [Minimax Org ID / OAuth] (collapsible)
    [TabBar pogled: Blagajna | KIR/KPR | Primerjaj KIRKPR | Primerjaj datoteke | Minimax]
    [1. Uvoz KIR/KPR] (vidno pri KIR/KPR)
    [Izvoz Excel · knjižbe · API]
    [Drevo / primerjave / strani]
[V-Paned spodaj: Pot & datoteke · Minimax nastavitve]
[Footer z verzijo]
```

**PREVERJENO** iz `build_ui_v21` / `_build_main_panels_v21`.

---

## 3. Zavihki / TabBar

| Kontrolnik | Vrednosti | Dogodek | Status |
|---|---|---|---|
| Pogled analize | Blagajna, KIR/KPR, Primerjaj KIRKPR, Primerjaj datoteke, Minimax | `_on_v21_view_tab_changed` | PREVERJENO |
| KIR/KPR knjiga | KIR, KPR | `_on_v21_kirkpr_sub_tab_changed` | PREVERJENO |
| Vir KIR/KPR | eDavki, Minimax | `_on_v21_kirkpr_source_tab_changed` | PREVERJENO |
| Izvoz | Excel & knjižbe, Izvoz v Minimax API | preklop panelov | PREVERJENO |
| Spodnji notebook | Pot & datoteke, Minimax nastavitve (+ Excel/API v v2.0) | `register_v2_notebook` | PREVERJENO |

---

## 4. Gumbi in ukazi (glavni tokovi)

### Blagajna / analiza

| Gumb | Handler (približno) | Namig | Status |
|---|---|---|---|
| Analiziraj / Uvozi Davčno blagajno | `_analyze` | ANALYZE_BLAGAJNA | PREVERJENO |
| FURS Blagajna | `_open_furs_and_optional_month_location` | FURS_BLAGAJNA (Chrome, ~2 s) | PREVERJENO |
| Filtriraj / Počisti filter | filter drevesa | FILTER_* | PREVERJENO |
| Vrednost Neobd.nabav | check | SHOW_NEOBD | PREVERJENO |
| Dodaj nov zapis | (KIR/KPR kontekst) | — | PREVERJENO (gumb obstaja) |
| Razširi / Skrči / Sprazni | drevo | TREE_* | PREVERJENO |

### KIR/KPR

| Gumb | Handler | Status |
|---|---|---|
| Prenos KIR/KPR eDavki | `_open_furs_kir_kpr_and_optional_month_location` | PREVERJENO |
| Prenos KIR/KPR minimax | `_prenos_minimax_kirkpr` | PREVERJENO |
| Uvozi podatke | `_uvozi_kirkpr` | PREVERJENO |

### Primerjave

| Gumb | Handler | Status |
|---|---|---|
| Primerjaj datoteki (ročno) | `_compare_files` | PREVERJENO |
| Primerjaj (prednastavitve) | `_compare_files_presets` | PREVERJENO |

### Minimax / izvoz

| Gumb | Handler | Status |
|---|---|---|
| OAuth… | `_open_oauth_settings_dialog` | PREVERJENO |
| Konti… / ↻ načini plačila | kontiranje / osvežitev | PREVERJENO |
| Shrani v Excel | shranjevanje | PREVERJENO |
| Izvoz podatkov v excel | izvoz analize | PREVERJENO |
| Knjižbe DDV po mesecih / dnevih | knjižbe | PREVERJENO |
| Minimax spletni uvoz | WebView2 avtomatizacija | PREVERJENO — zaklenjena pot |
| Pošlji mesec/dan API | IssuedInvoicePosting | PREVERJENO (namigi SEND_*) |

### Firme

| Gumb / kontrola | Handler | Status |
|---|---|---|
| Išči / ✕ | filter firm | PREVERJENO |
| Osveži | SQL reload | PREVERJENO |
| Evidenca Davčnih blagajn | filter Ev. | PREVERJENO |
| eDavki Odpri | portal link | PREVERJENO |
| Treeview firm | izbor firme | PREVERJENO |

### Pot & datoteke

| Kontrola | Pomen | Status |
|---|---|---|
| Root / … | mapa Blagajna | PREVERJENO |
| ZIP + ZIP paketi… | vključitev mesečnih ZIP | PREVERJENO |
| Shranjevanje / Datoteka / Sheet / CSV | izhodne poti | PREVERJENO |

---

## 5. Meniji

| Meni | Vsebina (iz kode) | Status |
|---|---|---|
| Verzija | preklop / zgodovina (`version_switch`, `version_history_ui`) | PREVERJENO |
| Nastavitve | tema, barve, fonti, layout, dostop eDavki/Minimax, povezave, primerjave datotek, oblika knjižbe, … | PREVERJENO (obsežen `settings_menu.py`) |

---

## 6. Poslovni tokovi (ohraniti 1:1)

1. **Izbor firme (SQL) → obdobje → analiza blagajne → drevo → Excel/knjižbe/API/WebUI uvoz**  
2. **FURS Blagajna** v že odprtem Chrome (PakR Od/do) — ne menjati motorja  
3. **KIR/KPR eDavki** CDP `:9222` — ne seliti v WebView2  
4. **KIR/KPR Minimax** prenos + uvoz + primerjava eDavki↔Minimax  
5. **Minimax spletni uvoz** WebView2 profil → Moje org → KN → Excel CDP — zaklenjeno  
6. **Po API** odpiranje Knjiženja IR/iztržkov (3.0.68)  
7. **Primerjava datotek** (ročno + prednastavitve)  
8. **Kontiranje** prihodkov / načinov plačila  
9. **Trajne nastavitve** (tema, dostop, poti, zadnja firma) — ločeno od poslovnih DB

---

## 7. Stanja in validacije (visoka raven)

- `_safe_call` ovija gumbe (napake → messagebox + log) — PREVERJENO (vzorec)  
- Označene vrstice drevesa vplivajo na izvoz — PREVERJENO (UI tekst)  
- OAuth/token pred API — PREVERJENO (namigi)  
- WebView2 samo če API ni mogoč (za dnevni pošiljanje) — PREVERJENO (SEND_DAILY_API namig)  
- Ne briši WebView2 profila med teki — PREVERJENO (`minimax_webview2.py` komentar/IPC clear)

---

## 8. Bližnjice / tipke

| Tipka | Dejanje | Status |
|---|---|---|
| Delete | izbris označene vrstice drevesa | PREVERJENO (UI tekst / TREE_CLEAR_ROW) |
| Enter v filtru | filtriraj | PREVERJENO (namig) |

Poln inventar vseh `bind(...)` v monolitni datoteki: **NI PREVERJENO** v celoti v tej fazi — dopolniti pred Fazo D implementacijo (PREDLAGANO).

---

## 9. Zunanje povezave (ne spreminjati brez DA)

- Chrome debug eDavki / Minimax  
- SQL EvidencaFirm  
- Minimax OAuth API  
- Trajni WebView2 profil na disku  
- Mape Trops / Blagajna / DDV / ZIP evidence
