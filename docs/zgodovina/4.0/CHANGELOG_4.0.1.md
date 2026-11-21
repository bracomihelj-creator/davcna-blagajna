# CHANGELOG — Davčna Blagajna **4.0.1 → 4.0.2**

**Datum:** 2026-11-16  
**Osnova:** stabilna **3.0.68** (nedotaknjena)  
**Mapa:** `D:\PISARNA\Python\DavčnaBlagajna_4.0.1`

## 4.0.2

- Popravek: `app.js` se ni izvedel (sintaksa) → UI obstal na »Seznam se nalaga…«.
- API klici zdaj pošiljajo `ticket`; boljše napake; Host `localhost` dovoljen.

## Zakaj

Prenova glavnega UI iz Tk/ttk v **HTML/CSS/JS + pywebview + Edge WebView2**, po `MASTER_PROMPT_QUICK_WEBVIEW2.md`, z ohranitvijo poslovne logike 3.0.68.

## Izvedeno

- Nova izolirana mapa `DavčnaBlagajna_4.0.1` (produkcijska 3.0.68 ni prepisana).
- `host.py` — lokalni HTTP + WebView2 okno (vzorec Evidence 8).
- `motor.py` — most na `DavcnaBlagajna.py` / `v2.companies_sql` iz mape 3.0.68.
- UI: firme SQL, obdobje, analiza blagajne + drevo, FURS Blagajna, KIR/KPR CDP, Minimax spletni uvoz (obstoječi WebView2 host), videz/tema, tooltips.
- `DavcnaBlagajna_4.0.1.pyw`, `ZAZENI_4.0.1.bat`, `INSTALL.pyw`.
- Rollback: meni → Odpri stabilno 3.0.68 (Tk).

## Ni spremenjeno

- Datoteke v `D:\PISARNA\Python\DavčnaBlagajna` (razen predhodnih analitičnih `.md`).
- Zaklenjene poti Minimax uvoz 3.0.42 / Knjiženje 3.0.68, FURS 2.2.28, eDavki CDP.
- SQL baze, uporabniški profili Chrome, WebView2 Minimax profil v 3.0.68.

## Omejitve te izdaje

- Celoten `settings_menu` Tk ni 1:1 prenesen (videz + ključni tokovi so).
- Primerjava datotek / KIR uvoz UI / Excel knjižbe gumbi — v 4.0.1 delno prek stabilnega Tk ali naslednjih 4.0.x.
- Glej `TESTI_4.0.1.md`.
