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

// ── Drawing ─────────────────────────────────

function drawParallel(canvas, axes, runs, opts) {
  const { width, height, hiddenStatuses, hoveredRun } = opts;
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

  // Draw axes
  ctx.strokeStyle = "#ccc";
  ctx.lineWidth = 1;
  ctx.setLineDash([]);
  for (let i = 0; i < axes.length; i++) {
    const x = axisX(i);
    ctx.beginPath();
    ctx.moveTo(x, pad.top);
    ctx.lineTo(x, pad.top + plotH);
    ctx.stroke();

    // Axis label
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

    // Tick labels for domain
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

  // Draw run polylines
  const visibleRuns = runs.filter(r => !hiddenStatuses.has(r.status));

  // Draw non-hovered runs first, then hovered on top
  const bgRuns = hoveredRun ? visibleRuns.filter(r => r.run_id !== hoveredRun) : visibleRuns;
  const fgRuns = hoveredRun ? visibleRuns.filter(r => r.run_id === hoveredRun) : [];

  for (const r of bgRuns) {
    drawRunLine(ctx, r, axes, axisX, pad, plotH, hoveredRun ? 0.25 : 0.6);
  }
  for (const r of fgRuns) {
    drawRunLine(ctx, r, axes, axisX, pad, plotH, 1.0, 3);
  }
}

function drawRunLine(ctx, run, axes, axisX, pad, plotH, alpha, lineWidth) {
  const color = STATUS_COLORS[run.status] || STATUS_COLORS.UNKNOWN;
  const dash = STATUS_DASH[run.status] || STATUS_DASH.UNKNOWN;

  ctx.save();
  ctx.globalAlpha = alpha;
  ctx.strokeStyle = color;
  ctx.lineWidth = lineWidth || 1.5;
  ctx.setLineDash(dash);
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

  // Draw dots at axis intersections
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

function findHoveredRun(mx, my, axes, runs, axisX, pad, plotH, hiddenStatuses) {
  let bestDist = 15;
  let bestRun = null;

  const visibleRuns = runs.filter(r => !hiddenStatuses.has(r.status));
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

// ── Widget render ───────────────────────────

function render({ model, el }) {
  const w = model.get("width") || 900;

  const container = document.createElement("div");
  container.style.fontFamily = "system-ui, sans-serif";
  container.style.padding = "12px";
  container.style.width = w + "px";
  container.style.boxSizing = "border-box";

  // ── Status filter row ──
  const filterRow = document.createElement("div");
  filterRow.style.cssText = "display:flex;align-items:center;gap:12px;margin-bottom:8px;font-size:12px;flex-wrap:wrap";

  const filterLabel = document.createElement("span");
  filterLabel.textContent = "Filter by status:";
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
      redraw();
    });
  }

  function updateCounts() {
    const runs = model.get("_runs_data") || [];
    const counts = {};
    for (const s of Object.keys(STATUS_LABELS)) counts[s] = 0;
    for (const r of runs) {
      if (counts[r.status] != null) counts[r.status]++;
    }
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

  // ── Legend ──
  const legendRow = document.createElement("div");
  legendRow.style.cssText = "display:flex;gap:16px;margin-top:6px;font-size:11px;color:#888;flex-wrap:wrap";

  for (const [status, label] of Object.entries(STATUS_LABELS)) {
    const item = document.createElement("div");
    item.style.cssText = "display:flex;align-items:center;gap:4px";

    const line = document.createElement("span");
    line.style.cssText = `display:inline-block;width:24px;height:0;border-top:2px ${STATUS_DASH[status].length > 0 ? "dashed" : "solid"} ${STATUS_COLORS[status]}`;

    const text = document.createElement("span");
    text.textContent = label;

    item.appendChild(line);
    item.appendChild(text);
    legendRow.appendChild(item);
  }

  container.appendChild(filterRow);
  container.appendChild(toolbar);
  container.appendChild(chartWrapper);
  container.appendChild(legendRow);
  el.appendChild(container);

  let hoveredRun = null;

  function redraw() {
    const axes = model.get("_axes_data") || [];
    const runs = model.get("_runs_data") || [];
    const w = model.get("width") || 900;
    const h = model.get("height") || 400;
    statusEl.textContent = model.get("_status") || "";

    drawParallel(chartCanvas, axes, runs, {
      width: w, height: h, hiddenStatuses, hoveredRun: hoveredRun ? hoveredRun.run_id : null,
    });
  }

  // ── Events ──

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

    const hit = findHoveredRun(mx, my, axes, runs, axisX, pad, plotH, hiddenStatuses);

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

      let tx = mx + 14;
      let ty = my - 10;
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

  model.on("change:_axes_data", () => { updateCounts(); redraw(); });
  model.on("change:_runs_data", () => { updateCounts(); redraw(); });
  model.on("change:_status", () => { statusEl.textContent = model.get("_status") || ""; });

  updateCounts();
  redraw();
}

export default { render };
