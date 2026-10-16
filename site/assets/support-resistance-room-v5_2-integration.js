/* TradeThesis Learning Room — V5.2 lesson integration.
 * Uses the existing long-form content and interaction pack; historical case-chart images stay withheld.
 */
(() => {
  "use strict";
  const LESSON_IDS = new Set([12, 13, 14]);
  const DATA_BASE = "module5-v5_2/assets/";
  const FIGURE_PANEL_LAYOUTS = {
    "FIG01_breakout_evidence_ladder.png": { width:2661, height:1209, panels:[["Intrabar excursion",0,.13,.33,.75],["Close outside",.33,.13,.32,.75],["Follow-through",.66,.13,.32,.75]]},
    "FIG02_filter_tradeoffs.png": { width:2661, height:1209, panels:[["One close outside",0,.13,.33,.75],["Two closes outside",.33,.13,.32,.75],["Require a return test",.66,.13,.32,.75]]},
    "FIG03_context_changes_the_question.png": { width:2501, height:1226, panels:[["Local view",0,.13,.485,.77],["Wider context",.515,.13,.475,.77]]},
    "FIG04_break_return_response.png": { width:2923, height:1106, panels:[["Before the break",0,.13,.25,.80],["The break",.25,.13,.245,.80],["Return to area",.495,.13,.245,.80],["Response develops",.74,.13,.245,.80]]},
    "FIG05_three_retest_outcomes.png": { width:2695, height:1243, panels:[["Holds beyond",0,.13,.32,.75],["Re-enters range",.32,.13,.33,.75],["Inconclusive",.65,.13,.33,.75]]},
    "FIG06_retest_is_not_owed.png": { width:2547, height:1604, panels:[["No retest",0,.08,.485,.40],["Delayed return",.485,.08,.50,.40],["Shallow return",0,.49,.485,.43],["Deep return, reclaim",.485,.49,.50,.43]]},
    "FIG07_failure_is_not_reverse_signal.png": { width:2695, height:1226, panels:[["Continues through range",0,.13,.33,.75],["Chops around the area",.33,.13,.33,.75],["Reclaims the boundary",.66,.13,.33,.75]]},
    "FIG08_volume_context_not_gate.png": { width:2847, height:1964, panels:[["Price holds · volume expands",0,.055,.48,.415],["Price fails · volume expands",.50,.055,.49,.415],["Price holds · volume muted",0,.53,.48,.425],["Price fails · volume muted",.50,.53,.49,.425]]},
    "FIG09_decision_record_timeline.png": { width:2923, height:1192, panels:[["Before",0,.12,.25,.82],["Break",.25,.12,.245,.82],["Contradiction",.495,.12,.245,.82],["Review",.74,.12,.245,.82]]},
    "FIG10_failed_signal_family.png": { width:3008, height:1792, panels:[["Range-edge upthrust",0,.09,.33,.415],["Spring / downside failure",.33,.09,.33,.415],["Trendline break reclaimed",.66,.09,.33,.415],["First pullback fails",0,.515,.33,.42],["Continuation pattern fails",.33,.515,.33,.42],["Prior swing break fails",.66,.515,.33,.42]]},
    "FIG11_first_pullback_later_failure.png": { width:2551, height:1243, panels:[["First pullback holds",0,.12,.49,.78],["Later pullback fails",.49,.12,.49,.78]]},
    "FIG12_after_failure_alternatives.png": { width:2711, height:1209, panels:[["Range travel",0,.12,.33,.80],["Range interior",.33,.12,.34,.80],["Boundary reclaimed",.67,.12,.32,.80]]},
    "FIG13_gap_and_spike_failures.png": { width:2567, height:1278, panels:[["Gap beyond, then return",0,.12,.475,.81],["Wide-range spike, no hold",.475,.12,.50,.81]]},
    "FIG15_failure_label_checklist.png": { width:2574, height:1295, panels:[["Define signal",0,.29,.255,.22],["Observe attempt",.255,.29,.24,.22],["Find contradiction",.495,.29,.24,.22],["Check response",.735,.29,.24,.22],["Final wording: describe evidence, not cause",.13,.60,.74,.23]]},
    "FIG16_retest_depth_and_closes.png": { width:2695, height:1226, panels:[["Shallow / stays outside",0,.12,.33,.80],["Enters / reclaims",.33,.12,.33,.80],["Closes back inside",.66,.12,.33,.80]]},
    "FIG17_range_vs_trendline_failure.png": { width:2551, height:1261, panels:[["Range boundary",0,.12,.48,.82],["Rising trendline",.48,.12,.495,.82]]},
    "FIG18_neckline_formation_failures.png": { width:2567, height:1261, panels:[["Top formation breakdown reclaims",0,.12,.48,.82],["Bottom formation breakout fails",.48,.12,.495,.82]]},
    "FIG19_simple_break_return_response.png": { width:2103, height:1053, panels:[["Break",.11,.13,.29,.76],["Return",.42,.13,.29,.76],["Response",.71,.13,.285,.76]]},
    "FIG20_simple_retest_outcomes.png": { width:1971, height:1011, panels:[["Hold-like response",.005,.14,.33,.70],["Failure-like response",.335,.14,.33,.70],["Inconclusive response",.665,.14,.333,.70]]},
    "FIG21_failed_breakout_structural_stop.png": { width:2363, height:1229, panels:[["Failed upside break · hypothetical short",0,.10,.495,.88],["Failed downside break · hypothetical long",.495,.10,.505,.88]]},
    "FIG25_continuation_pause_outcomes.png": { width:2721, height:1341, panels:[["Expected break holds",0,.10,.49,.82],["Pause breaks the wrong way",.49,.10,.505,.82]]}
  };
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
      const layout = FIGURE_PANEL_LAYOUTS[src.split("/").pop()];
      if (!layout) {
        return '<figure class="sr-v52-figure"><img loading="lazy" src="' + esc(url) + '" alt="' + esc(block.alt || "") + '"><figcaption>' +
          inline(block.caption || block.alt || "Teaching illustration.") + "</figcaption></figure>";
      }
      const panels = layout.panels.map((panel, index) => {
        const label = panel[0], x = Math.round(panel[1] * layout.width), y = Math.round(panel[2] * layout.height);
        const width = Math.round(panel[3] * layout.width), height = Math.round(panel[4] * layout.height);
        const panelAlt = "Panel " + (index + 1) + " of " + layout.panels.length + ": " + label + ". " + (block.alt || block.caption || "Schematic teaching illustration.");
        return '<figure class="sr-v52-figure sr-v52-figure--panel"><svg class="sr-v52-figure-panel" viewBox="' + x + " " + y + " " + width + " " + height +
          '" width="' + width + '" height="' + height + '" role="img" aria-label="' + esc(panelAlt) + '" data-zoomable="true" focusable="true"><image href="' +
          esc(url) + '" x="0" y="0" width="' + layout.width + '" height="' + layout.height + '" preserveAspectRatio="none"></image></svg><figcaption>' +
          inline(label) + "</figcaption></figure>";
      }).join("");
      return '<section class="sr-v52-figure-set"><p class="sr-v52-figure-set-intro">' +
        inline(block.caption || block.alt || "This figure contains several comparisons. Each panel is separated below for easier reading.") +
        '</p><div class="sr-v52-figure-panels">' + panels + '</div><details class="sr-v52-full-figure"><summary>View the complete original figure</summary>' +
        '<figure class="sr-v52-figure"><img loading="lazy" src="' + esc(url) + '" alt="' + esc(block.alt || "") + '"><figcaption>Complete original composition. Select it to inspect at full size.</figcaption></figure></details></section>';
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
    // SVG is the display source when available, but stage identity remains keyed to the canonical PNG filename.
    if (image.dataset && image.dataset.chartCanonicalFile) return image.dataset.chartCanonicalFile;
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