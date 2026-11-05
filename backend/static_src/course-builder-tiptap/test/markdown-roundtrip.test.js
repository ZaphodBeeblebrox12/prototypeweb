import assert from "node:assert/strict";
import test from "node:test";
import { JSDOM } from "jsdom";
import { Editor } from "@tiptap/core";
import StarterKit from "@tiptap/starter-kit";
import { TableKit } from "@tiptap/extension-table";
import { Markdown } from "@tiptap/markdown";

function createEditor(markdown) {
  const dom = new JSDOM("<!doctype html><html><body><div id='editor'></div></body></html>", {
    url: "https://tradethesis.test/",
  });

  globalThis.window = dom.window;
  globalThis.document = dom.window.document;
  globalThis.Node = dom.window.Node;
  globalThis.HTMLElement = dom.window.HTMLElement;
  globalThis.MutationObserver = dom.window.MutationObserver;
  globalThis.DOMParser = dom.window.DOMParser;
  globalThis.getComputedStyle = dom.window.getComputedStyle.bind(dom.window);
  Object.defineProperty(globalThis, "navigator", {
    configurable: true,
    value: dom.window.navigator,
  });

  const editor = new Editor({
    element: dom.window.document.querySelector("#editor"),
    extensions: [
      StarterKit.configure({ heading: { levels: [1, 2, 3] } }),
      TableKit.configure({ table: { resizable: false } }),
      Markdown.configure({ markedOptions: { gfm: true } }),
    ],
    content: markdown,
    contentType: "markdown",
  });

  return {
    editor,
    close() {
      editor.destroy();
      dom.window.close();
      delete globalThis.window;
      delete globalThis.document;
      delete globalThis.Node;
      delete globalThis.HTMLElement;
      delete globalThis.MutationObserver;
      delete globalThis.DOMParser;
      delete globalThis.getComputedStyle;
      delete globalThis.navigator;
    },
  };
}

test("Markdown round-trip preserves common lesson formatting", () => {
  const source = [
    "# Lesson heading",
    "",
    "A paragraph with **bold**, *italic*, and [a link](https://example.com).",
    "",
    "- First point",
    "- Second point",
    "",
    "> A short quotation.",
    "",
    "```text",
    "A code example",
    "```",
  ].join("\n");

  const harness = createEditor(source);
  try {
    const json = harness.editor.getJSON();
    const serialized = harness.editor.getMarkdown();

    assert.equal(json.content[0].type, "heading");
    assert.ok(json.content.some(node => node.type === "bulletList"));
    assert.ok(json.content.some(node => node.type === "blockquote"));
    assert.ok(json.content.some(node => node.type === "codeBlock"));
    assert.match(serialized, /# Lesson heading/);
    assert.match(serialized, /\*\*bold\*\*/);
    assert.match(serialized, /\[a link\]\(https:\/\/example\.com\)/);
  } finally {
    harness.close();
  }
});

test("GitHub-Flavored Markdown tables parse into structured table nodes", () => {
  const source = [
    "| Order type | Purpose |",
    "| --- | --- |",
    "| Market | Immediate execution |",
    "| Limit | Price-controlled entry |",
  ].join("\n");

  const harness = createEditor(source);
  try {
    const json = harness.editor.getJSON();
    const table = json.content.find(node => node.type === "table");

    assert.ok(table, "Expected a structured table node");
    assert.equal(table.content.length, 3);
    assert.match(harness.editor.getMarkdown(), /^\| Order type\s+\| Purpose\s+\|$/m);
  } finally {
    harness.close();
  }
});

test("TradeThesis reference tokens remain visible as text in the basic adapter", () => {
  const source = [
    "The figure is linked below.",
    "",
    "asset://sample-figure-123",
    "",
    "[[regional-block:india]]",
    "",
    "[[lesson:00000000-0000-4000-8000-000000000001]]",
  ].join("\n");

  const harness = createEditor(source);
  let serialized;
  try {
    serialized = harness.editor.getMarkdown();

    assert.match(serialized, /asset:\/\/sample-figure-123/);
    assert.match(serialized, /\\\[\[regional-block:india\\\]\]/);
    assert.match(serialized, /\\\[\[lesson:00000000-0000-4000-8000-000000000001\\\]\]/);
  } finally {
    harness.close();
  }

  // Tiptap escapes bracket markers in Markdown output. They must remain text
  // and reappear in the document when that escaped Markdown is parsed again.
  const roundTrip = createEditor(serialized);
  try {
    const documentText = JSON.stringify(roundTrip.editor.getJSON());
    assert.ok(documentText.includes("[[regional-block:india]]"));
    assert.ok(documentText.includes("[[lesson:00000000-0000-4000-8000-000000000001]]"));
  } finally {
    roundTrip.close();
  }
});
