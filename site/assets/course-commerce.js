/* Keep public course offers aligned with the live Academy catalogue. */
(() => {
  "use strict";

  const wrappers = Array.from(document.querySelectorAll("[data-course-commerce]"));
  if (!wrappers.length) return;

  const config = window.TRADETHESIS_ACADEMY_CONFIG || {};
  const academyBaseUrl = String(config.baseUrl || "").trim().replace(/\/+$/, "");
  const safeText = (element, value) => {
    if (element) element.textContent = String(value || "");
  };

  function setUnavailable(wrapper, reason) {
    wrapper.dataset.courseCommerceState = "unavailable";
    safeText(wrapper.querySelector("[data-course-price]"), "Temporarily unavailable");
    safeText(
      wrapper.querySelector("[data-course-price-note]"),
      "Current access could not be confirmed"
    );
    const message = reason ||
      "TradeThesis Academy could not confirm this course's current access details. Please try again shortly.";
    wrapper.querySelectorAll("[data-course-access-message]").forEach(node => {
      safeText(node, message);
    });
    wrapper.querySelectorAll("[data-course-enrol-cta]").forEach(link => {
      link.setAttribute("href", "#");
      link.setAttribute("aria-disabled", "true");
      link.classList.add("academy-link-unavailable");
      link.textContent = "Enrolment temporarily unavailable";
      link.addEventListener("click", event => event.preventDefault(), { once: true });
    });
  }

  function accessMessage(course) {
    switch (course.accessType) {
      case "free":
        return "No payment is required. Sign in or create an account to enrol.";
      case "membership":
        return "Included with TradeThesis Free. Sign in or create an account to join.";
      case "mixed":
        return "Review the included membership and individual purchase options in Academy.";
      case "paid":
        return "Your current market price and secure checkout are confirmed in Academy before payment.";
      default:
        return "Review the current course access options in Academy before enrolling.";
    }
  }

  function actionLabel(course) {
    switch (course.accessType) {
      case "free": return "Enrol for free ↗";
      case "membership": return "Join TradeThesis Free ↗";
      case "mixed": return "View access options ↗";
      case "paid": return "Continue to checkout ↗";
      default: return "View course access ↗";
    }
  }

  function canContinue(course) {
    if (!course || course.status !== "published" || !course.academyUrl) return false;
    if (course.accessType === "free" || course.accessType === "membership" ||
        course.accessType === "mixed") return true;
    return course.accessType === "paid" && Boolean(course.priceConfigured && course.price);
  }

  async function loadCourse(wrapper) {
    const slug = String(wrapper.getAttribute("data-course-commerce") || "").trim();
    if (!slug || !academyBaseUrl) {
      setUnavailable(wrapper, "Member access is not configured for this website yet.");
      return;
    }

    try {
      const response = await fetch(academyBaseUrl + "/api/academy/catalogue/", {
        method: "GET",
        mode: "cors",
        credentials: "omit",
        cache: "no-store",
        headers: { "Accept": "application/json" }
      });
      if (!response.ok) throw new Error("The Academy catalogue returned an error.");
      const payload = await response.json();
      const courses = Array.isArray(payload.courses) ? payload.courses : [];
      const course = courses.find(item => item && item.slug === slug);
      if (!course || !canContinue(course)) {
        setUnavailable(wrapper, "This course is not currently available for enrolment in your market.");
        return;
      }

      wrapper.dataset.courseCommerceState = "ready";
      safeText(
        wrapper.querySelector("[data-course-price]"),
        course.price || "Access options available"
      );
      safeText(
        wrapper.querySelector("[data-course-price-note]"),
        course.priceNote || "Current access terms confirmed by Academy"
      );
      wrapper.querySelectorAll("[data-course-access-message]").forEach(node => {
        safeText(node, accessMessage(course));
      });

      const academyUrl = new URL(course.academyUrl);
      if (academyUrl.protocol !== "https:" || academyUrl.origin !== academyBaseUrl) {
        throw new Error("The Academy returned an unexpected course destination.");
      }
      wrapper.querySelectorAll("[data-course-enrol-cta]").forEach(link => {
        link.href = academyUrl.href;
        link.removeAttribute("aria-disabled");
        link.classList.remove("academy-link-unavailable");
        link.textContent = actionLabel(course);
      });
    } catch (_error) {
      setUnavailable(wrapper);
    }
  }

  wrappers.forEach(loadCourse);
})();
