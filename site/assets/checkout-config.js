/* Staging-only route map. Production hostnames are intentionally not mapped to staging. */
(function () {
  const host = String(window.location.hostname || "").toLowerCase();
  const stagingRoutes = {
    "tradethesis-public-staging.onrender.com": "https://tradethesis-academy-staging.onrender.com"
  };
  window.TRADETHESIS_ACADEMY_BASE_URL = stagingRoutes[host] || "";
})();
