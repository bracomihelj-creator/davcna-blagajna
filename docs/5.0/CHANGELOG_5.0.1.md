# CHANGELOG — Davčna Blagajna 5.0.1

**Datum:** 2026-11-17  
**Osnova:** kopija 3.0.68 (`D:\PISARNA\Python\DavčnaBlagajna`)  
**3.0.68:** nedotaknjena  
**4.0.x:** ni osnova (hibrid Motor + tk_actions)

## Zakaj

4.0 ni bil 1:1, ker je HTML Motor držal svoje stanje in klical AppV21 v drugem procesu. 5.0.1 ima **en proces, en AppV21**. WebView2 je samo LOOK.

## Izvedeno

- Kopija 3.0.68 v `DavčnaBlagajna_5.0.1` (poslovna koda `DavcnaBlagajna.py` ni prepisana).
- `host_webview.py`: pywebview + Edge WebView2, `js_api` kliče **iste** metode AppV21.
- Tk glavno okno `withdraw` + črpalka `update()` (potrebna za `after` / FURS).
- Odložišče: Win32 `CF_UNICODETEXT` (adapter v hostu, ne začasni `tk.Tk()`).
- `tree_view.py`: prikaz iz Tk drevesa / `monthly` — ni drugega stanja.
- HTML QUICK: levi sidebar s 5 pogledi (Blagajna, KIR/KPR, Primerjaj KIRKPR, Primerjaj datoteke, Minimax).
- Zagon: `DavcnaBlagajna.pyw`, `DavcnaBlagajna_5.0.1.pyw`, `ZAZENI_5.0.1.bat`, `INSTALL.pyw`.

## Zaklenjeno (nespremenjeno)

- FURS PakR 2.2.28 v uporabnikovem Chrome
- KIR/KPR eDavki CDP `:9222`
- Minimax spletni uvoz WebView2 3.0.42
- `selenium_auto` = Avtomatika Pripravi+ZIP (Chrome, ni Selenium knjižnica)
- Predloga knjižb: `D:\Trops\MiniMax\KnjizbeInDDV.xlsx`
- `_sync_output_dir_with_root` ob izboru firme

## Česa ni

- `motor.py` / `tk_actions.py` iz 4.0
- sprememb mape 3.0.68
- selitve eDavki v WebView2
