# CHANGELOG — Davčna Blagajna 5.0.2

**Datum:** 2026-11-17  
**Osnova:** 5.0.1 v isti mapi `DavčnaBlagajna_5.0.1`

## Zakaj

Uporabnik: QUICK levi meni za pet pogledov tu **ni OK**. V 3.0.68 so zavihki zgoraj desno (`Pogled analize:` + TabBar), levo so samo firme.

## Izvedeno

- Odstranjen levi QUICK `.nav` (Blagajna / KIR/KPR / …).
- Pet pogledov spet **zgoraj v desnem panelu**, kot 3.0.68.
- Levi panel = firme SQL + leto/mesec + Ev. + eDavki.
- Poslovna koda `DavcnaBlagajna.py` nespremenjena.

## Nespremenjeno

En proces AppV21, FURS Chrome 2.2.28, KIR CDP :9222, Minimax WebView2 3.0.42, 3.0.68 mapa.
