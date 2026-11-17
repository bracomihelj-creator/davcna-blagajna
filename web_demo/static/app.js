let treeState = {
  columns: [],
  sumColumns: [],
  nodes: [],
  expanded: new Set(),
  loadedMonths: new Set(),
  monthChildren: new Map(),
};

const $ = (id) => document.getElementById(id);

async function apiJson(url, options = {}) {
  const res = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = data.detail || res.statusText;
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  return data;
}

function setStatus(el, text, kind = "") {
  el.textContent = text;
  el.className = "status" + (kind ? ` ${kind}` : "");
}

function renderCompanies(companies) {
  const tbody = $("companyTable").querySelector("tbody");
  tbody.innerHTML = "";
  for (const c of companies) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${escapeHtml(c["Zšt"] || "")}</td>
      <td>${escapeHtml(c["NAZIV"] || "")}</td>
      <td>${escapeHtml(c["DAVČNA"] || "")}</td>`;
    tr.addEventListener("click", () => {
      tbody.querySelectorAll("tr").forEach((r) => r.classList.remove("selected"));
      tr.classList.add("selected");
    });
    tbody.appendChild(tr);
  }
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function loadCompanies() {
  const q = $("companySearch").value.trim();
  const durs = $("dursPath").value.trim();
  setStatus($("companyStatus"), "Nalagam…");
  try {
    const data = await apiJson(
      `/api/companies?q=${encodeURIComponent(q)}&durs_path=${encodeURIComponent(durs)}`
    );
    renderCompanies(data.companies || []);
    setStatus(
      $("companyStatus"),
      `Prikazano ${data.count} / ${data.total} firm.`,
      "ok"
    );
  } catch (err) {
    setStatus($("companyStatus"), err.message, "error");
  }
}

function renderTreeHead() {
  const head = $("treeHead");
  head.innerHTML = "";
  const tr = document.createElement("tr");
  const thLabel = document.createElement("th");
  thLabel.textContent = "Obdobje";
  tr.appendChild(thLabel);
  for (const col of treeState.columns.slice(3)) {
    const th = document.createElement("th");
    th.textContent = col;
    th.className = "num";
    tr.appendChild(th);
  }
  head.appendChild(tr);
}

function sumCells(node) {
  const formatted = node.formatted || {};
  return treeState.sumColumns.map((c) => formatted[c] || "");
}

function appendTreeRow(tbody, node, depth) {
  const tr = document.createElement("tr");
  tr.dataset.id = node.id;
  tr.dataset.kind = node.kind;

  const tdLabel = document.createElement("td");
  const wrap = document.createElement("div");
  wrap.className = "tree-label";
  wrap.style.paddingLeft = `${depth * 1.25}rem`;

  const canExpand =
    node.kind === "year" ||
    node.kind === "month" ||
    node.kind === "day" ||
    (node.children && node.children.length);

  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "tree-toggle" + (canExpand ? "" : " placeholder");
  const isOpen = treeState.expanded.has(node.id);
  btn.textContent = canExpand ? (isOpen ? "▼" : "▶") : "▶";
  if (canExpand) {
    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      toggleNode(node);
    });
  }

  const span = document.createElement("span");
  span.className = `tree-kind-${node.kind}`;
  span.textContent = node.label;

  wrap.appendChild(btn);
  wrap.appendChild(span);
  tdLabel.appendChild(wrap);
  tr.appendChild(tdLabel);

  for (const val of sumCells(node)) {
    const td = document.createElement("td");
    td.className = "num";
    td.textContent = val;
    tr.appendChild(td);
  }

  tbody.appendChild(tr);
}

function childrenForNode(node) {
  if (node.kind === "month" && treeState.monthChildren.has(node.id)) {
    return treeState.monthChildren.get(node.id) || [];
  }
  return node.children || [];
}

function renderTreeNodes(tbody, nodes, depth) {
  for (const node of nodes) {
    appendTreeRow(tbody, node, depth);
    if (!treeState.expanded.has(node.id)) continue;
    renderTreeNodes(tbody, childrenForNode(node), depth + 1);
  }
}

function renderTree() {
  renderTreeHead();
  const tbody = $("treeBody");
  tbody.innerHTML = "";
  renderTreeNodes(tbody, treeState.nodes, 0);
}

async function loadMonthDays(node) {
  const key = node.id;
  if (treeState.loadedMonths.has(key)) return;
  const data = await apiJson(`/api/tree/month/${node.yyyy}/${node.mm}`);
  treeState.monthChildren.set(key, data.children || []);
  treeState.loadedMonths.add(key);
}

async function toggleNode(node) {
  if (treeState.expanded.has(node.id)) {
    treeState.expanded.delete(node.id);
  } else {
    treeState.expanded.add(node.id);
    if (node.kind === "month") {
      try {
        await loadMonthDays(node);
      } catch (err) {
        setStatus($("analyzeMessage"), err.message, "error");
        treeState.expanded.delete(node.id);
        return;
      }
    }
  }
  renderTree();
}

function applyTreePayload(tree) {
  treeState.columns = tree.columns || [];
  treeState.sumColumns = tree.sum_columns || [];
  treeState.nodes = tree.nodes || [];
  treeState.expanded.clear();
  treeState.loadedMonths.clear();
  treeState.monthChildren.clear();
  renderTree();
}

async function analyze() {
  const root_path = $("rootPath").value.trim();
  if (!root_path) {
    setStatus($("analyzeMessage"), "Vnesi root mapo.", "error");
    return;
  }
  setStatus($("analyzeMessage"), "Analiziram…");
  $("btnAnalyze").disabled = true;
  try {
    const data = await apiJson("/api/analyze", {
      method: "POST",
      body: JSON.stringify({
        root_path,
        csv_name: $("csvName").value.trim() || "blagajne.csv",
        include_zips: $("includeZips").checked,
      }),
    });
    applyTreePayload(data.tree || {});
    if (data.ok) {
      setStatus($("analyzeMessage"), data.message, "ok");
    } else {
      const warn = (data.warnings || []).slice(0, 3).join(" ");
      setStatus($("analyzeMessage"), (data.message || "Brez podatkov.") + " " + warn, "error");
    }
  } catch (err) {
    setStatus($("analyzeMessage"), err.message, "error");
  } finally {
    $("btnAnalyze").disabled = false;
  }
}

function expandAll() {
  for (const node of treeState.nodes) {
    if (node.kind === "year") treeState.expanded.add(node.id);
    if (node.children) {
      for (const ch of node.children) {
        if (ch.kind === "month") treeState.expanded.add(ch.id);
      }
    }
  }
  Promise.all(
    [...treeState.expanded]
      .filter((id) => id.startsWith("month:"))
      .map(async (id) => {
        const [_, yyyy, mm] = id.split(":");
        if (!treeState.loadedMonths.has(id)) {
          const data = await apiJson(`/api/tree/month/${yyyy}/${mm}`);
          treeState.monthChildren.set(id, data.children || []);
          treeState.loadedMonths.add(id);
        }
      })
  )
    .then(() => renderTree())
    .catch((err) => setStatus($("analyzeMessage"), err.message, "error"));
}

function collapseAll() {
  treeState.expanded.clear();
  renderTree();
}

$("btnLoadCompanies").addEventListener("click", loadCompanies);
$("companySearch").addEventListener("keydown", (e) => {
  if (e.key === "Enter") loadCompanies();
});
$("btnAnalyze").addEventListener("click", analyze);
$("btnExpandAll").addEventListener("click", expandAll);
$("btnCollapseAll").addEventListener("click", collapseAll);

renderTreeHead();
