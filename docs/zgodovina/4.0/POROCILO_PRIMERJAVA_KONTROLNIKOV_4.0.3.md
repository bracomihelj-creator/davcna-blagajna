# Primerjava kontrolnikov — 3.0.68 (Tk) ↔ 4.0.3 (WebView2)

**Datum:** 2026-11-16  
**Preverjeno:** inventar kode + API smoke (boot/firme/izbor/analiza/state).  
**Ni ročno kliknjeno v oknu:** FURS/Chrome, OAuth dialog, Excel/API (zahtevajo UI/poverilnice).

---

## 1. API smoke (PREVERJENO)

| Test | Rezultat |
|---|---|
| Boot 4.0.3 + 5 pogledov | OK |
| SQL firme | OK — **132** |
| Izbor firme → Root `D:\Trops\…\Blagajna` | OK |
| `/api/state` (chk polja) | OK |
| Obdobje 2025-09 | OK |
| Analiza (ta firma/mesec) | OK klic — **0 podatkov** (mapa prazna, ne napaka UI) |
| Neznana akcija zavrnjena | OK |

---

## 2. Checkboxi

| Chk 3.0.68 | 4.0.3 | Povezava | Delovanje |
|---|---|---|---|
| ZIP | `chkZip` | da → state + analyze | **OK** (API) |
| Evidenca Davčnih blagajn | `chkEvidenca` | da → reload | **šibko** — filter skoraj ne zmanjša seznama (polje Ev. v SQL vrstici pogosto manjka) |
| Vrednost Neobd.nabav | `chkNeob` | da → state | **delno** — shrani se; **ne** vpliva na preracun drevesa kot v Tk |
| DDV zavezanec | `chkDdv` | da → state | **OK** shranjevanje; uskladitev ob izboru firme **OK** |
| ✓ označitev meseca/dneva v drevesu | — | **ni** | **MANJKA** |

---

## 3. Gumbi / meniji — matrika

### Legend
- **OK** = UI + handler + backend pot obstaja  
- **MOST** = odpre lastni AppV21 (Tk dialog/metoda) v 4.0 mapi  
- **DELNO** = prikaz/handler, funkcija nepopolna  
- **MANJKA** = ni v 4.0.3 kot v 3.0.68  

| Kontrolnik 3.0.68 | 4.0.3 | Status |
|---|---|---|
| Osveži firme | Osveži / meni | **OK** |
| Išči / ✕ | Išči / ✕ | **OK** |
| eDavki Odpri | Odpri | **MOST** (`open_edavki_link`) |
| Org ID + OAuth… | da | **MOST** |
| Uvozi podatke (blagajna) | Uvozi podatke | **OK** (hitri API analyze) |
| Analiziraj (Tk) | Analiziraj (Tk) | **MOST** (dodatno) |
| FURS Blagajna | FURS Blagajna | **OK** (hitri CDP/pakr klic) |
| Prenos KIR/KPR eDavki | da | **MOST** |
| Prenos KIR/KPR minimax | da | **MOST** |
| Uvozi KIR/KPR | da | **MOST** |
| Evidenca KIR/KPR (CDP Od/do) | da | **OK**/MOST |
| Primerjaj datoteki / prednastavitve | da | **MOST** |
| Shrani Excel / Izvoz excel | da | **MOST** |
| Knjižbe mesec/dan | da | **MOST** |
| Minimax spletni uvoz | da | **MOST** |
| Pošlji mesec/dan API | da | **MOST** |
| Predloga … | da | **MOST** |
| Root … / Out … / ZIP paketi | da | **OK**/MOST |
| Filtriraj / Počisti filter | da | **DELNO** — samo shrani niz, **ne filtrira drevesa** |
| Razširi / Skrči | da | **OK** (HTML drevo) |
| Sprazni | gumb obstaja | **NE DELUJE** — samo status sporočilo |
| Dodaj nov zapis | — | **MANJKA** |
| Konti… / ↻ plačila | da | **MOST** |
| DocumentType / Vrsta prodaje | da | **OK** state |
| Nastavitve (8 zavihkov) | meni → Tk dialog | **MOST** |
| Zgodovina verzij | meni | **MOST** |
| Hitri videz WebView2 | da | **OK** |
| Detail panel izbire | — | **MANJKA** |
| Collapsible −/+ paneli | da | **OK** UI |
| TabBar 5 pogledov | da | **OK** preklop; vsebina primerjav = gumbi, ne vdelano drevo |

---

## 4. Primerjava z 3.0.68 — sklep

| Področje | Enakovrednost |
|---|---|
| Seznam firm + izbor + root | **visoka** |
| Analiza blagajne (API) | **visoka** (isti `build_*` v lastni kopiji) |
| Gumbi FURS / KIR / izvoz / OAuth / nastavitve | **povezani**, večinoma prek **Tk mosta** (AppV21 withdraw) — delujejo, a niso čisti HTML |
| Drevo ✓ / Sprazni / pravi filter / Dodaj zapis / detail | **nizka** — še ni 1:1 |
| Vdelane primerjave KIRKPR | **nizka** — odpre Tk, ni grid v WebView2 |
| Vizualni občutek 3.0.68 | **srednja** — isti sklopi, drugačna gostota |

**Ocena:** kontrolniki so **večinoma prisotni in povezani** (~85 % gumbov), a **polno HTML vedenje** (brez Tk mosta) še ni 100 %. Nekateri chk/gumbi so **navidezno OK**, funkcijsko **DELNO/MANJKA** (filter drevesa, Sprazni, ✓, Dodaj).

---

## 5. Priporočeni naslednji popravki (4.0.4)

1. Sprazni + filter drevesa v `motor`/`app.js` (brez Tk).  
2. ✓ označevanje vrstic + vpliv na izvoz.  
3. chk Neobd. → ponovni izračun agregatov.  
4. chk Evidenca: pravo polje iz SQL (`companies_sql`).  
5. Vdelan rezultat primerjave v HTML.  
6. Odstrani odvisnost od skritih Tk dialogov kjer je mogoče (ostanejo samo kompleksni urejevalniki).
