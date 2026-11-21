# POROČILO — zakaj 4.0.2 nima skoraj celotnega vmesnika 3.0.68

**Datum:** 2026-11-16  
**Primerjava:** stabilna Tk **3.0.68** (`DavčnaBlagajna` + `v2/ui_build*.py`) ↔ WebView2 **4.0.2** (`DavčnaBlagajna_4.0.1/ui/*`)  
**MASTER:** `MASTER_PROMPT_QUICK_WEBVIEW2.md` — zahteva **100 % funkcionalno enakovrednost** in inventar **vseh** kontrolnikov pred izvedbo.

---

## 1. Kratek sklep

**4.0.2 ni migracija UI — je tanek prototip / lupina.**  
Približno **10–15 %** glavnega vmesnika je nakazano; **večina kontrolnikov, panelov, dialogov in tokov iz 3.0.68 manjka**.  
To **ni** skladno z MASTER §5–§6 niti z lastnim predlogom v `PREDLOG_POPRAVKOV_4.0.1.md` (točka »ohranitev vseh poslovnih tokov«).

Vzrok ni »tehnična nemogočnost«, temveč **napačen obseg izvedbe**: namesto 1:1 HTML preslikave inventarja je bil narejen minimalni ekran z nekaj gumbi, ki kličejo backend.

---

## 2. Kaj 3.0.68 dejansko ima (PREVERJENO iz kode)

### 2.1 Glavna postavitev v2.1

| Območje | Vsebina |
|---|---|
| Header | naslov, badge verzije, Minimax status, izbrana firma |
| Levo | SQL firme, iskanje, ✕, Osveži, vir, Ev. check, eDavki Odpri, Treeview firm, obdobje |
| Desno zgoraj | Minimax Org ID / OAuth (collapsible) |
| TabBar pogled | **Blagajna · KIR/KPR · Primerjaj KIRKPR · Primerjaj datoteke · Minimax** |
| KIR/KPR | TabBar KIR/KPR + eDavki/Minimax + Prenos/Uvozi |
| Izvoz | Excel & knjižbe / API (collapsible) + gumbi |
| Drevo | filter, Neobd., Dodaj, Razširi/Skrči/Sprazni, ✓ označevanje, podrobnosti izbire |
| Spodaj | Notebook: **Pot & datoteke**, **Minimax nastavitve** (+ Excel/API v toku) |
| Meni | Verzija (zgodovina/preklop) + **obsežen Nastavitve** |

### 2.2 Gumbi / kontrolniki (izbor, ne popoln seznam)

**Blagajna / drevo:** Uvozi podatke, FURS Blagajna, Filtriraj, Počisti filter, Neobd.nabav, Dodaj nov zapis, Razširi, Skrči, Sprazni, ✓ vrstice.  

**KIR/KPR:** Prenos eDavki, Prenos Minimax, Uvozi podatke (×2 konteksta), Analiziraj KIR/KPR.  

**Primerjave:** Primerjaj datoteki (ročno), Primerjaj (prednastavitve), seznam presetov, primerjalno drevo.  

**Minimax / izvoz:** OAuth…, DocumentType, DDV zavezanec, Način plačila + Konti… + ↻, Vrsta prodaje + Konti…, Shrani Excel, Izvoz excel, Knjižbe po mesecih/dnevih, Minimax spletni uvoz, Predloga …, Pošlji mesec/dan API.  

**Pot:** Root …, ZIP, ZIP paketi…, Shranjevanje …, Datoteka, Sheet, CSV.  

**Dialogi:** OAuth, Kontiranje, ZIP paketi, Primerjava razlike, Zgodovina verzij, Nastavitve (8+ zavihkov).  

**Nastavitve (`settings_menu.py`):** Tema, Videz in postavitev, Barve/fonti, Širine, Obrobe, Dostop eDavki/Minimax, Povezave SQL, Vedenje, Primerjave datotek, Minimax knjižba forma, …

### 2.3 Okna

W1 glavno · W2 primerjava · W3 kontiranje · W4 ZIP · W5 OAuth · W6 Minimax WebView2 host · W7 nastavitve · W8 zgodovina verzij.

---

## 3. Kaj 4.0.2 dejansko ima (PREVERJENO iz `ui/index.html`)

| Element | Je |
|---|---|
| Header + badge | da (poenostavljeno) |
| Meni Datoteka / Nastavitve | da — **3 + 1** ukaz (ne Verzija, ne polne nastavitve) |
| Seznam firm + iskanje + Leto/Mesec | da — **brez** Ev., eDavki Odpri, ✕, stolpcev Ev./vir |
| Gumbi | Analiziraj, FURS, KIR/KPR CDP, Minimax uvoz, Root …, ZIP |
| Drevo rezultatov | osnovna tabela + Razširi/Skrči |
| Videz dialog | tema / accent / radius / font — **mini**, ne `settings_menu` |
| TabBar pogledi | v JS narisani — **vsebina pogledov KIR/primerjaj/… skoraj prazna** |

**Štetje (orientacijsko):**  
- 3.0.68 glavni UI: **60+** gumbov/polj/checkboxov + drevesa + notebook + dialogi.  
- 4.0.2: **~15** kontrolnikov na glavnem ekranu + 1 mini dialog.

---

## 4. Matrika manjkajočega (glavno)

| Skupina 3.0.68 | V 4.0.2 | Status |
|---|---|---|
| Pogled KIR/KPR (Prenos eDavki/Minimax, Uvozi, KIR/KPR tab) | ne | MANJKA |
| Pogled Primerjaj KIRKPR | ne | MANJKA |
| Pogled Primerjaj datoteke + presets | ne | MANJKA |
| Pogled Minimax (namesto spodnjih nastavitev) | ne | MANJKA |
| Panel Org ID / OAuth… | ne | MANJKA |
| Spodnji panel Pot & datoteke (Root/Out/Sheet/CSV/ZIP paketi) | le Root + ZIP | VEČINA MANJKA |
| Minimax nastavitve (DocumentType, DDV, plačila, prodaja, Konti) | ne | MANJKA |
| Excel & knjižbe (4+ gumbov + predloga) | ne | MANJKA |
| API pošiljanje (mesec/dan) | ne | MANJKA |
| Filter drevesa / Neobd. / Sprazni / Dodaj / ✓ označevanje | ne | MANJKA |
| Podrobnosti izbire (detail tree) | ne | MANJKA |
| Collapsible paneli −/+ | ne | MANJKA |
| Meni Verzija / zgodovina | ne | MANJKA |
| Nastavitve 8 zavihkov | mini videz | MANJKA |
| Dialogi OAuth, Konti, ZIP paketi, primerjava | ne | MANJKA |
| Stolpci firm (Ev., DURS, …) kot v Tk | le Zšt/Naziv/Davčna/Org | OKRNJENO |

---

## 5. Zakaj je tako — vzroki (ne izgovori)

### 5.1 Kršitev MASTER postopka pri izvedbi

MASTER zahteva: inventar → `.md` → **izrecna odobritev seznama** → šele nato **polna** migracija.  

Analiza (`FUNKCIONALNOSTI_4.0.1.md`, `UI_MIGRACIJA_4.0.1.md`) je popisala skoraj celoten UI.  
Ob izvedbi pa je bil narejen **samo »happy path« lupine** (firme + analiza + 3 zunanja dejanja), ne 1:1 preslikava.

V `PREDLOG` je bilo celo odprto vprašanje »celoten settings_menu ali kasneje« — to **ni** dovoljevalo izpustiti KIR, izvoz, notebook, dialoge.

### 5.2 Napačna razlaga »nadaljuj / avtomatsko potrjuj«

Namesto postopne, inventar-vodene migracije (kot Evidence 8 z bogatim `index.html` + `motor` akcijami) je bila izbrana **hitra skeleton** arhitektura: malo HTML + nekaj `/api/action`.

### 5.3 Tehnična izbira: most, ne UI kopija

`motor.py` uvaža 3.0.68 backend — **poslovna logika obstaja**, a **ni povezana na UI**, ker HTML nima kontrolnikov, ki bi te metode klicali.  
Primer: knjižbe, API, OAuth, filter, primerjave — v Pythonu so, v WebView2 UI jih ni.

### 5.4 Obseg dela

Polna enakovrednost = desetine panelov + dialogi + `settings_menu` (~1800 vrstic) + primerjalna drevesa.  
To **ni bilo izvedeno**; dokumentacija v CHANGELOG/TESTI je že priznala omejitve, a izdelek je bil predstavljen kot »4.0.1 generacija«, kar je zavajajoče glede na MASTER.

### 5.5 Primerjava z Evidence 8 (referenca v istem okolju)

Evidence 8 ima bogat HTML (meniji, zavihki, obrazci, šifrant, …) + širok `/api/action`.  
Davčna 4.0.2 je **red velikosti manjša** — zato »niti približno« ni kot 3.0.68.

---

## 6. Kaj MASTER zahteva, česar 4.0.2 ne izpolnjuje

| MASTER | 4.0.2 |
|---|---|
| §5 inventar + preslikava **vsakega** kontrolnika | delni inventar v `.md`, UI ne sledi |
| §6 100 % funkcionalna enakovrednost | ne |
| §8 celovit meni Videz in nastavitve | mini dialog |
| Brez praznih / navideznih funkcij | zavihki pogledov brez vsebine |
| Resnično delujoča app, ne prototip | **prototip** |

---

## 7. Priporočilo (samo poročilo — brez kode)

1. **3.0.68 ostane delovna** aplikacija (že je).  
2. **4.0.2** obravnavati kot **tehnični proof-of-concept** (WebView2 host + SQL firme + analiza), ne kot zamenjavo.  
3. Za pravo generacijo: nova verzija (npr. **4.1.1** ali **4.0.3** po dogovoru) z **obveznim** korakom — HTML 1:1 po `FUNKCIONALNOSTI` / `UI_MIGRACIJA`, panel za panelom, z DA po vsakem večjem sklopu.  
4. Pred naslednjo izvedbo: eksplicitno potrditi vrstni red sklopov, npr.  
   A) glavni layout + zavihki + spodnji notebook →  
   B) KIR/KPR →  
   C) izvoz Excel/API →  
   D) primerjave →  
   E) dialogi →  
   F) settings_menu.

---

## 8. Odgovor na vprašanje »zakaj manjka ogromno«

Ker **ni bil zgrajen vmesnik 3.0.68 v HTML**, ampak **nova, močno okrnjena lupina**. Backend 3.0.68 je na voljo; manjka **preslikava kontrolnikov in dogodkov**. To je produktna / izvedbena napaka glede na MASTER, ne omejitev WebView2.
