/* Public deployment configuration for the Academy service; never put secrets here. */
(() => {
  const stagingOrigin = "https://tradethesis-academy-staging.onrender.com";
  // A deployment may define window.TRADETHESIS_ACADEMY_BASE_URL before this script loads.
  const configuredBaseUrl = String(window.TRADETHESIS_ACADEMY_BASE_URL || stagingOrigin)
    .trim()
    .replace(/\/+$/, "");

  // This must be an origin, not a path or an arbitrary URL.
  if (!/^https:\/\/[^/]+$/i.test(configuredBaseUrl)) {
    window.TRADETHESIS_ACADEMY_CONFIG = Object.freeze({ baseUrl: "" });
    return;
  }

  window.TRADETHESIS_ACADEMY_CONFIG = Object.freeze({ baseUrl: configuredBaseUrl });

  // Keep legacy links in this page aligned with the configured Academy origin.
  // This lets a production cutover update one public config value rather than
  // leaving member links or status polling pointed at staging.
  if (configuredBaseUrl !== stagingOrigin) {
    document.querySelectorAll("*").forEach(element => {
      Array.from(element.attributes).forEach(attribute => {
        if (attribute.value.includes(stagingOrigin)) {
          element.setAttribute(attribute.name, attribute.value.split(stagingOrigin).join(configuredBaseUrl));
        }
      });
    });
  }
})();
