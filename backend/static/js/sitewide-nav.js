(() => {
  document.querySelectorAll("[data-sitewide-nav]").forEach((header) => {
    const toggle = header.querySelector("[data-sitewide-toggle]");
    const mobile = header.querySelector("[data-sitewide-mobile]");

    if (toggle && mobile) {
      const closeMobile = () => {
        mobile.classList.remove("open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.setAttribute("aria-label", "Open navigation");
        toggle.textContent = "☰";
      };
      const openMobile = () => {
        mobile.classList.add("open");
        toggle.setAttribute("aria-expanded", "true");
        toggle.setAttribute("aria-label", "Close navigation");
        toggle.textContent = "×";
      };
      toggle.addEventListener("click", () => {
        if (toggle.getAttribute("aria-expanded") === "true") closeMobile();
        else openMobile();
      });
      mobile.querySelectorAll("a").forEach((link) => link.addEventListener("click", closeMobile));
      document.addEventListener("keydown", (event) => { if (event.key === "Escape") closeMobile(); });
    }

    const control = header.querySelector("[data-youtube-live-control]");
    if (!control) return;
    const statusUrl = control.dataset.youtubeLiveStatusUrl;
    const liveToggle = control.querySelector("[data-youtube-live-toggle]");
    const popover = control.querySelector("[data-youtube-live-popover]");
    const watchLink = control.querySelector("[data-youtube-live-watch]");
    if (!statusUrl || !liveToggle || !popover || !watchLink) return;

    const closePopover = () => {
      popover.hidden = true;
      liveToggle.setAttribute("aria-expanded", "false");
    };
    const refreshStatus = async () => {
      try {
        const response = await fetch(statusUrl, {
          method: "GET",
          headers: { Accept: "application/json" },
          cache: "no-store",
          credentials: "omit"
        });
        if (!response.ok) throw new Error("Live status unavailable");
        const status = await response.json();
        const validWatchUrl = typeof status.watch_url === "string" &&
          status.watch_url.startsWith("https://www.youtube.com/watch?v=");
        if (status.is_live === true && validWatchUrl) {
          watchLink.href = status.watch_url;
          control.hidden = false;
        } else {
          control.hidden = true;
          closePopover();
        }
      } catch (_) {
        control.hidden = true;
        closePopover();
      }
    };

    liveToggle.addEventListener("click", () => {
      const opening = popover.hidden;
      popover.hidden = !opening;
      liveToggle.setAttribute("aria-expanded", String(opening));
    });
    document.addEventListener("click", (event) => { if (!control.contains(event.target)) closePopover(); });
    document.addEventListener("keydown", (event) => { if (event.key === "Escape") closePopover(); });

    refreshStatus();
    window.setInterval(refreshStatus, 90000);
  });
})();