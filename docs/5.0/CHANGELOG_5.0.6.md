# CHANGELOG — Davčna Blagajna 5.0.6

**Osnova:** 5.0.5 v isti mapi `DavčnaBlagajna_5.0.1`  
**3.0.68 ni spremenjena.**

## Vzrok (slika)

Klik na dan v drevesu ni napolnil desnega panela **Izbrano**. Ni bilo gumba **Ponastavi** in **Prenos v minimax**. Ponovni Minimax uvoz je odprl novo WebView2 okno namesto že odprtega.

## Spremembe

- Klik vrstice → panel Izbrano: stolpec + znesek (isti izračun kot 3.0.68).
- **Ponastavi** v panelu Izbrano počisti izbor (analiza ostane).
- **Prenos v minimax**: najprej API (`_send_daily_to_minimax_api`); če API ni mogoč, Excel v WebView2.
- Minimax WebView2: isti profil + IPC kot 3.0.68; če host že teče, nadaljuje v istem oknu (ne nov Edge).

Obstoječi gumbi (Knjižbe, spletni uvoz, FURS, …) ostanejo.
