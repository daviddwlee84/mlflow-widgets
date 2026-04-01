// ── Smoothing helpers ───────────────────────

function rollingMean(points, win) {
  if (win <= 1) return points;
  return points.map((p, i) => {
    const start = Math.max(0, i - win + 1);
    let sum = 0;
    for (let j = start; j <= i; j++) sum += points[j].y;
    return { x: p.x, y: sum / (i - start + 1) };
  });
}

function exponentialSmooth(points, alpha) {
  if (alpha <= 0 || points.length === 0) return points;
  const out = [{ x: points[0].x, y: points[0].y }];
  for (let i = 1; i < points.length; i++) {
    const prev = out[i - 1].y;
    out.push({ x: points[i].x, y: alpha * prev + (1 - alpha) * points[i].y });
  }
  return out;
}

function gaussianSmooth(points, sigma) {
  if (sigma <= 0 || points.length === 0) return points;
  const radius = Math.ceil(3 * sigma);
  const kernel = [];
  let kernelSum = 0;
  for (let j = -radius; j <= radius; j++) {
    const w = Math.exp(-0.5 * (j / sigma) * (j / sigma));
    kernel.push(w);
    kernelSum += w;
  }
  for (let j = 0; j < kernel.length; j++) kernel[j] /= kernelSum;

  return points.map((p, i) => {
    let sum = 0, wSum = 0;
    for (let j = -radius; j <= radius; j++) {
      const idx = i + j;
      if (idx < 0 || idx >= points.length) continue;
      const w = kernel[j + radius];
      sum += w * points[idx].y;
      wSum += w;
    }
    return { x: p.x, y: sum / wSum };
  });
}

// ── Series preparation ──────────────────────

const COLORS = [
  "#4e79a7","#f28e2b","#e15759","#76b7b2","#59a14f",
  "#edc948","#b07aa1","#ff9da7","#9c755f","#bab0ac"
];

const STATUS_COLORS = {
  FINISHED: "#1e7e34", RUNNING: "#856404", FAILED: "#721c24", KILLED: "#666", UNKNOWN: "#999",
};

const SLIDER_CONFIG = {
  rolling:     { label: "Rolling mean:",  min: 0,    max: 50,   step: 1,    fmt: v => v === 0 ? "off" : String(Math.round(v)), toParam: v => v < 2 ? null : v },
  exponential: { label: "EMA weight:",    min: 0,    max: 0.99, step: 0.01, fmt: v => v === 0 ? "off" : v.toFixed(2),          toParam: v => v === 0 ? null : v },
  gaussian:    { label: "Gaussian \u03c3:", min: 0,  max: 10,   step: 0.1,  fmt: v => v === 0 ? "off" : v.toFixed(1),          toParam: v => v === 0 ? null : v },
};

function prepareSeries(seriesData, smoothKind, smoothParam, xAxisMode) {
  return seriesData.map((s, i) => {
    const color = COLORS[i % COLORS.length];
    const rawPts = s.points || [];

    const raw = rawPts.map(p => {
      let x;
      if (xAxisMode === "wall") x = p.timestamp || 0;
      else if (xAxisMode === "relative") {
        const first = rawPts.length > 0 ? (rawPts[0].timestamp || 0) : 0;
        x = ((p.timestamp || 0) - first) / 1000.0;
      } else {
        x = p.step;
      }
      return { x, y: p.value };
    });

    let smoothed = raw;
    if (smoothParam != null && smoothParam > 0) {
      if (smoothKind === "rolling" && smoothParam >= 2)
        smoothed = rollingMean(raw, smoothParam);
      else if (smoothKind === "exponential")
        smoothed = exponentialSmooth(raw, smoothParam);
      else if (smoothKind === "gaussian")
        smoothed = gaussianSmooth(raw, smoothParam);
    }

    return {
      run_id: s.run_id || "",
      label: s.label || s.run_id || "run",
      parent_run_id: s.parent_run_id || null,
      status: s.status || "UNKNOWN",
      color,
      points: smoothed,
      raw: smoothed !== raw ? raw : [],
    };
  });
}

// ── X-axis formatting ───────────────────────

function formatXTick(v, mode) {
  if (mode === "wall") {
    const d = new Date(v);
    return d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  }
  if (mode === "relative") {
    if (v < 60) return v.toFixed(1) + "s";
    if (v < 3600) return (v / 60).toFixed(1) + "m";
    return (v / 3600).toFixed(1) + "h";
  }
  return Math.round(v).toString();
}

function formatXTooltip(v, mode) {
  if (mode === "wall") {
    const d = new Date(v);
    return d.toLocaleString();
  }
  if (mode === "relative") return formatXTick(v, mode);
  return "step " + Math.round(v);
}

function xAxisLabel(mode) {
  if (mode === "wall") return "wall time";
  if (mode === "relative") return "relative time";
  return "step";
}

// ── Canvas chart drawing ────────────────────

function drawChart(canvas, series, opts) {
  const { title, width, height, xAxisMode } = opts;
  const dpr = window.devicePixelRatio || 1;
  canvas.width = width * dpr;
  canvas.height = height * dpr;
  canvas.style.width = width + "px";
  canvas.style.height = height + "px";

  const ctx = canvas.getContext("2d");
  ctx.scale(dpr, dpr);

  const pad = { top: 30, right: 20, bottom: 40, left: 60 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;

  ctx.clearRect(0, 0, width, height);

  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (const s of series) {
    for (const p of s.points) {
      if (p.x < minX) minX = p.x;
      if (p.x > maxX) maxX = p.x;
      if (p.y < minY) minY = p.y;
      if (p.y > maxY) maxY = p.y;
    }
  }

  if (!isFinite(minX)) {
    ctx.fillStyle = "#999";
    ctx.font = "13px system-ui, sans-serif";
    ctx.textAlign = "center";
    ctx.fillText("Waiting for data\u2026", width / 2, height / 2);
    return;
  }

  const yPad = (maxY - minY) * 0.05 || 0.1;
  minY -= yPad;
  maxY += yPad;

  const scaleX = v => pad.left + ((v - minX) / (maxX - minX || 1)) * plotW;
  const scaleY = v => pad.top + plotH - ((v - minY) / (maxY - minY || 1)) * plotH;

  ctx.strokeStyle = "#e0e0e0";
  ctx.lineWidth = 0.5;
  ctx.setLineDash([4, 4]);

  const nY = 5;
  for (let i = 0; i <= nY; i++) {
    const y = scaleY(minY + (i / nY) * (maxY - minY));
    ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(pad.left + plotW, y); ctx.stroke();
  }
  const nX = 6;
  for (let i = 0; i <= nX; i++) {
    const x = scaleX(minX + (i / nX) * (maxX - minX));
    ctx.beginPath(); ctx.moveTo(x, pad.top); ctx.lineTo(x, pad.top + plotH); ctx.stroke();
  }
  ctx.setLineDash([]);

  ctx.fillStyle = "#666";
  ctx.font = "11px system-ui, sans-serif";
  ctx.textAlign = "right";
  ctx.textBaseline = "middle";
  for (let i = 0; i <= nY; i++) {
    const v = minY + (i / nY) * (maxY - minY);
    ctx.fillText(v.toPrecision(3), pad.left - 6, scaleY(v));
  }
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  for (let i = 0; i <= nX; i++) {
    const v = minX + (i / nX) * (maxX - minX);
    ctx.fillText(formatXTick(v, xAxisMode), scaleX(v), pad.top + plotH + 6);
  }

  ctx.fillStyle = "#333";
  ctx.font = "bold 13px system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "top";
  ctx.fillText(title, pad.left + plotW / 2, 6);

  ctx.fillStyle = "#999";
  ctx.font = "11px system-ui, sans-serif";
  ctx.fillText(xAxisLabel(xAxisMode), pad.left + plotW / 2, pad.top + plotH + 22);

  for (const s of series) {
    if (s.raw.length === 0) continue;
    ctx.globalAlpha = 0.2;
    ctx.strokeStyle = s.color;
    ctx.lineWidth = 1;
    ctx.beginPath();
    for (let i = 0; i < s.raw.length; i++) {
      const px = scaleX(s.raw[i].x), py = scaleY(s.raw[i].y);
      i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
    }
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  for (const s of series) {
    if (s.points.length === 0) continue;
    ctx.strokeStyle = s.color;
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    for (let i = 0; i < s.points.length; i++) {
      const px = scaleX(s.points[i].x), py = scaleY(s.points[i].y);
      i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
    }
    ctx.stroke();
  }
}

// ── Widget render ───────────────────────────

function render({ model, el }) {
  const w = model.get("width") || 700;
  const selectStyle = "font-size:12px;padding:1px 4px;border:1px solid #ccc;border-radius:3px;background:#fff;font-family:system-ui,sans-serif";

  const container = document.createElement("div");
  container.style.fontFamily = "system-ui, sans-serif";
  container.style.padding = "12px";
  container.style.width = w + "px";
  container.style.boxSizing = "border-box";

  // ── Controls row ──
  const controlsRow = document.createElement("div");
  controlsRow.style.cssText = "display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;font-size:13px;color:#666;flex-wrap:wrap;gap:8px";

  let kind = model.get("smoothing_kind") || "gaussian";
  let cfg = SLIDER_CONFIG[kind] || SLIDER_CONFIG.gaussian;

  const smoothGroup = document.createElement("div");
  smoothGroup.style.cssText = "display:flex;align-items:center;gap:8px";

  const kindSelect = document.createElement("select");
  kindSelect.style.cssText = selectStyle;
  for (const [value, label] of [["rolling", "Rolling"], ["exponential", "Exponential"], ["gaussian", "Gaussian"]]) {
    const opt = document.createElement("option");
    opt.value = value;
    opt.textContent = label;
    if (value === kind) opt.selected = true;
    kindSelect.appendChild(opt);
  }

  const smoothSlider = document.createElement("input");
  smoothSlider.type = "range";
  smoothSlider.min = String(cfg.min);
  smoothSlider.max = String(cfg.max);
  smoothSlider.step = String(cfg.step);
  const initParam = model.get("smoothing_param") ?? 0;
  smoothSlider.value = String(initParam);
  smoothSlider.style.width = "120px";

  const smoothValEl = document.createElement("span");
  smoothValEl.textContent = cfg.fmt(parseFloat(smoothSlider.value));

  function configureSlider() {
    cfg = SLIDER_CONFIG[kind] || SLIDER_CONFIG.gaussian;
    smoothSlider.min = String(cfg.min);
    smoothSlider.max = String(cfg.max);
    smoothSlider.step = String(cfg.step);
    smoothSlider.value = "0";
    smoothValEl.textContent = "off";
  }

  smoothGroup.appendChild(kindSelect);
  smoothGroup.appendChild(smoothSlider);
  smoothGroup.appendChild(smoothValEl);
  if (model.get("show_slider")) controlsRow.appendChild(smoothGroup);

  // X-axis mode selector
  const xGroup = document.createElement("div");
  xGroup.style.cssText = "display:flex;align-items:center;gap:4px";
  const xLabel = document.createElement("span");
  xLabel.textContent = "X-axis:";
  xLabel.style.cssText = "color:#666;font-size:12px";
  const xSelect = document.createElement("select");
  xSelect.style.cssText = selectStyle;
  let xAxisMode = model.get("x_axis") || "step";
  for (const [val, txt] of [["step", "Step"], ["wall", "Wall time"], ["relative", "Relative time"]]) {
    const o = document.createElement("option");
    o.value = val; o.textContent = txt;
    if (val === xAxisMode) o.selected = true;
    xSelect.appendChild(o);
  }
  xGroup.appendChild(xLabel);
  xGroup.appendChild(xSelect);
  controlsRow.appendChild(xGroup);

  const refreshBtn = document.createElement("button");
  refreshBtn.textContent = "\u21bb Refresh";
  refreshBtn.style.cssText = "padding:2px 8px;font-size:12px;cursor:pointer;border:1px solid #ccc;border-radius:4px;background:#f5f5f5;font-family:system-ui,sans-serif;margin-left:auto";
  controlsRow.appendChild(refreshBtn);

  // ── Chart canvas + tooltip ──
  const chartCanvas = document.createElement("canvas");
  chartCanvas.style.display = "block";

  const tooltip = document.createElement("div");
  tooltip.style.cssText = "position:absolute;display:none;background:rgba(0,0,0,0.8);color:#fff;padding:6px 10px;border-radius:4px;font-size:12px;pointer-events:none;white-space:nowrap;z-index:10";

  const chartWrapper = document.createElement("div");
  chartWrapper.style.position = "relative";
  chartWrapper.style.display = "inline-block";
  chartWrapper.appendChild(chartCanvas);
  chartWrapper.appendChild(tooltip);

  // ── Interactive legend ──
  const legendPanel = document.createElement("div");
  legendPanel.style.cssText = "margin-top:6px;font-size:12px";

  const hiddenRuns = new Set();

  function buildLegend(allSeries) {
    legendPanel.innerHTML = "";
    if (allSeries.length === 0) return;

    const hasNesting = allSeries.some(s => s.parent_run_id);

    if (hasNesting) {
      const parentIds = new Set();
      const childrenOf = new Map();
      const standalone = [];

      for (const s of allSeries) {
        if (s.parent_run_id) {
          if (!childrenOf.has(s.parent_run_id)) childrenOf.set(s.parent_run_id, []);
          childrenOf.get(s.parent_run_id).push(s);
          parentIds.add(s.parent_run_id);
        }
      }
      for (const s of allSeries) {
        if (parentIds.has(s.run_id)) {
          // This is a parent; render as group header
        } else if (!s.parent_run_id) {
          standalone.push(s);
        }
      }

      // Render parent groups
      for (const pid of parentIds) {
        const parentSeries = allSeries.find(s => s.run_id === pid);
        const children = childrenOf.get(pid) || [];

        const groupDiv = document.createElement("div");
        groupDiv.style.cssText = "margin-bottom:4px";

        const header = document.createElement("div");
        header.style.cssText = "display:flex;align-items:center;gap:6px;cursor:pointer;user-select:none;padding:2px 0;color:#555;font-weight:500";

        const groupToggle = document.createElement("span");
        const allChildrenHidden = children.every(c => hiddenRuns.has(c.run_id));
        groupToggle.textContent = allChildrenHidden ? "\u25b6" : "\u25bc";
        groupToggle.style.cssText = "font-size:10px;width:12px";

        const groupLabel = document.createElement("span");
        groupLabel.textContent = parentSeries ? parentSeries.label : pid.slice(0, 8);

        if (parentSeries) {
          const dot = document.createElement("span");
          dot.style.cssText = `display:inline-block;width:8px;height:8px;border-radius:50%;background:${STATUS_COLORS[parentSeries.status] || "#999"}`;
          header.appendChild(dot);
        }

        header.appendChild(groupToggle);
        header.appendChild(groupLabel);

        header.addEventListener("click", () => {
          const allHidden = children.every(c => hiddenRuns.has(c.run_id));
          for (const c of children) {
            if (allHidden) hiddenRuns.delete(c.run_id);
            else hiddenRuns.add(c.run_id);
          }
          redraw();
        });

        groupDiv.appendChild(header);

        const childRow = document.createElement("div");
        childRow.style.cssText = "display:flex;flex-wrap:wrap;gap:8px;padding-left:20px";
        for (const child of children) {
          childRow.appendChild(makeLegendItem(child));
        }
        groupDiv.appendChild(childRow);
        legendPanel.appendChild(groupDiv);
      }

      // Render standalone
      if (standalone.length > 0) {
        const row = document.createElement("div");
        row.style.cssText = "display:flex;flex-wrap:wrap;gap:8px;margin-top:4px";
        for (const s of standalone) row.appendChild(makeLegendItem(s));
        legendPanel.appendChild(row);
      }
    } else {
      const row = document.createElement("div");
      row.style.cssText = "display:flex;flex-wrap:wrap;gap:8px";
      for (const s of allSeries) row.appendChild(makeLegendItem(s));
      legendPanel.appendChild(row);
    }
  }

  function makeLegendItem(s) {
    const item = document.createElement("div");
    const isHidden = hiddenRuns.has(s.run_id);
    item.style.cssText = `display:flex;align-items:center;gap:4px;cursor:pointer;user-select:none;padding:2px 6px;border-radius:3px;${isHidden ? "opacity:0.4;text-decoration:line-through;" : ""}`;

    const swatch = document.createElement("span");
    swatch.style.cssText = `display:inline-block;width:16px;height:3px;background:${s.color};border-radius:1px`;

    const dot = document.createElement("span");
    dot.style.cssText = `display:inline-block;width:7px;height:7px;border-radius:50%;background:${STATUS_COLORS[s.status] || "#999"}`;

    const nameEl = document.createElement("span");
    nameEl.textContent = s.label;
    nameEl.style.color = "#333";

    item.appendChild(swatch);
    item.appendChild(dot);
    item.appendChild(nameEl);

    item.addEventListener("click", () => {
      if (hiddenRuns.has(s.run_id)) hiddenRuns.delete(s.run_id);
      else hiddenRuns.add(s.run_id);
      redraw();
    });

    item.addEventListener("mouseenter", () => { if (!isHidden) item.style.background = "#f0f4ff"; });
    item.addEventListener("mouseleave", () => { item.style.background = ""; });

    return item;
  }

  // Status line
  const statusEl = document.createElement("div");
  statusEl.style.cssText = "margin-top:4px;color:#666;font-size:12px";
  statusEl.textContent = model.get("_status") || "Waiting for data\u2026";

  container.appendChild(controlsRow);
  container.appendChild(chartWrapper);
  container.appendChild(legendPanel);
  container.appendChild(statusEl);
  el.appendChild(container);

  let lastAllSeries = [];
  let lastSeries = [];

  function getSliderParam() {
    const v = parseFloat(smoothSlider.value);
    return cfg.toParam(v);
  }

  function redraw() {
    const seriesData = model.get("_series_data") || [];
    const key = model.get("metric_key") || "metric";
    const w = model.get("width") || 700;
    const h = model.get("height") || 300;
    lastAllSeries = prepareSeries(seriesData, kind, getSliderParam(), xAxisMode);
    lastSeries = lastAllSeries.filter(s => !hiddenRuns.has(s.run_id));
    drawChart(chartCanvas, lastSeries, { title: key, width: w, height: h, xAxisMode });
    buildLegend(lastAllSeries);
    statusEl.textContent = model.get("_status") || "";
  }

  // ── Event handlers ──

  kindSelect.addEventListener("change", () => {
    kind = kindSelect.value;
    model.set("smoothing_kind", kind);
    configureSlider();
    model.set("smoothing_param", null);
    model.save_changes();
    redraw();
  });

  smoothSlider.addEventListener("input", () => {
    let v = parseFloat(smoothSlider.value);
    if (kind === "rolling" && v === 1) { smoothSlider.value = "2"; v = 2; }
    smoothValEl.textContent = cfg.fmt(v);
    model.set("smoothing_param", cfg.toParam(v));
    model.save_changes();
    redraw();
  });

  xSelect.addEventListener("change", () => {
    xAxisMode = xSelect.value;
    model.set("x_axis", xAxisMode);
    model.save_changes();
    redraw();
  });

  refreshBtn.addEventListener("click", () => {
    model.set("_do_refresh", (model.get("_do_refresh") || 0) + 1);
    model.save_changes();
  });

  chartCanvas.addEventListener("mousemove", (e) => {
    if (lastSeries.length === 0) { tooltip.style.display = "none"; return; }
    const rect = chartCanvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const w = model.get("width") || 700;
    const h = model.get("height") || 300;
    const pad = { top: 30, right: 20, bottom: 40, left: 60 };

    let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
    for (const s of lastSeries) {
      for (const p of s.points) {
        if (p.x < minX) minX = p.x; if (p.x > maxX) maxX = p.x;
        if (p.y < minY) minY = p.y; if (p.y > maxY) maxY = p.y;
      }
    }
    if (!isFinite(minX)) return;
    const yPad = (maxY - minY) * 0.05 || 0.1;
    minY -= yPad; maxY += yPad;
    const plotW = w - pad.left - pad.right;
    const plotH = h - pad.top - pad.bottom;
    const sx = v => pad.left + ((v - minX) / (maxX - minX || 1)) * plotW;
    const sy = v => pad.top + plotH - ((v - minY) / (maxY - minY || 1)) * plotH;

    let bestDist = 25, bestS = null, bestP = null;
    for (const s of lastSeries) {
      for (const p of s.points) {
        const dx = sx(p.x) - mx, dy = sy(p.y) - my;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < bestDist) { bestDist = d; bestS = s; bestP = p; }
      }
    }

    if (bestP) {
      tooltip.style.display = "block";
      tooltip.style.left = (sx(bestP.x) + 12) + "px";
      tooltip.style.top = (sy(bestP.y) - 10) + "px";
      tooltip.textContent = bestS.label + " | " + formatXTooltip(bestP.x, xAxisMode) + " | " + bestP.y.toFixed(4);
    } else {
      tooltip.style.display = "none";
    }
  });
  chartCanvas.addEventListener("mouseleave", () => { tooltip.style.display = "none"; });

  model.on("change:_series_data", redraw);
  model.on("change:_status", () => { statusEl.textContent = model.get("_status") || ""; });
  model.on("change:metric_key", redraw);
  model.on("change:x_axis", () => {
    xAxisMode = model.get("x_axis") || "step";
    xSelect.value = xAxisMode;
    redraw();
  });

  redraw();
}

export default { render };
