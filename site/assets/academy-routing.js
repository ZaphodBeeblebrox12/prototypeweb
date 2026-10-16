/* Keep static member links pointed at the configured Django Academy host. */
(() => {
  "use strict";
  const setting = document.querySelector('meta[name="academy-base-url"]');
  const base = (setting?.content || "").trim().replace(/\/+$/, "");
  if (!base) return;

  const routePrefixes = [
    "/learn/", "/accounts/", "/dashboard/", "/payments/",
    "/bot/", "/support/", "/auth/", "/profile/"
  ];

  document.querySelectorAll("a[href]").forEach(link => {
    const raw = link.getAttribute("href");
    if (!raw || !raw.startsWith("/")) return;
    if (!routePrefixes.some(prefix => raw.startsWith(prefix))) return;
    link.href = base + raw;
  });
})();
