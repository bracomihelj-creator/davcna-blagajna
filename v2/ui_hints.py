"""Besedila namigov (tooltip) za gumbe v v2 / v2.1 vmesniku."""

# —— Orodna vrstica ——
ANALYZE_BLAGAJNA = (
    "Uvozi podatke davčne blagajne za izbrano leto/mesec.\n"
    "Prebere CSV/ZIP iz mape firme (YYYY-MM) in napolni dreveso rezultatov."
)
IMPORT_BLAGAJNA = ANALYZE_BLAGAJNA
ANALYZE_KIRKPR = (
    "Analizira KIR/KPR za izbrano leto/mesec (v2.0 orodna vrstica).\n"
    "V v2.1 uporabi zavihek KIR/KPR in gumb «Uvozi podatke»."
)
IMPORT_KIRKPR = (
    "Uvozi KIR in KPR iz iste datoteke (DDV_KIR_KPR):\n"
    "• eDavki — Evidenca KIRKPR_YYYYMM.zip iz mape Blagajna\n"
    "• Minimax — KIRKPR iz mape DDV (.zip ali .xml)\n"
    "Zavihek KIR / KPR samo preklopi pogled med knjigama."
)
COMPARE_FILES = (
    "Primerja dve datoteki (npr. KIR evidence ↔ davčna blagajna).\n"
    "Izberi točno 2 datoteki; prikaže razlike po mesecih, dnevih in dokumentih."
)
FURS_BLAGAJNA = (
    "V že odprtem Chrome odpre nov zavihek DPR-PakR in v ~2 s vpiše Od/do\n"
    "(enako kot ver 2.2.20). Izberi firmo in leto/mesec pred klikom."
)
FURS_KIRKPR = (
    "Prenos KIR/KPR eDavki v že odprtem Chrome (CDP :9222) — brez Selenium.\n"
    "Nov zavihek + Obdobje od/do (kot MRN/FURS) + Išči.\n"
    "Datum = prvi/zadnji dan meseca (09 → 01.09.–30.09., 10 → 01.10.–31.10.)."
)
EVIDENCA_KIRKPR = FURS_KIRKPR
OAUTH = (
    "Odpre nastavitve OAuth za Minimax API\n"
    "(Client ID, Client Secret, token, API URL)."
)
MINIMAX_WEB_UVOZ = (
    "Odpre samostojno WebView2 okno (brez vtičnikov).\n"
    "Sejo vzame iz aktivnega Minimax Chrome ali iz shranjenega spomina\n"
    "(ob zagonu app se Minimax/eDavki/eVEM/AJPES shranijo iz Chrome).\n"
    "Pot: Moje org → klik naziva → Uvoz → KN → radio → IR/datum/opis → Excel → Uvozi."
)

# —— v2.1 zavihek Davčna blagajna ——
# (isti ANALYZE_BLAGAJNA, FURS_BLAGAJNA)

# —— v2.1 zavihek KIR/KPR ——
PRENOS_EDAVKI = (
    "Prenos KIR/KPR eDavki: nov zavihek v Chrome (:9222) + CDP Od/do + Išči.\n"
    "Brez Selenium; eDavki ostane v Chrome (Halcom), ne v WebView2.\n"
    "Shrani ZIP: Evidenca eDavki KIRKPR_YYYYMM.zip v mapi Blagajna.\n"
    "Pravila: Nastavitve → Dostop eDavki, Minimax."
)
PRENOS_MINIMAX = (
    "Odpre povezavo iz Nastavitve → Dostop eDavki, Minimax\n"
    "(privzeto ObracunDDV.aspx) v novem zavihku Chrome.\n"
    "Shrani ZIP/XML v Trops\\{Žšt}\\DDV."
)
IZVOZ_EDAVKI = (
    "Poišče že preneseni ZIP iz eDavkov (Evidenca eDavki KIRKPR_YYYYMM.zip)\n"
    "v mapi Blagajna in odpre datoteko v Raziskovalcu.\n"
    "Ne prenaša — samo locira obstoječi izvoz."
)
IZVOZ_MINIMAX = (
    "Poišče Minimax izvoz KIR/KPR v Trops\\{Žit}\\DDV\n"
    "(Evidenca minimax KIRKPR_YYYYMM.xml) in odpre datoteko.\n"
    "Če obstaja tudi eDavki ZIP, ponudi primerjavo eDavki ↔ Minimax."
)

# —— Dreveso rezultatov ——
FILTER_APPLY = (
    "Filtrira dokumente v drevesu po delnem nizu\n"
    "(Zap. št. / P3). Podpora za * (npr. blag* / *97846)."
)
FILTER_CLEAR = "Počisti filter dokumentov in prikaže vse vrstice."
SHOW_NEOBD = (
    "Vključi neobdavčljive nabave (P10) v «Vrednost računa»\n"
    "pri KIR analizi in primerjavi."
)
TREE_EXPAND = "Razširi vse veje drevesa rezultatov."
TREE_COLLAPSE = "Skrči vse veje drevesa (le leti/meseci)."
PANEL_TREE_COLLAPSE = (
    "Skrči panel drevesa (−).\n"
    "Skrije tabelo rezultatov; podrobnosti in spodnji trak ostanejo."
)
PANEL_TREE_EXPAND = (
    "Razširi panel drevesa (+).\n"
    "Prikaže tabelo leti → meseci → dnevi → ZIP."
)
PANEL_DETAIL_COLLAPSE = (
    "Skrči podrobnosti izbire (−).\n"
    "Več prostora za drevo rezultatov."
)
PANEL_DETAIL_EXPAND = (
    "Razširi podrobnosti izbire (+).\n"
    "Prikaže stolpce in zneske izbrane vrstice."
)
TREE_CLEAR_ROW = (
    "Izbriše označeno vrstico iz drevesa (tudi tipka Delete).\n"
    "Uporabno za ročno odstranitev dneva/meseca iz pogleda."
)

# —— Firme ——
COMPANY_SEARCH_CLEAR = "Počisti iskalno polje za seznam firm."
PICK_DURS = "Excel DURSanalitika — samo v arhivu 2.2.xx; od 3.0 so firme iz SQL."
LOAD_COMPANIES = (
    "Osveži seznam firm iz SQL Evidence firm (dbo.Clients).\n"
    "Povezava: EvidencaFirm/config.json (Nastavitve → Povezave)."
)
FILTER_EVIDENCA = "Prikaže samo firme z evidenco davčnih blagajn (kljukica Ev. v tabeli)."
DOC_FILTER_ENTRY = (
    "Delni niz za iskanje po Zap. št. ali P3.\n"
    "Enter ali gumb Filtriraj. Podpora za *."
)

# —— Pot & datoteke ——
PICK_ROOT = "Izberi koreninsko mapo firme (…\\Blagajna)."
ZIP_PACKAGES = (
    "Nastavitve ZIP paketov — katere mesečne ZIP datoteke\n"
    "vključiti v analizo davčne blagajne."
)
PICK_OUT = "Izberi mapo za shranjevanje (Excel, CSV, izvozi)."

# —— Minimax nastavitve ——
KONTI = "Uredi kontiranje prihodkov (konti po vrsti prodaje)."

# —— Excel & knjižbe ——
SAVE_EXCEL = "Shrani trenutne rezultate analize v Excel (Blagajna.xlsx)."
EXPORT_ANALYSIS_EXCEL = "Izvozi analizo v ločen Excel (podrobnejši izvoz)."
KNJIZBE_MONTH = (
    "Kopira mesečne knjižbe DDV v predlogo KnjizbeInDDV.xlsx\n"
    "za izbrani mesec."
)
KNJIZBE_DAILY = (
    "Kopira dnevne knjižbe DDV v predlogo KnjizbeInDDV.xlsx\n"
    "za označene/izbrane dneve."
)
PICK_TEMPLATE = "Izberi Excel predlogo za knjižbe (KnjižbeInDDV.xlsx)."

# —— Izvoz API ——
SEND_MONTH_API = (
    "Pošlje mesečne podatke v Minimax prek API\n"
    "(IssuedInvoicePosting). Pred tem OAuth prijava."
)
SEND_DAILY_API = (
    "Če je API mogoč (token ali OAuth v nastavitvah) → pošlje prek API.\n"
    "WebView2 samo, če API res ni mogoč — isto kot «Minimax spletni uvoz»."
)
