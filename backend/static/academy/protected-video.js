(() => {
  "use strict";

  const container = document.querySelector("[data-protected-video-container]");
  if (!container) return;

  const video = container.querySelector("[data-protected-video]");
  const status = container.querySelector("[data-video-player-status]");
  const manifestUrl = video && video.dataset.manifestUrl;

  const showStatus = message => {
    if (status) status.textContent = message;
  };

  if (!video || !manifestUrl) {
    showStatus("This protected video is not configured correctly. Please contact support.");
    return;
  }

  if (video.canPlayType("application/vnd.apple.mpegurl")) {
    // Safari and supported Apple browsers can play HLS natively.
    video.src = manifestUrl;
  } else if (window.Hls && window.Hls.isSupported()) {
    const player = new window.Hls({
      enableWorker: true,
      lowLatencyMode: false,
      xhrSetup: xhr => {
        xhr.withCredentials = true;
      }
    });

    player.loadSource(manifestUrl);
    player.attachMedia(video);
    player.on(window.Hls.Events.MANIFEST_PARSED, () => showStatus(""));
    player.on(window.Hls.Events.ERROR, (_event, data) => {
      if (!data.fatal) return;
      if (data.type === window.Hls.ErrorTypes.NETWORK_ERROR) {
        showStatus("The protected stream could not be reached. Refresh the lesson and try again.");
      } else if (data.type === window.Hls.ErrorTypes.MEDIA_ERROR) {
        showStatus("Your browser could not decode this stream. Try the latest version of Chrome, Edge or Safari.");
        player.destroy();
      } else {
        showStatus("Protected video playback failed. Please contact support.");
        player.destroy();
      }
    });
    container.addEventListener("tradeThesisVideoDestroy", () => player.destroy(), { once: true });
  } else {
    showStatus("This browser does not support HLS playback. Please use a current version of Chrome, Edge or Safari.");
  }

  video.addEventListener("error", () => {
    if (video.error) {
      showStatus("The protected video could not be loaded. Refresh the lesson and try again.");
    }
  });

  // The personalized watermark is deliberately intermittent and relocates while visible.
  // It deters casual screen captures but is not a substitute for server-side watermarking or DRM.
  const watermark = container.querySelector("[data-video-watermark]");
  if (!watermark) return;

  const positions = [
    { left: "7%", top: "12%" },
    { left: "65%", top: "13%" },
    { left: "10%", top: "72%" },
    { left: "63%", top: "70%" },
    { left: "34%", top: "9%" },
    { left: "38%", top: "76%" },
    { left: "77%", top: "43%" },
    { left: "8%", top: "42%" }
  ];

  let lastPosition = -1;
  const moveWatermark = () => {
    let next = Math.floor(Math.random() * positions.length);
    if (positions.length > 1 && next === lastPosition) {
      next = (next + 1) % positions.length;
    }
    lastPosition = next;
    const point = positions[next];
    watermark.style.left = point.left;
    watermark.style.right = "auto";
    watermark.style.top = point.top;
    watermark.style.bottom = "auto";
  };

  let cycleTimer = null;
  let movementTimer = null;
  let hideTimer = null;

  const stopWatermark = () => {
    window.clearTimeout(cycleTimer);
    window.clearTimeout(hideTimer);
    window.clearInterval(movementTimer);
    watermark.classList.remove("is-visible");
  };

  const scheduleWatermark = delay => {
    window.clearTimeout(cycleTimer);
    cycleTimer = window.setTimeout(showWatermarkCycle, delay);
  };

  function showWatermarkCycle() {
    if (video.paused || video.ended || document.hidden) return;

    moveWatermark();
    watermark.classList.add("is-visible");
    movementTimer = window.setInterval(moveWatermark, 3600);

    hideTimer = window.setTimeout(() => {
      window.clearInterval(movementTimer);
      watermark.classList.remove("is-visible");
      scheduleWatermark(22000);
    }, 9000);
  }

  video.addEventListener("play", () => scheduleWatermark(1400));
  video.addEventListener("pause", stopWatermark);
  video.addEventListener("ended", stopWatermark);
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      stopWatermark();
    } else if (!video.paused && !video.ended) {
      scheduleWatermark(1400);
    }
  });
})();
