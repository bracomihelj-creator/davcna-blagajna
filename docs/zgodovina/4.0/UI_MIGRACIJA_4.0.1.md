# UI_MIGRACIJA — Tk/ttk → HTML/CSS/JS + WebView2 · **4.0.1**

**Namen:** preslikava prikaza; Python ostane backend.  
**Status dokumenta:** PREDLAGANO (načrt) na podlagi PREVERJENEGA inventarja 3.0.68.

---

## 1. Arhitekturna shema (PREDLAGANO)

```
┌─────────────────────────────────────────────┐
│  Windows okno (pywebview + Edge WebView2)   │
│  ┌───────────────────────────────────────┐  │
│  │  HTML/CSS/JS  (glavni UI 4.0.1)       │  │
│  │  tabele, zavihki, obrazci, meni       │  │
│  └───────────────┬───────────────────────┘  │
│                  │ bridge (dovoljeni klici) │
│  ┌───────────────▼───────────────────────┐  │
│  │  Python 3.10 backend                  │  │
│  │  DavcnaBlagajna.py + v2 moduli        │  │
│  │  SQL, API, Excel, FURS/Chrome, …      │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
        │
        ├── ločeno: Minimax WebView2 host (3.0.42/3.0.68) — NE zamenjati
        └── ločeno: Chrome :9222 eDavki / FURS — NE seliti v WebView2
```

**Implementacija hosta:** PREDLAGANO enaka družina kot `v2/minimax_webview2_host.py` (pywebview + trajni profil po potrebi), **brez** FastAPI strežnika za produkcijski UI (web_demo ostane referenca/demo).  
**ZAHTEVA ODOBRITEV** pred izbiro končnega host vzorca.

---

## 2. Preslikava kontrolnikov

| Tk / ttk (zdaj) | WebView2 UI (cilj) | Opomba |
|---|---|---|
| `Tk` glavno okno | Eno WebView2 okno + `.pyw` | PREDLAGANO |
| `Toplevel` dialogi | Modal/nemodal HTML dialogi ali drugo WebView2 okno | OAuth, ZIP, Kontiranje, Primerjava |
| `Frame` / `Labelframe` / `Panedwindow` | CSS Grid / Flex / split pane | H+V paned |
| `Label` / `Entry` / rumeni vnosi | label + input (rumena tema ohraniti kot opcijo) | V2Theme |
| `ttk.Combobox` | searchable select | DocumentType, plačila, … |
| `ttk.Treeview` (+ scroll) | Data grid / hierarchical table | firme, drevo, podrobnosti |
| `ttk.Notebook` / `TabBar` | Tabs | pogledi + KIR/KPR + izvoz |
| `ttk.Button` / accent | Button (+ tooltip) | vsi `_mk_btn` |
| `Checkbutton` / `Radiobutton` | checkbox / radio / switch | ZIP, Ev., Neobd., DDV |
| `Menu` menubar | Application menu | Verzija, Nastavitve |
| `messagebox` | Dialog / toast | napake, potrditve |
| `Progressbar` (če obstaja) | Progress | NI PREVERJENO vse lokacije |
| `attach_tooltip` / rumena pasica | CSS tooltip `#ffffe0`, Segoe UI 9, ~380 px | ohraniti pravilo UI namigov |
| Collapsible −/+ | accordion / disclosure | paneli |

---

## 3. Preslikava po območjih UI

### 3.1 Header

| Element | Tk | HTML | Status |
|---|---|---|---|
| Naslov »Davčna Blagajna« | `tk.Label` | `<h1>` | PREDLAGANO |
| Badge verzije | `get_current_patch_version()` | badge `4.0.1` | PREDLAGANO |
| `minimax_status` | Label + StringVar | status strip | PREDLAGANO |
| `selected_company_label` | Label | status strip | PREDLAGANO |

### 3.2 Levo — firme

| Element | Preslikava | Backend klic (ohraniti) |
|---|---|---|
| Iskalnik | input + clear | filter lokalno / Python |
| Osveži | button | SQL reload (`companies_sql`) |
| Ev. check | checkbox | filter |
| eDavki Odpri | button | portal |
| Treeview firm | data-grid | izbor → root_dir / Org ID |

### 3.3 Desno — pogledi

| Pogled | Tk danes | HTML |
|---|---|---|
| Blagajna | drevo + akcije | hierarchical grid + action bar |
| KIR/KPR | TabBar KIR/KPR + eDavki/Minimax gumbi + uvoz | tabs + action bar + grid |
| Primerjaj KIRKPR | host frame | primerjalna tabela |
| Primerjaj datoteke | gumbi + presets + host | enako |
| Minimax | muted placeholder + spodnje nastavitve | nastavitve + status |

### 3.4 Izvoz

| Tk | HTML | Backend |
|---|---|---|
| Shrani Excel / izvoz / knjižbe | gumbi | obstoječe metode |
| Minimax spletni uvoz | gumb | **obstoječi** WebView2 controller (ne reimplementirati) |
| API pošiljanje | gumbi | OAuth + API |

### 3.5 Spodnji panel

Pot & datoteke + Minimax nastavitve → accordion / tabs z rumenimi polji, DocumentType, DDV check, načini plačila, vrsta prodaje, Konti…

### 3.6 Dialogi

| Dialog | Strategija |
|---|---|
| OAuth | HTML modal + Python shrani skrivnosti **samo na disku kot danes** |
| ZIP paketi | HTML modal + ista logika |
| Kontiranje | HTML tabela urejanja |
| Primerjava razlike | polna stran / modal z gridom |
| Nastavitve tema | meni »Videz in nastavitve« (MASTER §8) |

---

## 4. Bridge — dovoljeni klici (osnutek, PREDLAGANO)

Kategorije (končen seznam v Fazi D po odobritvi):

1. `companies.*` — list, select, refresh, search  
2. `period.*` — get/set year/month  
3. `blagajna.analyze` / `kirkpr.import` / `kirkpr.transfer_*`  
4. `furs.open_pakr` / `furs.open_kirkpr`  
5. `export.excel` / `export.knjizbe_*` / `export.api_*` / `export.web_uvoz`  
6. `compare.*`  
7. `settings.*` / `theme.*` / `oauth.*` / `konti.*`  
8. `ui.state` — restore window, tabs, column widths, last company  

Pravila: validacija sporočil, async, napredek, prepoved podvojitev, log; **brez** poslovne logike v JS.

---

## 5. Videz (MASTER §4 + §8)

- Profesionalen namizni slog (zaobljeni gumbi, zavihki, tabele)  
- Reference: QUICK eDAVKI (`QUICK_eDAVKI.pyw`), Fakturiranje v7, Video Transkript  
- Meni **Videz in nastavitve**: ozadje, barve, pisave, radius, gostota, light/dark, reset QUICK teme  
- Ohraniti shranjevanje: zadnja firma, zavihek, filtri, velikost okna, širine stolpcev  

---

## 6. Kaj se NE migrira v isti WebView2 seji glavnega UI

| Funkcija | Ostane | Razlog |
|---|---|---|
| Minimax uvoz host | ločen WebView2 | zaklenjeno 3.0.42/3.0.68 |
| FURS PakR | Chrome | zaklenjeno 2.2.28 |
| eDavki KIR/KPR Od/do | Chrome CDP :9222 | Halcom; ne WebView2 brez DA |

---

## 7. Tveganja migracije UI

- Treeview hierarhija (leto→mesec→dan→ZIP) je kompleksna — potrebuje enakovreden grid.  
- Collapsible + paned sash pozicije — obnovitev stanja.  
- Rumena polja + tooltips — ohraniti UX pravila.  
- Dolg `_safe_call` / messagebox tok — mapirati na toast + modal.  
- `settings_menu.py` je zelo obsežen — migrirati po sklopih (PREDLAGANO faze znotraj 4.0.x).
