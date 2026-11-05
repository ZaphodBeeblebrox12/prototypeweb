import { Editor } from "@tiptap/core";
import StarterKit from "@tiptap/starter-kit";
import { TableKit } from "@tiptap/extension-table";
import { Markdown } from "@tiptap/markdown";
import { TradeThesisExtensions, prepareTradeThesisMarkdown } from "./tradethesis-nodes.js";

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

  if (!mount || !state || !jsonOutput || !tableTools) return;

  const documentEnvelope = document => ({
    format: "tradethesis.lesson-document",
    version: 1,
    document,
  });

  let editor;
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

  function syncJson() {
    jsonOutput.textContent = JSON.stringify(currentDocument(), null, 2);
    state.textContent = "Prototype · not saved";
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
    }
    tableTools.classList.toggle("is-visible", editor.isActive("table"));
    const heading = editor.getAttributes("heading").level;
    headingSelect.value = editor.isActive("heading") ? String(heading || 1) : "paragraph";
    root.querySelector('[data-action="undo"]').disabled = !editor.can().undo();
    root.querySelector('[data-action="redo"]').disabled = !editor.can().redo();
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
    editorProps: {
      attributes: {
        "aria-label": "Lesson content",
        spellcheck: "true",
      },
    },
    onCreate: () => {
      syncJson();
      syncToolbar();
      state.textContent = "Ready · prototype only";
    },
    onUpdate: () => {
      syncJson();
      syncToolbar();
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
    const value = headingSelect.value;
    if (value === "paragraph") {
      editor.chain().focus().setParagraph().run();
    } else {
      editor.chain().focus().setHeading({ level: Number(value) }).run();
    }
  });

  root.addEventListener("click", async event => {
    const button = event.target.closest("[data-markdown]");
    if (!button || !markdownInput || !markdownStatus) return;

    const action = button.dataset.markdown;
    if (action === "import") {
      const source = markdownInput.value;
      if (!source.trim()) {
        markdownStatus.textContent = "Paste Markdown into the box first.";
        return;
      }
      const confirmed = window.confirm(
        "Replace the editor contents with this Markdown? Recognised TradeThesis markers will appear as reference placeholders; linked records and protected media are not loaded in this sandbox."
      );
      if (!confirmed) return;
      try {
        editor.commands.setContent(prepareTradeThesisMarkdown(source), { contentType: "markdown" });
        markdownStatus.textContent = "Imported Markdown with typed TradeThesis reference placeholders. Linked records are not loaded.";
        state.textContent = "Markdown imported · prototype only";
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
    if (!button) return;
    const json = JSON.stringify(currentDocument(), null, 2);
    if (button.dataset.export === "copy") {
      try {
        await navigator.clipboard.writeText(json);
        state.textContent = "JSON copied · not saved";
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
    state.textContent = "JSON downloaded · not saved";
  });

  window.addEventListener("beforeunload", () => editor?.destroy(), { once: true });
})();

// If the application bundle was loaded but initialization failed, expose a
// visible fallback rather than leaving a blank editor surface.
window.addEventListener("error", event => {
  if (!String(event?.message || "").includes("tiptap")) return;
  const fallback = document.querySelector("[data-editor-error]");
  if (fallback) fallback.hidden = false;
});
