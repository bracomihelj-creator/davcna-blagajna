# CHANGELOG — Davčna Blagajna 5.0.4

**Osnova:** 5.0.3 v isti mapi `DavčnaBlagajna_5.0.1`  
**LOOK:** HTML / pywebview + Edge WebView2 — **ni Tk okna**.

## Vzrok

5.0.3 je drevo risal iz skritega Tk Treeview. Klik v HTML ni razširil (dnevi se v 3.0.68 naložijo šele ob odprtju). ✓ je imel podvojen stolpec brez handlerja. Ping vsakih 400 ms je zamašil most — zato počasnost in občutek, da »dela Tk«.

## Spremembe

- Drevo LOOK = `monthly` / `daily` / `daily_docs` (HTML ▸/▾).
- ✓ kliče `_tree_checked` v App, prikaz je HTML celica.
- Skrito AppV21 okno: `withdraw` + `-alpha 0` + `-toolwindow` + `Map` → spet skrij.
- Odstranjen interval `ping` 400 ms; `set_fields` ne vrača drevesa.

3.0.68 ni spremenjena.
