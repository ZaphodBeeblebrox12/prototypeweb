/* Staging-only route map. Production hostnames are intentionally not mapped to staging. */
(function () {
  const host = String(window.location.hostname || "").toLowerCase();
  const stagingRoutes = {
    "tradethesis-public-staging.onrender.com": "https://tradethesis-academy-staging.onrender.com"
  };
  // Preserve an explicit deployment override; only fall back to the staging
  // route map when no Academy origin has been supplied.
  if (!String(window.TRADETHESIS_ACADEMY_BASE_URL || "").trim()) {
    window.TRADETHESIS_ACADEMY_BASE_URL = stagingRoutes[host] || "";
  }
})();
