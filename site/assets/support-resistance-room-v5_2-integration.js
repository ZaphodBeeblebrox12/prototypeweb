/* TradeThesis Learning Room — V5.2 lesson integration.
 * Uses the existing long-form content and interaction pack; historical case-chart images stay withheld.
 */
(() => {
  "use strict";
  const LESSON_IDS = new Set([12, 13, 14]);
  const DATA_BASE = "module5-v5_2/assets/";
  let deepPack = null;
  let interactionPack = null;
  let renderedLessonId = null;
  const attemptedStages = new Set();
  let shouldSyncUrl = new URLSearchParams(window.location.search).has("lesson");
  const byId = id => document.getElementById(id);
  const esc = value => String(value == null ? "" : value).replace(/[&<>"']/g, ch => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
  })[ch]);

  function inline(value) {
    return esc(value)
      .replace(/\x60([^\x60]+)\x60/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>")
      .replace(/\*([^*]+)\*/g, "<em>$1</em>");
  }

  function loadScript(globalName, fileName) {
    if (window[globalName]) return Promise.resolve(window[globalName]);
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = new URL(DATA_BASE + fileName, window.location.href).href;
      script.dataset.srV52Loaded = fileName;
      script.onload = () => window[globalName] ? resolve(window[globalName]) : reject(new Error(globalName + " not exported by " + fileName));
      script.onerror = () => reject(new Error("Could not load " + fileName));
      document.head.appendChild(script);
    });
  }

  function ensurePanel() {
    let panel = byId("sr-v52-longform");
    if (panel) return panel;
    const anchor = byId("sr-work-grid");
    if (!anchor || !anchor.parentNode) return null;
    panel = document.createElement("section");
    panel.id = "sr-v52-longform";
    panel.className = "sr-v52-reading";
    panel.hidden = true;
    panel.setAttribute("aria-labelledby", "sr-v52-heading");
    anchor.parentNode.insertBefore(panel, anchor);
    return panel;
  }

  function textOnlyCase(block, lessonId) {
    return '<aside class="sr-v52-case-study" aria-label="Text-only case study">' +
      '<div class="sr-v52-kicker">CASE STUDY · TEXT ONLY</div>' +
      '<strong>Historical chart image withheld pending redistribution-rights review</strong>' +
      '<p>' + inline(block.caption || "Historical case reference.") + '</p>' +
      '<p class="sr-v52-rights-note">The original historical chart is not displayed. The staged exercise uses synthetic illustrative candles and is not the historical case data.</p>' +
      '<p>' + inline(block.question || "Describe the visible evidence and state what remains uncertain.") + '</p>' +
      '<button class="button sr-room-secondary sr-v52-jump" type="button" data-sr-v52-jump="chart" data-sr-v52-lesson="' + lessonId + '">Open the staged synthetic chart →</button>' +
      '</aside>';
  }

  function renderBlock(block, lessonId) {
    if (!block || typeof block !== "object") return "";
    if (block.type === "p") return "<p>" + inline(block.text || "") + "</p>";
    if (block.type === "quote") return '<blockquote class="sr-v52-quote">' + inline(block.text || "") + "</blockquote>";
    if (block.type === "ul") return "<ul>" + (block.items || []).map(item => "<li>" + inline(item) + "</li>").join("") + "</ul>";
    if (block.type === "table") {
      return '<div class="sr-v52-table-wrap"><table><thead><tr>' +
        (block.headers || []).map(item => "<th scope=\"col\">" + inline(item) + "</th>").join("") +
        "</tr></thead><tbody>" + (block.rows || []).map(row => "<tr>" + row.map(item => "<td>" + inline(item) + "</td>").join("") + "</tr>").join("") +
        "</tbody></table></div>";
    }
    if (block.type === "relatedCourse") {
      return '<aside class="sr-v52-related"><span>' + esc(block.label || "RELATED COURSE") + "</span><h4>" +
        esc(block.title || "Continue learning") + "</h4><p>" + inline(block.text || "") + "</p>" +
        (block.note ? "<p>" + inline(block.note) + "</p>" : "") + "</aside>";
    }
    if (block.type === "figure") {
      const src = String(block.src || "");
      if (!src.startsWith("assets/figures/")) return '<aside class="sr-v52-figure-note">Figure withheld: this is not an approved schematic asset.</aside>';
      const url = new URL("module5-v5_2/" + src, window.location.href).href;
      return '<figure class="sr-v52-figure"><img loading="lazy" src="' + esc(url) + '" alt="' + esc(block.alt || "") + '"><figcaption>' +
        inline(block.caption || block.alt || "Teaching illustration.") + "</figcaption></figure>";
    }
    if (block.type === "caseChart") return textOnlyCase(block, lessonId);
    return '<aside class="sr-v52-figure-note"><strong>Content block needs review</strong><p>Unsupported source block type: ' + esc(block.type || "(missing type)") + "</p></aside>";
  }

  function currentLessonId() {
    const label = byId("sr-lesson-number") ? byId("sr-lesson-number").textContent : "";
    const match = label.match(/LESSON\s+(\d+)/i);
    return match ? Number(match[1]) : Number(new URLSearchParams(window.location.search).get("lesson")) || 1;
  }

  function renderLesson(lessonId) {
    const panel = ensurePanel();
    if (!panel) return;
    const lesson = deepPack && deepPack[String(lessonId)];
    if (!LESSON_IDS.has(lessonId) || !lesson) {
      panel.hidden = true;
      panel.replaceChildren();
      renderedLessonId = null;
      byId("sr-v52-stage-model-answer")?.remove();
      return;
    }
    panel.hidden = false;
    if (renderedLessonId === lessonId) {
      updateModelAnswer();
      updateFinalReview();
      return;
    }
    const sections = Array.isArray(lesson.sections) ? lesson.sections : [];
    const sectionHtml = sections.map(section => '<section class="sr-v52-section"><h3>' + esc(section.title || "Lesson section") + "</h3>" +
      (section.blocks || []).map(block => renderBlock(block, lessonId)).join("") + "</section>").join("");
    const keys = ["observation", "interpretation", "alternative", "revision"];
    const labels = { observation: "Observation", interpretation: "Interpretation", alternative: "Alternative explanation", revision: "What would change your view?" };
    const prompts = lesson.notePrompts || {};
    const promptHtml = keys.map(key => {
      const item = prompts[key];
      if (!item || !item.prompt) return "";
      return '<div class="sr-v52-note-prompt"><strong>' + esc(item.title || labels[key]) + "</strong><p>" + inline(item.prompt) + "</p></div>";
    }).join("");
    const interaction = interactionPack && interactionPack[String(lessonId)] || {};
    const rubric = Array.isArray(interaction.modelAnswerRubric) ? interaction.modelAnswerRubric : [];
    const rubricHtml = rubric.map(item => "<li>" + inline(item) + "</li>").join("");
    const title = byId("sr-lesson-title") ? byId("sr-lesson-title").textContent : "Complete lesson";
    panel.innerHTML = '<header class="sr-v52-reading-header"><div><span class="sr-room-eyebrow">MODULE 5 · FULL-LENGTH TEACHING</span><h3 id="sr-v52-heading">' + esc(title) +
      '</h3></div><span class="sr-v52-section-count">' + sections.length + " sections</span></header>" +
      '<p class="sr-v52-intro">Full V5.2 lesson material, with teaching distinctions, worked explanations, tables and schematic figures. Historical chart images remain withheld; exercise charts are synthetic and separately labelled.</p>' +
      '<div class="sr-v52-sections">' + sectionHtml + "</div>" +
      (promptHtml ? '<section class="sr-v52-field-notes"><div class="sr-v52-kicker">FIELD NOTE FRAMEWORK</div><h4>Keep the first read, then record what changed</h4><div class="sr-v52-note-grid">' + promptHtml +
        '</div><p class="sr-v52-note-help">These prompts work with the existing My notes tab. Notes continue to use the Learning Room’s current browser-local storage.</p><button type="button" class="button sr-room-secondary sr-v52-jump" data-sr-v52-jump="notes">Open My notes →</button></section>' : "") +
      '<div class="sr-v52-reading-end"><strong>Carry the method forward</strong><p>' + inline(lesson.takeaway || "Describe the evidence, state a provisional interpretation, and keep an alternative open.") +
      '</p><button type="button" class="button sr-room-primary sr-v52-jump" data-sr-v52-jump="chart">Work through the staged chart →</button></div>' +
      '<section class="sr-v52-final-review" id="sr-v52-final-review" hidden><div class="sr-v52-kicker">AFTER THE REVEAL</div><h4>Review the sequence, not just the ending</h4><p>' +
      inline(interaction.reveal || "Compare the evidence you recorded with the way the sequence developed.") + "</p>" +
      (rubricHtml ? "<h5>Self-check rubric</h5><ul>" + rubricHtml + "</ul>" : "") + "</section>";
    const noteField = byId("sr-lesson-notes");
    if (noteField) noteField.placeholder = keys.map(key => prompts[key] && prompts[key].prompt ?
      (prompts[key].title || labels[key]) + "\n" + prompts[key].prompt : "").filter(Boolean).join("\n\n");
    renderedLessonId = lessonId;
    updateModelAnswer();
    updateFinalReview();
  }

  function syncUrl(lessonId) {
    if (!shouldSyncUrl) return;
    const url = new URL(window.location.href);
    url.searchParams.set("lesson", String(lessonId));
    window.history.replaceState(window.history.state, "", url.href);
  }

  function currentChartFilename() {
    const image = byId("sr-chart-image");
    if (!image || !image.getAttribute("src")) return "";
    try { return new URL(image.getAttribute("src"), window.location.href).pathname.split("/").pop(); }
    catch (_) { return image.getAttribute("src").split("/").pop(); }
  }

  function currentStageKey(lessonId) {
    const filename = currentChartFilename();
    return filename ? String(lessonId) + ":" + filename : "";
  }

  function stageForCurrentChart(lessonId) {
    if (!LESSON_IDS.has(lessonId) || !interactionPack) return null;
    const filename = currentChartFilename();
    if (!filename) return null;
    const stages = interactionPack[String(lessonId)] && interactionPack[String(lessonId)].stages || [];
    return stages.find(stage => String(stage.image || "").split("/").pop() === filename) || null;
  }

  function updateModelAnswer() {
    const id = currentLessonId();
    const stage = stageForCurrentChart(id);
    const countText = byId("sr-chart-stage-count") ? byId("sr-chart-stage-count").textContent : "";
    const countMatch = countText.match(/View\s+(\d+)\s+of\s+(\d+)/i);
    const stageKey = currentStageKey(id);
    const hasAttempt = !!stageKey && attemptedStages.has(stageKey);
    if (!stage || !countMatch) {
      byId("sr-v52-stage-model-answer")?.remove();
      return;
    }
    const cue = byId("sr-practice-cue");
    const host = cue && cue.closest(".sr-room-cue") || byId("sr-practice-response") && byId("sr-practice-response").parentElement;
    if (!host) return;
    let panel = byId("sr-v52-stage-model-answer");
    if (!panel) {
      panel = document.createElement("section");
      panel.id = "sr-v52-stage-model-answer";
      panel.className = "sr-v52-model-answer";
      panel.setAttribute("aria-label", "V5.2 model response");
      host.after(panel);
    }
    const answerKey = id + ":" + (stage.image || "") + ":" + (stage.title || "");
    if (panel.dataset.answerKey !== answerKey) {
      panel.dataset.answerKey = answerKey;
      panel.replaceChildren();
      const kicker = document.createElement("span");
      kicker.className = "sr-room-eyebrow";
      kicker.textContent = "V5.2 MODEL RESPONSE · " + (stage.title || ("LESSON " + id));
      const details = document.createElement("details");
      details.className = "sr-v52-model-details";
      const summary = document.createElement("summary");
      summary.textContent = "Compare with a model response";
      const body = document.createElement("div");
      body.className = "sr-v52-model-body";
      const answer = document.createElement("p");
      answer.textContent = stage.modelAnswer || "Compare your description with the visible candles. Name the evidence, keep the claim limited, and retain an alternative.";
      body.appendChild(answer);
      if (stage.selfCheck) {
        const check = document.createElement("p");
        check.className = "sr-v52-self-check";
        check.textContent = "Self-check: " + stage.selfCheck;
        body.appendChild(check);
      }
      details.append(summary, body);
      panel.append(kicker, details);
    }
    panel.hidden = !hasAttempt;
  }

  function updateFinalReview() {
    const panel = byId("sr-v52-final-review");
    if (!panel) return;
    const match = ((byId("sr-chart-stage-count") && byId("sr-chart-stage-count").textContent) || "").match(/View\s+(\d+)\s+of\s+(\d+)/i);
    const lessonId = currentLessonId();
    const stageKey = currentStageKey(lessonId);
    const hasAttempt = !!stageKey && attemptedStages.has(stageKey);
    const last = match && Number(match[1]) === Number(match[2]);
    panel.hidden = !LESSON_IDS.has(lessonId) || !last || !hasAttempt;
  }

  function onJump(event) {
    const button = event.target.closest("[data-sr-v52-jump]");
    if (!button) return;
    event.preventDefault();
    if (button.dataset.srV52Jump === "notes") {
      const notesTab = byId("sr-tab-button-notes");
      if (notesTab) notesTab.click();
      const field = byId("sr-lesson-notes");
      if (field) {
        field.scrollIntoView({ behavior: "smooth", block: "center" });
        window.setTimeout(() => field.focus({ preventScroll: true }), 0);
      }
    } else {
      const chart = byId("sr-chart-figure");
      const response = byId("sr-practice-response");
      if (chart) chart.scrollIntoView({ behavior: "smooth", block: "start" });
      if (response) window.setTimeout(() => response.focus({ preventScroll: true }), 180);
    }
  }

  async function init() {
    const sheet = document.createElement("link");
    sheet.rel = "stylesheet";
    sheet.href = new URL("assets/support-resistance-room-v5_2-integration.css", window.location.href).href;
    sheet.dataset.srV52Style = "true";
    document.head.appendChild(sheet);
    try {
      const values = await Promise.all([
        loadScript("MODULE5_DEEP_CONTENT", "module5-deep-content.js"),
        loadScript("MODULE5_INTERACTIONS", "module5-interactions.js")
      ]);
      deepPack = values[0];
      interactionPack = values[1];
    } catch (error) {
      const panel = ensurePanel();
      if (panel) {
        panel.hidden = false;
        panel.innerHTML = '<div class="sr-v52-load-error"><strong>The full lesson reading could not be loaded.</strong><p>The shorter lesson remains available. Refresh to retry.</p><small>' + esc(error.message) + "</small></div>";
      }
      console.error("TradeThesis V5.2 integration failed to load its content source.", error);
      return;
    }
    if (!byId("sr-lesson-title") || !byId("sr-lesson-number")) return;
    const param = Number(new URLSearchParams(window.location.search).get("lesson"));
    if ([12, 13, 14].includes(param) && param !== currentLessonId()) {
      const button = document.querySelector('[data-lesson-id="' + param + '"]');
      if (button) button.click();
    }
    renderLesson(currentLessonId());
    syncUrl(currentLessonId());
    const lessonObserver = new MutationObserver(() => {
      const id = currentLessonId();
      if (id !== renderedLessonId) renderLesson(id);
      syncUrl(id);
      updateModelAnswer();
      updateFinalReview();
    });
    lessonObserver.observe(byId("sr-lesson-number"), { childList: true, characterData: true, subtree: true });
    lessonObserver.observe(byId("sr-lesson-title"), { childList: true, characterData: true, subtree: true });
    const stageObserver = new MutationObserver(() => { updateModelAnswer(); updateFinalReview(); });
    if (byId("sr-chart-stage-count")) stageObserver.observe(byId("sr-chart-stage-count"), { childList: true, characterData: true, subtree: true });
    document.addEventListener("input", event => {
      if (event.target && event.target.id === "sr-practice-response") {
        const key = currentStageKey(currentLessonId());
        if (key && event.target.value.trim()) attemptedStages.add(key);
        updateModelAnswer();
        updateFinalReview();
      }
    });
    document.addEventListener("change", event => {
      if (event.target && event.target.id === "sr-attempt-made") {
        const key = currentStageKey(currentLessonId());
        if (key && event.target.checked) attemptedStages.add(key);
        updateModelAnswer();
        updateFinalReview();
      }
    });
    document.addEventListener("click", event => {
      onJump(event);
      if (event.target.closest("[data-lesson-id], #sr-previous-button, #sr-next-button")) {
        shouldSyncUrl = true;
        window.requestAnimationFrame(() => syncUrl(currentLessonId()));
      }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init, { once: true });
  else init();
})();