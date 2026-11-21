/* Davčna Blagajna 5.1.00 — LOOK HTML; drevo/✓ v WebView2, ni Tk oken */
(function () {
  function $(id) { return document.getElementById(id); }
  var state = {
    boot: null, companies: [], selectedZst: "", tree: null, selectedTreeId: "",
    viewIdx: 0, kirkprBook: 0, kirkprSource: 0, exportTab: 0, settingsTab: 0
  };
  var hudPending = 0;
  var hudTimer = null;
  var hudEpoch = 0;
  var hudContext = "LOOK WebView2";
  var SILENT_CALL = { set_fields: 1, set_period: 1, ping: 1, close_window: 1 };
  var ACTION_LABEL = {
    boot: "Zagon",
    invoke: "Opravilo",
    select_company: "Izbor firme",
    load_companies: "Osveži firme",
    companies: "Seznam firm",
    toggle_evidenca: "Evidenca firme",
    tree_toggle: "Drevo",
    tree_check: "Označitev",
    tree_reset_selection: "Ponastavi izbor",
    set_preset: "Prednastavitev",
    appearance: "Videz",
    open_history: "Zgodovina verzij",
    open_settings: "Nastavitve",
    open_legacy_tk: "Odpri Tk 3.0.68",
    look_save: "Shrani LOOK",
    compare_presets: "Prednastavitve primerjave",
    _analyze: "Analiziraj",
    import_if_folder_has_data: "Analiziraj",
    _open_furs_and_optional_month_location: "FURS Blagajna",
    _open_furs_kir_kpr_and_optional_month_location: "Prenos KIR/KPR eDavki",
    _prenos_minimax_kirkpr: "Prenos KIR/KPR Minimax",
    _uvozi_kirkpr: "Uvozi KIR/KPR",
    _analyze_kirkpr: "Analiza KIR/KPR",
    _compare_files: "Primerjava datotek",
    _compare_files_presets: "Primerjava prednastavitev",
    _open_oauth_settings_dialog: "OAuth / Minimax",
    _open_kontiranje_placila_editor: "Kontiranje plačil",
    _open_kontiranje_prihodkov_editor: "Kontiranje prihodkov",
    _refresh_minimax_payment_methods: "Načini plačila",
    _save: "Shrani Excel",
    _export_analysis_to_excel: "Izvoz analize",
    _copy_to_knjizbe: "Knjižbe mesec",
    _copy_daily_to_knjizbe: "Knjižbe dan",
    _open_minimax_web_uvoz_browser: "Oddaja Excel",
    _send_month_file_to_minimax_api: "Prenos mesec → Minimax",
    _send_daily_to_minimax_api: "Prenos v Minimax",
    _pick_template: "Predloga",
    _pick_root: "Izbor Root",
    _pick_out: "Izbor mape",
    _open_zip_packages_dialog: "ZIP paketi",
    _open_kirkpr_new_record_editor: "Dodaj KIR/KPR zapis",
    _apply_doc_filter: "Filter dokumentov",
    _clear_doc_filter: "Počisti filter",
    _on_show_neobdavcljive_toggle: "Neobdavčljive",
    _tree_expand_all: "Razširi drevo",
    _tree_collapse_all: "Skrči drevo",
    _tree_clear_selected_result_row: "Sprazni vrstico",
    _load_companies: "Osveži firme",
    _on_evidenca_filter_toggle: "Filter evidence",
    _open_edavki_link_combo: "eDavki povezava"
  };

  function actionLabel(name, args) {
    if (name === "invoke" && args && args[0]) {
      return ACTION_LABEL[args[0]] || String(args[0]);
    }
    if (name === "look_save" && args && args[0]) {
      return ACTION_LABEL[args[0]] || ACTION_LABEL.look_save;
    }
    return ACTION_LABEL[name] || name;
  }

  function hudShow(message, kind, context) {
    var hud = $("actionHud");
    if (!hud) return;
    var state = kind === false || kind === "error" ? "error" : kind === true || kind === "done" ? "done" : "running";
    var epoch = ++hudEpoch;
    clearTimeout(hudTimer);
    hud.hidden = false;
    hud.classList.remove("running", "error", "done");
    hud.classList.add(state);
    if (context) hudContext = context;
    if ($("actionHudContext")) $("actionHudContext").textContent = hudContext || "LOOK WebView2";
    if ($("actionHudMessage")) $("actionHudMessage").textContent = String(message || "");
    if ($("actionHudStage")) {
      $("actionHudStage").textContent = state === "error"
        ? "Napaka · preveri sporočilo"
        : state === "done" ? "Uspešno končano" : "Opravilo poteka …";
    }
    if ($("actionHudFill")) $("actionHudFill").style.width = state === "running" ? "35%" : "100%";
    if ($("actionHudTrack")) $("actionHudTrack").setAttribute("aria-valuenow", state === "running" ? "35" : "100");
    if (state === "done" && hudPending <= 0) {
      hudTimer = setTimeout(function () {
        if (epoch === hudEpoch && hudPending <= 0) hud.hidden = true;
      }, 6500);
    }
  }

  function api() {
    return (window.pywebview && window.pywebview.api) || null;
  }
  function call(name, args) {
    var a = api();
    var label = actionLabel(name, args);
    var silent = !!SILENT_CALL[name];
    if (!silent) {
      hudPending += 1;
      hudShow("Izvajam: " + label + " …", "running", label);
    }
    if (!a || typeof a[name] !== "function") {
      if (!silent) {
        hudPending = Math.max(0, hudPending - 1);
        hudShow("Most ni pripravljen (" + name + ").", "error", label);
      }
      return Promise.resolve({ ok: false, msg: "Most ni pripravljen (" + name + ")." });
    }
    try {
      return Promise.resolve(a[name].apply(a, args || [])).then(function (res) {
        if (!silent) {
          hudPending = Math.max(0, hudPending - 1);
          if (!res || res.ok === false) {
            hudShow((res && res.msg) || ("Napaka: " + label), "error", label);
          } else if (hudPending <= 0) {
            hudShow((res && res.msg) || (label + " — končano."), "done", label);
          }
        }
        return res;
      }, function (err) {
        if (!silent) {
          hudPending = Math.max(0, hudPending - 1);
          hudShow(String(err && err.message ? err.message : err), "error", label);
        }
        return { ok: false, msg: String(err && err.message ? err.message : err) };
      });
    } catch (err) {
      if (!silent) {
        hudPending = Math.max(0, hudPending - 1);
        hudShow(String(err && err.message ? err.message : err), "error", label);
      }
      return Promise.resolve({ ok: false, msg: String(err && err.message ? err.message : err) });
    }
  }
  function setStatus(msg, ok) {
    var el = $("statusLine");
    if (el) {
      el.textContent = msg || "";
      el.style.color = ok === false ? "#c84b63" : "";
    }
    if (msg) hudShow(msg, ok === false ? "error" : ok === true ? "done" : "running", hudContext);
  }
  function setCheckedSum(txt) {
    var el = $("checkedSum");
    if (el) el.textContent = txt || "";
  }
  function esc(s) {
    return String(s == null ? "" : s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function fillSelect(id, values, current) {
    var el = $(id);
    if (!el) return;
    var cur = current != null ? String(current) : el.value;
    el.innerHTML = "";
    (values || []).forEach(function (v) {
      var o = document.createElement("option");
      o.value = String(v);
      o.textContent = String(v);
      el.appendChild(o);
    });
    if (cur) el.value = cur;
  }
  function normalizeTheme(theme) {
    return String(theme || "").toLowerCase() === "dark" ? "dark" : "light";
  }
  function normalizeLook(look) {
    return String(look || "").toLowerCase() === "t4" ? "t4" : "t5";
  }
  function applyAppearance(a) {
    a = a || {};
    var root = document.documentElement;
    var theme = normalizeTheme(a.theme);
    var look = normalizeLook(a.look || root.getAttribute("data-look"));
    root.setAttribute("data-theme", theme);
    root.setAttribute("data-look", look);
    document.body.classList.remove("theme-dark");
    root.style.removeProperty("--accent");
    root.style.removeProperty("--radius");
    if (a.font_size) root.style.setProperty("--font-size", a.font_size + "px");
    var dens = a.density === "compact" || a.density === "comfortable" ? a.density : "normal";
    document.body.classList.toggle("density-compact", dens === "compact");
    document.body.classList.toggle("density-comfortable", dens === "comfortable");
    if ($("densitySel")) $("densitySel").value = dens;
    if ($("themeSel")) $("themeSel").value = theme;
    if ($("lookSel")) $("lookSel").value = look;
    if ($("accentIn")) $("accentIn").value = look === "t4" ? "#5968e8" : "#4f46e5";
    if ($("radiusIn")) $("radiusIn").value = look === "t4" ? 14 : 12;
    if ($("fontIn")) $("fontIn").value = a.font_size || 13;
    document.querySelectorAll("[data-look-btn]").forEach(function (btn) {
      var on = btn.getAttribute("data-look-btn") === look;
      btn.classList.toggle("on", on);
      btn.setAttribute("aria-pressed", on ? "true" : "false");
    });
    var themeBtn = $("themeBtn");
    if (themeBtn) {
      themeBtn.textContent = theme === "dark" ? "Svetla" : "Temna";
      themeBtn.title = theme === "dark" ? "Preklopi na svetlo temo" : "Preklopi na temno temo";
    }
  }
  function appearancePayload(extra) {
    var root = document.documentElement;
    var look = normalizeLook(root.getAttribute("data-look"));
    var a = {
      theme: normalizeTheme(root.getAttribute("data-theme")),
      look: look,
      density: document.body.classList.contains("density-compact") ? "compact" :
        (document.body.classList.contains("density-comfortable") ? "comfortable" : "normal"),
      font_size: $("fontIn") && $("fontIn").value ? Number($("fontIn").value) : 13,
      accent: look === "t4" ? "#5968e8" : "#4f46e5",
      radius: look === "t4" ? 14 : 12
    };
    if (extra) Object.keys(extra).forEach(function (k) { a[k] = extra[k]; });
    return a;
  }
  function persistAppearance(extra) {
    var a = appearancePayload(extra);
    applyAppearance(a);
    return call("appearance", [a]);
  }
  function setLook(look) {
    persistAppearance({ look: normalizeLook(look) }).then(function () {
      setStatus("Videz: " + (normalizeLook(look) === "t4" ? "Trops 4" : "Trops 5"), true);
    });
  }
  function setTheme(theme) {
    persistAppearance({ theme: normalizeTheme(theme) }).then(function () {
      setStatus(normalizeTheme(theme) === "dark" ? "Temna tema" : "Svetla tema", true);
    });
  }
  function setupLookControls() {
    document.querySelectorAll("[data-look-btn], [data-look-act]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        setLook(btn.getAttribute("data-look-btn") || btn.getAttribute("data-look-act") || "t5");
      });
    });
    document.querySelectorAll("[data-theme-act]").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        setTheme(btn.getAttribute("data-theme-act") || "light");
      });
    });
    var themeBtn = $("themeBtn");
    if (themeBtn) {
      themeBtn.addEventListener("click", function () {
        var next = normalizeTheme(document.documentElement.getAttribute("data-theme")) === "dark" ? "light" : "dark";
        setTheme(next);
      });
    }
    document.querySelectorAll("#viewNav [data-view-idx]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        showView(Number(btn.getAttribute("data-view-idx")) || 0);
      });
    });
  }

  var VIEW_TIPS = {
    "Blagajna": "Davčna blagajna: uvoz CSV/ZIP, FURS PakR, drevo.",
    "KIR/KPR": "KIR/KPR eDavki ali Minimax — prenos in uvoz.",
    "Primerjaj KIRKPR": "Primerjava eDavki KIR/KPR ↔ Minimax.",
    "Primerjaj datoteke": "Prednastavljene in ročne primerjave datotek.",
    "Minimax": "Minimax spletni uvoz in API."
  };

  function renderTabs(hostId, labels, active, onClick) {
    var host = $(hostId);
    if (!host) return;
    host.innerHTML = "";
    (labels || []).forEach(function (label, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "tab" + (i === active ? " active" : "");
      b.textContent = label;
      if (hostId === "viewTabs" && VIEW_TIPS[label]) b.setAttribute("data-tip", VIEW_TIPS[label]);
      b.onclick = function () { onClick(i); };
      host.appendChild(b);
    });
  }

  function showView(idx, fromApp) {
    state.viewIdx = idx;
    var labels = (state.boot && state.boot.views) || ["Blagajna", "KIR/KPR", "Primerjaj KIRKPR", "Primerjaj datoteke", "Minimax"];
    renderTabs("viewTabs", labels, idx, function (i) { showView(i); });
    document.querySelectorAll("#viewNav [data-view-idx]").forEach(function (btn) {
      var on = Number(btn.getAttribute("data-view-idx")) === idx;
      btn.classList.toggle("active", on);
    });
    if ($("pageTitle")) $("pageTitle").textContent = labels[idx] || "Davčna Blagajna";
    $("panelBlagajnaActions").classList.toggle("hidden", idx !== 0 && idx !== 4);
    $("panelKirkpr").classList.toggle("hidden", idx !== 1);
    $("panelCompareKirkpr").classList.toggle("hidden", idx !== 2);
    $("panelCompareFiles").classList.toggle("hidden", idx !== 3);
    $("exportBar").classList.toggle("hidden", idx === 2 || idx === 3);
    if (idx === 2 || idx === 3) loadComparePresets();
    if (!fromApp) {
      call("set_view", [idx]).then(applySnap);
    }
  }

  function showKirkprBook(idx) {
    state.kirkprBook = idx;
    renderTabs("kirkprBookTabs", ["KIR", "KPR"], idx, function (i) {
      call("set_kirkpr_book", [i]).then(function (res) {
        showKirkprBook(i);
        applySnap(res);
      });
    });
  }
  function showKirkprSource(idx) {
    state.kirkprSource = idx;
    renderTabs("kirkprSourceTabs", ["eDavki", "Minimax"], idx, function (i) {
      call("set_kirkpr_source", [i]).then(function (res) {
        showKirkprSource(i);
        applySnap(res);
      });
    });
    $("kirkprEdavkiBar").classList.toggle("hidden", idx !== 0);
    $("kirkprMinimaxBar").classList.toggle("hidden", idx !== 1);
  }
  function showExportTab(idx) {
    state.exportTab = idx;
    renderTabs("exportTabs", ["Excel & knjižbe", "Izvoz v Minimax API"], idx, showExportTab);
    $("exportExcel").classList.toggle("hidden", idx !== 0);
    $("exportApi").classList.toggle("hidden", idx !== 1);
  }
  function showSettingsTab(idx) {
    state.settingsTab = idx;
    renderTabs("settingsTabs", ["Pot & datoteke", "Minimax nastavitve"], idx, showSettingsTab);
    $("tabPaths").classList.toggle("hidden", idx !== 0);
    $("tabMinimax").classList.toggle("hidden", idx !== 1);
  }

  function evMark(c) {
    if (c && (c["Ev."] || c.Ev)) return c["Ev."] || c.Ev;
    return "☐";
  }
  function renderCompanies(rows) {
    var tb = $("companyTable").querySelector("tbody");
    tb.innerHTML = "";
    (rows || []).forEach(function (c) {
      var tr = document.createElement("tr");
      if (String(c["Zšt"]) === String(state.selectedZst)) tr.classList.add("selected");
      tr.innerHTML =
        '<td class="evCell" title="Klik: dodaj/odstrani iz evidence">' + esc(evMark(c)) + "</td>" +
        "<td>" + esc(c["Zšt"]) + "</td>" +
        "<td>" + esc(c["NAZIV"]) + "</td>" +
        "<td>" + esc(c["DAVČNA"]) + "</td>" +
        "<td>" + esc(c["DURS sifra"]) + "</td>" +
        "<td>" + esc(c["Org_ID"]) + "</td>";
      tr.querySelector(".evCell").onclick = function (e) {
        e.stopPropagation();
        toggleEvidenca(c["Zšt"]);
      };
      tr.onclick = function () { selectCompany(c["Zšt"]); };
      tb.appendChild(tr);
    });
  }
  function applyCompaniesResult(res) {
    if (!res || !res.ok) {
      setStatus((res && res.msg) || "SQL napaka", false);
      $("countLabel").textContent = "Napaka SQL";
      return;
    }
    state.companies = res.companies || [];
    renderCompanies(state.companies);
    var evPart = (res.evidenca_count != null) ? (" · Ev. " + res.evidenca_count) : "";
    $("countLabel").textContent = (res.count || 0) + " / " + (res.total || 0) + evPart;
    if ($("srcLbl")) $("srcLbl").textContent = "Vir: " + (res.source || "—");
    if (res.msg) setStatus(res.msg, true);
  }
  function loadCompanies() {
    var q = ($("searchIn") && $("searchIn").value) || "";
    $("countLabel").textContent = "Nalagam …";
    return call("set_fields", [{ filter_evidenca: $("chkEvidenca").checked }]).then(function () {
      return call("companies", [q]);
    }).then(applyCompaniesResult);
  }
  function toggleEvidenca(zst) {
    return call("toggle_evidenca", [String(zst)]).then(applyCompaniesResult);
  }
  function selectCompany(zst) {
    setStatus("Izbiram firmo …");
    return collectFields().then(function () {
      return call("select_company", [String(zst)]);
    }).then(function (res) {
      if (!res || !res.ok) { setStatus((res && res.msg) || "Izbor ni uspel", false); return; }
      state.selectedZst = String(zst);
      state.selectedTreeId = "";
      applySnap(res);
      applyDetail({ detail_title: "(ni izbire)", detail_rows: [] });
      renderCompanies(state.companies);
    });
  }

  function checkable(kind) {
    return kind === "month" || kind === "day" || kind === "year" || kind === "yearsum" || kind === "grandtotal" || kind === "zipfile";
  }
  function skipCheckCol(name) {
    return name === "✓" || name === "×";
  }
  function valueCells(node, cols) {
    var f = node.formatted || {};
    var vals = node.values || [];
    return cols.map(function (c, i) {
      if (skipCheckCol(c)) return "";
      var v = f[c];
      if (v == null || v === "") {
        v = vals[i] == null ? "" : vals[i];
        if (v === "☑" || v === "☐" || v === "×") v = vals[i + 2] != null ? vals[i + 2] : "";
      }
      return '<td class="num">' + esc(v) + "</td>";
    }).join("");
  }
  function applyDetail(res) {
    var title = (res && (res.detail_title || res.title)) || "(ni izbire)";
    if ($("detailTitle")) $("detailTitle").textContent = title;
    var tb = $("detailRows");
    if (!tb) return;
    tb.innerHTML = "";
    var rows = (res && (res.detail_rows || res.rows)) || [];
    if (!rows.length) {
      tb.innerHTML = "<tr><td colspan='2' class='muted'>Ni analitičnih postavk.</td></tr>";
      return;
    }
    rows.forEach(function (r) {
      var tr = document.createElement("tr");
      tr.innerHTML = "<td>" + esc(r.label) + "</td><td class='num'>" + esc(r.value) + "</td>";
      tb.appendChild(tr);
    });
  }
  function renderDetail(node) {
    $("detailTitle").textContent = (node && node.label) || "(ni izbire)";
  }
  function selectTreeRow(tr, node) {
    document.querySelectorAll("#treeBody tr.selected").forEach(function (el) {
      el.classList.remove("selected");
    });
    if (tr) tr.classList.add("selected");
    state.selectedTreeId = (node && node.id) || "";
    call("select_tree", [state.selectedTreeId, (node && node.iid) || ""]).then(applyDetail);
  }
  function toggleCheckCell(node, cell) {
    return call("toggle_check", [node.id || "", node.iid || ""]).then(function (res) {
      if (!res || !res.ok) {
        setStatus((res && res.msg) || "Označitev ni uspela", false);
        return;
      }
      if (cell) cell.textContent = res.on ? "☑" : "☐";
      setCheckedSum(res.checked_sum || "");
    });
  }
  function renderTree(tree) {
    state.tree = tree;
    var head = $("treeHead"), body = $("treeBody");
    head.innerHTML = ""; body.innerHTML = "";
    if (!tree || !tree.nodes || !tree.nodes.length) {
      body.innerHTML = "<tr><td>Ni podatkov — uvozi / analiziraj.</td></tr>";
      return;
    }
    var cols = (tree.sum_columns && tree.sum_columns.length)
      ? tree.sum_columns
      : (tree.value_columns || []).filter(function (c) { return !skipCheckCol(c); });
    var hr = document.createElement("tr");
    hr.innerHTML = "<th>✓</th><th>Obdobje</th>" + cols.map(function (c) {
      return "<th class='num'>" + esc(c) + "</th>";
    }).join("");
    head.appendChild(hr);

    function addRow(node, indent) {
      var tr = document.createElement("tr");
      tr.className = (node.kind || "") + (node.id === state.selectedTreeId ? " selected" : "");
      tr.dataset.id = node.id || "";
      var canCheck = checkable(node.kind);
      var mark = node.check || (canCheck ? (node.checked ? "☑" : "☐") : "");
      var depth = node.depth != null ? node.depth : indent;
      var caret = node.has_children ? (node.open ? "▾ " : "▸ ") : "";
      tr.innerHTML =
        '<td class="chkCell">' + esc(canCheck ? mark : "") + "</td>" +
        '<td class="tree-label indent-' + Math.min(depth, 4) + '">' +
        '<span class="tree-caret">' + caret + "</span>" + esc(node.label || "") + "</td>" +
        valueCells(node, cols);
      var chk = tr.querySelector(".chkCell");
      if (canCheck) {
        chk.onclick = function (e) {
          e.stopPropagation();
          toggleCheckCell(node, chk);
        };
      }
      tr.onclick = function () {
        selectTreeRow(tr, node);
        renderDetail(node);
        if (node.has_children) {
          call("tree_toggle", [node.id || "", node.iid || ""]).then(function (res) {
            applySnap(res);
            applyDetail(res);
            if (state.selectedTreeId) {
              var escId = (window.CSS && CSS.escape) ? CSS.escape(state.selectedTreeId) : state.selectedTreeId.replace(/:/g, "\\:");
              var keep = document.querySelector('#treeBody tr[data-id="' + escId + '"]');
              if (keep) keep.classList.add("selected");
            }
          });
        }
      };
      body.appendChild(tr);
      if (node.open) {
        (node.children || []).forEach(function (ch) {
          addRow(ch, Math.min(indent + 1, 4));
        });
      }
    }
    tree.nodes.forEach(function (n) { addRow(n, 0); });
  }

  function applySnap(res) {
    if (!res) return res;
    if (res.ok === false) {
      setStatus(res.msg || "Napaka", false);
      return res;
    }
    if (res.company_label) $("companyPill").textContent = res.company_label;
    if (res.minimax_status) $("mmPill").textContent = res.minimax_status;
    if (res.root_path) {
      $("rootLbl").textContent = res.root_path;
      $("rootIn").value = res.root_path;
    }
    if (res.out_dir != null) $("outDirIn").value = res.out_dir;
    if (res.out_file != null) $("outFileIn").value = res.out_file;
    if (res.sheet_name != null) $("sheetIn").value = res.sheet_name;
    if (res.csv_name != null) $("csvIn").value = res.csv_name;
    if (res.template_path && $("tplIn")) $("tplIn").value = res.template_path;
    if (res.org_id != null) $("orgIdIn").value = res.org_id;
    if (res.year) $("yearIn").value = res.year;
    if (res.month) $("monthIn").value = String(parseInt(res.month, 10));
    if (res.doc_filter != null) $("docFilter").value = res.doc_filter;
    if (res.doc_type) $("docTypeIn").value = res.doc_type;
    if (res.vrsta_prodaje) $("vrstaIn").value = res.vrsta_prodaje;
    if (res.pay != null) $("payIn").value = res.pay;
    if (typeof res.include_zips === "boolean") $("chkZip").checked = res.include_zips;
    if (typeof res.show_neob === "boolean") $("chkNeob").checked = res.show_neob;
    if (typeof res.ddv_zavezanec === "boolean") $("chkDdv").checked = res.ddv_zavezanec;
    if (typeof res.filter_evidenca === "boolean") $("chkEvidenca").checked = res.filter_evidenca;
    if (res.zst) state.selectedZst = String(res.zst);
    if (res.tree) {
      var newNodes = (res.tree.nodes || []).length;
      var hadNodes = state.tree && state.tree.nodes && state.tree.nodes.length;
      if (res.force_tree || newNodes || !hadNodes) {
        if (res.force_tree) state.selectedTreeId = "";
        renderTree(res.tree);
      }
    }
    setCheckedSum(res.checked_sum || "");
    if ($("analysisInfo")) $("analysisInfo").textContent = res.analysis_info || "";
    if ($("fursZipHint")) {
      $("fursZipHint").textContent = res.furs_zip ? ("ZIP: " + res.furs_zip) : "";
    }
    if ($("autoHint")) {
      $("autoHint").textContent = res.selenium_auto
        ? "Avtomatika Pripravi+ZIP: vklopljena"
        : "Avtomatika Pripravi+ZIP: izklopljena (Nastavitve → Dostop)";
    }
    if (res.edavki_link && $("edavkiLink")) $("edavkiLink").value = res.edavki_link;
    if (typeof res.view_idx === "number" && res.view_idx !== state.viewIdx) {
      showView(res.view_idx, true);
    }
    if (typeof res.kirkpr_book === "number") showKirkprBook(res.kirkpr_book);
    if (typeof res.kirkpr_source === "number") showKirkprSource(res.kirkpr_source);
    if (res.look_panel) openLookPanel(res);
    if (res.msg) setStatus(res.msg, res.ok !== false);
    return res;
  }

  function closeLookPanel() {
    var dlg = $("dlgLook");
    if (dlg) dlg.hidden = true;
  }

  function openLookPanel(res) {
    var panel = res.look_panel;
    if (panel === "videz") {
      $("dlgVidez").hidden = false;
      return;
    }
    var dlg = $("dlgLook"), title = $("dlgLookTitle"), body = $("dlgLookBody"), btns = $("dlgLookBtns");
    if (!dlg || !title || !body || !btns) return;
    dlg.hidden = false;
    btns.innerHTML = "";
    if (panel === "history") {
      title.textContent = "Zgodovina verzij — " + (res.current || "5.1.00");
      var html = '<p class="note">Tk okno zgodovine je odstranjeno. Pregled je v LOOK.</p>';
      (res.versions || []).forEach(function (v) {
        html += "<div class='preset'><div><strong>" + esc(v.id) + "</strong> · " + esc(v.date) +
          "</div><span>" + esc(v.title) + "</span>" +
          (v.changes ? "<p class='note'>" + esc(v.changes) + "</p>" : "") + "</div>";
      });
      body.innerHTML = html || "<p class='note'>Ni zapisov.</p>";
      btns.innerHTML = "<button class='btn' type='button' id='btnLookClose' data-tip='Zapri zgodovino.'>Zapri</button>";
      $("btnLookClose").onclick = closeLookPanel;
      return;
    }
    if (panel === "oauth") {
      title.textContent = "OAuth / Minimax";
      var form = "<p class='note'>Ista polja kot 3.0.68, v LOOK. Gesla ostanejo lokalno.</p>";
      (res.oauth_fields || []).forEach(function (f) {
        form += "<label class='fld'>" + esc(f.label) +
          "<input class='field-yellow oauthFld' data-key='" + esc(f.key) + "' type='" +
          (f.secret ? "password" : "text") + "' value='" + esc(f.value || "") + "'></label>";
      });
      form += "<label class='check'><input type='checkbox' id='oauthDdv'" +
        (res.minimax_ddv_zavezanec ? " checked" : "") + "> Podjetje je zavezanec za DDV</label>";
      body.innerHTML = form;
      btns.innerHTML =
        "<button class='btn primary' type='button' id='btnOauthSave' data-tip='Shrani OAuth v JSON ob aplikaciji.'>Shrani</button>" +
        "<button class='btn' type='button' id='btnOauthLogin' data-tip='OAuth prijava v Minimax API.'>OAuth prijava</button>" +
        "<button class='btn' type='button' id='btnLookClose' data-tip='Zapri.'>Zapri</button>";
      function oauthPayload() {
        var data = {
          minimax_ddv_zavezanec: !!($("oauthDdv") && $("oauthDdv").checked)
        };
        document.querySelectorAll(".oauthFld").forEach(function (inp) {
          data[inp.getAttribute("data-key")] = inp.value;
        });
        return data;
      }
      $("btnOauthSave").onclick = function () {
        call("look_save", ["oauth", oauthPayload()]).then(function (r) {
          applySnap(r);
          closeLookPanel();
        });
      };
      $("btnOauthLogin").onclick = function () {
        call("look_save", ["oauth", oauthPayload()]).then(function () {
          return call("look_save", ["oauth_login", {}]);
        }).then(function (r) { applySnap(r); });
      };
      $("btnLookClose").onclick = closeLookPanel;
      return;
    }
    if (panel === "zip") {
      title.textContent = "ZIP paketi — FURS blagajna";
      var rows = res.zip_rows || [];
      if (!rows.length) {
        body.innerHTML = "<p class='note'>" + esc(res.msg || "Ni ZIP paketov.") + "</p>";
        btns.innerHTML = "<button class='btn' type='button' id='btnLookClose' data-tip='Zapri.'>Zapri</button>";
        $("btnLookClose").onclick = closeLookPanel;
        return;
      }
      var table = "<table class='dlgTable'><thead><tr><th>✓</th><th>Datoteka</th><th>Paket</th><th>Računov</th><th>Vrednost</th></tr></thead><tbody>";
      rows.forEach(function (r) {
        table += "<tr><td><input type='checkbox' class='zipChk' data-name='" + esc(r.name) + "'" +
          (r.enabled ? " checked" : "") + "></td><td>" + esc(r.name) + "</td><td>" +
          esc(r.label) + "</td><td>" + esc(r.docs) + "</td><td>" + esc(r.value) + "</td></tr>";
      });
      table += "</tbody></table>";
      body.innerHTML = table;
      btns.innerHTML =
        "<button class='btn primary' type='button' id='btnZipSave' data-tip='Shrani izbor ZIP paketov.'>Shrani</button>" +
        "<button class='btn' type='button' id='btnLookClose' data-tip='Zapri brez shranjevanja.'>Zapri</button>";
      $("btnZipSave").onclick = function () {
        var enabled = {};
        document.querySelectorAll(".zipChk").forEach(function (cb) {
          enabled[cb.getAttribute("data-name")] = !!cb.checked;
        });
        call("look_save", ["zip", { enabled: enabled }]).then(function (r) {
          applySnap(r);
          closeLookPanel();
        });
      };
      $("btnLookClose").onclick = closeLookPanel;
      return;
    }
    if (panel === "konti_pay" || panel === "konti_vrsta") {
      title.textContent = panel === "konti_pay" ? "Kontiranje — načini plačila" : "Kontiranje — prihodki";
      var keys = panel === "konti_pay" ? ["typ", "name", "konto"] : ["konto", "label", "blago_storitev"];
      var labels = panel === "konti_pay" ? ["Tip", "Naziv", "Konto"] : ["Konto", "Opis", "B/S"];
      var krows = res.konti_rows || [];
      var kh = "<table class='dlgTable'><thead><tr>" + labels.map(function (l) {
        return "<th>" + esc(l) + "</th>";
      }).join("") + "</tr></thead><tbody>";
      krows.forEach(function (row, i) {
        kh += "<tr>";
        keys.forEach(function (k) {
          kh += "<td><input class='field-yellow kontiCell' data-i='" + i + "' data-k='" + esc(k) +
            "' value='" + esc(row[k] || "") + "'></td>";
        });
        kh += "</tr>";
      });
      kh += "</tbody></table>";
      body.innerHTML = kh;
      btns.innerHTML =
        "<button class='btn primary' type='button' id='btnKontiSave' data-tip='Shrani kontiranje.'>Shrani</button>" +
        "<button class='btn' type='button' id='btnLookClose' data-tip='Zapri.'>Zapri</button>";
      $("btnKontiSave").onclick = function () {
        var out = krows.map(function (row) { return Object.assign({}, row); });
        document.querySelectorAll(".kontiCell").forEach(function (inp) {
          var i = parseInt(inp.getAttribute("data-i"), 10);
          var k = inp.getAttribute("data-k");
          if (!isNaN(i) && out[i]) out[i][k] = inp.value;
        });
        call("look_save", [panel, { rows: out }]).then(function (r) {
          applySnap(r);
          closeLookPanel();
        });
      };
      $("btnLookClose").onclick = closeLookPanel;
      return;
    }
    title.textContent = "LOOK";
    body.innerHTML = "<p class='note'>" + esc(res.msg || "Tk okno je odstranjeno.") + "</p>";
    btns.innerHTML = "<button class='btn' type='button' id='btnLookClose' data-tip='Zapri.'>Zapri</button>";
    $("btnLookClose").onclick = closeLookPanel;
  }

  function collectFields() {
    var tpl = ($("tplIn") && $("tplIn").value) || "";
    var payload = {
      out_dir: $("outDirIn").value,
      out_file: $("outFileIn").value,
      sheet_name: $("sheetIn").value,
      csv_name: $("csvIn").value,
      minimax_document_type: $("docTypeIn").value,
      vrsta_prodaje: $("vrstaIn").value,
      ddv_zavezanec: $("chkDdv").checked,
      include_zips: $("chkZip").checked,
      show_neob: $("chkNeob").checked,
      payment_method_label: $("payIn").value,
      doc_filter: $("docFilter").value,
      filter_evidenca: $("chkEvidenca").checked,
      edavki_link: $("edavkiLink").value
    };
    if (tpl.trim()) payload.template_path = tpl;
    var y = parseInt($("yearIn").value, 10);
    var m = parseInt($("monthIn").value, 10);
    return call("set_fields", [payload]).then(function () {
      if (!isNaN(y) && !isNaN(m)) return call("set_period", [y, m]);
    });
  }

  function act(name) {
    setStatus("Izvajam: " + (ACTION_LABEL[name] || name) + " …");
    return collectFields().then(function () {
      return call("invoke", [name]);
    }).then(function (res) {
      applySnap(res);
      if (name === "_load_companies" || name === "_on_evidenca_filter_toggle") return loadCompanies();
      return res;
    }).catch(function (err) {
      setStatus(String(err), false);
    });
  }

  function loadComparePresets() {
    return call("compare_presets", []).then(function (res) {
      function fill(id) {
        var host = $(id);
        if (!host) return;
        host.innerHTML = "";
        if (!res || !res.ok) {
          host.innerHTML = '<div class="preset"><span>' + esc((res && res.msg) || "Ni prednastavitev") + "</span></div>";
          return;
        }
        var list = res.presets || [];
        if (!list.length) {
          host.innerHTML = '<div class="preset"><span>Ni omogočenih prednastavitev — uredi v Nastavitve.</span></div>';
          return;
        }
        list.forEach(function (p) {
          var div = document.createElement("div");
          div.className = "preset";
          var cb = document.createElement("input");
          cb.type = "checkbox";
          cb.checked = !!p.selected;
          cb.onchange = function () { call("set_preset", [p.idx, cb.checked]); };
          var body = document.createElement("div");
          body.innerHTML = "<strong>" + esc(p.name) + "</strong><span>" + esc(p.desc) + "</span>";
          div.appendChild(cb);
          div.appendChild(body);
          host.appendChild(div);
        });
      }
      fill("comparePresetListKirkpr");
      fill("comparePresetListFiles");
    });
  }

  function setupMenus() {
    function closeMenus() {
      document.querySelectorAll(".menu, .menuGroup").forEach(function (m) { m.classList.remove("open"); });
    }
    document.querySelectorAll(".menu, .menuGroup").forEach(function (menu) {
      var btn = menu.querySelector(":scope > button");
      if (!btn) return;
      btn.addEventListener("click", function (e) {
        e.stopPropagation();
        var open = menu.classList.contains("open");
        closeMenus();
        if (!open) menu.classList.add("open");
      });
    });
    document.addEventListener("click", closeMenus);
    document.querySelectorAll(".flyout, .menuDrop").forEach(function (el) {
      el.addEventListener("click", function (e) { e.stopPropagation(); });
    });
    document.querySelectorAll("[data-act]").forEach(function (el) {
      el.addEventListener("click", function () {
        var a = el.getAttribute("data-act");
        if (a === "close") { call("close_window"); return; }
        if (a === "reload") { act("_load_companies"); return; }
        if (a === "videz") { $("dlgVidez").hidden = false; return; }
        if (a === "history") { call("open_history").then(applySnap); return; }
        if (a === "settings") { call("open_settings").then(applySnap); return; }
        if (a === "legacy_tk") {
          call("open_legacy_tk").then(function (r) { setStatus((r && r.msg) || "", !!(r && r.ok)); });
          return;
        }
        if (a === "oauth") { act("_open_oauth_settings_dialog"); return; }
      });
    });
  }
  function setupTooltips() {
    var tip = $("tip");
    if (!tip) return;
    document.body.addEventListener("mousemove", function (e) {
      var t = e.target.closest("[data-tip]");
      if (!t) { tip.hidden = true; return; }
      tip.textContent = t.getAttribute("data-tip");
      tip.hidden = false;
      tip.style.left = Math.min(e.clientX + 14, window.innerWidth - 400) + "px";
      tip.style.top = Math.min(e.clientY + 16, window.innerHeight - 80) + "px";
    });
  }
  function setupSplitter() {
    var spl = $("splitter"), drag = false;
    if (!spl) return;
    spl.addEventListener("mousedown", function () { drag = true; spl.classList.add("drag"); });
    window.addEventListener("mouseup", function () { drag = false; spl.classList.remove("drag"); });
    window.addEventListener("mousemove", function (e) {
      if (!drag) return;
      document.documentElement.style.setProperty("--left-px", Math.max(260, Math.min(640, e.clientX)) + "px");
    });
  }
  function setupCollapsibles() {
    document.querySelectorAll(".colToggle").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var id = btn.getAttribute("data-target");
        var body = $(id);
        if (!body) return;
        var hide = !body.classList.contains("hidden");
        body.classList.toggle("hidden", hide);
        btn.textContent = hide ? "+" : "−";
      });
    });
  }

  function bind() {
    $("btnReload").onclick = function () { act("_load_companies"); };
    $("btnClearSearch").onclick = function () { $("searchIn").value = ""; loadCompanies(); };
    var searchTimer = null;
    $("searchIn").oninput = function () {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(loadCompanies, 250);
    };
    $("chkEvidenca").onchange = function () {
      var on = $("chkEvidenca").checked;
      setStatus(on ? "Seznam: samo evidenca …" : "Seznam: vse firme …");
      loadCompanies().then(function () {
        setStatus(on ? "Prikazane so samo firme z evidenco davčnih blagajn." : "Prikazane so vse firme.", true);
      });
    };
    $("btnEdavki").onclick = function () { act("_open_edavki_link_combo"); };
    $("btnAnalyze").onclick = function () { act("_analyze"); };
    $("btnFurs").onclick = function () { act("_open_furs_and_optional_month_location"); };
    $("btnPrenosEdavki").onclick = function () { act("_open_furs_kir_kpr_and_optional_month_location"); };
    $("btnUvoziKirkpr").onclick = function () { act("_uvozi_kirkpr"); };
    $("btnPrenosMm").onclick = function () { act("_prenos_minimax_kirkpr"); };
    $("btnUvoziKirkpr2").onclick = function () { act("_uvozi_kirkpr"); };
    $("btnComparePresets").onclick = function () { act("_compare_files_presets"); };
    $("btnComparePresets2").onclick = function () { act("_compare_files_presets"); };
    $("btnCompareManual").onclick = function () { act("_compare_files"); };
    $("btnAddRecord").onclick = function () { act("_open_kirkpr_new_record_editor"); };
    $("btnAddRecord2").onclick = function () { act("_open_kirkpr_new_record_editor"); };
    $("btnSaveExcel").onclick = function () { act("_save"); };
    $("btnExportExcel").onclick = function () { act("_export_analysis_to_excel"); };
    $("btnKnjMesec").onclick = function () { act("_copy_to_knjizbe"); };
    $("btnKnjDan").onclick = function () { act("_copy_daily_to_knjizbe"); };
    $("btnPrenosMinimax").onclick = function () { act("_send_daily_to_minimax_api"); };
    $("btnMinimaxUvoz").onclick = function () { act("_open_minimax_web_uvoz_browser"); };
    $("btnResetDetail").onclick = function () {
      state.selectedTreeId = "";
      document.querySelectorAll("#treeBody tr.selected").forEach(function (el) {
        el.classList.remove("selected");
      });
      call("tree_reset_selection").then(function (res) {
        applyDetail(res || { detail_title: "(ni izbire)", detail_rows: [] });
        setStatus((res && res.msg) || "Izbor ponastavljen.", true);
      });
    };
    $("btnSendMonth").onclick = function () { act("_send_month_file_to_minimax_api"); };
    $("btnSendDaily").onclick = function () { act("_send_daily_to_minimax_api"); };
    $("btnPickTpl").onclick = function () { act("_pick_template"); };
    $("btnPickRoot").onclick = function () { act("_pick_root"); };
    $("btnPickRoot2").onclick = function () { act("_pick_root"); };
    $("btnPickOut").onclick = function () { act("_pick_out"); };
    $("btnZipPaketi").onclick = function () { act("_open_zip_packages_dialog"); };
    $("btnFilter").onclick = function () { act("_apply_doc_filter"); };
    $("btnFilterClear").onclick = function () { act("_clear_doc_filter"); };
    $("docFilter").addEventListener("keydown", function (e) {
      if (e.key === "Enter") act("_apply_doc_filter");
    });
    $("chkNeob").onchange = function () { act("_on_show_neobdavcljive_toggle"); };
    $("btnExpand").onclick = function () { act("_tree_expand_all"); };
    $("btnCollapse").onclick = function () { act("_tree_collapse_all"); };
    $("btnClearTree").onclick = function () {
      if (!state.selectedTreeId) {
        setStatus("Označi vrstico v drevesu (leto/mesec/dan).", false);
        return;
      }
      act("_tree_clear_selected_result_row");
    };
    $("btnOauth").onclick = function () { act("_open_oauth_settings_dialog"); };
    $("btnKontiPay").onclick = function () { act("_open_kontiranje_placila_editor"); };
    $("btnKontiVrsta").onclick = function () { act("_open_kontiranje_prihodkov_editor"); };
    $("btnPayRefresh").onclick = function () { act("_refresh_minimax_payment_methods"); };
    $("yearIn").onchange = function () {
      collectFields().then(function () { return call("import_if_folder_has_data", [true]); }).then(applySnap);
    };
    $("monthIn").onchange = function () {
      collectFields().then(function () { return call("import_if_folder_has_data", [true]); }).then(applySnap);
    };
    document.addEventListener("keydown", function (e) {
      if (e.key === "Delete" && state.selectedTreeId) act("_tree_clear_selected_result_row");
    });
    $("btnResetTheme").onclick = function () {
      applyAppearance({ theme: "light", look: "t5", font_size: 13, density: "normal" });
    };
    $("btnSaveTheme").onclick = function () {
      var a = appearancePayload({
        theme: $("themeSel").value,
        look: $("lookSel") ? $("lookSel").value : "t5",
        font_size: parseInt($("fontIn").value, 10) || 13,
        density: $("densitySel") ? $("densitySel").value : "normal"
      });
      persistAppearance(a).then(function () { $("dlgVidez").hidden = true; setStatus("Videz shranjen", true); });
    };
    $("btnCloseTheme").onclick = function () { $("dlgVidez").hidden = true; };
  }

  function init() {
    var hudClose = $("actionHudClose");
    if (hudClose) {
      hudClose.onclick = function () {
        var hud = $("actionHud");
        if (hud) hud.hidden = true;
      };
    }
    setupMenus();
    setupLookControls();
    setupTooltips();
    setupSplitter();
    setupCollapsibles();
    bind();
    showKirkprBook(0);
    showKirkprSource(0);
    showExportTab(0);
    showSettingsTab(0);
    setStatus("Povezujem AppV21 …");
    call("boot").then(function (res) {
      if (!res || !res.ok) {
        setStatus((res && res.msg) || "Zagon ni uspel", false);
        return;
      }
      state.boot = res;
      $("brandVer").textContent = "WebView2 · " + (res.version || "5.1.00") + " · isti AppV21";
      $("footVer").textContent = res.version || "5.1.00";
      fillSelect("yearIn", res.years && res.years.length ? res.years : [String(new Date().getFullYear())], res.year);
      fillSelect("docTypeIn", res.doc_types || [], res.doc_type);
      fillSelect("vrstaIn", res.vrsta_labels || [], res.vrsta_prodaje);
      fillSelect("edavkiLink", res.edavki_links || [], res.edavki_link);
      applyAppearance(res.appearance);
      applySnap(res);
      showView(res.view_idx || 0, true);
      return loadCompanies();
    }).then(function () {
      setStatus("Pripravljeno.", true);
    });
  }

  window.addEventListener("pywebviewready", init);
  if (api()) init();
})();
