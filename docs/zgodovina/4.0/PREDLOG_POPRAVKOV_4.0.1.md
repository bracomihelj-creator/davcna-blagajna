# PREDLOG_POPRAVKOV — Davčna Blagajna **4.0.1**

**Faza:** D/E — **IZVEDENO** 2026-11-16 (uporabnik: nadaljuj + avtomatsko potrjuj)  
**Mapa:** `D:\PISARNA\Python\DavčnaBlagajna_4.0.1`

---

## 1. Predlagana različica in lokacija

| Postavka | Vrednost | Status |
|---|---|---|
| Zadnja stabilna | **3.0.68** | PREVERJENO |
| Nova generacija UI | **4.0.1** | PREDLAGANO |
| Nova mapa | `D:\PISARNA\Python\DavčnaBlagajna_4.0.1` | PREDLAGANO — ZAHTEVA ODOBRITEV |
| Zagonska datoteka | `DavcnaBlagajna_4.0.1.pyw` | PREDLAGANO |
| Installer | `INSTALL.pyw` (WebView2 Runtime check, backup, ne prepiše 3.0.68) | PREDLAGANO |
| Rollback | zagon obstoječe 3.0.68 iz trenutne mape | PREDLAGANO |

Alternativa mape (če želite znotraj projekta): `DavčnaBlagajna\gen_4.0.1\` — ZAHTEVA ODOBRITEV.

---

## 2. Obseg sprememb (po odobritvi — Faza D)

### Vključeno (PREDLAGANO)

1. Nova izolirana mapa + varnostna kopija izvorne 3.0.68.  
2. HTML/CSS/JS frontend za glavni UI (preslikava iz `UI_MIGRACIJA_4.0.1.md`).  
3. Python WebView2 host + dvosmerni bridge na obstoječe metode `DavcnaBlagajna.py` / `v2/*`.  
4. Ohranitev vseh poslovnih tokov iz `FUNKCIONALNOSTI_4.0.1.md`.  
5. Meni »Videz in nastavitve« (MASTER §8).  
6. Tooltips / rumena pasica po pravilu UI namigov.  
7. Popravek neskladnega `APP_TITLE` »2.0« → oznaka 4.0.1 v novi generaciji.  
8. `.pyw` + `INSTALL.pyw` + dokumentacija (`CHANGELOG_4.0.1.md`, `TESTI_4.0.1.md` po izvedbi).  
9. Verzioniranje: nova serija `4.0` (ločeno od `3.0` JSON, da 3.0.68 ostane).

### Izključeno / nedotaknjeno (PREDLAGANO)

- Produkcijska mapa **3.0.68** (brez in-place prepisovanja).  
- SQL baze, uporabniške nastavitve, WebView2 Minimax profil, Chrome profili.  
- Zaklenjene poti: Minimax uvoz 3.0.42, motor Knjiženje 3.0.68, FURS 2.2.28, eDavki CDP.  
- Referenčni projekti (QUICK eDAVKI, Fakturiranje, Transcript).  
- Zamenjava Chrome Bridge / Playwright za FURS/eDavki.  
- Prenos poslovne logike v JavaScript.

### Odprto za ločeno DA

- Ali uporabiti FastAPI/`web_demo` kot vmesni sloj ali **samo** pywebview (priporočilo: samo pywebview).  
- Ali 4.0.1 v prvi izdaji migrira **celoten** `settings_menu` ali najprej jedro + nastavitve v 4.0.2+.  
- Točna pot nove mape.

---

## 3. Načrt po datotekah (PREDLAGANO)

| Akcija | Pot (v novi mapi) |
|---|---|
| Kopija | `DavcnaBlagajna.py`, `v2/*` (backend) |
| Novo | `ui_webview2/` — `index.html`, `app.js`, `styles.css`, komponente |
| Novo | `v2/main_webview2_host.py` — host glavnega okna |
| Novo | `v2/ui_bridge.py` — dovoljeni API klici |
| Novo | `DavcnaBlagajna_4.0.1.pyw` |
| Novo | `INSTALL.pyw` |
| Prilagodi | theme/version badge → 4.0.1 (samo v novi generaciji) |
| Ne spreminjaj | `v2/minimax_webview2_host.py` potek uvoza (razen mosta iz novega UI gumba) |

---

## 4. Vpliv na funkcije

| Funkcija | Pričakovan vpliv |
|---|---|
| Analiza blagajne / KIR/KPR | Enaki rezultati; spremenjen samo prikaz |
| Excel / knjižbe / API | Enako |
| Minimax spletni uvoz | Klic obstoječega controllerja |
| FURS / eDavki | Enaki Chrome tokovi |
| Nastavitve/tema | Nov UI; shranjevanje združljivo ali migracijski adapter |
| web_demo | Ostane; ni produkcijski zamenjevalec |

---

## 5. Rollback

1. Zapri 4.0.1.  
2. Zaženi `DavcnaBlagajna.pyw` / `ZAZENI_DavcnaBlagajna_PY.bat` iz mape 3.0.68.  
3. Podatki (SQL, nastavitve, profili) ostanejo — 4.0.1 jih ne sme uničiti.  
4. Po potrebi odstrani samo mapo `DavčnaBlagajna_4.0.1`.

---

## 6. Testni kriteriji (po izvedbi — Faza E)

- [ ] Zagon / zapiranje `.pyw`  
- [ ] Izbor firme, obdobje, analiza blagajne — primerjava drevesa s 3.0.68  
- [ ] KIR/KPR uvoz eDavki + Minimax  
- [ ] FURS Blagajna Od/do v odprtem Chrome  
- [ ] Excel, knjižbe, API (če so poverilnice)  
- [ ] Minimax spletni uvoz (WebView2)  
- [ ] Primerjava datotek  
- [ ] OAuth / Konti / ZIP dialogi  
- [ ] Tema light/dark + ponastavitev  
- [ ] Tooltips na gumbih  
- [ ] 3.0.68 še vedno deluje nespremenjeno  

**Ne trditi 100 % uspeha, dokler testi niso dejansko izvedeni.**

---

## 7. Varnostne kopije (ob DA)

Pred kopiranjem kode:

1. Kopija trenutne mape ali git stash/commit **samo če uporabnik zahteva commit**.  
2. Ne briši `Arhiv/2.2.29`, `verzije/`, `data/webview2/`.

---

## 8. Vprašanje za odobritev (Faza C)

Predlagam:

- novo verzijo **4.0.1**,  
- novo mapo `D:\PISARNA\Python\DavčnaBlagajna_4.0.1`,  
- UI = HTML/CSS/JS v **pywebview + Edge WebView2**,  
- Python backend = obstoječa logika 3.0.68,  
- brez posega v zaklenjene Minimax/FURS/eDavki poteke,  
- obseg kot v §2 tega dokumenta.

**Ali potrjuješ navedeni seznam sprememb za predlagano različico 4.0.1?**

Odgovori npr.:

- **DA** — izvedi Fazo D po tem predlogu  
- **DA z popravki:** … (mapa / obseg nastavitev / FastAPI da-ne)  
- **NE** — ostani pri analizi
