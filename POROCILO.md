# POROČILO — Davčna Blagajna 5.1 (uskladitev treh verzij)

**Datum:** 2026-11-21 · **Mapa:** `D:\PISARNA\Python\DavčnaBlagajna_5.1` (preimenovana iz `DavčnaBlagajna_5.0.1`)
**Verzija:** 5.1.00 · **Izhodišče:** commit `19649d5` (stanje 5.0.14)
**Viri (samo branje, niso spremenjeni):** `DavčnaBlagajna` (Tk 3.0.68), `DavčnaBlagajna_4.0.1` (WebView2 4.0.7)

## 1. Ključna ugotovitev

Poslovna logika je v vseh treh mapah **enaka**: `DavcnaBlagajna.py` (25.972 vrstic) je byte-identičen,
`v2/` prav tako (razen oznak verzije in Minimax WebView2 seje). Zato so vsi popravki 3.0.14–3.0.68
(nikoli commitani v 3.0) **že vsebovani v 5.1**. Iz 3.0 in 4.0 ni bilo treba prenesti nobenega izračuna.
`DavcnaBlagajna.py` v tej uskladitvi **ni bil spremenjen** (git diff 19649d5..HEAD je prazen).

## 2. Kaj je bilo zajeto in od kod

### Iz 3.0.68 (`DavčnaBlagajna`)
- Zapis necommitanega dela 3.0.14–3.0.68: `docs/zgodovina/3.0/` (2 patcha + README s stanjem gita in seznamom datotek). Samo evidenca.
- Cursor pravila: `edavki-furs-pakr-fast.mdc` (FURS PakR 2.2.28), `ne-spreminjaj-delujoce.mdc` (zaklenjene poti), `pywebview-webview2-motor.mdc` (Minimax WebView2 3.0.42/3.0.68), `ui-namigi.mdc` (rumeni namigi).
- Minimax WebView2 seja: `data\webview2\minimax_uvoz_profile` (641 datotek, 88,8 MB) kopirana v 5.1. Vir je bil samo prebran. Prejšnji 5.0 profil je ohranjen kot `minimax_uvoz_profile_5.0_stari_20261121`. Ni v gitu.
- Dnevnik verzij 2.1.01–3.0.68 (168 TXT + JSON), predloga `blagajna_minimax_settings.example.json`, pomožni skripti (Chrome debug, `_ensure_davcna_pyw.py`) — bili so že v 5.1 (preverjeno, nič ne manjka).

### Iz 4.0.7 (`DavčnaBlagajna_4.0.1`)
- Dokumenti: CHANGELOG 4.0.1–4.0.7, TESTI 4.0.1/4.0.4, POROČILA 4.0.2–4.0.4, README 4.0.1 → `docs/zgodovina/4.0/`.
- Cursor pravila 4.0 (100 % vedenje, samostojna, webview2) → `docs/zgodovina/4.0/cursor_rules/` (znanje; bistvo prenešeno v pravilo 5.1).
- **Meni Datoteka → Odpri Tk 3.0.68** (rollback; iz `motor.open_legacy_308_tk`): `Bridge.open_legacy_tk` zažene nespremenjeno 3.0.68 iz njene mape (`pyw -3.10 DavcnaBlagajna.pyw`). Pot je mogoče spremeniti z `DAVCNA_BLAGAJNA_LEGACY_ROOT`.
- **Gostota** v Videzu (kompaktno / normalno / prostorno; v 4.0 je bila samo shranjena, v 5.1 dejansko spremeni višino gumbov in polj).
- **Ni prenešeno:** `host.py`, `motor.py`, `tk_actions.py`, `tree_data*.py` (HTTP strežnik + ločen proces za vsako akcijo; v 5.1 nadomešča `host_webview.py`, en proces). `session_state.json` ni potreben — AppV21 že hrani zadnjo firmo, obdobje, pogled in poti v `blagajna_ui_settings.json`.

## 3. Kaj je bilo premaknjeno / odstranjeno

| Kaj | Kam | Zakaj |
|---|---|---|
| ANALIZA / FUNKCIONALNOSTI / PREDLOG / UI_MIGRACIJA 5.0.1, CHANGELOG 5.0.x, TESTI 5.0.x | `docs/5.0/` | urejen koren |
| *_4.0.1.md analize (kopije iz 3.0) | `docs/zgodovina/4.0/` | zgodovina |
| `web_demo/`, `ZAZENI_BLAGAJNA_EXE.bat`, `ZGRADI_DAVCNA_BLAGAJNA.bat`, `Zagon_davcnaBlagajna_V3.bat` | `tools/legacy/` | 5.1 jih ne uporablja (EXE, V3, Flask demo) |
| `ZAZENI_5.0.1.bat`, `DavcnaBlagajna_5.0.14.pyw` | → `ZAZENI_5.1.bat`, `DavcnaBlagajna_5.1.pyw` | ime verzije |
| pravilo `davcna-blagajna-5.0.1-webview2.mdc` | → `davcna-blagajna-5.1-webview2.mdc` (prepisano) | 5.1 |
| trda pot na Minimax sejo v mapi 3.0.68 (`v2/minimax_webview2.py`) | odstranjena; seja relativno na 5.1 | neodvisnost od 3.0 |

Ostalo zunaj gita (na disku nedotaknjeno): `data/`, `dist/` (EXE + kopija gesel), `__pycache__/`, `blagajna_error.log`,
`blagajna_minimax_settings.json`, `blagajna_ui_settings.json`, `blagajna_v2_access.json`, `DavcnaBlagajna_evidenca.json`, `*.spec`.
Ni preneseno iz 3.0: `Arhiv/` (2.2.29), `data/_napaka_frames` (zaslonske slike), pravilo `evidenca-8-webview.mdc` (velja za drugo aplikacijo).
`.gitignore` je dopolnjen (arhivi, `*.lnk`, `*.zip`, `*.bak`, certifikati `*.pfx/*.p12`, `*settings.local.json`, `blagajna_minimax_settings*.json`).

## 4. Spremembe kode (brez poslovne logike)

- `host_webview.py`: verzija 5.1.00, `LEGACY_TK_ROOT` + `Bridge.open_legacy_tk`, `density` v privzetem videzu.
- `ui/index.html`, `ui/app.js`, `ui/app.css`: meni »Odpri Tk 3.0.68 …«, izbira Gostota, oznake 5.1.00.
- `v2/minimax_webview2.py`: profil in IPC Minimax seje = `data/webview2/…` v mapi 5.1 (prej 3.0.68). ⚠️ Integracija Minimax (pot seje), ne izračun.
- `INSTALL.pyw`: ime 5.1, bližnjica `DavcnaBlagajna_5.1.lnk`, `ensure_minimax_session()` (če seje ni, jo enkrat kopira iz 3.0.68).
- `v2/version_journal.py` serija 5.1, `v2/app_v21.py` UI_VERSION 5.1, dnevnik verzij + `verzije/Davčna blagajna ver 5.1.00.txt`.

## 5. Preverjanje (statično, aplikacija ni bila zagnana)

- `py_compile` (izhod v %TEMP%) za 10 datotek, vključno z `DavcnaBlagajna.py`: OK.
- Uvoz `host_webview`, `v2.version_journal`, `v2.minimax_webview2` brez oken in omrežja: OK. Verzija 5.1.00, serija 5.1, naslednja bi bila 5.1.01.
- `node --check ui/app.js`: OK. HTML: `<div>` 84/84 uravnoteženih.
- `git diff 19649d5..HEAD -- DavcnaBlagajna.py`: prazen (poslovna logika nespremenjena).
- Skrivnosti: v gitu jih ni (preverjena zgodovina; `blagajna_edavki_links.json` nima gesla, primer nastavitev ima prazna polja).
- **Ročno preveri:** zagon `ZAZENI_5.1.bat`; naslov 5.1.00; Minimax spletni uvoz brez ponovne prijave; meni Datoteka → Odpri Tk 3.0.68; Videz → Gostota.

## 6. Znane težave (ostajajo) in priporočeni popravki

1. **Minimax API `401 Unauthorized`** (accounts, vatrates, issuedinvoicepostings/pay) v dnevnikih 3.0 in 5.0. Verjetno potekel OAuth/geslo. → Preveri poverilnice v Nastavitve → OAuth; po potrebi nov client secret. (Ne spreminja izračunov.)
2. **`open_knjizenje` timeout** v WebView2 (3×, »ukaz se v X s ni zaključil«). → Diagnostika `v2/minimax_webview2*.py` (časovna meja, prevzem obstoječega okna); ⚠️ Minimax knjiženje — samo z DA.
3. **Manjka QUICK_eNDM `browser_bridge`** (`v2/portal_bridge.py` → `D:\PISARNA\Python\QUICK_eNDM`) — najpogostejša napaka v vseh treh dnevnikih. → Namesti/poveži QUICK_eNDM ali gumb Plače iz Minimax tiho onemogoči, če moduli manjkajo.
4. **Tk dialogi še ostajajo** (skrita AppV21): OAuth, ZIP paketi, kontiranje plačil/prihodkov, nov zapis KIR/KPR. → Postopno v HTML.
5. **Ni avtomatskih testov.** → pytest: uvoz modulov, `tree_view.build_*` na vzorčnih podatkih, `version_journal`, Bridge allow-list (samo branje).
6. **Gesla Minimax v navadnem JSON** (`blagajna_minimax_settings.json`, tudi kopija v `dist/`). V gitu niso. → Prenos v Windows Credential Manager (keyring); kopijo v `dist/` po potrditvi pobrisati.
7. **Dnevnik napak** brez rotacije (`blagajna_error.log` 1,07 MB, večinoma debug). → Rotacija 1 MB × 3.
8. **Namizna bližnjica** `DavcnaBlagajna_5.0.1.lnk` (če obstaja) kaže na staro mapo. → Ponovno zaženi `INSTALL.pyw` (ustvari `DavcnaBlagajna_5.1.lnk`; ob tem preveri tudi pywebview).
9. `v2/version_switch.py` kaže na `Arhiv/2.2.29`, ki ga v 5.1 ni (meni za preklop na 2.2.29 v Tk ne bo deloval). Mrtva pot, ni v LOOK.
10. Trde poti v jedru (`D:\Trops\...`, `D:\PISARNA\Python\Podatki\...`, `FURS\edavki_halcom_win.py`, `Chrome_add\...`) — namenoma nespremenjene (poslovna datoteka).
11. ~~Ni oddaljenega repozitorija.~~ **Urejeno:** zaseben GitHub repozitorij `bracomihelj-creator/davcna-blagajna` (veja master).
12. ~~Proces Python ostane v ozadju po zaprtju okna~~ (pywebview 6.2.1 ne vrne iz `webview.start()`). **Popravljeno** v `host_webview.py`: ob dogodku `closed` se shrani `blagajna_ui_settings.json`, ustavi Tk zanka, splakne dnevnik, nato varnostni `os._exit(0)` po 3 s. Preizkušeno: proces izgine v ~6 s (gumb X in meni Zapri).

## 7. Commiti uskladitve

Glej `git log --oneline 19649d5..HEAD`.