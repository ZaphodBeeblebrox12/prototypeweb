/* TradeThesis instructional-image inspection — no dependencies. */
(() => {
  "use strict";
  const SELECTOR = [
    ".sr-room-teaching-figure img", ".sr-room-chart-figure img", ".sr-v52-figure img",
    ".sr-v52-figure-panel", ".generated-figure img", ".reading-figure img",
    ".case-chart-figure img", "[data-zoomable]"
  ].join(",");
  const attached = new WeakSet();
  const dialog = document.createElement("dialog");
  dialog.className = "tt-image-inspector";
  dialog.setAttribute("aria-label", "Instructional image inspector");
  dialog.innerHTML = [
    '<div class="tt-image-inspector-shell">',
    '<header class="tt-image-inspector-toolbar"><div class="tt-image-inspector-heading"><strong>Image inspection</strong><span data-tt-image-title aria-live="polite"></span><small class="tt-image-inspector-source" data-tt-image-source></small></div>',
    '<div class="tt-image-inspector-actions"><button type="button" data-tt-action="zoom-out" aria-label="Zoom out" title="Zoom out (−)">−</button>',
    '<span class="tt-image-inspector-zoom" data-tt-zoom aria-live="polite">Fit</span>',
    '<button type="button" data-tt-action="zoom-in" aria-label="Zoom in" title="Zoom in (+)">+</button>',
    '<button type="button" data-tt-action="fit" aria-label="Fit image to screen" title="Fit to screen (0)">Fit</button>',
    '<button type="button" data-tt-action="close" class="tt-image-inspector-close" aria-label="Close image inspector" title="Close (Esc)">×</button></div></header>',
    '<div class="tt-image-inspector-stage" data-tt-stage tabindex="0" role="region" aria-label="Zoomable image. Use plus and minus to zoom, zero to fit, arrow keys to pan, or drag to pan. On touch screens, pinch to zoom.">',
    '<div class="tt-image-inspector-canvas" data-tt-canvas></div></div>',
    '<footer class="tt-image-inspector-footer"><span>Drag to pan · + / − to zoom · 0 to fit · Esc to close</span><span>Viewing aid only; learning activity state is unchanged.</span></footer>',
    '</div>'
  ].join("");
  document.body.append(dialog);
  const stage = dialog.querySelector("[data-tt-stage]");
  const canvas = dialog.querySelector("[data-tt-canvas]");
  const titleNode = dialog.querySelector("[data-tt-image-title]");
  const zoomNode = dialog.querySelector("[data-tt-zoom]");
  const sourceNode = dialog.querySelector("[data-tt-image-source]");
  let trigger = null, media = null, naturalWidth = 0, naturalHeight = 0;
  let fitScale = 1, currentScale = 1, scrollBeforeOpen = { left: 0, top: 0 };
  let pointers = new Map(), dragOrigin = null, pinchOrigin = null;
  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
  const isSvg = el => el instanceof SVGElement;
  const labelFor = el => {
    const label = el.getAttribute("alt") || el.getAttribute("aria-label") || "";
    if (label.trim()) return label.trim();
    return (el.closest("figure")?.querySelector("figcaption")?.textContent || "").trim() || "Instructional chart or diagram";
  };
  const sourceFor = el => el instanceof HTMLImageElement ? (el.currentSrc || el.src) : "";
  function sourceDetailText(el) {
    if (isSvg(el)) {
      const embeddedRaster = Array.from(el.querySelectorAll("image")).find(imageNode => {
        const href = imageNode.getAttribute("href") ||
          imageNode.getAttributeNS("http://www.w3.org/1999/xlink", "href") || "";
        return /\.(?:png|jpe?g|webp|gif|avif)(?:[?#].*)?$/i.test(href);
      });
      if (embeddedRaster) {
        const width = Number(embeddedRaster.getAttribute("width")) || 0;
        const height = Number(embeddedRaster.getAttribute("height")) || 0;
        const dimensions = width > 0 && height > 0
          ? " · original figure " + width.toLocaleString() + " × " + height.toLocaleString() + " px"
          : "";
        return "Cropped panel from a raster chart" + dimensions +
          ". Enlargement cannot restore detail missing from the source.";
      }
      return "Vector diagram. Lines and labels stay sharp when enlarged.";
    }
    const src = sourceFor(el);
    if (/\.svg(?:[?#].*)?$/i.test(src)) {
      return "Vector SVG. Lines and labels stay sharp when enlarged.";
    }
    const width = el instanceof HTMLImageElement
      ? (el.naturalWidth || (media && media.naturalWidth) || naturalWidth) : naturalWidth;
    const height = el instanceof HTMLImageElement
      ? (el.naturalHeight || (media && media.naturalHeight) || naturalHeight) : naturalHeight;
    if (width > 0 && height > 0) {
      return "Raster source · " + width.toLocaleString() + " × " + height.toLocaleString() +
        " px. Enlargement reveals stored detail; it cannot recreate detail absent from the file.";
    }
    return "Source dimensions are not available yet. The original file determines how much detail can be inspected.";
  }
  function updateSourceDetail(el) {
    sourceNode.textContent = sourceDetailText(el);
  }
  function setMediaSize(nextScale, keepViewport = true) {
    if (!media || !naturalWidth || !naturalHeight) return;
    const previousScale = currentScale || nextScale;
    const centerX = stage.scrollLeft + stage.clientWidth / 2;
    const centerY = stage.scrollTop + stage.clientHeight / 2;
    currentScale = clamp(nextScale, Math.max(0.1, fitScale * 0.5), Math.max(2, fitScale * 8));
    const width = Math.max(1, Math.round(naturalWidth * currentScale));
    const height = Math.max(1, Math.round(naturalHeight * currentScale));
    const canvasWidth = Math.max(stage.clientWidth, width);
    const canvasHeight = Math.max(stage.clientHeight, height);
    canvas.style.width = canvasWidth + "px";
    canvas.style.height = canvasHeight + "px";
    media.style.width = width + "px";
    media.style.height = height + "px";
    media.style.left = Math.max(0, Math.round((canvasWidth - width) / 2)) + "px";
    media.style.top = Math.max(0, Math.round((canvasHeight - height) / 2)) + "px";
    zoomNode.textContent = Math.round(currentScale / Math.max(fitScale, 0.001) * 100) + "%";
    if (keepViewport && previousScale > 0) {
      const ratio = currentScale / previousScale;
      stage.scrollLeft = Math.max(0, centerX * ratio - stage.clientWidth / 2);
      stage.scrollTop = Math.max(0, centerY * ratio - stage.clientHeight / 2);
    }
  }
  function fitToScreen(startInMobileDetail = false) {
    if (!media || !naturalWidth || !naturalHeight) return;
    fitScale = Math.min(1, Math.max(1, stage.clientWidth - 28) / naturalWidth, Math.max(1, stage.clientHeight - 28) / naturalHeight);
    currentScale = fitScale;
    setMediaSize(fitScale, false);
    stage.scrollLeft = 0; stage.scrollTop = 0;
    zoomNode.textContent = "Fit · 100%";
    if (startInMobileDetail && window.matchMedia("(max-width: 680px)").matches) {
      // Whole-chart fit can make chart annotations too small to read on a phone.
      // Start enlarged, but keep Fit available for seeing the complete context.
      setMediaSize(fitScale * 2, false);
      stage.scrollLeft = Math.max(0, Math.round((stage.scrollWidth - stage.clientWidth) / 2));
      stage.scrollTop = Math.max(0, Math.round((stage.scrollHeight - stage.clientHeight) / 2));
      zoomNode.textContent = "Detail · " + Math.round(currentScale / Math.max(fitScale, 0.001) * 100) + "%";
    }
  }
  function svgDimensions(el) {
    const vb = el.viewBox?.baseVal;
    if (vb && vb.width > 0 && vb.height > 0) return { width: vb.width, height: vb.height };
    return { width: Number(el.getAttribute("width")) || el.getBoundingClientRect().width, height: Number(el.getAttribute("height")) || el.getBoundingClientRect().height };
  }
  function prepareMedia(el) {
    canvas.replaceChildren();
    titleNode.textContent = labelFor(el);
    if (isSvg(el)) {
      media = el.cloneNode(true);
      media.classList.add("tt-image-inspector-media");
      media.removeAttribute("tabindex"); media.removeAttribute("role");
      media.setAttribute("aria-hidden", "true");
      const dims = svgDimensions(el);
      naturalWidth = dims.width; naturalHeight = dims.height;
      canvas.append(media);
      updateSourceDetail(el);
      return;
    }
    media = document.createElement("img");
    media.className = "tt-image-inspector-media";
    media.alt = labelFor(el); media.draggable = false; media.decoding = "async";
    media.addEventListener("load", () => {
      naturalWidth = media.naturalWidth; naturalHeight = media.naturalHeight;
      fitToScreen(true);
      updateSourceDetail(el);
    }, { once: true });
    media.addEventListener("error", () => { titleNode.textContent = "This image could not be loaded at full size."; }, { once: true });
    canvas.append(media);
    media.src = sourceFor(el);
    if (media.complete && media.naturalWidth > 0) {
      naturalWidth = media.naturalWidth; naturalHeight = media.naturalHeight;
      updateSourceDetail(el);
    } else {
      zoomNode.textContent = "Loading…";
      sourceNode.textContent = "Loading source dimensions…";
    }
  }
  function openInspector(el) {
    if (!el || dialog.open) return;
    trigger = el; scrollBeforeOpen = { left: window.scrollX, top: window.scrollY };
    pointers = new Map(); dragOrigin = null; pinchOrigin = null;
    prepareMedia(el);
    dialog.showModal();
    requestAnimationFrame(() => {
      if (!media) return;
      if (isSvg(el) || (media.complete && media.naturalWidth > 0)) fitToScreen(true);
      dialog.querySelector('[data-tt-action="close"]').focus();
    });
  }
  function closeInspector() { if (dialog.open) dialog.close(); }
  function attach(el) {
    if (attached.has(el) || dialog.contains(el)) return;
    if (el.closest("[data-no-image-zoom],a,button") && !el.hasAttribute("data-zoomable")) return;
    attached.add(el);
    el.classList.add("tt-image-inspector-image");
    el.setAttribute("tabindex", "0");
    el.setAttribute("role", "button");
    el.setAttribute("aria-label", labelFor(el) + ". Open image inspector.");
    el.setAttribute("title", "Select to inspect this image at a larger size");
    const figure = el.closest("figure");
    const figcaption = figure && figure.querySelector("figcaption");
    if (figcaption && !figcaption.querySelector(".tt-image-inspector-hint")) {
      const hint = document.createElement("span");
      hint.className = "tt-image-inspector-hint";
      hint.textContent = "Select image to inspect details";
      figcaption.append(hint);
    }
    el.addEventListener("click", event => { if (!event.defaultPrevented) openInspector(el); });
    el.addEventListener("keydown", event => {
      if (event.target === el && ["Enter", " "].includes(event.key)) { event.preventDefault(); openInspector(el); }
    });
  }
  function scan(root) {
    if (root.nodeType === Node.ELEMENT_NODE && root.matches?.(SELECTOR)) attach(root);
    root.querySelectorAll?.(SELECTOR).forEach(attach);
  }
  dialog.querySelectorAll("[data-tt-action]").forEach(button => button.addEventListener("click", () => {
    switch (button.dataset.ttAction) {
      case "close": closeInspector(); break;
      case "zoom-in": setMediaSize(currentScale * 1.25); break;
      case "zoom-out": setMediaSize(currentScale / 1.25); break;
      case "fit": fitToScreen(); break;
    }
  }));
  dialog.addEventListener("click", event => { if (event.target === dialog) closeInspector(); });
  dialog.addEventListener("close", () => {
    canvas.replaceChildren(); media = null; naturalWidth = 0; naturalHeight = 0;
    if (trigger?.isConnected) trigger.focus({ preventScroll: true });
    if (Math.abs(window.scrollY - scrollBeforeOpen.top) > 2 ||
        Math.abs(window.scrollX - scrollBeforeOpen.left) > 2) {
      window.scrollTo({ left: scrollBeforeOpen.left, top: scrollBeforeOpen.top, behavior: "auto" });
    }
    trigger = null;
  });
  stage.addEventListener("keydown", event => {
    if (event.key === "+" || event.key === "=") { event.preventDefault(); setMediaSize(currentScale * 1.25); }
    else if (event.key === "-" || event.key === "_") { event.preventDefault(); setMediaSize(currentScale / 1.25); }
    else if (event.key === "0") { event.preventDefault(); fitToScreen(); }
    else if (event.key === "ArrowLeft") { event.preventDefault(); stage.scrollLeft -= 80; }
    else if (event.key === "ArrowRight") { event.preventDefault(); stage.scrollLeft += 80; }
    else if (event.key === "ArrowUp") { event.preventDefault(); stage.scrollTop -= 80; }
    else if (event.key === "ArrowDown") { event.preventDefault(); stage.scrollTop += 80; }
  });
  const distance = (a,b) => Math.hypot(a.x-b.x, a.y-b.y);
  stage.addEventListener("pointerdown", event => {
    if (!dialog.open) return;
    event.preventDefault();
    stage.setPointerCapture?.(event.pointerId);
    pointers.set(event.pointerId, { x:event.clientX, y:event.clientY });
    if (pointers.size === 2) {
      const pts = [...pointers.values()];
      pinchOrigin = { distance:distance(pts[0],pts[1]), scale:currentScale };
      dragOrigin = null;
    } else dragOrigin = { x:event.clientX, y:event.clientY, left:stage.scrollLeft, top:stage.scrollTop };
  });
  stage.addEventListener("pointermove", event => {
    if (!pointers.has(event.pointerId)) return;
    pointers.set(event.pointerId, { x:event.clientX, y:event.clientY });
    if (pointers.size >= 2 && pinchOrigin) {
      const pts = [...pointers.values()];
      if (pinchOrigin.distance > 0) setMediaSize(pinchOrigin.scale * distance(pts[0],pts[1]) / pinchOrigin.distance);
    } else if (dragOrigin) {
      stage.scrollLeft = dragOrigin.left - (event.clientX - dragOrigin.x);
      stage.scrollTop = dragOrigin.top - (event.clientY - dragOrigin.y);
    }
  });
  const endPointer = event => { pointers.delete(event.pointerId); if (pointers.size < 2) pinchOrigin = null; dragOrigin = null; };
  stage.addEventListener("pointerup", endPointer);
  stage.addEventListener("pointercancel", endPointer);
  stage.addEventListener("lostpointercapture", endPointer);
  window.addEventListener("resize", () => {
    if (!dialog.open || !media || !naturalWidth || !naturalHeight) return;
    const zoomRatio = currentScale / Math.max(fitScale, 0.001);
    fitToScreen();
    if (zoomRatio > 1.02) setMediaSize(fitScale * zoomRatio, false);
  });
  scan(document);
  new MutationObserver(records => records.forEach(record => record.addedNodes.forEach(node => {
    if (node.nodeType === Node.ELEMENT_NODE) scan(node);
  }))).observe(document.body, { childList:true, subtree:true });
})();