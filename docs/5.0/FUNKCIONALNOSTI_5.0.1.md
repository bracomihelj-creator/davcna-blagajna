# FUNKCIONALNOSTI — inventar 3.0.68 za **5.0.1**

**Osnova:** `DavčnaBlagajna` 3.0.68 — `v2/ui_build_v21.py`, `v2/ui_build.py`, `v2/app_v21.py`, `v2/menubar.py`, `v2/settings_menu.py`, `DavcnaBlagajna.py`  
**Status:** PREVERJENO iz kode (ne pomeni, da je vsak gumb v tej seji kliknjen).

Vse vrstice so **obvezne** v 5.0.1 (isti handler, isto stanje App). LOOK se spremeni; logika ne.

---

## 1. Okna

| ID | 3.0.68 | 5.0.1 LOOK | Handler / vir |
|---|---|---|---|
| W1 | Glavno AppV21 | WebView2 glavno okno | `AppV21` isti proces |
| W2 | Primerjava razlik Toplevel | HTML panel / dialog v istem oknu | `_compare_files` / `_compare_files_presets` |
| W3 | Kontiranje Toplevel | HTML dialog | `_open_kontiranje_placila_editor`, `_open_kontiranje_prihodkov_editor` |
| W4 | ZIP paketi Toplevel | HTML dialog | `_open_zip_packages_dialog` |
| W5 | OAuth Minimax Toplevel | HTML dialog | `_open_oauth_settings_dialog` |
| W6 | Minimax WebView2 host | **nespremenjen** ločen host | `v2/minimax_webview2*` |
| W7 | Nastavitve (8 sklopov) | HTML »Videz in nastavitve« | `open_settings_dialog` vsebina |
| W8 | Zgodovina verzij | HTML dialog | `open_version_history_window` |

---

## 2. Levi panel (firme) — 3.0.68 `_build_company_panel`

| Kontrola | Handler | Status |
|---|---|---|
| Obdobje Leto / Mesec | `period_year` / `period_month` | PREVERJENO |
| Išči + ✕ | `company_search` → `_render_companies` | PREVERJENO |
| Vir SQL + Osveži | `_load_companies` | PREVERJENO |
| Evidenca Davčnih blagajn | `_on_evidenca_filter_toggle` | PREVERJENO |
| eDavki combo + Odpri | `_open_edavki_link_combo` | PREVERJENO |
| Treeview firm + Ev. | izbor → `_apply_selected_company` | PREVERJENO |

---

## 3. Zavihki pogleda (3.0.68 zgoraj → 5.0.1 levo)

| Zavihek | Indeks | Dogodek 3.0.68 | 5.0.1 |
|---|---|---|---|
| Blagajna | 0 | `_on_v21_view_tab_changed` | sidebar nav |
| KIR/KPR | 1 | isto | sidebar nav |
| Primerjaj KIRKPR | 2 | isto | sidebar nav |
| Primerjaj datoteke | 3 | isto | sidebar nav |
| Minimax | 4 | isto | sidebar nav |
| KIR / KPR knjiga | podzavihek | `_on_v21_kirkpr_sub_tab_changed` | v desnem delu KIR/KPR |
| eDavki / Minimax vir | podzavihek | `_on_v21_kirkpr_source_tab_changed` | v desnem delu KIR/KPR |
| Excel & knjižbe / API | izvoz | `_build_export_workflow_panel` | desno, kot zdaj |

---

## 4. Gumbi — isti klici kot 3.0.68

### Blagajna / drevo

| Gumb | Metoda |
|---|---|
| Uvozi podatke | `_analyze` |
| FURS Blagajna | `_open_furs_and_optional_month_location` |
| Filtriraj | `_apply_doc_filter` |
| Počisti filter | `_clear_doc_filter` |
| Vrednost Neobd.nabav | `_on_show_neobdavcljive_toggle` |
| Dodaj nov zapis | `_open_kirkpr_new_record_editor` |
| Razširi | `_tree_expand_all` |
| Skrči | `_tree_collapse_all` |
| Sprazni | `_tree_clear_selected_result_row` |
| ✓ drevo | `_toggle_tree_check` |

### KIR/KPR

| Gumb | Metoda |
|---|---|
| Prenos KIR/KPR eDavki | `_open_furs_kir_kpr_and_optional_month_location` |
| Prenos KIR/KPR minimax | `_prenos_minimax_kirkpr` |
| Uvozi podatke | `_uvozi_kirkpr` |

### Primerjave / izvoz / Minimax

| Gumb | Metoda |
|---|---|
| Primerjaj datoteki | `_compare_files` |
| Primerjaj (prednastavitve) | `_compare_files_presets` |
| OAuth… | `_open_oauth_settings_dialog` |
| Konti plačila / prihodki | kontiranje editorja |
| ↻ načini plačila | `_refresh_minimax_payment_methods` |
| Shrani v Excel | `_save` |
| Izvoz podatkov v excel | `_export_analysis_to_excel` |
| Knjižbe DDV po mesecih | `_copy_to_knjizbe` |
| Knjižbe DDV po dnevih | `_copy_daily_to_knjizbe` |
| Minimax spletni uvoz | `_open_minimax_web_uvoz_browser` |
| Pošlji mesec/dan API | `_send_month_file_to_minimax_api` / `_send_daily_to_minimax_api` |
| Predloga … | `_pick_template` |
| Root … / Out … | `_pick_root` / `_pick_out` |
| ZIP + ZIP paketi | `include_zips` / `_open_zip_packages_dialog` |

### Meni

| Meni | Vsebina |
|---|---|
| Verzija | zgodovina (`version_history_ui`) |
| Nastavitve | tema, dostop, povezave, primerjave, knjižba forma |

---

## 5. Stanje, ki mora ostati v App (ne v JS)

- `selected_company`, `root_dir`, `out_dir`, `template_path` (= `MINIMAX_TEMPLATE` privzeto)
- `monthly` / `daily` / `daily_docs` / `_tree_checked`
- `_apply_selected_company` → `_sync_output_dir_with_root`
- seje/nastavitve kot v 3.0.68 (zadnja firma, zavihki, dostop)
- `_safe_call` za napake

---

## 6. Zaklenjene poti (ne menjati)

1. FURS PakR v **uporabnikovem Chrome** (2.2.28)  
2. KIR/KPR eDavki CDP `:9222`  
3. Minimax spletni uvoz WebView2 3.0.42  
4. Po API: Knjiženje 3.0.68  

---

## 7. Bližnjice

- Delete na drevesu = Sprazni (`_tree_clear_selected_result_row`) — PREVERJENO v 3.0.68  
- Enter v filtru dokumentov = Filtriraj  
