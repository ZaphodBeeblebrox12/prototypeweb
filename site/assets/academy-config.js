/* Public deployment configuration for the Academy service; never put secrets here. */
(() => {
  const stagingOrigin = "https://tradethesis-academy-staging.onrender.com";
  const hostname = String(window.location.hostname || "").toLowerCase();
  const pathname = String(window.location.pathname || "");
  const isGitHubPagesPreview = hostname === "zaphodbeeblebrox12.github.io" &&
    (pathname === "/prototypeweb" || pathname.startsWith("/prototypeweb/"));
  // A deployment may define window.TRADETHESIS_ACADEMY_BASE_URL before this script loads.
  const inheritedBaseUrl = String(window.TRADETHESIS_ACADEMY_BASE_URL || "").trim().replace(/\/+$/, "");
  const isValidOrigin = value => {
    try {
      const url = new URL(value);
      return url.protocol === "https:" && url.origin === value && !url.username && !url.password;
    } catch (_error) {
      return false;
    }
  };
  const isLocalPreview = hostname === "localhost" || hostname === "127.0.0.1" || hostname === "::1";
  const isKnownPublicPreview = hostname === "tradethesis-public-staging.onrender.com" ||
    isLocalPreview || isGitHubPagesPreview;
  const configuredBaseUrl = isValidOrigin(inheritedBaseUrl)
    ? inheritedBaseUrl
    : (isKnownPublicPreview ? stagingOrigin : "");

  window.TRADETHESIS_ACADEMY_CONFIG = Object.freeze({ baseUrl: configuredBaseUrl });

  // All Academy paths are represented as paths in HTML and resolved here.
  // Staging is enabled only on the public staging host, local previews, and the
  // repository GitHub Pages preview (/prototypeweb/). Unknown production hosts
  // must never silently send learners to staging.
  document.querySelectorAll("[data-academy-path]").forEach(element => {
    const path = String(element.getAttribute("data-academy-path") || "");
    if (!path.startsWith("/") || path.startsWith("//")) return;

    if (configuredBaseUrl) {
      const target = configuredBaseUrl + path;
      if (element instanceof HTMLFormElement) {
        element.setAttribute("action", target);
      } else if (element instanceof HTMLAnchorElement) {
        element.setAttribute("href", target);
        element.removeAttribute("aria-disabled");
      }
      return;
    }

    if (element instanceof HTMLAnchorElement) {
      element.setAttribute("href", "#");
      element.setAttribute("aria-disabled", "true");
      element.classList.add("academy-link-unavailable");
      element.addEventListener("click", event => event.preventDefault());
    } else if (element instanceof HTMLFormElement) {
      element.setAttribute("action", "#");
      element.setAttribute("aria-disabled", "true");
      element.addEventListener("submit", event => event.preventDefault());
      element.querySelectorAll("input, button, select, textarea").forEach(control => {
        control.disabled = true;
      });
      const notice = document.createElement("p");
      notice.className = "academy-config-notice";
      notice.setAttribute("role", "status");
      notice.textContent = "Member access is not configured for this website yet.";
      element.insertAdjacentElement("beforebegin", notice);
    }
  });

  document.querySelectorAll("[data-youtube-live-status-path]").forEach(element => {
    const path = String(element.getAttribute("data-youtube-live-status-path") || "");
    if (configuredBaseUrl && path.startsWith("/") && !path.startsWith("//")) {
      element.setAttribute("data-youtube-live-status-url", configuredBaseUrl + path);
    } else {
      element.removeAttribute("data-youtube-live-status-url");
    }
  });
})();
