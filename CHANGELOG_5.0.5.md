# CHANGELOG — Davčna Blagajna 5.0.5

**Osnova:** 5.0.4 v isti mapi `DavčnaBlagajna_5.0.1`

## Vzrok

Kljukica **Evidenca Davčnih blagajn** je šla čez `invoke("_on_evidenca_filter_toggle")`. Status je pokazal `Izvedeno: _on_evidenca_filter_toggle`, seznam firm se ni osvežil v HTML, snapshot pa je desno drevo zamenjal s praznim.

## Spremembe

- Evidenca = samo filter seznama firm (levo), drevo ostane.
- Snapshot brez vozlišč ne pobriše obstoječega drevesa.
- Po analizi se odpre leto/mesec izbranega obdobja.
- Statusi so slovenski stavki, ne ime metode.

3.0.68 ni spremenjena.
