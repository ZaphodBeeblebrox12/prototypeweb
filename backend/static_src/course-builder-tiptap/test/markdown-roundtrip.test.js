import assert from "node:assert/strict";
import test from "node:test";
import { readFileSync } from "node:fs";
import { JSDOM } from "jsdom";
import { Editor } from "@tiptap/core";
import StarterKit from "@tiptap/starter-kit";
import { TableKit } from "@tiptap/extension-table";
import { Markdown } from "@tiptap/markdown";
import { TradeThesisExtensions, prepareTradeThesisMarkdown } from "../src/tradethesis-nodes.js";

function createEditor(content, contentType = "markdown") {
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

  const options = {
    element: dom.window.document.querySelector("#editor"),
    extensions: [
      StarterKit.configure({ heading: { levels: [1, 2, 3] } }),
      TableKit.configure({ table: { resizable: false } }),
      ...TradeThesisExtensions,
      Markdown.configure({ markedOptions: { gfm: true } }),
    ],
    content: {
      type: "doc",
      content: [{ type: "paragraph" }],
    },
  };

  const editor = new Editor(options);
  if (content && contentType === "markdown") {
    editor.commands.setContent(prepareTradeThesisMarkdown(content), { contentType: "markdown" });
  } else if (content && contentType === "json") {
    editor.commands.setContent(content);
  }
  return {
    editor,
    dom,
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

function collectNodes(root, type, output = []) {
  if (!root || typeof root !== "object") return output;
  if (root.type === type) output.push(root);
  for (const child of root.content || []) collectNodes(child, type, output);
  return output;
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
    "~~~text",
    "A code example",
    "~~~",
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

test("TradeThesis reference markers parse to typed nodes and serialize unchanged", () => {
  const lessonId = "00000000-0000-4000-8000-000000000001";
  const courseId = "00000000-0000-4000-8000-000000000002";
  const source = [
    "## Reference compatibility",
    "",
    "[[teaching-figure:figure_01]]",
    "",
    "[[image-group:group_01]]",
    "",
    "[[lesson:" + lessonId + "]]",
    "",
    "[[lesson-card:" + lessonId + "]]",
    "",
    "[[course-card:" + courseId + "]]",
    "",
    "[[course-card:coming-soon:" + courseId + "]]",
    "",
    "[[regional-block:india]]",
    "",
    "[[table-block:table_01]]",
    "",
    "[[lesson-tab:practice]]",
  ].join("\n");

  const harness = createEditor(source);
  try {
    const json = harness.editor.getJSON();
    const serialized = harness.editor.getMarkdown();

    assert.equal(collectNodes(json, "courseFigure")[0]?.attrs.figureId, "figure_01");
    assert.equal(collectNodes(json, "imageGroup")[0]?.attrs.groupId, "group_01");
    assert.equal(collectNodes(json, "lessonReference")[0]?.attrs.displayMode, "inline");
    assert.equal(collectNodes(json, "lessonReference")[1]?.attrs.displayMode, "card");
    assert.equal(collectNodes(json, "courseCard")[0]?.attrs.comingSoon, false);
    assert.equal(collectNodes(json, "courseCard")[1]?.attrs.comingSoon, true);
    assert.equal(collectNodes(json, "regionalBlock")[0]?.attrs.blockId, "india");
    assert.equal(collectNodes(json, "tableReference")[0]?.attrs.tableId, "table_01");
    assert.equal(collectNodes(json, "lessonTab")[0]?.attrs.tab, "practice");

    for (const marker of [
      "[[teaching-figure:figure_01]]",
      "[[image-group:group_01]]",
      "[[lesson:" + lessonId + "]]",
      "[[lesson-card:" + lessonId + "]]",
      "[[course-card:" + courseId + "]]",
      "[[course-card:coming-soon:" + courseId + "]]",
      "[[regional-block:india]]",
      "[[table-block:table_01]]",
      "[[lesson-tab:practice]]",
    ]) {
      assert.ok(serialized.includes(marker), "Expected exact marker in export: " + marker);
    }
  } finally {
    harness.close();
  }
});

test("unknown TradeThesis markers are retained as explicit legacy nodes", () => {
  const source = "Before.\n\n[[future-widget:opaque-value]]\n\nAfter.";
  const harness = createEditor(source);
  try {
    const legacy = collectNodes(harness.editor.getJSON(), "legacyMarkdown");
    assert.equal(legacy.length, 1);
    assert.equal(legacy[0].attrs.tokenKind, "future-widget");
    assert.equal(legacy[0].attrs.rawToken, "[[future-widget:opaque-value]]");
    assert.ok(harness.editor.getMarkdown().includes("[[future-widget:opaque-value]]"));
  } finally {
    harness.close();
  }
});

test("asset-backed Markdown images retain their stable asset ID", () => {
  const assetId = "00000000-0000-4000-8000-000000000003";
  const source = "![Market structure](asset://" + assetId + ")";
  const harness = createEditor(source);
  try {
    const image = collectNodes(harness.editor.getJSON(), "image")[0];
    assert.ok(image, "Expected a structured image node");
    assert.equal(image.attrs.assetId, assetId);
    assert.equal(image.attrs.src, "asset://" + assetId);
    assert.equal(harness.editor.getMarkdown(), source);
    assert.ok(harness.dom.window.document.querySelector('[data-tt-node="image"][data-tt-asset-id="' + assetId + '"]'));
    assert.equal(harness.dom.window.document.querySelector("img"), null);
  } finally {
    harness.close();
  }
});

test("JSON-only TradeThesis blocks survive as typed references and block lossy Markdown export", () => {
  const harness = createEditor("");
  try {
    harness.editor.commands.setContent({
      type: "doc",
      content: [{
        type: "paragraph",
        content: [
          { type: "practiceQuestion", attrs: { questionId: "question-01" } },
          { type: "videoBlock", attrs: { videoId: "video-01" } },
          { type: "notebookBlock", attrs: { notebookId: "notebook-01" } },
          { type: "reflectionBlock", attrs: { reflectionId: "reflection-01" } },
          { type: "callout", attrs: { tone: "note", title: "Context" } },
        ],
      }],
    });

    const json = harness.editor.getJSON();
    assert.equal(collectNodes(json, "practiceQuestion")[0]?.attrs.questionId, "question-01");
    assert.equal(collectNodes(json, "videoBlock")[0]?.attrs.videoId, "video-01");
    assert.equal(collectNodes(json, "notebookBlock")[0]?.attrs.notebookId, "notebook-01");
    assert.equal(collectNodes(json, "reflectionBlock")[0]?.attrs.reflectionId, "reflection-01");
    assert.equal(collectNodes(json, "callout")[0]?.attrs.title, "Context");
    assert.throws(
      () => harness.editor.getMarkdown(),
      /no lossless Markdown representation yet/,
    );
  } finally {
    harness.close();
  }
});


function collectText(root) {
  if (!root || typeof root !== "object") return "";
  if (root.type === "text") return root.text || "";
  return (root.content || []).map(collectText).join("");
}

test("Bollinger Bands course source parses and round-trips without losing lesson structure", () => {
  const courseRoot = new URL("../../../../course-source/understand-bollinger-bands/", import.meta.url);
  const manifest = JSON.parse(readFileSync(new URL("course-manifest.json", courseRoot), "utf8"));
  let lessonCount = 0;
  let imageCount = 0;
  let tableCount = 0;

  for (const module of manifest.modules) {
    const source = readFileSync(new URL(module.source, courseRoot), "utf8");
    lessonCount += (source.match(/^## Lesson \d+\.\d+/gm) || []).length;

    const first = createEditor(source);
    try {
      const originalJson = first.editor.getJSON();
      const markdown = first.editor.getMarkdown();
      const originalImages = collectNodes(originalJson, "image").length;
      const originalTables = collectNodes(originalJson, "table").length;
      const originalHeadings = collectNodes(originalJson, "heading").length;

      imageCount += originalImages;
      tableCount += originalTables;

      assert.ok(originalHeadings > 0, module.source + " should contain lesson headings");
      const second = createEditor(markdown);
      try {
        const roundTripped = second.editor.getJSON();
        assert.equal(
          collectNodes(roundTripped, "image").length,
          originalImages,
          module.source + " image references must survive round-trip",
        );
        assert.equal(
          collectNodes(roundTripped, "table").length,
          originalTables,
          module.source + " tables must survive round-trip",
        );
        assert.equal(
          collectNodes(roundTripped, "heading").length,
          originalHeadings,
          module.source + " heading structure must survive round-trip",
        );
        assert.equal(
          collectText(roundTripped),
          collectText(originalJson),
          module.source + " authored text must survive round-trip",
        );
      } finally {
        second.close();
      }
    } finally {
      first.close();
    }
  }

  assert.equal(lessonCount, 30, "The manifest declares 30 Bollinger Bands lessons");
  assert.equal(imageCount, 62, "The source package contains 62 image references");
  assert.ok(tableCount > 0, "The course source includes structured Markdown tables");
});

test("reference-looking text inside inline and fenced code stays code", () => {
  const marker = "[[regional-block:india]]";
  const tick = String.fromCharCode(96);
  const source = [
    "Inline " + tick + marker + tick + " should remain literal code.",
    "",
    "~~~text",
    marker,
    "~~~",
  ].join("\n");
  const harness = createEditor(source);
  try {
    const json = harness.editor.getJSON();
    assert.equal(collectNodes(json, "regionalBlock").length, 0);
    assert.equal(collectNodes(json, "codeBlock").length, 1);
    const serialized = harness.editor.getMarkdown();
    assert.ok(serialized.includes(tick + marker + tick));
    assert.ok(serialized.includes("~~~text\n" + marker + "\n~~~"));
  } finally {
    harness.close();
  }
});
