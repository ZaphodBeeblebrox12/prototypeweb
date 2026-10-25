(() => {
  "use strict";

  document.addEventListener("click", event => {
    const tab = event.target.closest("[data-tab-name]");
    if (tab) {
      const root = tab.closest("[data-learning-tabs]");
      if (!root) return;
      root.querySelectorAll("[data-tab-name]").forEach(button => {
        const active = button === tab;
        button.classList.toggle("is-active", active);
        button.setAttribute("aria-selected", String(active));
        button.setAttribute("tabindex", active ? "0" : "-1");
      });
      root.querySelectorAll("[data-tab-panel]").forEach(panel => {
        panel.hidden = panel.dataset.tabPanel !== tab.dataset.tabName;
      });
      return;
    }

    const openTab = event.target.closest("[data-open-tab]");
    if (openTab) {
      const root = openTab.closest("[data-learning-tabs]");
      const target = root && Array.from(root.querySelectorAll("[data-tab-name]"))
        .find(button => button.dataset.tabName === openTab.dataset.openTab);
      if (target) {
        target.click();
        target.focus();
      }
      return;
    }

    const close = event.target.closest("[data-figure-close]");
    const dialog = document.querySelector("[data-figure-dialog]");
    if (close && dialog?.open) {
      dialog.close();
      return;
    }
    const image = event.target.closest(".tt-tab-panel img");
    if (image && dialog && typeof dialog.showModal === "function") {
      const target = dialog.querySelector("[data-figure-dialog-image]");
      const caption = dialog.querySelector("[data-figure-dialog-caption]");
      if (!target) return;
      target.src = image.currentSrc || image.src;
      target.alt = image.alt || "Enlarged course figure";
      if (caption) caption.textContent = image.closest("figure")?.querySelector("figcaption")?.textContent || image.alt || "";
      dialog.showModal();
    }
  });

  document.addEventListener("click", event => {
    const dialog = event.target;
    if (dialog.matches?.("[data-figure-dialog]") && dialog.open) {
      const rect = dialog.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
    }
  });

  document.addEventListener("keydown", event => {
    if ((event.key === "Enter" || event.key === " ") && event.target.matches?.(".tt-tab-panel img[role='button']")) {
      event.preventDefault();
      event.target.click();
      return;
    }
    if (event.key === "Escape") {
      const dialog = document.querySelector("[data-figure-dialog]");
      if (dialog?.open) dialog.close();
    }
  });

  document.addEventListener("input", event => {
    if (event.target.matches("[data-outline-search]")) {
      const query = event.target.value.trim().toLocaleLowerCase();
      document.querySelectorAll("[data-outline-item]").forEach(item => {
        item.hidden = query !== "" && !item.textContent.toLocaleLowerCase().includes(query);
      });
    }
  });

  document.addEventListener("submit", async event => {
    const form = event.target.closest("[data-notebook-response]");
    if (!form) return;
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    const feedback = form.querySelector("[data-notebook-feedback]");
    if (!button || !feedback) return;
    button.disabled = true;
    feedback.textContent = "Saving reflection…";
    try {
      const response = await fetch(form.action, {
        method: "POST",
        credentials: "same-origin",
        headers: { "X-CSRFToken": form.querySelector('[name="csrfmiddlewaretoken"]').value },
        body: new FormData(form)
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Reflection could not be saved.");
      feedback.textContent = "Reflection saved to your account.";
    } catch (error) {
      feedback.textContent = error.message || "Reflection could not be saved.";
    } finally {
      button.disabled = false;
    }
  });
  document.addEventListener("submit", async function (event) {
    const form = event.target.closest("[data-guided-reflection]");
    if (!form) return;
    event.preventDefault();
    const button = form.querySelector('button[type="submit"]');
    const feedback = form.querySelector("[data-guided-reflection-feedback]");
    if (!button || !feedback) return;
    button.disabled = true;
    feedback.textContent = "Saving your first reading…";
    try {
      const csrf = form.querySelector('[name="csrfmiddlewaretoken"]');
      const response = await fetch(form.action, {
        method: "POST",
        credentials: "same-origin",
        headers: { "X-CSRFToken": csrf ? csrf.value : "" },
        body: new FormData(form)
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.detail || "Your reflection could not be saved.");
      feedback.textContent = "Saved to your account. Now compare your reasoning with the model reading.";
    } catch (error) {
      feedback.textContent = error.message || "Your reflection could not be saved.";
    } finally {
      button.disabled = false;
    }
  });

})();
