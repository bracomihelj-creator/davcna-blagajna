# UI_MIGRACIJA — Tk 3.0.68 → WebView2 **5.0.1**

**LOOK:** QUICK eDAVKI PRO WebView2 (`sidebar` + `.nav`).  
**Logika:** isti `AppV21` klici. HTML ne podvaja izračunov.

---

## 1. Postavitev

### 3.0.68 (PREVERJENO)

```
Header (naslov + badge + firma)
[Zgoraj TabBar: Blagajna | KIR/KPR | Primerjaj KIRKPR | Primerjaj datoteke | Minimax]
H-Paned:
  Levo: Firme (SQL) + Leto/Mesec
  Desno: Minimax bar, KIR panel, izvoz, drevo
Spodaj: Pot & datoteke | Minimax nastavitve
```

### 5.0.1 (PREDLAGANO) — zavihki v levi drevesni/sidebar panel (kot QUICK)

```
┌─ sidebar (QUICK nav) ────────┬─ vsebina ─────────────────────┐
│ brand Davčna Blagajna 5.0.1  │ header: firma + Org ID        │
│ Delovno okolje               │ akcije pogleda (FURS, Uvozi…) │
│  ▦ Blagajna                  │ izvoz / drevo ali primerjava  │
│  ▫ KIR/KPR                   │                               │
│  ▤ Primerjaj KIRKPR          │                               │
│  ▤ Primerjaj datoteke        │                               │
│  ◫ Minimax                   │                               │
│ Firme (SQL drevo)            │                               │
│ Leto / Mesec / iskanje / Ev. │                               │
└──────────────────────────────┴───────────────────────────────┘
```

- Zgornji TabBar **odpade**; pet pogledov = levi `.nav` (`data-view`).
- Seznam firm ostane v levem panelu pod navigacijo (drevo firm).
- Desno: samo vsebina izbranega pogleda + izvoz + drevo rezultatov.
- Accent `#5968e8`, radius 11 px, bg `#f4f7fc`, gumbi QUICK.
- Namigi: rumena `#ffffe0`, Segoe UI 9, ~380 px.

---

## 2. Preslikava kontrolnikov

| Tk / ttk | 5.0.1 |
|---|---|
| `tk.Tk` AppV21 | pywebview okno; App v istem procesu (`withdraw`) |
| TabBar pogledov | `aside.sidebar` gumbi `.nav` |
| Treeview firm | HTML tabela/grid |
| Treeview rezultatov | HTML tabela drevesa (podatki iz App, ne iz Motor) |
| Entry rumena | `.field-yellow` |
| Checkbutton | checkbox |
| Combobox | select |
| Button / accent | `.btn` / `.btn.primary` |
| PanedWindow | CSS grid + drsnik širine |
| Toplevel dialogi | HTML overlay v istem WebView2 |
| filedialog | Win32 izbira mape/datoteke (**brez** začasnega `tk.Tk()`) |
| messagebox | toast / HTML dialog; napake iz `_safe_call` |
| Menu | HTML meni Datoteka / Verzija / Nastavitve |
| Progress | status vrstica |

---

## 3. Bridge (en proces)

Dovoljeni klici = **imena metod App**, npr.:

`_analyze`, `_open_furs_and_optional_month_location`, `_uvozi_kirkpr`, `_copy_daily_to_knjizbe`, `_apply_selected_company`, …

Potek: JS → `pywebview.api.call(name, payload)` → `getattr(app, name)` v **istem** App → JSON za prikaz (drevo, status, poti).

Prepovedano:
- `tk_actions.py` subprocess
- drugi `Motor` z lastnim `monthly`/`daily`
- FURS/KIR v WebView2 namesto Chrome

---

## 4. Videz in nastavitve

Meni Nastavitve (vsebina 3.0.68) + hitri WebView2 videz (tema, accent, radius, pisava), shranjeno ločeno od SQL.

---

## 5. Kaj se ne seli v glavni WebView2

- eDavki / Halcom → Chrome
- Minimax uvoz/Knjiženje → obstoječi host 3.0.42/3.0.68
