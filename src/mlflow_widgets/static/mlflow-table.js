function formatDuration(seconds) {
  if (seconds == null) return "-";
  if (seconds < 60) return seconds.toFixed(1) + "s";
  if (seconds < 3600) return (seconds / 60).toFixed(1) + "m";
  return (seconds / 3600).toFixed(1) + "h";
}

function formatTime(ms) {
  if (!ms) return "-";
  const d = new Date(ms);
  return d.toLocaleString(undefined, {
    month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit", second: "2-digit",
  });
}

function formatMetric(v) {
  if (v == null) return "-";
  if (typeof v === "number") {
    if (Number.isInteger(v)) return String(v);
    return v.toPrecision(5);
  }
  return String(v);
}

const STATUS_BADGE = {
  FINISHED: { bg: "#e6f4ea", fg: "#1e7e34", label: "finished" },
  RUNNING:  { bg: "#fff3cd", fg: "#856404", label: "running"  },
  FAILED:   { bg: "#f8d7da", fg: "#721c24", label: "failed"   },
  KILLED:   { bg: "#f5f5f5", fg: "#666",    label: "killed"   },
};

function buildTree(data) {
  const byId = new Map();
  for (const row of data) byId.set(row.run_id, row);

  const roots = [];
  const childrenOf = new Map();
  for (const row of data) {
    const pid = row.parent_run_id;
    if (pid && byId.has(pid)) {
      if (!childrenOf.has(pid)) childrenOf.set(pid, []);
      childrenOf.get(pid).push(row);
    } else {
      roots.push(row);
    }
  }
  return { roots, childrenOf };
}

function flattenTree(roots, childrenOf, expanded, sortFn) {
  const result = [];
  const sorted = sortFn ? [...roots].sort(sortFn) : roots;
  for (const row of sorted) {
    const children = childrenOf.get(row.run_id) || [];
    const hasChildren = children.length > 0;
    result.push({ row, depth: 0, hasChildren });
    if (hasChildren && expanded.has(row.run_id)) {
      const sortedChildren = sortFn ? [...children].sort(sortFn) : children;
      for (const child of sortedChildren) {
        const grandchildren = childrenOf.get(child.run_id) || [];
        result.push({ row: child, depth: 1, hasChildren: grandchildren.length > 0 });
        if (grandchildren.length > 0 && expanded.has(child.run_id)) {
          const sortedGC = sortFn ? [...grandchildren].sort(sortFn) : grandchildren;
          for (const gc of sortedGC) {
            result.push({ row: gc, depth: 2, hasChildren: false });
          }
        }
      }
    }
  }
  return result;
}

function render({ model, el }) {
  const container = document.createElement("div");
  container.style.fontFamily = "system-ui, sans-serif";
  container.style.padding = "12px";
  container.style.boxSizing = "border-box";
  container.style.overflowX = "auto";

  const toolbar = document.createElement("div");
  toolbar.style.cssText = "display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;font-size:13px;color:#666";

  const statusEl = document.createElement("span");
  statusEl.textContent = model.get("_status") || "";

  const refreshBtn = document.createElement("button");
  refreshBtn.textContent = "\u21bb Refresh";
  refreshBtn.style.cssText = "padding:2px 8px;font-size:12px;cursor:pointer;border:1px solid #ccc;border-radius:4px;background:#f5f5f5;font-family:system-ui,sans-serif";

  const pollSec = model.get("poll_seconds");
  const autoLabel = document.createElement("span");
  autoLabel.style.cssText = "font-size:11px;color:#999;margin-left:8px";
  if (pollSec != null) {
    autoLabel.textContent = "(auto-refresh every " + pollSec + "s)";
  }

  toolbar.appendChild(statusEl);
  if (pollSec != null) toolbar.appendChild(autoLabel);
  toolbar.appendChild(refreshBtn);

  const tableWrapper = document.createElement("div");
  tableWrapper.style.overflowX = "auto";

  container.appendChild(toolbar);
  container.appendChild(tableWrapper);
  el.appendChild(container);

  let sortCol = null;
  let sortAsc = true;
  const expanded = new Set();

  function makeSortFn() {
    if (!sortCol) return null;
    return (a, b) => {
      let va, vb;
      if (sortCol === "run_name" || sortCol === "status") {
        va = (a[sortCol] || "").toLowerCase();
        vb = (b[sortCol] || "").toLowerCase();
      } else if (sortCol === "start_time" || sortCol === "duration_s") {
        va = a[sortCol] ?? -Infinity;
        vb = b[sortCol] ?? -Infinity;
      } else if (sortCol.startsWith("p:")) {
        const k = sortCol.slice(2);
        va = (a.params || {})[k] || "";
        vb = (b.params || {})[k] || "";
        const na = parseFloat(va), nb = parseFloat(vb);
        if (!isNaN(na) && !isNaN(nb)) { va = na; vb = nb; }
      } else if (sortCol.startsWith("m:")) {
        const k = sortCol.slice(2);
        va = (a.metrics || {})[k] ?? -Infinity;
        vb = (b.metrics || {})[k] ?? -Infinity;
      } else {
        va = 0; vb = 0;
      }
      if (va < vb) return sortAsc ? -1 : 1;
      if (va > vb) return sortAsc ? 1 : -1;
      return 0;
    };
  }

  function buildTable() {
    const data = model.get("_table_data") || [];
    const paramKeys = model.get("_param_keys") || [];
    const metricKeys = model.get("_metric_keys") || [];
    statusEl.textContent = model.get("_status") || "";

    if (data.length === 0) {
      tableWrapper.innerHTML = '<div style="color:#999;padding:20px;text-align:center">No runs found</div>';
      return;
    }

    const { roots, childrenOf } = buildTree(data);
    const hasNesting = childrenOf.size > 0;
    const flatRows = flattenTree(roots, childrenOf, expanded, makeSortFn());

    const table = document.createElement("table");
    table.style.cssText = "border-collapse:collapse;width:100%;font-size:13px";

    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    const columns = [
      { key: "run_name",   label: "Run Name" },
      { key: "status",     label: "Status" },
      { key: "start_time", label: "Started" },
      { key: "duration_s", label: "Duration" },
      ...paramKeys.map(k => ({ key: "p:" + k, label: "P: " + k })),
      ...metricKeys.map(k => ({ key: "m:" + k, label: "M: " + k })),
    ];

    for (const col of columns) {
      const th = document.createElement("th");
      th.style.cssText = "padding:6px 10px;text-align:left;border-bottom:2px solid #ddd;cursor:pointer;white-space:nowrap;user-select:none;background:#fafafa";
      const arrow = sortCol === col.key ? (sortAsc ? " \u25b2" : " \u25bc") : "";
      th.textContent = col.label + arrow;
      th.addEventListener("click", () => {
        if (sortCol === col.key) {
          sortAsc = !sortAsc;
        } else {
          sortCol = col.key;
          sortAsc = true;
        }
        buildTable();
      });
      headerRow.appendChild(th);
    }
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    for (const { row, depth, hasChildren } of flatRows) {
      const tr = document.createElement("tr");
      const bgDefault = depth > 0 ? "#fafbff" : "";
      tr.style.background = bgDefault;
      tr.addEventListener("mouseenter", () => { tr.style.background = "#f5f8ff"; });
      tr.addEventListener("mouseleave", () => { tr.style.background = bgDefault; });

      for (const col of columns) {
        const td = document.createElement("td");
        td.style.cssText = "padding:5px 10px;border-bottom:1px solid #eee;white-space:nowrap";

        if (col.key === "run_name") {
          const indent = depth * 20;
          td.style.paddingLeft = (10 + indent) + "px";
          td.style.fontWeight = "500";

          if (hasChildren && hasNesting) {
            const toggle = document.createElement("span");
            toggle.style.cssText = "cursor:pointer;display:inline-block;width:16px;font-size:11px;color:#888;user-select:none";
            const isExpanded = expanded.has(row.run_id);
            toggle.textContent = isExpanded ? "\u25bc" : "\u25b6";
            toggle.addEventListener("click", (e) => {
              e.stopPropagation();
              if (expanded.has(row.run_id)) expanded.delete(row.run_id);
              else expanded.add(row.run_id);
              buildTable();
            });
            td.appendChild(toggle);
          } else if (hasNesting) {
            const spacer = document.createElement("span");
            spacer.style.display = "inline-block";
            spacer.style.width = depth > 0 ? "16px" : "16px";
            if (depth > 0) {
              spacer.textContent = "\u2514";
              spacer.style.cssText = "display:inline-block;width:16px;color:#ccc;font-size:12px";
            }
            td.appendChild(spacer);
          }

          const nameSpan = document.createElement("span");
          nameSpan.textContent = row.run_name || row.run_id.slice(0, 8);
          td.appendChild(nameSpan);
          td.title = row.run_id;
        } else if (col.key === "status") {
          const badge = STATUS_BADGE[row.status] || { bg: "#f5f5f5", fg: "#666", label: row.status };
          const span = document.createElement("span");
          span.textContent = badge.label;
          span.style.cssText = `padding:2px 8px;border-radius:10px;font-size:11px;font-weight:500;background:${badge.bg};color:${badge.fg}`;
          td.appendChild(span);
        } else if (col.key === "start_time") {
          td.textContent = formatTime(row.start_time);
          td.style.color = "#666";
        } else if (col.key === "duration_s") {
          td.textContent = formatDuration(row.duration_s);
          td.style.color = "#666";
        } else if (col.key.startsWith("p:")) {
          const k = col.key.slice(2);
          td.textContent = (row.params || {})[k] || "-";
          td.style.color = "#555";
        } else if (col.key.startsWith("m:")) {
          const k = col.key.slice(2);
          td.textContent = formatMetric((row.metrics || {})[k]);
          td.style.fontFamily = "monospace";
        }

        tr.appendChild(td);
      }
      tbody.appendChild(tr);
    }
    table.appendChild(tbody);

    tableWrapper.innerHTML = "";
    tableWrapper.appendChild(table);
  }

  refreshBtn.addEventListener("click", () => {
    model.set("_do_refresh", (model.get("_do_refresh") || 0) + 1);
    model.save_changes();
  });

  model.on("change:_table_data", buildTable);
  model.on("change:_status", () => { statusEl.textContent = model.get("_status") || ""; });

  buildTable();
}

export default { render };
