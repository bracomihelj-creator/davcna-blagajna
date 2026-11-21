# tools/legacy — samo za evidenco (5.1 jih ne uporablja)

| Datoteka | Zakaj je tu |
|---|---|
| `web_demo/` | zgodnji Flask spletni demo (3.0, avgust 2026); nadomeščen z `ui/` + pywebview |
| `ZAZENI_BLAGAJNA_EXE.bat` | zagon `dist\DavcnaBlagajna.exe` (PyInstaller, 3.0); 5.1 se ne gradi v EXE |
| `ZGRADI_DAVCNA_BLAGAJNA.bat` | gradnja EXE s `DavcnaBlagajna.spec` (spec ni v gitu) |
| `Zagon_davcnaBlagajna_V3.bat` | zaganjalnik 3.0 (V3); v 5.1 bi zagnal WebView2 LOOK pod napačnim imenom |

Bat datoteke uporabljajo `%~dp0`, zato iz te podmape **ne delujejo** — so samo zapis.
Za Tk 3.0.68 uporabi meni **Datoteka → Odpri Tk 3.0.68** ali bat v mapi `D:\PISARNA\Python\DavčnaBlagajna`.
Za Tk način iz mape 5.1 (diagnostika s konzolo) ostane `ZAZENI_DavcnaBlagajna_PY.bat` v korenu.