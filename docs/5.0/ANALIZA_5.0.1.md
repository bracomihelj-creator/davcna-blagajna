# ANALIZA — Davčna Blagajna **5.0.1**

**Datum:** 2026-11-17  
**MASTER:** `D:\PISARNA\Python\Navodila_PROMPT\MASTER_PROMPT_QUICK_WEBVIEW2.md`  
**Faza:** A+B (samo `.md`, **brez kode**)  
**Status:** pregled kode — ne runtime klik vseh gumbov

---

## 1. Verzije (PREVERJENO)

| Vir | Vrednost | Status |
|---|---|---|
| `DavčnaBlagajna/verzije/davcna_blagajna_verzije.json` → `current` | **3.0.68** | PREVERJENO |
| `v2/app_v21.py` → `UI_VERSION` | `"3.0"` (serija) | PREVERJENO |
| Naslov AppV21 | `Davčna Blagajna {get_current_patch_version()}` | PREVERJENO |
| Mapa produkcije Tk | `D:\PISARNA\Python\DavčnaBlagajna` | PREVERJENO |
| Zagon 3.0.68 | `DavcnaBlagajna.pyw` / `ZAZENI_DavcnaBlagajna_PY.bat` | PREVERJENO |

### Neskladje / zasedenost major (PREVERJENO)

- MASTER: nova UI generacija = **major + 1 → .0.1**. Iz 3.0.68 bi bila **4.0.1**.
- **4.0.1 že obstaja:** `D:\PISARNA\Python\DavčnaBlagajna_4.0.1` — hibrid HTML + `Motor` + `tk_actions` subprocess (**dvojno stanje**). Ni 1:1 vedenje.
- MASTER točka 2.5: zasedene glavne številke ne prepisuj.

**Predlog NOVA_VERZIJA: 5.0.1** (uporabnik 2026-11-17: DA za 5.0.1 iz 3.0.68).  
**ZAHTEVA ODOBRITEV** tega seznama (faza C).

| Vloga | Verzija | Mapa |
|---|---|---|
| Stabilna osnova (nedotaknjena) | **3.0.68** | `DavčnaBlagajna` |
| Neuporabljati kot osnovo | 4.0.x | `DavčnaBlagajna_4.0.1` |
| Nova UI generacija | **5.0.1** | `DavčnaBlagajna_5.0.1` |

---

## 2. Kaj je šlo narobe v 4.0 (PREVERJENO)

- `DavcnaBlagajna.py` v 4.0 = **ista** datoteka kot 3.0.68 (SHA256 enak).
- Prikaz pa **ni** isti program: `Motor` (svoje drevo/seja) + ob akciji **nov** AppV21 (`tk_actions.py`) + `destroy`.
- Posledice: prazna predloga → Permission denied; FURS brez PakR URL; clipboard Tk; `out_dir` napačne firme.

**5.0.1 tega ne sme ponoviti.**

---

## 3. Osnova za prenovo

- **Kopirati** 3.0.68 (`DavcnaBlagajna.py`, `v2/*`, nastavitvene JSON sheme, predloge).
- **Ne kopirati** 4.0 `motor.py` / `tk_actions.py` / dvojnega stanja.
- SQL EvidencaFirm, Trops mape, Minimax/eDavki profili ostanejo kjer so (skupni podatki).
- 3.0.68 zagon ostane.

---

## 4. Odvisnosti (PREVERJENO iz kode)

| Sklop | Modul / pot | Opomba |
|---|---|---|
| Jedro | `DavcnaBlagajna.py` (`class App`) | analiza, FURS, knjižbe, drevo |
| UI 3.0 | `v2/app_v21.py` + `ui_build_v21.py` | zavihki pogleda |
| SQL firme | `v2/companies_sql.py` | EvidencaFirm |
| Minimax uvoz | `v2/minimax_webview2*.py` | zaklenjeno 3.0.42/3.0.68 — **ločeno okno** |
| FURS PakR | `_open_furs_and_optional_month_location` | Chrome 2.2.28, **ne** WebView2 |
| KIR/KPR eDavki | CDP Chrome :9222 | **ne** seliti v WebView2 |
| Tema | `v2/theme.py`, `v2/settings_menu.py` | Videz |
| Python | 3.10 | Windows |

**Referenca LOOK (pregledana, nespremenjena):**  
`D:\PISARNA\Python\QUICK eDAVKI PRO V1\output\webview2_2_0_1\app\ui\` — levi `aside.sidebar` + `.nav` gumbi (accent `#5968e8`, radius 11, bg `#f4f7fc`).

---

## 5. Tveganja

| Tveganje | Stopnja | Mitigacija |
|---|---|---|
| Ponovitev 4.0 mostu | visoka | **prepoved** subprocess AppV21; en `App` v istem procesu |
| Tk dialogi (OAuth, konti, ZIP, primerjava) | srednja | HTML v istem oknu; datoteke = Win32, ne začasni Tk |
| eDavki v WebView2 | visoka | ostane Chrome (Halcom) |
| Minimax host konflikt | srednja | ostane ločen WebView2 profil kot 3.0.68 |
| 100 % gumbi v prvi izdaji | srednja | inventar + testni seznam; ni tihih izpustov |

---

## 6. Arhitektura 5.0.1 (PREDLAGANO — ZAHTEVA ODOBRITEV)

```
pywebview + Edge WebView2 (LOOK)
        │  js_api / evaluate_js
        ▼
AppV21 / App  (ISTI proces, ISTO stanje kot 3.0.68)
        │
        ├── DavcnaBlagajna.py metode (_analyze, _open_furs_…, _copy_daily_to_knjizbe, …)
        └── v2/* (SQL, nastavitve, Minimax host)
```

- **Ni** drugega `Motor` stanja.
- **Ni** `tk_actions` subprocess.
- Tk glavno okno se **ne** kaže (`withdraw`); LOOK = samo WebView2.
- HTML **ne** računa seštevkov — samo prikaže, kar vrne App.
- Zavihki Blagajna / KIR/KPR / Primerjaj KIRKPR / Primerjaj datoteke / Minimax → **levi sidebar** (QUICK nav), ne zgornji TabBar.
