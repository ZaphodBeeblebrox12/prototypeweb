(() => {
  "use strict";

  const container = document.querySelector("[data-personalized-video-status]");
  if (!container) return;

  const statusUrl = container.dataset.statusUrl;
  const message = container.querySelector("[data-personalized-video-status-message]");
  if (!statusUrl || !message) return;

  let stopped = false;
  let timer = null;
  let attempts = 0;

  const poll = async () => {
    if (stopped || !container.isConnected) return;
    attempts += 1;
    try {
      const response = await fetch(statusUrl, {
        method: "GET",
        credentials: "same-origin",
        cache: "no-store",
        headers: { "Accept": "application/json" }
      });
      if (!response.ok) {
        if (response.status === 401 || response.status === 403 || response.status === 404) {
          stopped = true;
          message.textContent = "Your course access could not be verified. Refresh the lesson or contact support.";
          return;
        }
        throw new Error("The video preparation status could not be checked.");
      }
      const payload = await response.json();
      if (payload.ready || payload.status === "ready") {
        stopped = true;
        message.textContent = "Your video is ready. Opening your personalised lesson…";
        window.location.reload();
        return;
      }
      if (payload.failed || ["failed", "revoked"].includes(payload.status)) {
        stopped = true;
        message.textContent = payload.message || "Your personalised video could not be prepared. Please contact support.";
        return;
      }
      message.textContent = payload.message || "We are preparing your personal video. This page will update automatically.";
    } catch (_error) {
      message.textContent = "Your video is still being prepared. Checking again shortly…";
    }
    if (!stopped) {
      // Back off gently so status polling stays negligible during longer encodes.
      const delay = Math.min(15000, 4000 + Math.max(0, attempts - 1) * 1000);
      timer = window.setTimeout(poll, delay);
    }
  };

  poll();
  window.addEventListener("pagehide", () => {
    stopped = true;
    if (timer !== null) window.clearTimeout(timer);
  }, { once: true });
})();
