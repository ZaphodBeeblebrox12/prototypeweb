(() => {
  const canvas = document.getElementById("tt-growth-chart");
  const dataNode = document.getElementById("tt-growth-data");
  const legend = document.getElementById("growth-chart-legend");
  if (!canvas || !dataNode) return;

  let chart;
  try {
    chart = JSON.parse(dataNode.textContent || "{}");
  } catch (_error) {
    return;
  }
  const series = Array.isArray(chart.series) ? chart.series : [];
  const labels = Array.isArray(chart.labels) ? chart.labels : [];
  if (!series.length || !labels.length) return;

  const palette = ["#355a46", "#c96f50", "#8b967a", "#b58b44"];
  const context = canvas.getContext("2d");
  if (!context) return;

  if (legend) {
    legend.replaceChildren();
    series.forEach((item, index) => {
      const label = document.createElement("span");
      label.className = "tt-admin-legend-item";
      const swatch = document.createElement("span");
      swatch.className = "tt-admin-legend-swatch";
      swatch.style.backgroundColor = palette[index % palette.length];
      swatch.setAttribute("aria-hidden", "true");
      const text = document.createElement("span");
      text.textContent = item.name || "Series";
      label.append(swatch, text);
      legend.append(label);
    });
  }

  const formatTick = (value) => {
    if (value >= 1000000) return (value / 1000000).toFixed(1) + "m";
    if (value >= 1000) return (value / 1000).toFixed(1) + "k";
    return String(Math.round(value));
  };

  function draw() {
    const bounds = canvas.getBoundingClientRect();
    const width = Math.max(280, bounds.width);
    const height = Math.max(230, Number.parseFloat(getComputedStyle(canvas).height) || 290);
    const ratio = Math.max(1, window.devicePixelRatio || 1);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    context.setTransform(ratio, 0, 0, ratio, 0, 0);
    context.clearRect(0, 0, width, height);

    const pad = { top: 14, right: 14, bottom: 34, left: 42 };
    const plotWidth = width - pad.left - pad.right;
    const plotHeight = height - pad.top - pad.bottom;
    const values = series.flatMap((item) => (item.values || []).map((v) => Number(v) || 0));
    const maxValue = Math.max(1, ...values);
    const magnitude = Math.pow(10, Math.floor(Math.log10(maxValue)));
    const step = Math.max(1, Math.ceil(maxValue / 4 / magnitude) * magnitude);
    const ceiling = Math.max(step * 4, Math.ceil(maxValue / step) * step);
    const y = (value) => pad.top + plotHeight - (value / ceiling) * plotHeight;
    const x = (index) => pad.left + (labels.length <= 1 ? plotWidth / 2 : index * plotWidth / (labels.length - 1));

    context.font = "11px system-ui, sans-serif";
    context.textBaseline = "middle";
    for (let tick = 0; tick <= ceiling; tick += step) {
      const lineY = y(tick);
      context.beginPath();
      context.strokeStyle = "#e7e1d6";
      context.lineWidth = 1;
      context.moveTo(pad.left, lineY);
      context.lineTo(width - pad.right, lineY);
      context.stroke();
      context.fillStyle = "#687268";
      context.textAlign = "right";
      context.fillText(formatTick(tick), pad.left - 8, lineY);
    }

    const maxLabels = width < 440 ? 4 : 7;
    const labelStep = Math.max(1, Math.ceil(labels.length / maxLabels));
    context.fillStyle = "#687268";
    context.textAlign = "center";
    context.textBaseline = "top";
    for (let index = 0; index < labels.length; index += labelStep) {
      context.fillText(labels[index], x(index), height - pad.bottom + 10);
    }
    if (labels.length > 1 && (labels.length - 1) % labelStep !== 0) {
      context.fillText(labels[labels.length - 1], x(labels.length - 1), height - pad.bottom + 10);
    }

    series.forEach((item, index) => {
      const valuesForSeries = item.values || [];
      if (!valuesForSeries.length) return;
      const color = palette[index % palette.length];
      context.beginPath();
      context.strokeStyle = color;
      context.lineWidth = 2.4;
      context.lineJoin = "round";
      context.lineCap = "round";
      valuesForSeries.forEach((rawValue, valueIndex) => {
        const pointX = x(valueIndex);
        const pointY = y(Number(rawValue) || 0);
        if (valueIndex === 0) context.moveTo(pointX, pointY);
        else context.lineTo(pointX, pointY);
      });
      context.stroke();

      if (labels.length <= 31) {
        valuesForSeries.forEach((rawValue, valueIndex) => {
          context.beginPath();
          context.fillStyle = color;
          context.arc(x(valueIndex), y(Number(rawValue) || 0), 2.6, 0, Math.PI * 2);
          context.fill();
        });
      }
    });
  }

  draw();
  window.addEventListener("resize", draw, { passive: true });
})();