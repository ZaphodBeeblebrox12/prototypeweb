import { Editor } from "@tiptap/core";
import StarterKit from "@tiptap/starter-kit";
import { TableKit } from "@tiptap/extension-table";
import { Markdown } from "@tiptap/markdown";
import { TradeThesisExtensions } from "./tradethesis-nodes.js";
import {
  appendTradeThesisSidecarNodes,
  buildTradeThesisSidecarReferences,
  resolveTradeThesisDocument,
} from "./tradethesis-sidecar.js";

(() => {
  const root = document.querySelector("[data-tiptap-lab]");
  if (!root) return;

  const mount = root.querySelector("[data-editor-mount]");
  const state = root.querySelector("[data-editor-state]");
  const jsonOutput = root.querySelector("[data-json-output]");
  const markdownInput = root.querySelector("[data-markdown-input]");
  const markdownStatus = root.querySelector("[data-markdown-status]");
  const tableTools = root.querySelector("[data-table-tools]");
  const error = root.querySelector("[data-editor-error]");
  const headingSelect = root.querySelector("[data-heading]");
  const formatButtons = [...root.querySelectorAll("[data-action]")];
  const draftSelect = root.querySelector("[data-draft-select]");
  const lessonSelect = root.querySelector("[data-lesson-select]");
  const loadLessonButton = root.querySelector("[data-load-lesson]");
  const lessonTitle = root.querySelector("[data-lesson-title]");
  const saveButton = root.querySelector("[data-save-draft]");
  const saveStatus = root.querySelector("[data-save-status]");
  const learnerPreview = root.querySelector("[data-learner-preview]");
  const sidecarPanel = root.querySelector("[data-sidecars]");
  const sidecarCopy = root.querySelector("[data-sidecars-copy]");
  const apiBase = String(root.dataset.apiUrl || "");

  if (
    !mount || !state || !jsonOutput || !tableTools || !draftSelect
    || !lessonSelect || !loadLessonButton || !saveButton || !apiBase
  ) return;

  const documentEnvelope = documentValue => ({
    format: "tradethesis.lesson-document",
    version: 1,
    document: documentValue,
  });

  let editor;
  let currentDraftId = "";
  let currentLessonId = "";
  let expectedUpdatedAt = "";
  let currentPreviewUrl = "";
  let isLoading = false;
  let isDirty = false;
  let hasCompatibilityBlockers = false;
  let loaded = false;
  let conflict = false;

  const actionMap = {
    bold: () => editor.chain().focus().toggleBold().run(),
    italic: () => editor.chain().focus().toggleItalic().run(),
    underline: () => editor.chain().focus().toggleUnderline().run(),
    strike: () => editor.chain().focus().toggleStrike().run(),
    bulletList: () => editor.chain().focus().toggleBulletList().run(),
    orderedList: () => editor.chain().focus().toggleOrderedList().run(),
    blockquote: () => editor.chain().focus().toggleBlockquote().run(),
    codeBlock: () => editor.chain().focus().toggleCodeBlock().run(),
    horizontalRule: () => editor.chain().focus().setHorizontalRule().run(),
    table: () => editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run(),
    undo: () => editor.chain().focus().undo().run(),
    redo: () => editor.chain().focus().redo().run(),
    addRowBefore: () => editor.chain().focus().addRowBefore().run(),
    addRowAfter: () => editor.chain().focus().addRowAfter().run(),
    deleteRow: () => editor.chain().focus().deleteRow().run(),
    addColumnBefore: () => editor.chain().focus().addColumnBefore().run(),
    addColumnAfter: () => editor.chain().focus().addColumnAfter().run(),
    deleteColumn: () => editor.chain().focus().deleteColumn().run(),
    deleteTable: () => editor.chain().focus().deleteTable().run(),
  };

  function currentDocument() {
    return documentEnvelope(editor.getJSON());
  }

  function csrfToken() {
    const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  function setStatus(message, tone = "normal") {
    state.textContent = message;
    state.dataset.tone = tone;
    if (saveStatus) saveStatus.textContent = message;
  }

  function syncJson() {
    if (!editor) return;
    jsonOutput.textContent = JSON.stringify(currentDocument(), null, 2);
    if (isLoading) return;
    if (isDirty) {
      setStatus("Unsaved changes", "warning");
    } else if (loaded && !conflict) {
      setStatus("Saved draft · ready to edit", "success");
    } else if (!loaded) {
      setStatus("Choose a saved draft and lesson");
    }
    syncSaveControls();
  }

  function syncSaveControls() {
    const canSave = loaded && isDirty && !conflict && !hasCompatibilityBlockers;
    saveButton.disabled = !canSave;
    loadLessonButton.disabled = !draftSelect.value || !lessonSelect.value;
  }

  function syncToolbar() {
    if (!editor) return;
    const active = {
      bold: editor.isActive("bold"),
      italic: editor.isActive("italic"),
      underline: editor.isActive("underline"),
      strike: editor.isActive("strike"),
      bulletList: editor.isActive("bulletList"),
      orderedList: editor.isActive("orderedList"),
      blockquote: editor.isActive("blockquote"),
      codeBlock: editor.isActive("codeBlock"),
    };
    for (const button of formatButtons) {
      const action = button.dataset.action;
      if (Object.prototype.hasOwnProperty.call(active, action)) {
        button.setAttribute("aria-pressed", String(active[action]));
      }
      button.disabled = !loaded;
    }
    tableTools.classList.toggle("is-visible", editor.isActive("table"));
    headingSelect.value = editor.isActive("heading")
      ? String(editor.getAttributes("heading").level || 1)
      : "paragraph";
    headingSelect.disabled = !loaded;
    const undo = root.querySelector('[data-action="undo"]');
    const redo = root.querySelector('[data-action="redo"]');
    if (undo) undo.disabled = !loaded || !editor.can().undo();
    if (redo) redo.disabled = !loaded || !editor.can().redo();
  }

  function safeLink(value) {
    try {
      const parsed = new URL(value, window.location.origin);
      return ["http:", "https:", "mailto:"].includes(parsed.protocol) ? parsed.href : "";
    } catch {
      return "";
    }
  }

  function addLink() {
    const previous = editor.getAttributes("link").href || "";
    const entered = window.prompt("Enter a link address", previous);
    if (entered === null) return;
    const href = safeLink(entered.trim());
    if (!href) {
      window.alert("Use a valid http, https or mailto link.");
      return;
    }
    editor.chain().focus().extendMarkRange("link").setLink({ href }).run();
  }

  function markDirty() {
    if (!loaded || isLoading || conflict) return;
    isDirty = true;
    syncJson();
  }

  async function fetchJson(url, options = {}) {
    const response = await fetch(url, {
      credentials: "same-origin",
      cache: "no-store",
      ...options,
      headers: {
        ...(options.headers || {}),
        ...(options.method && options.method !== "GET" ? { "X-CSRFToken": csrfToken() } : {}),
      },
    });
    let payload;
    try {
      payload = await response.json();
    } catch {
      throw new Error("The server returned an unreadable response.");
    }
    if (!response.ok) {
      const errorMessage = Array.isArray(payload.detail)
        ? payload.detail.join(" ")
        : String(payload.detail || "The request could not be completed.");
      const requestError = new Error(errorMessage);
      requestError.status = response.status;
      requestError.payload = payload;
      throw requestError;
    }
    return payload;
  }

  function populateDrafts(drafts) {
    draftSelect.replaceChildren();
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = drafts.length ? "Select a saved draft…" : "No editable drafts found";
    draftSelect.append(placeholder);

    for (const draft of drafts) {
      const option = document.createElement("option");
      option.value = draft.id;
      const date = draft.updated_at ? new Date(draft.updated_at).toLocaleString() : "";
      option.textContent = draft.title + (draft.status === "rejected" ? " · Returned" : "")
        + (date ? " · " + date : "");
      option.dataset.draft = JSON.stringify(draft);
      draftSelect.append(option);
    }
    draftSelect.disabled = drafts.length === 0;
    lessonSelect.replaceChildren(new Option("Choose a draft first", ""));
    lessonSelect.disabled = true;
    syncSaveControls();
  }

  function selectedDraft() {
    const option = draftSelect.selectedOptions[0];
    if (!option || !option.dataset.draft) return null;
    try {
      return JSON.parse(option.dataset.draft);
    } catch {
      return null;
    }
  }

  function populateLessons(draft) {
    lessonSelect.replaceChildren();
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = "Select a lesson…";
    lessonSelect.append(placeholder);
    for (const module of draft?.modules || []) {
      const group = document.createElement("optgroup");
      group.label = module.title || "Module";
      for (const lesson of module.lessons || []) {
        const option = document.createElement("option");
        option.value = lesson.id;
        option.textContent = lesson.title || "Untitled lesson";
        group.append(option);
      }
      if (group.children.length) lessonSelect.append(group);
    }
    lessonSelect.disabled = !draft || !draft.modules?.some(module => module.lessons?.length);
    syncSaveControls();
  }

  function displaySidecars(sidecar) {
    if (!sidecarPanel || !sidecarCopy) return;
    const items = [];
    const questionCount = Object.keys(sidecar.questions || {}).length;
    if (questionCount) items.push(questionCount + " practice question" + (questionCount === 1 ? "" : "s"));
    if (Object.keys(sidecar.figures || {}).length) {
      items.push(Object.keys(sidecar.figures).length + " figure / image-group reference(s)");
    }
    if (sidecar.tables && Object.keys(sidecar.tables).length) {
      items.push(Object.keys(sidecar.tables).length + " structured table(s)");
    }
    if (Object.keys(sidecar.regionalBlocks || {}).length
      || Object.keys(sidecar.regionalLessonContent || {}).length) {
      items.push("regional lesson content");
    }
    if (sidecar.notebook) items.push("notebook prompts");
    if (sidecar.reflection) items.push("reflection content");
    if (sidecar.protectedVideo) items.push("protected video · " + sidecar.protectedVideo.status);
    sidecarCopy.textContent = items.length
      ? items.join(" · ") + ". These records stay in their existing Academy fields and are retained when you save the lesson body."
      : "No separate question, notebook, reflection or protected-video records were found for this lesson.";
    sidecarPanel.hidden = false;
  }

  function populatePreview(url) {
    currentPreviewUrl = String(url || "");
    if (!learnerPreview) return;
    learnerPreview.href = currentPreviewUrl;
    learnerPreview.hidden = !currentPreviewUrl;
  }

  function loadDocumentFromLesson(lesson) {
    if (lesson.documentValidationError) {
      throw new Error(
        "This lesson contains a structured document version the current editor cannot safely open: "
        + lesson.documentValidationError + " The lesson is read-only here; use the legacy editor or a compatible editor version.",
      );
    }
    if (lesson.document && lesson.document.document) {
      editor.commands.setContent(lesson.document.document);
    } else {
      editor.commands.setContent(String(lesson.content || ""), { contentType: "markdown" });
    }

    const sidecar = buildTradeThesisSidecarReferences(lesson);
    const withSidecars = appendTradeThesisSidecarNodes(currentDocument(), sidecar);
    editor.commands.setContent(withSidecars.document || withSidecars);
    const resolved = resolveTradeThesisDocument(currentDocument(), sidecar);
    const blocking = resolved.diagnostics.filter(item => item.reason !== "preserved-opaque-marker");
    hasCompatibilityBlockers = blocking.length > 0;
    displaySidecars(sidecar);

    if (blocking.length) {
      const summary = blocking.slice(0, 3).map(item => item.nodeType + ": " + item.reason).join(" · ");
      setStatus("Compatibility warning — " + summary, "warning");
      saveStatus.textContent = "Saving is disabled because one or more lesson references could not be resolved. Nothing has been removed.";
    } else if (resolved.diagnostics.length) {
      setStatus("Loaded · unknown markers preserved", "warning");
    }
    return sidecar;
  }

  async function loadLesson() {
    const draftId = draftSelect.value;
    const lessonId = lessonSelect.value;
    if (!draftId || !lessonId) return;
    if (isDirty && !window.confirm("Discard the unsaved changes in this lesson and open another one?")) {
      return;
    }

    isLoading = true;
    loaded = false;
    isDirty = false;
    conflict = false;
    hasCompatibilityBlockers = false;
    syncSaveControls();
    setStatus("Loading saved lesson…");
    saveStatus.textContent = "Loading the saved Course Builder lesson.";
    try {
      const url = apiBase + encodeURIComponent(draftId) + "/" + encodeURIComponent(lessonId) + "/";
      const payload = await fetchJson(url);
      const lesson = payload.lesson;
      currentDraftId = draftId;
      currentLessonId = lessonId;
      expectedUpdatedAt = payload.expected_updated_at;
      lessonTitle.textContent = payload.draft.title + " · " + lesson.title;
      populatePreview(payload.learner_preview_url);
      loadDocumentFromLesson(lesson);
      loaded = !lesson.documentValidationError;
      isDirty = false;
      conflict = false;
      setStatus(loaded ? "Loaded saved lesson" : "Read-only compatibility warning", loaded ? "success" : "warning");
      saveStatus.textContent = loaded
        ? "Edits are saved only to this Course Builder draft. Review and publishing remain separate."
        : "This document version is not supported here. The saved lesson has not been changed.";
      markdownInput.value = String(lesson.content || "");
      markdownStatus.textContent = "Loaded the current Markdown compatibility mirror.";
    } catch (loadError) {
      loaded = false;
      setStatus("Could not load lesson", "error");
      saveStatus.textContent = String(loadError.message || loadError);
      window.alert("The lesson could not be opened: " + String(loadError.message || loadError));
    } finally {
      isLoading = false;
      syncToolbar();
      syncJson();
      syncSaveControls();
    }
  }

  async function saveDraft() {
    if (!loaded || !isDirty || conflict || hasCompatibilityBlockers) return;
    let markdown;
    try {
      markdown = editor.getMarkdown();
    } catch (exportError) {
      saveStatus.textContent = "Save stopped: " + String(exportError?.message || "The lesson cannot be exported without losing content.");
      return;
    }

    saveButton.disabled = true;
    saveStatus.textContent = "Saving this lesson to the selected draft…";
    try {
      const url = apiBase + encodeURIComponent(currentDraftId) + "/" + encodeURIComponent(currentLessonId) + "/";
      const payload = await fetchJson(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          expected_updated_at: expectedUpdatedAt,
          document: currentDocument(),
          markdown,
        }),
      });
      expectedUpdatedAt = payload.updated_at;
      currentPreviewUrl = payload.learner_preview_url || currentPreviewUrl;
      populatePreview(currentPreviewUrl);
      isDirty = false;
      conflict = false;
      setStatus("Saved · draft updated", "success");
      saveStatus.textContent = "Saved successfully. Open the learner preview to compare the saved draft with the existing Academy renderer.";
      markdownInput.value = markdown;
      markdownStatus.textContent = "Markdown compatibility mirror updated with the saved lesson.";
    } catch (saveError) {
      if (saveError.status === 409 || saveError.status === 410) {
        conflict = true;
        setStatus("Save blocked · draft changed", "warning");
        saveStatus.textContent = String(saveError.message || saveError) + " Reload the lesson before editing further.";
      } else {
        saveStatus.textContent = "Save failed: " + String(saveError.message || saveError) + " Your unsaved changes remain in this editor.";
      }
    } finally {
      syncSaveControls();
    }
  }

  function setInitialEditorEnabled(enabled) {
    editor.setEditable(Boolean(enabled));
    for (const control of root.querySelectorAll("[data-action], [data-heading], [data-markdown], [data-export]")) {
      control.disabled = !enabled;
    }
    syncToolbar();
  }

  editor = new Editor({
    element: mount,
    extensions: [
      StarterKit.configure({ heading: { levels: [1, 2, 3] } }),
      TableKit.configure({ table: { resizable: true } }),
      ...TradeThesisExtensions,
      Markdown.configure({ markedOptions: { gfm: true } }),
    ],
    content: {
      type: "doc",
      content: [{ type: "paragraph" }],
    },
    editable: false,
    editorProps: {
      attributes: {
        "aria-label": "Lesson content",
        spellcheck: "true",
      },
    },
    onCreate: () => {
      syncJson();
      syncToolbar();
      setStatus("Loading saved course drafts…");
    },
    onUpdate: () => {
      if (loaded && !isLoading) isDirty = true;
      syncJson();
      syncToolbar();
      syncSaveControls();
    },
    onSelectionUpdate: syncToolbar,
    onTransaction: syncToolbar,
  });

  root.addEventListener("click", event => {
    const button = event.target.closest("[data-action]");
    if (!button || button.disabled) return;
    const action = button.dataset.action;
    if (action === "link") {
      addLink();
      return;
    }
    const run = actionMap[action];
    if (run) run();
  });

  headingSelect.addEventListener("change", () => {
    if (!loaded) return;
    const value = headingSelect.value;
    if (value === "paragraph") {
      editor.chain().focus().setParagraph().run();
    } else {
      editor.chain().focus().setHeading({ level: Number(value) }).run();
    }
  });

  draftSelect.addEventListener("change", () => {
    populateLessons(selectedDraft());
  });
  loadLessonButton.addEventListener("click", loadLesson);
  saveButton.addEventListener("click", saveDraft);

  root.addEventListener("click", async event => {
    const button = event.target.closest("[data-markdown]");
    if (!button || !markdownInput || !markdownStatus || !loaded) return;

    const action = button.dataset.markdown;
    if (action === "import") {
      const source = markdownInput.value;
      if (!source.trim()) {
        markdownStatus.textContent = "Paste Markdown into the box first.";
        return;
      }
      const confirmed = window.confirm("Replace the editor contents with this Markdown?");
      if (!confirmed) return;
      try {
        editor.commands.setContent(source, { contentType: "markdown" });
        markdownStatus.textContent = "Imported Markdown with typed TradeThesis references. Save to update the selected draft.";
      } catch (importError) {
        markdownStatus.textContent = "Markdown could not be imported: " + String(importError?.message || "Unknown conversion error.");
      }
      return;
    }

    let markdown;
    try {
      markdown = editor.getMarkdown();
    } catch (exportError) {
      markdownStatus.textContent = "Markdown export failed: " + String(exportError?.message || "Unknown conversion error.");
      return;
    }
    markdownInput.value = markdown;
    if (action === "export") {
      markdownStatus.textContent = "Current editor content exported to the Markdown box.";
      return;
    }
    if (action === "copy") {
      try {
        await navigator.clipboard.writeText(markdown);
        markdownStatus.textContent = "Markdown copied to clipboard.";
      } catch {
        markdownStatus.textContent = "Clipboard unavailable. Select and copy the Markdown in the box.";
      }
      return;
    }
    if (action === "download") {
      const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = "tradethesis-lesson-test.md";
      anchor.click();
      URL.revokeObjectURL(url);
      markdownStatus.textContent = "Markdown file downloaded.";
    }
  });

  root.addEventListener("click", async event => {
    const button = event.target.closest("[data-export]");
    if (!button || !loaded) return;
    const json = JSON.stringify(currentDocument(), null, 2);
    if (button.dataset.export === "copy") {
      try {
        await navigator.clipboard.writeText(json);
        state.textContent = "JSON copied";
      } catch {
        state.textContent = "Clipboard unavailable · use Download JSON";
      }
      return;
    }
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "tradethesis-lesson-document-v1.json";
    anchor.click();
    URL.revokeObjectURL(url);
  });

  window.addEventListener("beforeunload", event => {
    if (loaded && isDirty) {
      event.preventDefault();
      event.returnValue = "";
    }
    editor?.destroy();
  }, { once: true });

  async function initialiseDraftList() {
    try {
      const payload = await fetchJson(apiBase);
      populateDrafts(payload.drafts || []);
      if (!payload.drafts?.length) {
        setStatus("No editable saved drafts found", "warning");
        saveStatus.textContent = "Create or save a draft in the Course Builder first. It will appear here.";
        return;
      }
      draftSelect.value = payload.drafts[0].id;
      populateLessons(payload.drafts[0]);
      const firstLesson = payload.drafts[0].modules
        ?.flatMap(module => module.lessons || [])[0];
      if (firstLesson) {
        lessonSelect.value = firstLesson.id;
        await loadLesson();
      } else {
        setStatus("The selected draft contains no lessons", "warning");
      }
    } catch (loadError) {
      setStatus("Could not load saved drafts", "error");
      saveStatus.textContent = String(loadError.message || loadError);
    }
  }

  window.addEventListener("error", event => {
    if (!String(event?.message || "").toLowerCase().includes("tiptap")) return;
    if (error) error.hidden = false;
  });

  setInitialEditorEnabled(false);
  initialiseDraftList();
})();
