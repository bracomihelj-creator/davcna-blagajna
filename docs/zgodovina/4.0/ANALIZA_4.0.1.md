# ANALIZA — Davčna Blagajna · predlagana generacija **4.0.1**

**Faza:** A/B (pregled + poročilo) — **brez sprememb kode**  
**Datum pregleda:** 2026-11-16  
**Vir pravil:** `D:\PISARNA\Python\Navodila_PROMPT\MASTER_PROMPT_QUICK_WEBVIEW2.md`  
**Oznake:** PREVERJENO / PREDLAGANO / NI PREVERJENO / ZAHTEVA ODOBRITEV

---

## 1. Ugotovljene verzije

| Vir | Vrednost | Status |
|---|---|---|
| `verzije/davcna_blagajna_verzije.json` → `current` | **3.0.68** | PREVERJENO |
| `verzije/davcna_blagajna_verzije.json` → `series` | `3.0` | PREVERJENO |
| Zadnji dnevnik | `verzije/Davčna blagajna ver 3.0.68.txt` (2026-10-11) | PREVERJENO |
| Naslov v UI (badge/footer) | `get_current_patch_version()` → **3.0.68** | PREVERJENO |
| `v2/app_v21.py` → `UI_VERSION` | `"3.0"` (serija, ne patch) | PREVERJENO |
| `v2/theme.py` → `APP_TITLE` | `"Davčna Blagajna 2.0"` | PREVERJENO — **neskladje** z 3.0.xx |
| Legacy `DavcnaBlagajna.py` → `APP_TITLE` | `"Blagajna — mesečni seštevki + firme"` (brez patch) | PREVERJENO |
| Arhiv | `Arhiv/2.2.29/` | PREVERJENO |
| Zaklenjeni delujoči poteki (pravila projekta) | Minimax WebView2 uvoz **3.0.42**, motor pywebview+WebView2 **3.0.68**, FURS PakR **2.2.28**, KIR/KPR eDavki Od/do **3.0.44** | PREVERJENO (dokumentacija/pravila) |

### Sklep o verzijah

- **Zadnja stabilna / delovna / uradna current:** **3.0.68** (vsi uradni viri se ujemajo).
- **Osnova za prenovo UI:** trenutna produkcijska koda v `D:\PISARNA\Python\DavčnaBlagajna` (serija 3.0, patch 68).
- **Neskladje:** `V2Theme.APP_TITLE` še vedno kaže »2.0«, medtem ko badge/footer/JSON kažejo 3.0.68 — ob migraciji urediti (PREDLAGANO, ZAHTEVA ODOBRITEV pri izvedbi).

### Predlagana nova generacija

Po MASTER §2 (glavna + 1, začetek `.0.1`):

| | |
|---|---|
| Obstoječa glavna | **3** |
| **NOVA_VERZIJA (PREDLAGANO)** | **4.0.1** |
| Nova mapa (PREDLAGANO) | npr. `D:\PISARNA\Python\DavčnaBlagajna_4.0.1` ali `DavčnaBlagajna\releases\4.0.1` — **ZAHTEVA ODOBRITEV** |
| Stabilna osnova ostane | **3.0.68** nedotaknjena | PREDLAGANO |

---

## 2. Pregledane datoteke / moduli (izbor)

### Zagonske / jedro

- `DavcnaBlagajna.py` — poslovna logika + legacy Tk `App` (velika monolitna datoteka)
- `DavcnaBlagajna.pyw`, `DavcnaBlagajna_v2_1.py` — zagon
- `ZAZENI_DavcnaBlagajna_PY.bat`, `ZAZENI_CHROME_*_DEBUG.bat`, `ZAZENI_BLAGAJNA_EXE.bat`

### UI sloj (Tk / ttk) — kandidat za WebView2 prenovo

- `v2/app.py`, `v2/app_v21.py`
- `v2/ui_build.py`, `v2/ui_build_v21.py`
- `v2/theme.py`, `v2/tooltip.py`, `v2/ui_hints.py`
- `v2/tab_bar.py`, `v2/collapsible.py`, `v2/menubar.py`, `v2/settings_menu.py`
- `v2/version_journal.py`, `v2/version_switch.py`, `v2/version_history_ui.py`
- `v2/date_picker.py`, `v2/filtered_combobox.py`
- Dialogi v `DavcnaBlagajna.py`: `KontiranjeEditorDialog`, `ZipPackagesDialog`, OAuth Toplevel, primerjava Toplevel

### Že WebView2 (ne mešati z UI-prenovo glavnega okna)

- `v2/minimax_webview2.py`, `v2/minimax_webview2_host.py` — **ločeno** pomožno okno za Minimax uvoz/Knjiženje (zaklenjeno 3.0.42 / 3.0.68)
- `v2/browser_inapp.py`, `v2/portal_bridge.py`, `v2/chrome_session_sync.py`

### Podatki / nastavitve

- `v2/companies_sql.py` — SQL EvidencaFirm
- `v2/access_settings.py`, `v2/edavki_links_settings.py`, `v2/file_compare_settings.py`
- `v2/kirkpr_editor.py`, `v2/kirkpr_knjizba_form_layout.py`, `v2/knjizba_form_designer.py`
- `verzije/davcna_blagajna_verzije.json` + 178 vnosov zgodovine
- profili: `data/webview2/...` (ne brisati)

### Obstoječi web_demo (NI enakovreden produkciji)

- `web_demo/` — FastAPI + Jinja2 demo drevesa (`requirements.txt`: fastapi, uvicorn, jinja2)
- **PREVERJENO:** obstaja; **NI PREVERJENO**, da pokriva 100 % funkcij 3.0.68 — ne sme se zamenjati z novo 4.0.1 brez ločene odobritve.

---

## 3. Odvisnosti (pregled)

| Področje | Tehnologija | Status |
|---|---|---|
| UI danes | Tkinter / ttk | PREVERJENO |
| Minimax spletni zajem | **pywebview + Edge WebView2** (trajni profil) | PREVERJENO (zaklenjeno) |
| FURS PakR | Chrome že odprt + hitri vpis Od/do (~2.2.28) | PREVERJENO (pravila) |
| KIR/KPR eDavki | CDP v Chrome `:9222` (ne WebView2 / Halcom) | PREVERJENO (pravila) |
| SQL firme | EvidencaFirm / config | PREVERJENO (modul obstaja) |
| Minimax API | OAuth + IssuedInvoicePosting | PREVERJENO (gumbi/namigi) |
| web_demo | FastAPI (samo demo) | PREVERJENO |

Korenska `requirements.txt` za glavno app **ni** najdena v korenu projekta (samo `web_demo/requirements.txt`) — NI PREVERJENO popoln seznam pip paketov produkcije; ob Fazi D dopolniti inventar iz uvozov.

---

## 4. Vizualne reference (MASTER §4)

| Reference | Pot | Status |
|---|---|---|
| QUICK_eDAVKI_PRO.pyw (kot v promptu) | **ni** datoteke s tem imenom | PREVERJENO — manjka točno ime |
| Nadomestek | `D:\PISARNA\Python\QUICK eDAVKI PRO\QUICK_eDAVKI.pyw` | PREVERJENO — obstaja; **NI PREVERJENO** celoten vizualni audit vsebine |
| Fakturiranje_v7.pyw | `D:\PISARNA\Python\Fakturiranje_7.0.0.01\Fakturiranje_v7.pyw` | PREVERJENO — obstaja |
| Video Transkript Studio | `D:\PISARNA\Python\Transcript\Video_Transkript_GUI.py` | PREVERJENO — obstaja |

**Referenčnih projektov nismo spreminjali.** Za Fazo D: vizualno uskladiti z QUICK eDAVKI + Fakturiranje v7 + Video Transkript, **brez** prenosa njihove poslovne kode.

---

## 5. Tveganja

1. **Monolit `DavcnaBlagajna.py`** — ogromna površina; UI-prenova mora ohraniti Python backend, ne prepisati poslovne logike.  
2. **Dvojni WebView2 konteksti** — že obstaja Minimax host; glavno okno 4.0.1 ne sme pokvariti uvoza 3.0.42/3.0.68.  
3. **Chrome-only poti** (FURS, eDavki Halcom) — **ne** seliti v WebView2 brez ločenega DA.  
4. **Naslov »2.0« v temi** — zmeda uporabnikov ob 4.0.1.  
5. **SQL / nastavitve / WebView2 profili** — Faza D: samo branje/povezava, brez brisanja/ponastavitve.  
6. **web_demo FastAPI** — druga arhitektura (strežnik); MASTER predlaga samostojno WebView2 okno brez nepotrebnega strežnika — PREDLAGANO: pywebview host kot pri Minimax, ne FastAPI kot produkcijski UI.

---

## 6. Kaj je dovoljeno v tej fazi / kaj ne

| Dovoljeno zdaj | Prepovedano do DA |
|---|---|
| Analitični `.md` (ta dokument + 3 sorodni) | Spreminjanje `.py` / `.pyw` / installerja |
| Predlog verzije **4.0.1** | Ustvarjanje nove mape / kopiranje kode |
| ASK za odobritev | Poseg v baze, profile, Chrome, WebView2 |

---

## 7. Naslednji korak

Glej `PREDLOG_POPRAVKOV_4.0.1.md` in vprašanje za odobritev. **Kode se ne spreminja, dokler uporabnik ne potrdi seznama.**
