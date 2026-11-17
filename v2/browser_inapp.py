"""
Migracija Chrome vtičnikov → avtomatika v Davčna Blagajna.

Cilj: aplikacija je neodvisna od chrome-extension:// skript.
Vtičniki so bili: chrome.scripting + localhost sprožilci.

Status
------
FURS PakR (Od/do ~2 s)
  → DONE — chrome --new-tab v že odprtem Chrome (zaklenjeno 2.2.28).

Minimax spletni uvoz (Knjižbe in DDV)
  → DONE — samostojni WebView2 (zaklenjeno 3.0.42; docs uskladitev 3.0.45).
     CDP :9333 samo za priponko Excel v ISTI WebView2 seji.

KIR/KPR eDavki Obdobje od/do
  → DONE — CDP v Chrome :9222 (brez Selenium; 3.0.43/3.0.44).
     eDavki ostane v Chrome (Halcom), ne WebView2.

Portal most (QUICK_eNDM PortalRouter) — 3.0.58/3.0.59
  → DONE — bistvo v v2/portal_bridge.py (brez playbookov v tej app).
     Aktivni Chrome portal → ta seja; sicer trajni WebView2 profil
     (minimax / edavki / ajpes / spot). Brez kopiranja kukijev, brez vtičnikov.
     Plače/eNDM SQL ostanejo v QUICK_eNDM — ne v Davčni Blagajni / KIRKPR.

Po API: pregled Knjiženja — 3.0.68 ZAKLENJENO (video OdpriKnjiženjeIRinIztržkov)
  → DONE — motor pywebview + Edge WebView2 (isti profil kot KN uvoz):
     HARD firma → Knjiženje IR/iztržkov → Najdi.
     Uporabnik: »3.0.68 deluje — ta motor si zapomni« (tudi za druge app).
     Trigger: »motor je pywebview + Edge WebView2« → ti postopki.
     NE Chrome Bridge, NE Playwright brez DA. KN uvoz 3.0.42 nespremenjen.

Minimax podjetja (KIR PR odhodek, konto 62, MRN)
  → TODO (CDP/Selenium na Minimax/eDavki debug Chrome).

Plače Oddaje (BOD / virmani / e-pošta)
  → TODO (strežnik :5091; ločena app / eNDM — ne tlačiti v blagajno).

CDP Snemalnik (seje / replay)
  → TODO.
"""

from __future__ import annotations

from typing import Dict

MIGRATION_STATUS: Dict[str, str] = {
    "minimax_podjetja.furs_pakr": "done",
    "minimax_web_uvoz_webview2": "done",
    "edavki_kirkpr_period_cdp": "done",
    "portal_bridge_endm": "done",
    "minimax_podjetja.org_open": "todo",
    "minimax_podjetja.kirkpr_pr": "todo",
    "minimax_podjetja.konto62": "todo",
    "minimax_podjetja.mrn": "todo",
    "place_oddaje": "todo",
    "cdp_snemalnik": "todo",
}


def migrated(feature: str) -> bool:
    return MIGRATION_STATUS.get(feature) == "done"
