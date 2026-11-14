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
      if (event.key === "Escape" && shell.classList.contains("is-mobile-open")) {
        setMobileOpen(false);
      }
    });

    mobileQuery.addEventListener("change", function (event) {
      if (!event.matches) shell.classList.remove("is-mobile-open");
      if (mobileToggle) mobileToggle.setAttribute("aria-expanded", "false");
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initAdminDeskShell, { once: true });
  } else {
    initAdminDeskShell();
  }
})();