(() => {
  document.querySelectorAll("[data-sitewide-nav]").forEach((header) => {
    const toggle = header.querySelector("[data-sitewide-toggle]");
    const mobile = header.querySelector("[data-sitewide-mobile]");
    if (!toggle || !mobile) return;

    const close = () => {
      mobile.classList.remove("open");
      toggle.setAttribute("aria-expanded", "false");
      toggle.setAttribute("aria-label", "Open navigation");
      toggle.textContent = "☰";
    };
    const open = () => {
      mobile.classList.add("open");
      toggle.setAttribute("aria-expanded", "true");
      toggle.setAttribute("aria-label", "Close navigation");
      toggle.textContent = "×";
    };

    toggle.addEventListener("click", () => {
      if (toggle.getAttribute("aria-expanded") === "true") close();
      else open();
    });
    mobile.querySelectorAll("a").forEach((link) => link.addEventListener("click", close));
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") close();
    });
  });
})();
