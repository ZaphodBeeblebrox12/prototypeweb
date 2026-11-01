(() => {
  "use strict";

  const container = document.querySelector("[data-protected-video-container]");
  if (!container) return;

  const video = container.querySelector("[data-protected-video]");
  const status = container.querySelector("[data-video-player-status]");
  const manifestUrl = video && video.dataset.manifestUrl;
  const fullscreenButton = container.querySelector("[data-video-fullscreen]");
  const watermark = container.querySelector("[data-video-watermark]");

  // Keep the viewer identity visible continuously, but move it to a new
  // unpredictable position over the video every few seconds. Coordinates are
  // calculated from the rendered video box, so the same behavior works in
  // normal and fullscreen layouts.
  let watermarkMoveTimer = null;
  let previousWatermarkPoint = null;

  const moveWatermark = () => {
    if (!video || !watermark || !container.isConnected) return;

    const videoRect = video.getBoundingClientRect();
    const containerRect = container.getBoundingClientRect();
    if (videoRect.width <= 0 || videoRect.height <= 0) return;

    const watermarkRect = watermark.getBoundingClientRect();
    const markWidth = watermarkRect.width || watermark.offsetWidth;
    const markHeight = watermarkRect.height || watermark.offsetHeight;
    const edgePadding = 12;
    // Keep clear of the native video control strip at the bottom.
    const bottomControlsReserve = 66;
    const maxX = Math.max(edgePadding, videoRect.width - markWidth - edgePadding);
    const maxY = Math.max(
      edgePadding,
      videoRect.height - markHeight - bottomControlsReserve
    );

    let chosen = { x: edgePadding, y: edgePadding };
    const minTravel = Math.max(70, Math.min(videoRect.width, videoRect.height) * 0.22);
    const fullscreenRect = fullscreenButton?.getBoundingClientRect();

    for (let attempt = 0; attempt < 24; attempt += 1) {
      const candidate = {
        x: edgePadding + Math.random() * Math.max(0, maxX - edgePadding),
        y: edgePadding + Math.random() * Math.max(0, maxY - edgePadding)
      };

      // Do not cover the custom fullscreen button.
      if (fullscreenRect && fullscreenRect.width > 0) {
        const candidateLeft = videoRect.left + candidate.x;
        const candidateTop = videoRect.top + candidate.y;
        const overlapsFullscreen =
          candidateLeft < fullscreenRect.right + 10 &&
          candidateLeft + markWidth > fullscreenRect.left - 10 &&
          candidateTop < fullscreenRect.bottom + 10 &&
          candidateTop + markHeight > fullscreenRect.top - 10;
        if (overlapsFullscreen) continue;
      }

      if (previousWatermarkPoint) {
        const distance = Math.hypot(
          candidate.x - previousWatermarkPoint.x,
          candidate.y - previousWatermarkPoint.y
        );
        if (distance < minTravel) continue;
      }

      chosen = candidate;
      break;
    }

    watermark.style.left = `${videoRect.left - containerRect.left + chosen.x}px`;
    watermark.style.top = `${videoRect.top - containerRect.top + chosen.y}px`;
    watermark.style.right = "auto";
    watermark.style.bottom = "auto";
    watermark.style.visibility = "visible";
    previousWatermarkPoint = chosen;
  };

  const scheduleWatermarkMove = () => {
    if (watermarkMoveTimer !== null) {
      window.clearTimeout(watermarkMoveTimer);
    }
    watermarkMoveTimer = window.setTimeout(() => {
      moveWatermark();
      scheduleWatermarkMove();
    }, 2700 + Math.random() * 2300);
  };

  if (watermark && video) {
    moveWatermark();
    scheduleWatermarkMove();
    window.addEventListener("resize", moveWatermark);
    document.addEventListener("fullscreenchange", () => {
      window.setTimeout(moveWatermark, 120);
    });
  }

  const showStatus = message => {
    if (status) status.textContent = message || "";
  };

  if (!video || !manifestUrl) {
    showStatus("This protected video is not configured correctly. Please contact support.");
    return;
  }

  // Keep the viewer identity watermark in the player at all times. Do not hide
  // it on pause, during buffering, or when the tab loses focus.
  if (fullscreenButton) {
    const updateFullscreenLabel = () => {
      const active = document.fullscreenElement === container;
      fullscreenButton.textContent = active ? "Exit full screen" : "Full screen";
      fullscreenButton.setAttribute("aria-label", active ? "Exit full screen video" : "View video full screen");
    };

    fullscreenButton.addEventListener("click", async () => {
      try {
        if (document.fullscreenElement === container) {
          await document.exitFullscreen();
        } else if (container.requestFullscreen) {
          await container.requestFullscreen();
        } else {
          showStatus("Full screen with the viewer watermark is not supported by this browser.");
        }
      } catch (_error) {
        showStatus("The browser did not allow full screen mode. You can continue watching in this window.");
      }
    });

    document.addEventListener("fullscreenchange", updateFullscreenLabel);
    updateFullscreenLabel();
  }

  video.addEventListener("loadstart", () => showStatus("Loading protected video…"));
  video.addEventListener("loadedmetadata", () => showStatus("Video ready."));
  video.addEventListener("canplay", () => showStatus(""));
  video.addEventListener("playing", () => showStatus(""));
  video.addEventListener("waiting", () => showStatus("Buffering video…"));
  video.addEventListener("stalled", () => showStatus("The video connection has stalled. Waiting for the stream…"));
  video.addEventListener("error", () => {
    if (!video.error) return;
    const errorNames = {
      1: "playback was interrupted",
      2: "a network error occurred",
      3: "the browser could not decode the video data",
      4: "the browser could not read this video format"
    };
    const reason = errorNames[video.error.code] || "an unknown media error occurred";
    showStatus(`Video playback failed: ${reason}. Refresh the lesson and try again.`);
  });

  // Prefer hls.js when Media Source Extensions are available. Some browsers
  // return a positive canPlayType() result for HLS without reliably playing
  // encrypted HLS playlists. Native HLS remains the fallback for Safari/iOS,
  // where Media Source Extensions may not be available.
  const nativeHlsAvailable = Boolean(video.canPlayType("application/vnd.apple.mpegurl"));
  const Hls = window.Hls;
  if (!Hls || !Hls.isSupported()) {
    if (nativeHlsAvailable) {
      showStatus("Loading protected video…");
      video.src = manifestUrl;
      video.load();
      return;
    }
    showStatus("This browser does not support protected HLS playback. Please use a current version of Chrome, Edge or Safari.");
    return;
  }
  const player = new Hls({
    enableWorker: true,
    // AES-128 encrypted HLS must be decrypted as a complete segment. Keep
    // progressive FetchLoader mode disabled even if a future Hls build changes
    // its loader-selection defaults.
    progressive: false,
    lowLatencyMode: false,
    backBufferLength: 30,
    xhrSetup: xhr => {
      xhr.withCredentials = true;
    }
  });

  let recoveredMediaError = false;
  let parsingFailed = false;
  let loadedFragments = 0;
  let lastHlsError = "";
  let metadataWatchdog = window.setTimeout(() => {
    if (!Number.isFinite(video.duration) || video.duration <= 0) {
      const detail = lastHlsError ? ` Playback diagnostic: ${lastHlsError}.` : "";
      showStatus(
        "The stream reached your browser, but the browser has not decoded a playable video yet." +
        detail +
        " Try refreshing once; if it continues, send this message to support."
      );
    }
  }, 18000);

  const clearMetadataWatchdog = () => {
    window.clearTimeout(metadataWatchdog);
    metadataWatchdog = null;
  };

  video.addEventListener("loadedmetadata", clearMetadataWatchdog, { once: true });
  video.addEventListener("error", clearMetadataWatchdog, { once: true });

  player.on(Hls.Events.MEDIA_ATTACHED, () => {
    showStatus("Connecting to the protected video…");
    player.loadSource(manifestUrl);
  });

  player.on(Hls.Events.MANIFEST_LOADING, () => showStatus("Loading video playlist…"));

  player.on(Hls.Events.MANIFEST_PARSED, (_event, data) => {
    const levels = Array.isArray(data.levels) ? data.levels.length : 0;
    showStatus(levels ? "Playlist loaded. Preparing video…" : "Playlist loaded, but no playable video quality was found.");
  });

  player.on(Hls.Events.LEVEL_LOADED, (_event, data) => {
    const details = data.details;
    if (details && (!Number.isFinite(details.totalduration) || details.totalduration <= 0)) {
      lastHlsError = "the playlist reports zero duration";
      showStatus("The playlist loaded, but it reports no playable duration. The video needs to be reprocessed.");
      return;
    }
    if (details && Array.isArray(details.fragments)) {
      showStatus(`Video playlist loaded (${details.fragments.length} segments). Preparing playback…`);
    }
  });

  player.on(Hls.Events.FRAG_LOADED, () => {
    showStatus("Video segment received. Preparing playback…");
  });

  player.on(Hls.Events.FRAG_PARSED, () => {
    showStatus("Video data decoded. Preparing playback…");
  });

  player.on(Hls.Events.FRAG_BUFFERED, () => {
    loadedFragments += 1;
    showStatus(loadedFragments === 1 ? "Video ready. Press Play to watch." : "");
  });

  player.on(Hls.Events.ERROR, (_event, data) => {
    const detail = String(data.details || data.type || "unknown HLS error")
      .replace(/[^a-zA-Z0-9_ -]/g, "")
      .slice(0, 100);
    // Include hls.js's parser reason; the event name alone does not tell us
    // whether the decrypted segment has invalid TS sync bytes, bad PES data,
    // missing tables, or another demux problem. Never log signed request URLs.
    const underlyingError = data.error || data.err;
    const rawReason = String(
      (typeof underlyingError === "string" ? underlyingError : underlyingError?.message) ||
      data.reason ||
      "No underlying parser exception was provided."
    );
    const errorName = String(underlyingError?.name || "")
      .replace(/[^a-zA-Z0-9_.-]/g, "")
      .slice(0, 50);
    const reason = rawReason
      .replace(/ticket=[^&\s]+/gi, "ticket=[redacted]")
      .replace(/https?:\/\/[^\s]+/gi, "[url redacted]")
      .replace(/[^a-zA-Z0-9_ .,:;()'-]/g, " ")
      .trim()
      .slice(0, 220);
    lastHlsError = [detail, errorName, reason].filter(Boolean).join(": ");
    console.warn("TradeThesis protected-video playback error", {
      type: data.type,
      details: data.details,
      errorName: errorName || undefined,
      reason: reason || undefined,
      fatal: Boolean(data.fatal)
    });

    if (!data.fatal) {
      // hls.js reports these details in camelCase (for example,
      // fragParsingError and bufferAppendError). Normalize separators and case
      // so parser/decrypt/buffer failures cannot leave the player on a stale
      // "segment received" message indefinitely.
      const normalizedDetail = String(data.details || "")
        .toLowerCase()
        .replace(/[^a-z0-9]/g, "");
      const mediaPreparationError =
        /fragparsingerror|fragdecrypterror|keyloaderror|keyloadtimeout|bufferappenderror|bufferaddcodecerror|bufferincompatiblecodecserror|transmuxererror/.test(normalizedDetail);
      if (mediaPreparationError) {
        clearMetadataWatchdog();
        if (normalizedDetail === "fragparsingerror" && !parsingFailed) {
          parsingFailed = true;
          player.stopLoad();
        }
        showStatus(
          `The segment downloaded, but the browser could not prepare it (${detail})` +
          (reason ? `: ${reason}` : ".")
        );
      } else if (loadedFragments === 0 && normalizedDetail) {
        showStatus(`The protected stream reported a playback issue (${detail})${reason ? `: ${reason}` : "."}`);
      }
      return;
    }

    if (data.type === Hls.ErrorTypes.NETWORK_ERROR) {
      showStatus(`A protected video request failed (${detail}). Check your connection and refresh the lesson.`);
      player.startLoad();
    } else if (data.type === Hls.ErrorTypes.MEDIA_ERROR && !recoveredMediaError) {
      recoveredMediaError = true;
      showStatus("The browser could not decode the first video segment. Attempting playback recovery…");
      player.recoverMediaError();
    } else {
      clearMetadataWatchdog();
      showStatus(`Protected video playback failed (${detail}). Please contact support.`);
      player.destroy();
    }
  });

  container.addEventListener("tradeThesisVideoDestroy", () => {
    clearMetadataWatchdog();
    if (watermarkMoveTimer !== null) window.clearTimeout(watermarkMoveTimer);
    window.removeEventListener("resize", moveWatermark);
    player.destroy();
  }, { once: true });

  showStatus("Loading protected video…");
  player.attachMedia(video);
})();
