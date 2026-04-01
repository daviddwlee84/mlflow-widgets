// ── Status colors and styles ────────────────

const STATUS_COLORS = {
  FINISHED: "#59a14f",
  RUNNING:  "#f28e2b",
  FAILED:   "#e15759",
  KILLED:   "#bab0ac",
  UNKNOWN:  "#999",
};

const STATUS_DASH = {
  FINISHED: [],
  RUNNING:  [6, 3],
  FAILED:   [2, 3],
  KILLED:   [8, 4],
  UNKNOWN:  [4, 4],
};

const STATUS_LABELS = {
  FINISHED: "finished",
  RUNNING:  "running",
  FAILED:   "failed",
  KILLED:   "killed",
};

const COLORS = [
  "#4e79a7","#f28e2b","#e15759","#76b7b2","#59a14f",
  "#edc948","#b07aa1","#ff9da7","#9c755f","#bab0ac"
];

function lerpColor(a, b, t) {
  const ah = parseInt(a.slice(1), 16), bh = parseInt(b.slice(1), 16);
  const ar = (ah >> 16) & 0xff, ag = (ah >> 8) & 0xff, ab = ah & 0xff;
  const br = (bh >> 16) & 0xff, bg = (bh >> 8) & 0xff, bb = bh & 0xff;
  const r = Math.round(ar + (br - ar) * t);
  const g = Math.round(ag + (bg - ag) * t);
  const bl = Math.round(ab + (bb - ab) * t);
  return "#" + ((1 << 24) | (r << 16) | (g << 8) | bl).toString(16).slice(1);
}

// ── Color resolver ──────────────────────────

function resolveRunColor(run, runIndex, colorMode, axes, runs) {
  if (colorMode === "status") {
    return { color: STATUS_COLORS[run.status] || STATUS_COLORS.UNKNOWN, dash: STATUS_DASH[run.status] || STATUS_DASH.UNKNOWN };
  }
  if (colorMode === "run") {
    return { color: COLORS[runIndex % COLORS.length], dash: [] };
  }
  if (colorMode.startsWith("param:")) {
    const axName = colorMode.slice(6);
    const ax = axes.find(a => a.name === axName);
    if (ax && ax.type === "categorical") {
      const val = run.raw_values[axName];
      const idx = ax.domain.indexOf(String(val));
      return { color: COLORS[(idx >= 0 ? idx : 0) % COLORS.length], dash: [] };
    }
    return { color: "#999", dash: [] };
  }
  if (colorMode.startsWith("metric:")) {
    const axName = colorMode.slice(7);
    const norm = run.values[axName];
    if (norm != null) {
      return { color: lerpColor("#4e79a7", "#e15759", norm), dash: [] };
    }
    return { color: "#999", dash: [4, 4] };
  }
  return { color: "#999", dash: [] };
}

// ── Drawing ─────────────────────────────────

function drawParallel(canvas, axes, runs, opts) {
  const { width, height, hiddenRunIds, hoveredRun, colorMode } = opts;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  canvas.style.width = width + "px";
  canvas.style.height = height + "px";

  const ctx = canvas.getContext("2d");
  ctx.scale(dpr, dpr);
  ctx.clearRect(0, 0, width, height);

  if (axes.length === 0) {
    ctx.fillStyle = "#999";
    ctx.font = "13px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("No axes to display", width / 2, height / 2);
    return;
  }

  const pad = { top: 50, bottom: 60, left: 60, right: 40 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;

  const axisSpacing = axes.length > 1 ? plotW / (axes.length - 1) : 0;
  const axisX = (i) => pad.left + i * axisSpacing;

  ctx.strokeStyle = "#ccc";
  ctx.lineWidth = 1;
  ctx.setLineDash([]);
  for (let i = 0; i < axes.length; i++) {
    const x = axisX(i);
    ctx.beginPath();
    ctx.moveTo(x, pad.top);
    ctx.lineTo(x, pad.top + plotH);
    ctx.stroke();

    ctx.save();
    ctx.fillStyle = "#333";
    ctx.font = "bold 11px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "top";
    const label = axes[i].name;
    const maxLen = Math.floor(axisSpacing / 7) || 12;
    const display = label.length > maxLen ? label.slice(0, maxLen - 1) + "\u2026" : label;
    ctx.fillText(display, x, pad.top + plotH + 8);
    ctx.restore();

    const ax = axes[i];
    ctx.fillStyle = "#888";
    ctx.font = "10px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.textBaseline = "bottom";

    if (ax.type === "numeric") {
      const lo = ax.domain[0], hi = ax.domain[1];
      ctx.fillText(formatNum(hi), x, pad.top - 4);
      ctx.textBaseline = "top";
      ctx.fillText(formatNum(lo), x, pad.top + plotH + 22);
    } else if (ax.type === "categorical") {
      const cats = ax.domain;
      for (let ci = 0; ci < cats.length; ci++) {
        const norm = cats.length > 1 ? ci / (cats.length - 1) : 0.5;
        const y = pad.top + plotH - norm * plotH;
        ctx.textBaseline = "middle";
        ctx.textAlign = "right";
        ctx.fillText(cats[ci], x - 6, y);
        ctx.beginPath();
        ctx.arc(x, y, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = "#ccc";
        ctx.fill();
        ctx.fillStyle = "#888";
      }
    }
  }

  const visibleRuns = runs.filter(r => !hiddenRunIds.has(r.run_id));
  const bgRuns = hoveredRun ? visibleRuns.filter(r => r.run_id !== hoveredRun) : visibleRuns;
  const fgRuns = hoveredRun ? visibleRuns.filter(r => r.run_id === hoveredRun) : [];

  for (const r of bgRuns) {
    const ri = runs.indexOf(r);
    const { color, dash } = resolveRunColor(r, ri, colorMode, axes, runs);
    drawRunLine(ctx, r, axes, axisX, pad, plotH, hoveredRun ? 0.25 : 0.6, undefined, color, dash);
  }
  for (const r of fgRuns) {
    const ri = runs.indexOf(r);
    const { color } = resolveRunColor(r, ri, colorMode, axes, runs);
    drawRunLine(ctx, r, axes, axisX, pad, plotH, 1.0, 3, color, []);
  }
}

function drawRunLine(ctx, run, axes, axisX, pad, plotH, alpha, lineWidth, color, dash) {
  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = color;
  ctx.lineWidth = lineWidth || 1.5;
  ctx.setLineDash(dash || []);
  ctx.lineJoin = "round";

  ctx.beginPath();
  let started = false;
  for (let i = 0; i < axes.length; i++) {
    const norm = run.values[axes[i].name];
    if (norm == null) continue;
    const x = axisX(i);
    const y = pad.top + plotH - norm * plotH;
    if (!started) { ctx.moveTo(x, y); started = true; }
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  for (let i = 0; i < axes.length; i++) {
    const norm = run.values[axes[i].name];
    if (norm == null) continue;
    const x = axisX(i);
    const y = pad.top + plotH - norm * plotH;
    ctx.setLineDash([]);
    ctx.beginPath();
    ctx.arc(x, y, lineWidth > 2 ? 4 : 2.5, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
  }

  ctx.restore();
}

function formatNum(v) {
  if (v == null) return "-";
  if (Number.isInteger(v)) return String(v);
  if (Math.abs(v) >= 100) return v.toFixed(1);
  if (Math.abs(v) >= 1) return v.toFixed(3);
  return v.toPrecision(3);
}

// ── Hit testing ─────────────────────────────

function findHoveredRun(mx, my, axes, runs, axisX, pad, plotH, hiddenRunIds) {
  let bestDist = 15;
  let bestRun = null;
  const visibleRuns = runs.filter(r => !hiddenRunIds.has(r.run_id));
  for (const r of visibleRuns) {
    for (let i = 0; i < axes.length; i++) {
      const norm = r.values[axes[i].name];
      if (norm == null) continue;
      const x = axisX(i);
      const y = pad.top + plotH - norm * plotH;
      const dx = x - mx, dy = y - my;
      const d = Math.sqrt(dx * dx + dy * dy);
      if (d < bestDist) { bestDist = d; bestRun = r; }
    }
  }
  return bestRun;
}

// ── Filter helpers ──────────────────────────

function computeHiddenRunIds(runs, hiddenStatuses, axisFilters, axes) {
  const hidden = new Set();
  for (const r of runs) {
    if (hiddenStatuses.has(r.status)) { hidden.add(r.run_id); continue; }
    for (const ax of axes) {
      const f = axisFilters.get(ax.name);
      if (!f) continue;
      if (ax.type === "categorical") {
        const val = String(r.raw_values[ax.name] ?? "");
        if (f.hiddenValues && f.hiddenValues.has(val)) { hidden.add(r.run_id); break; }
      } else if (ax.type === "numeric") {
        const raw = r.raw_values[ax.name];
        if (raw == null) continue;
        const v = typeof raw === "number" ? raw : parseFloat(raw);
        if (isNaN(v)) continue;
        if (v < f.min || v > f.max) { hidden.add(r.run_id); break; }
      }
    }
  }
  return hidden;
}

// ── Widget render ───────────────────────────

function render({ model, el }) {
  const w = model.get("width") || 900;
  const selectStyle = "font-size:12px;padding:1px 4px;border:1px solid #ccc;border-radius:3px;background:#fff;font-family:system-ui,sans-serif";

  const container = document.createElement("div");
  container.style.fontFamily = "system-ui, sans-serif";
  container.style.padding = "12px";
  container.style.width = w + "px";
  container.style.boxSizing = "border-box";

  // ── Status filter row ──
  const filterRow = document.createElement("div");
  filterRow.style.cssText = "display:flex;align-items:center;gap:12px;margin-bottom:8px;font-size:12px;flex-wrap:wrap";

  const filterLabel = document.createElement("span");
  filterLabel.textContent = "Status:";
  filterLabel.style.color = "#666";
  filterLabel.style.fontWeight = "500";
  filterRow.appendChild(filterLabel);

  const hiddenStatuses = new Set();
  const statusCheckboxes = {};

  for (const [status, info] of Object.entries(STATUS_LABELS)) {
    const label = document.createElement("label");
    label.style.cssText = "display:flex;align-items:center;gap:4px;cursor:pointer;user-select:none";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = true;
    statusCheckboxes[status] = cb;
    const colorDot = document.createElement("span");
    colorDot.style.cssText = `display:inline-block;width:10px;height:10px;border-radius:50%;background:${STATUS_COLORS[status]}`;
    const text = document.createElement("span");
    text.style.color = "#555";
    label.appendChild(cb);
    label.appendChild(colorDot);
    label.appendChild(text);
    filterRow.appendChild(label);
    cb.addEventListener("change", () => {
      if (cb.checked) hiddenStatuses.delete(status);
      else hiddenStatuses.add(status);
      updateCounts();
      recomputeAndRedraw();
    });
  }

  // ── Color mode row ──
  const colorRow = document.createElement("div");
  colorRow.style.cssText = "display:flex;align-items:center;gap:8px;margin-bottom:8px;font-size:12px";

  const colorLabel = document.createElement("span");
  colorLabel.textContent = "Color by:";
  colorLabel.style.cssText = "color:#666;font-weight:500";

  const colorSelect = document.createElement("select");
  colorSelect.style.cssText = selectStyle;

  let colorMode = "status";

  function rebuildColorOptions() {
    const axes = model.get("_axes_data") || [];
    colorSelect.innerHTML = "";
    for (const [val, txt] of [["status", "Status"], ["run", "Per run"]]) {
      const o = document.createElement("option");
      o.value = val; o.textContent = txt;
      if (val === colorMode) o.selected = true;
      colorSelect.appendChild(o);
    }
    for (const ax of axes) {
      if (ax.type === "categorical") {
        const o = document.createElement("option");
        o.value = "param:" + ax.name; o.textContent = ax.name;
        if (o.value === colorMode) o.selected = true;
        colorSelect.appendChild(o);
      }
    }
    for (const ax of axes) {
      if (ax.type === "numeric" && ax.is_metric) {
        const o = document.createElement("option");
        o.value = "metric:" + ax.name; o.textContent = ax.name + " (gradient)";
        if (o.value === colorMode) o.selected = true;
        colorSelect.appendChild(o);
      }
    }
  }

  colorRow.appendChild(colorLabel);
  colorRow.appendChild(colorSelect);

  // ── Axis filter panel ──
  const axisFilterPanel = document.createElement("div");
  axisFilterPanel.style.cssText = "margin-bottom:8px;font-size:12px";

  const axisFilterToggle = document.createElement("button");
  axisFilterToggle.textContent = "\u25b6 Param/Metric Filters";
  axisFilterToggle.style.cssText = "padding:2px 8px;font-size:11px;cursor:pointer;border:1px solid #ddd;border-radius:3px;background:#fafafa;font-family:system-ui,sans-serif;color:#666;margin-bottom:4px";
  let filtersOpen = false;

  const axisFilterContent = document.createElement("div");
  axisFilterContent.style.cssText = "display:none;padding:6px 8px;border:1px solid #eee;border-radius:4px;background:#fafbff;max-height:200px;overflow-y:auto";

  const axisFilters = new Map();

  function buildAxisFilters() {
    const axes = model.get("_axes_data") || [];
    const runs = model.get("_runs_data") || [];
    axisFilterContent.innerHTML = "";
    axisFilters.clear();

    for (const ax of axes) {
      const row = document.createElement("div");
      row.style.cssText = "display:flex;align-items:center;gap:6px;margin-bottom:4px;flex-wrap:wrap";

      const lbl = document.createElement("span");
      lbl.textContent = ax.name + ":";
      lbl.style.cssText = "font-weight:500;color:#555;min-width:80px;font-size:11px";
      row.appendChild(lbl);

      if (ax.type === "categorical") {
        const filter = { hiddenValues: new Set() };
        axisFilters.set(ax.name, filter);
        for (const cat of ax.domain) {
          const catLabel = document.createElement("label");
          catLabel.style.cssText = "display:flex;align-items:center;gap:2px;cursor:pointer;user-select:none;font-size:11px";
          const cb = document.createElement("input");
          cb.type = "checkbox"; cb.checked = true;
          cb.addEventListener("change", () => {
            if (cb.checked) filter.hiddenValues.delete(cat);
            else filter.hiddenValues.add(cat);
            recomputeAndRedraw();
          });
          const span = document.createElement("span");
          span.textContent = cat;
          catLabel.appendChild(cb);
          catLabel.appendChild(span);
          row.appendChild(catLabel);
        }
      } else if (ax.type === "numeric") {
        const lo = ax.domain[0], hi = ax.domain[1];
        const filter = { min: lo, max: hi };
        axisFilters.set(ax.name, filter);

        const minInput = document.createElement("input");
        minInput.type = "number"; minInput.value = lo; minInput.step = "any";
        minInput.style.cssText = "width:70px;font-size:11px;padding:1px 3px;border:1px solid #ccc;border-radius:2px";
        const sep = document.createElement("span");
        sep.textContent = " \u2013 ";
        sep.style.color = "#999";
        const maxInput = document.createElement("input");
        maxInput.type = "number"; maxInput.value = hi; maxInput.step = "any";
        maxInput.style.cssText = "width:70px;font-size:11px;padding:1px 3px;border:1px solid #ccc;border-radius:2px";

        minInput.addEventListener("change", () => { filter.min = parseFloat(minInput.value) || lo; recomputeAndRedraw(); });
        maxInput.addEventListener("change", () => { filter.max = parseFloat(maxInput.value) || hi; recomputeAndRedraw(); });

        row.appendChild(minInput);
        row.appendChild(sep);
        row.appendChild(maxInput);
      }
      axisFilterContent.appendChild(row);
    }
  }

  axisFilterToggle.addEventListener("click", () => {
    filtersOpen = !filtersOpen;
    axisFilterContent.style.display = filtersOpen ? "block" : "none";
    axisFilterToggle.textContent = (filtersOpen ? "\u25bc" : "\u25b6") + " Param/Metric Filters";
  });

  axisFilterPanel.appendChild(axisFilterToggle);
  axisFilterPanel.appendChild(axisFilterContent);

  function updateCounts() {
    const runs = model.get("_runs_data") || [];
    const counts = {};
    for (const s of Object.keys(STATUS_LABELS)) counts[s] = 0;
    for (const r of runs) { if (counts[r.status] != null) counts[r.status]++; }
    for (const [status, info] of Object.entries(STATUS_LABELS)) {
      const label = statusCheckboxes[status].parentElement;
      const text = label.querySelector("span:last-child");
      text.textContent = `${info} (${counts[status]})`;
    }
  }

  // ── Toolbar ──
  const toolbar = document.createElement("div");
  toolbar.style.cssText = "display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;font-size:13px;color:#666";

  const statusEl = document.createElement("span");
  statusEl.textContent = model.get("_status") || "";

  const refreshBtn = document.createElement("button");
  refreshBtn.textContent = "\u21bb Refresh";
  refreshBtn.style.cssText = "padding:2px 8px;font-size:12px;cursor:pointer;border:1px solid #ccc;border-radius:4px;background:#f5f5f5;font-family:system-ui,sans-serif";

  toolbar.appendChild(statusEl);
  toolbar.appendChild(refreshBtn);

  // ── Canvas + tooltip ──
  const chartCanvas = document.createElement("canvas");
  chartCanvas.style.display = "block";

  const tooltip = document.createElement("div");
  tooltip.style.cssText = "position:absolute;display:none;background:rgba(0,0,0,0.85);color:#fff;padding:8px 12px;border-radius:6px;font-size:12px;pointer-events:none;white-space:pre-line;z-index:10;max-width:300px;line-height:1.5";

  const chartWrapper = document.createElement("div");
  chartWrapper.style.position = "relative";
  chartWrapper.style.display = "inline-block";
  chartWrapper.appendChild(chartCanvas);
  chartWrapper.appendChild(tooltip);

  // ── Dynamic legend ──
  const legendRow = document.createElement("div");
  legendRow.style.cssText = "display:flex;gap:12px;margin-top:6px;font-size:11px;color:#888;flex-wrap:wrap;align-items:center";

  function rebuildLegend() {
    legendRow.innerHTML = "";
    const axes = model.get("_axes_data") || [];
    const runs = model.get("_runs_data") || [];

    if (colorMode === "status") {
      for (const [status, label] of Object.entries(STATUS_LABELS)) {
        const item = document.createElement("div");
        item.style.cssText = "display:flex;align-items:center;gap:4px";
        const line = document.createElement("span");
        line.style.cssText = `display:inline-block;width:20px;height:0;border-top:2px ${STATUS_DASH[status].length > 0 ? "dashed" : "solid"} ${STATUS_COLORS[status]}`;
        const text = document.createElement("span");
        text.textContent = label;
        item.appendChild(line);
        item.appendChild(text);
        legendRow.appendChild(item);
      }
    } else if (colorMode === "run") {
      for (let i = 0; i < runs.length; i++) {
        const item = document.createElement("div");
        item.style.cssText = "display:flex;align-items:center;gap:4px";
        const dot = document.createElement("span");
        dot.style.cssText = `display:inline-block;width:10px;height:10px;border-radius:50%;background:${COLORS[i % COLORS.length]}`;
        const text = document.createElement("span");
        text.textContent = runs[i].run_name;
        item.appendChild(dot);
        item.appendChild(text);
        legendRow.appendChild(item);
      }
    } else if (colorMode.startsWith("param:")) {
      const axName = colorMode.slice(6);
      const ax = axes.find(a => a.name === axName);
      if (ax && ax.type === "categorical") {
        for (let i = 0; i < ax.domain.length; i++) {
          const item = document.createElement("div");
          item.style.cssText = "display:flex;align-items:center;gap:4px";
          const dot = document.createElement("span");
          dot.style.cssText = `display:inline-block;width:10px;height:10px;border-radius:50%;background:${COLORS[i % COLORS.length]}`;
          const text = document.createElement("span");
          text.textContent = ax.domain[i];
          item.appendChild(dot);
          item.appendChild(text);
          legendRow.appendChild(item);
        }
      }
    } else if (colorMode.startsWith("metric:")) {
      const bar = document.createElement("div");
      bar.style.cssText = "display:flex;align-items:center;gap:4px";
      const grad = document.createElement("span");
      grad.style.cssText = "display:inline-block;width:80px;height:10px;border-radius:2px;background:linear-gradient(to right,#4e79a7,#e15759)";
      const lo = document.createElement("span");
      lo.textContent = "low";
      const hi = document.createElement("span");
      hi.textContent = "high";
      bar.appendChild(lo);
      bar.appendChild(grad);
      bar.appendChild(hi);
      legendRow.appendChild(bar);
    }
  }

  container.appendChild(filterRow);
  container.appendChild(colorRow);
  container.appendChild(axisFilterPanel);
  container.appendChild(toolbar);
  container.appendChild(chartWrapper);
  container.appendChild(legendRow);
  el.appendChild(container);

  let hoveredRun = null;
  let hiddenRunIds = new Set();

  function recomputeAndRedraw() {
    const axes = model.get("_axes_data") || [];
    const runs = model.get("_runs_data") || [];
    hiddenRunIds = computeHiddenRunIds(runs, hiddenStatuses, axisFilters, axes);
    redraw();
  }

  function redraw() {
    const axes = model.get("_axes_data") || [];
    const runs = model.get("_runs_data") || [];
    const w = model.get("width") || 900;
    const h = model.get("height") || 400;
    statusEl.textContent = model.get("_status") || "";

    drawParallel(chartCanvas, axes, runs, {
      width: w, height: h, hiddenRunIds, hoveredRun: hoveredRun ? hoveredRun.run_id : null, colorMode,
    });
  }

  // ── Events ──

  colorSelect.addEventListener("change", () => {
    colorMode = colorSelect.value;
    rebuildLegend();
    redraw();
  });

  refreshBtn.addEventListener("click", () => {
    model.set("_do_refresh", (model.get("_do_refresh") || 0) + 1);
    model.save_changes();
  });

  chartCanvas.addEventListener("mousemove", (e) => {
    const axes = model.get("_axes_data") || [];
    const runs = model.get("_runs_data") || [];
    if (axes.length === 0 || runs.length === 0) { tooltip.style.display = "none"; return; }

    const rect = chartCanvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;

    const w = model.get("width") || 900;
    const h = model.get("height") || 400;
    const pad = { top: 50, bottom: 60, left: 60, right: 40 };
    const plotW = w - pad.left - pad.right;
    const plotH = h - pad.top - pad.bottom;
    const axisSpacing = axes.length > 1 ? plotW / (axes.length - 1) : 0;
    const axisX = (i) => pad.left + i * axisSpacing;

    const hit = findHoveredRun(mx, my, axes, runs, axisX, pad, plotH, hiddenRunIds);

    if (hit) {
      hoveredRun = hit;
      redraw();
      const lines = [hit.run_name + " (" + (STATUS_LABELS[hit.status] || hit.status) + ")"];
      for (const ax of axes) {
        const raw = hit.raw_values[ax.name];
        const formatted = raw != null ? (typeof raw === "number" ? formatNum(raw) : raw) : "-";
        lines.push(ax.name + ": " + formatted);
      }
      tooltip.textContent = lines.join("\n");
      tooltip.style.display = "block";
      let tx = mx + 14, ty = my - 10;
      if (tx + 200 > w) tx = mx - 200;
      if (ty < 0) ty = my + 14;
      tooltip.style.left = tx + "px";
      tooltip.style.top = ty + "px";
    } else {
      if (hoveredRun) { hoveredRun = null; redraw(); }
      tooltip.style.display = "none";
    }
  });

  chartCanvas.addEventListener("mouseleave", () => {
    tooltip.style.display = "none";
    if (hoveredRun) { hoveredRun = null; redraw(); }
  });

  function onDataChange() {
    updateCounts();
    rebuildColorOptions();
    buildAxisFilters();
    rebuildLegend();
    recomputeAndRedraw();
  }

  model.on("change:_axes_data", onDataChange);
  model.on("change:_runs_data", onDataChange);
  model.on("change:_status", () => { statusEl.textContent = model.get("_status") || ""; });

  onDataChange();
}

export default { render };
