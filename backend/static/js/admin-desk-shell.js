(function () {
  "use strict";

  function initAdminDeskShell() {
    const shell = document.querySelector("[data-admin-desk-shell]");
    if (!shell || shell.dataset.deskShellReady === "true") return;
    shell.dataset.deskShellReady = "true";

    const sidebar = shell.querySelector("#ttDeskSidebar");
    const mobileToggle = shell.querySelector("[data-desk-mobile-toggle]");
    const collapseToggle = shell.querySelector("[data-desk-collapse]");
    const backdrop = shell.querySelector("[data-desk-backdrop]");
    if (!sidebar) return;

    const mobileQuery = window.matchMedia("(max-width: 820px)");

    function setMobileOpen(open) {
      shell.classList.toggle("is-mobile-open", open);
      document.body.classList.toggle("tt-desk-drawer-open", open);
      if (mobileToggle) mobileToggle.setAttribute("aria-expanded", String(open));
      if (backdrop) backdrop.setAttribute("aria-hidden", String(!open));
      if (open) {
        const firstLink = sidebar.querySelector("a[href]");
        if (firstLink) firstLink.focus();
      } else if (mobileToggle) {
        mobileToggle.focus();
      }
    }

    if (mobileToggle) {
      mobileToggle.addEventListener("click", function () {
        setMobileOpen(!shell.classList.contains("is-mobile-open"));
      });
    }
    if (backdrop) {
      backdrop.addEventListener("click", function () {
        setMobileOpen(false);
      });
    }
    if (collapseToggle) {
      collapseToggle.addEventListener("click", function () {
        if (mobileQuery.matches) return;
        const collapsed = shell.classList.toggle("is-collapsed");
        collapseToggle.setAttribute("aria-expanded", String(!collapsed));
        collapseToggle.setAttribute(
          "aria-label",
          collapsed ? "Expand Admin Desk navigation" : "Collapse Admin Desk navigation"
        );
        collapseToggle.title = collapsed ? "Expand navigation" : "Collapse navigation";
      });
    }

    sidebar.addEventListener("click", function (event) {
      const link = event.target.closest("a[href]");
      if (link && mobileQuery.matches) setMobileOpen(false);
    });

    document.addEventListener("keydown", function (event) {
      if (!shell.classList.contains("is-mobile-open")) return;
      if (event.key === "Escape") {
        event.preventDefault();
        setMobileOpen(false);
        return;
      }
      if (event.key !== "Tab") return;

      const focusable = Array.from(
        sidebar.querySelectorAll('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])')
      ).filter(function (element) {
        return element.getClientRects().length > 0;
      });
      if (!focusable.length) {
        event.preventDefault();
        return;
      }
      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (event.shiftKey && (document.activeElement === first || !sidebar.contains(document.activeElement))) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });

    mobileQuery.addEventListener("change", function (event) {
      if (!event.matches) {
        shell.classList.remove("is-mobile-open");
        document.body.classList.remove("tt-desk-drawer-open");
      }
      if (mobileToggle) mobileToggle.setAttribute("aria-expanded", "false");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAdminDeskShell, { once: true });
  } else {
    initAdminDeskShell();
  }
})();