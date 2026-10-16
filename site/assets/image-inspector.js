/* TradeThesis instructional-image inspection viewer.
 * Deliberately opt-in: decorative brand and marketing imagery is not enlarged.
 */
(() => {
  "use strict";

  const SELECTOR = [
    "#sr-chart-image",
    ".sr-room-teaching-figure img",
    ".sr-v52-figure img",
    "img[data-image-inspect='true']"
  ].join(",");
  let dialog, stage, viewerImage, heading, caption, zoomOut, zoomIn;
  let activeImage = null;
  let savedScroll = { left: 0, top: 0 };
  let fitScale = 1;
  let scale = 1;
  let maxScale = 1;
  let baseWidth = 0;
  let baseHeight = 0;
  let translateX = 0;
  let translateY = 0;
  let gesture = null;
  const pointers = new Map();

  const clamp = (value, min, max) => Math.max(min, Math.min(max, value));
  const make = (tag, className, text) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  };

  function button(label, title, handler, extraClass) {
    const node = make("button", "image-inspector-button" + (extraClass ? " " + extraClass : ""), label);
    node.type = "button";
    node.title = title;
    node.setAttribute("aria-label", title);
    node.addEventListener("click", handler);
    return node;
  }

  function sourceCaption(img) {
    const figure = img.closest("figure");
    const figcaption = figure && figure.querySelector("figcaption");
    if (!figcaption) return "";
    const copy = figcaption.cloneNode(true);
    copy.querySelectorAll(".image-inspector-hint").forEach(item => item.remove());
    return copy.textContent.trim();
  }

  function prepareImage(img) {
    if (!(img instanceof HTMLImageElement) || !img.matches(SELECTOR)) return;
    if (img.dataset.imageInspectorReady !== "true") {
      img.dataset.imageInspectorReady = "true";
      img.tabIndex = 0;
      img.setAttribute("role", "button");
      img.setAttribute("aria-haspopup", "dialog");
      img.setAttribute("aria-label", "Open image for detailed inspection");
      img.title = "Open image to zoom and inspect details";
    }

    const figure = img.closest("figure");
    const figcaption = figure && figure.querySelector("figcaption");
    if (figcaption && !figcaption.querySelector(".image-inspector-hint")) {
      figcaption.appendChild(make("span", "image-inspector-hint", "Click or tap image to inspect"));
    }
  }

  function ensureViewer() {
    if (dialog) return;

    dialog = make("dialog", "image-inspector-dialog");
    dialog.setAttribute("aria-label", "Instructional image viewer");
    dialog.addEventListener("click", event => {
      if (event.target === dialog) dialog.close();
    });
    dialog.addEventListener("close", () => {
      document.body.classList.remove("image-inspector-open");
      viewerImage.removeAttribute("src");
      viewerImage.alt = "";
      pointers.clear();
      gesture = null;
      const prior = activeImage;
      activeImage = null;
      if (prior && prior.isConnected) {
        prior.focus({ preventScroll: true });
      }
      window.scrollTo({ left: savedScroll.left, top: savedScroll.top, behavior: "auto" });
    });

    const shell = make("div", "image-inspector-shell");
    const toolbar = make("div", "image-inspector-toolbar");
    const titleWrap = make("div", "image-inspector-heading");
    heading = make("h2", "", "Image detail");
    heading.id = "image-inspector-title";
    const help = make("p", "image-inspector-help",
      "Use +/− or pinch to zoom. Drag to pan. Raster detail is limited by the original source.");
    titleWrap.append(heading, help);

    const controls = make("div", "image-inspector-controls");
    zoomOut = button("−", "Zoom out", () => setScale(scale / 1.25));
    zoomIn = button("+", "Zoom in", () => setScale(scale * 1.25));
    const fit = button("Fit", "Fit image to the available screen", fitToScreen);
    const close = button("×", "Close image viewer", () => dialog.close(), "image-inspector-button-close");
    controls.append(zoomOut, zoomIn, fit, close);
    toolbar.append(titleWrap, controls);

    stage = make("div", "image-inspector-stage");
    stage.tabIndex = 0;
    stage.setAttribute("role", "region");
    stage.setAttribute("aria-label", "Zoomable image canvas. Use arrow keys to pan and plus or minus to zoom.");
    viewerImage = make("img", "image-inspector-image");
    viewerImage.alt = "";
    viewerImage.draggable = false;
    viewerImage.addEventListener("load", fitToScreen);
    stage.appendChild(viewerImage);

    caption = make("div", "image-inspector-caption");
    caption.id = "image-inspector-caption";
    dialog.setAttribute("aria-labelledby", heading.id);
    dialog.setAttribute("aria-describedby", caption.id);
    shell.append(toolbar, stage, caption);
    dialog.appendChild(shell);
    document.body.appendChild(dialog);

    stage.addEventListener("pointerdown", pointerDown);
    stage.addEventListener("pointermove", pointerMove);
    stage.addEventListener("pointerup", pointerEnd);
    stage.addEventListener("pointercancel", pointerEnd);
    stage.addEventListener("lostpointercapture", pointerEnd);
    stage.addEventListener("wheel", event => {
      event.preventDefault();
      setScale(scale * (event.deltaY < 0 ? 1.15 : 1 / 1.15));
    }, { passive: false });

    dialog.addEventListener("keydown", event => {
      if (event.altKey || event.ctrlKey || event.metaKey) return;
      if (event.key === "+" || event.key === "=") {
        event.preventDefault();
        setScale(scale * 1.25);
      } else if (event.key === "-" || event.key === "_") {
        event.preventDefault();
        setScale(scale / 1.25);
      } else if (event.key === "0") {
        event.preventDefault();
        fitToScreen();
      } else if (event.key.startsWith("Arrow") && event.target === stage) {
        event.preventDefault();
        const step = event.shiftKey ? 90 : 36;
        if (event.key === "ArrowLeft") translateX += step;
        if (event.key === "ArrowRight") translateX -= step;
        if (event.key === "ArrowUp") translateY += step;
        if (event.key === "ArrowDown") translateY -= step;
        clampPan();
        applyTransform();
      }
    });

    window.addEventListener("resize", () => {
      if (dialog.open) fitToScreen();
    }, { passive: true });
  }

  function isVectorSource() {
    const src = viewerImage.currentSrc || viewerImage.src || "";
    return /\.svg(?:[?#].*)?$/i.test(src);
  }

  function fitToScreen() {
    if (!dialog || !dialog.open || !viewerImage.naturalWidth || !stage.clientWidth || !stage.clientHeight) return;
    const availableWidth = Math.max(100, stage.clientWidth - 32);
    const availableHeight = Math.max(100, stage.clientHeight - 32);
    const rawFit = Math.min(availableWidth / viewerImage.naturalWidth, availableHeight / viewerImage.naturalHeight);
    fitScale = isVectorSource() ? rawFit : Math.min(rawFit, 1);
    fitScale = Math.max(0.01, fitScale);
    baseWidth = viewerImage.naturalWidth * fitScale;
    baseHeight = viewerImage.naturalHeight * fitScale;
    viewerImage.style.width = baseWidth + "px";
    viewerImage.style.height = baseHeight + "px";
    maxScale = isVectorSource() ? 8 : Math.max(1, 1 / fitScale);
    scale = 1;
    translateX = 0;
    translateY = 0;
    applyTransform();
  }

  function clampPan() {
    const scaledWidth = baseWidth * scale;
    const scaledHeight = baseHeight * scale;
    const maxX = Math.max(0, (scaledWidth - stage.clientWidth) / 2 + 12);
    const maxY = Math.max(0, (scaledHeight - stage.clientHeight) / 2 + 12);
    translateX = clamp(translateX, -maxX, maxX);
    translateY = clamp(translateY, -maxY, maxY);
    if (scale <= 1.001) {
      translateX = 0;
      translateY = 0;
    }
  }

  function applyTransform() {
    if (!viewerImage) return;
    clampPan();
    viewerImage.style.transform = "translate3d(" + translateX + "px," + translateY + "px,0) scale(" + scale + ")";
    zoomOut.disabled = scale <= 1.001;
    zoomIn.disabled = scale >= maxScale - 0.001;
    stage.classList.toggle("is-panning", Boolean(gesture && gesture.type === "pan"));
  }

  function setScale(next) {
    scale = clamp(next, 1, maxScale);
    clampPan();
    applyTransform();
  }

  function pointerDown(event) {
    if (event.pointerType === "mouse" && event.button !== 0) return;
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    try { stage.setPointerCapture(event.pointerId); } catch (_) {}
    if (pointers.size === 1) {
      gesture = {
        type: scale > 1.001 ? "pan" : "none",
        pointerId: event.pointerId,
        startX: event.clientX,
        startY: event.clientY,
        startTX: translateX,
        startTY: translateY
      };
    } else if (pointers.size === 2) {
      const pair = Array.from(pointers.values());
      gesture = {
        type: "pinch",
        distance: Math.max(1, Math.hypot(pair[0].x - pair[1].x, pair[0].y - pair[1].y)),
        scale: scale,
        tx: translateX,
        ty: translateY,
        midX: (pair[0].x + pair[1].x) / 2,
        midY: (pair[0].y + pair[1].y) / 2
      };
    }
    applyTransform();
  }

  function pointerMove(event) {
    if (!pointers.has(event.pointerId)) return;
    pointers.set(event.pointerId, { x: event.clientX, y: event.clientY });
    if (!gesture) return;

    if (pointers.size >= 2 && gesture.type === "pinch") {
      const pair = Array.from(pointers.values());
      const distance = Math.max(1, Math.hypot(pair[0].x - pair[1].x, pair[0].y - pair[1].y));
      const midX = (pair[0].x + pair[1].x) / 2;
      const midY = (pair[0].y + pair[1].y) / 2;
      scale = clamp(gesture.scale * (distance / gesture.distance), 1, maxScale);
      translateX = gesture.tx + (midX - gesture.midX);
      translateY = gesture.ty + (midY - gesture.midY);
      applyTransform();
    } else if (pointers.size === 1 && gesture.type === "pan" && scale > 1.001) {
      translateX = gesture.startTX + event.clientX - gesture.startX;
      translateY = gesture.startTY + event.clientY - gesture.startY;
      applyTransform();
    }
  }

  function pointerEnd(event) {
    if (!pointers.has(event.pointerId)) return;
    pointers.delete(event.pointerId);
    if (pointers.size === 1) {
      const entry = Array.from(pointers.entries())[0];
      gesture = {
        type: scale > 1.001 ? "pan" : "none",
        pointerId: entry[0],
        startX: entry[1].x,
        startY: entry[1].y,
        startTX: translateX,
        startTY: translateY
      };
    } else if (pointers.size === 0) {
      gesture = null;
    } else {
      gesture = null;
    }
    applyTransform();
  }

  function openViewer(img) {
    prepareImage(img);
    if (!img.currentSrc && !img.src) return;
    ensureViewer();
    activeImage = img;
    savedScroll = { left: window.scrollX, top: window.scrollY };
    const alt = (img.alt || "").trim();
    heading.textContent = alt || sourceCaption(img) || "Image detail";
    viewerImage.alt = alt || heading.textContent;
    caption.textContent = sourceCaption(img);
    viewerImage.src = img.currentSrc || img.src;
    dialog.showModal();
    document.body.classList.add("image-inspector-open");
    const closeButton = dialog.querySelector(".image-inspector-button-close");
    if (closeButton) closeButton.focus({ preventScroll: true });
    if (viewerImage.complete && viewerImage.naturalWidth) fitToScreen();
  }

  document.addEventListener("click", event => {
    const img = event.target instanceof Element ? event.target.closest(SELECTOR) : null;
    if (!img) return;
    prepareImage(img);
    event.preventDefault();
    openViewer(img);
  });

  document.addEventListener("keydown", event => {
    if (dialog && dialog.open) return;
    if (event.key !== "Enter" && event.key !== " ") return;
    const img = event.target instanceof Element ? event.target.closest(SELECTOR) : null;
    if (!img) return;
    event.preventDefault();
    openViewer(img);
  });

  document.querySelectorAll(SELECTOR).forEach(prepareImage);
  const observer = new MutationObserver(records => {
    records.forEach(record => {
      if (record.type === "attributes" && record.target instanceof HTMLImageElement) {
        prepareImage(record.target);
      } else {
        record.addedNodes.forEach(node => {
          if (!(node instanceof Element)) return;
          if (node.matches && node.matches(SELECTOR)) prepareImage(node);
          if (node.querySelectorAll) node.querySelectorAll(SELECTOR).forEach(prepareImage);
        });
      }
    });
  });
  observer.observe(document.documentElement, {
    subtree: true,
    childList: true,
    attributes: true,
    attributeFilter: ["src", "alt"]
  });
})();