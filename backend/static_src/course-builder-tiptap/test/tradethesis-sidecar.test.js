import assert from "node:assert/strict";
import test from "node:test";

import {
  appendTradeThesisSidecarNodes,
  buildTradeThesisSidecarReferences,
  createTradeThesisSidecarNodes,
  resolveTradeThesisDocument,
} from "../src/tradethesis-sidecar.js";

const LESSON_ID = "00000000-0000-4000-8000-000000000011";
const COURSE_ID = "00000000-0000-4000-8000-000000000012";
const RELATED_LESSON_ID = "00000000-0000-4000-8000-000000000013";
const ASSET_ID = "00000000-0000-4000-8000-000000000014";
const VIDEO_ID = "00000000-0000-4000-8000-000000000015";

function sampleLesson() {
  return {
    id: LESSON_ID,
    content: [
      "![Market structure](asset://" + ASSET_ID + ")",
      "[[image-group:group-01]]",
      "[[teaching-figure:comparison-01]]",
      "[[lesson:" + RELATED_LESSON_ID + "]]",
      "[[course-card:" + COURSE_ID + "]]",
      "[[regional-block:india-note]]",
      "[[table-block:market-table]]",
    ].join("\n\n"),
    images: [{
      id: "builder-image-1",
      assetUuid: ASSET_ID,
      title: "Market structure",
      alt: "An annotated market structure chart",
      caption: "Illustrative chart.",
    }],
    imageGroups: [{
      id: "group-01",
      title: "Two-stage comparison",
      imageIds: ["builder-image-1"],
      description: "Compare the initial and later structure.",
    }],
    teachingFigures: [{
      id: "comparison-01",
      title: "Evidence and interpretation",
      cards: [{
        kicker: "Observation",
        title: "What is visible",
        body: "Price returned to a similar area.",
      }],
    }],
    tables: {
      "market-table": {
        title: "Order comparison",
        columnWidths: [40, 60],
        rows: [{
          section: "head",
          cells: [{ text: "Order", header: true }, { text: "Purpose", header: true }],
        }, {
          section: "body",
          cells: [{ text: "Limit" }, { text: "Control the entry price" }],
        }],
      },
    },
    regionalBlocks: [{
      id: "india-note",
      title: "India audience note",
      baseContent: "Base lesson copy.",
      variants: [{
        id: "india-variant",
        scope: "country",
        code: "IN",
        content: "India-specific copy.",
        hidden: false,
      }],
    }],
    regionalContent: {
      "country:IN": "Complete India lesson body.",
      "region:APAC": "Complete APAC lesson body.",
    },
    questions: [{
      id: "question-01",
      prompt: "Which reading is supported by the chart?",
      options: ["A visible reaction", "A guaranteed reversal"],
      correctIndex: 0,
      explanation: "The first option describes observable evidence.",
      imageId: "builder-image-1",
    }],
    notebook: {
      title: "Your Chart Reading Notes",
      prompts: [{ label: "Describe", text: "What evidence is visible?" }],
    },
    reflectionPrompt: "What would change your view?",
    reflectionModelReasoning: "Separate observations from interpretation.",
    reflectionChartNotes: "The later test is inconclusive.",
    protectedVideo: {
      id: VIDEO_ID,
      kind: "protected",
      status: "ready",
      source_file: "private/source.mp4",
      stream_directory: "private/streams/key/",
      manifest_url: "/private/manifest.m3u8",
    },
    callouts: [{
      id: "risk-note",
      tone: "warning",
      title: "Risk",
      body: "A reference is not a prediction.",
    }],
    relatedCourseIds: [COURSE_ID],
  };
}

test("sidecar adapter indexes all existing Academy lesson content by stable IDs", () => {
  const sidecar = buildTradeThesisSidecarReferences(sampleLesson());

  assert.equal(sidecar.format, "tradethesis.lesson-sidecar");
  assert.equal(sidecar.version, 1);
  assert.equal(sidecar.lessonId, LESSON_ID);

  assert.equal(sidecar.assets[ASSET_ID].alt, "An annotated market structure chart");
  assert.equal(sidecar.figures["group-01"].type, "image-group");
  assert.deepEqual(sidecar.figures["group-01"].imageIds, [ASSET_ID]);
  assert.equal(sidecar.figures["comparison-01"].type, "comparison-cards");
  assert.equal(sidecar.figures["comparison-01"].cards[0].title, "What is visible");

  assert.equal(sidecar.tables["market-table"].rows.length, 2);
  assert.equal(sidecar.regionalBlocks["india-note"].variants[0].code, "IN");
  assert.deepEqual(sidecar.regionalLessonContent, {
    "country:IN": "Complete India lesson body.",
    "region:APAC": "Complete APAC lesson body.",
  });
  assert.deepEqual(sidecar.references.regionalLessonVariantKeys, ["country:IN", "region:APAC"]);
  assert.equal(sidecar.questions["question-01"].prompt, "Which reading is supported by the chart?");
  assert.deepEqual(sidecar.questions["question-01"].options, [
    "A visible reaction",
    "A guaranteed reversal",
  ]);
  assert.equal(sidecar.questions["question-01"].imageId, ASSET_ID);

  assert.equal(sidecar.notebook.id, "notebook-" + LESSON_ID);
  assert.equal(sidecar.reflection.id, "reflection-" + LESSON_ID);
  assert.equal(sidecar.protectedVideo.id, VIDEO_ID);
  assert.equal(sidecar.protectedVideo.status, "ready");
  assert.equal(sidecar.callouts["risk-note"].title, "Risk");

  assert.deepEqual(sidecar.references.lessonIds, [RELATED_LESSON_ID]);
  assert.deepEqual(sidecar.references.courseIds, [COURSE_ID]);
  assert.deepEqual(sidecar.references.regionalBlockIds, ["india-note"]);
  assert.deepEqual(sidecar.references.tableIds, ["market-table"]);
});

test("saved image sidecars hydrate the private preview URL without changing the asset ID", () => {
  const previewUrl = "/staff/course-builder/assets/draft/" + ASSET_ID + "/";
  const sidecar = buildTradeThesisSidecarReferences({
    id: LESSON_ID,
    content: "![Market structure](asset://" + ASSET_ID + ")",
    images: [{
      id: "builder-image",
      assetUuid: ASSET_ID,
      alt: "Market structure",
      data: previewUrl,
    }],
  });
  const resolved = resolveTradeThesisDocument({
    type: "doc",
    content: [{
      type: "image",
      attrs: { src: "asset://" + ASSET_ID, assetId: ASSET_ID },
    }],
  }, sidecar);

  assert.equal(sidecar.assets[ASSET_ID].previewUrl, previewUrl);
  assert.equal(resolved.document.content[0].attrs.assetId, ASSET_ID);
  assert.equal(resolved.document.content[0].attrs.previewUrl, previewUrl);
  assert.deepEqual(resolved.diagnostics, []);
});

test("published Lesson.content_json sidecars preserve figures, tables, regional content and learner tools", () => {
  const sidecar = buildTradeThesisSidecarReferences({
    id: LESSON_ID,
    content_markdown: "![Structure](asset://" + ASSET_ID + ")",
    contentJson: {},
    regionalContent: {},
    content_json: {
      asset_ids: [ASSET_ID],
      figures: {
        [ASSET_ID]: {
          type: "image",
          title: "Published figure",
          alt: "Published alt text",
          caption: "Published caption.",
        },
        "published-group": {
          type: "image-group",
          title: "Published group",
          image_ids: [ASSET_ID],
        },
        "published-comparison": {
          type: "comparison-cards",
          title: "Published comparison",
          cards: [{ title: "Observe", body: "Describe what is visible." }],
        },
      },
      tables: {
        "published-table": {
          title: "Published table",
          rows: [{ section: "body", cells: [{ text: "Evidence" }] }],
        },
      },
      regional_blocks: {
        "published-region": {
          title: "Published inline region",
          base_content: "Base copy.",
          variants: [{ scope: "country", code: "IN", content: "India copy." }],
        },
      },
      regional_lesson_content: {
        "country:IN": "Complete published India lesson body.",
      },
      questions: [{
        id: "published-question",
        prompt: "Which choice describes the evidence?",
        options: ["Evidence", "Prediction"],
        image_asset_id: ASSET_ID,
        correctIndex: 0,
        explanation: "Private authoring explanation.",
      }],
      notebook: {
        title: "Published notebook",
        prompts: [{ label: "Observe", text: "Describe the chart." }],
      },
      reflection: {
        prompt: "What would change your view?",
        model_reasoning: "Private instructor context.",
        chart_notes: "Visible chart notes.",
      },
      related_course_ids: [COURSE_ID],
    },
  });

  assert.equal(sidecar.assets[ASSET_ID].alt, "Published alt text");
  assert.equal(sidecar.assets[ASSET_ID].caption, "Published caption.");
  assert.equal(sidecar.figures["published-group"].type, "image-group");
  assert.equal(sidecar.figures["published-comparison"].type, "comparison-cards");
  assert.equal(sidecar.tables["published-table"].rows[0].cells[0].text, "Evidence");
  assert.equal(sidecar.regionalBlocks["published-region"].variants[0].code, "IN");
  assert.equal(sidecar.regionalLessonContent["country:IN"], "Complete published India lesson body.");
  assert.equal(sidecar.questions["published-question"].imageId, ASSET_ID);
  assert.equal(Object.hasOwn(sidecar.questions["published-question"], "correctIndex"), false);
  assert.equal(Object.hasOwn(sidecar.questions["published-question"], "explanation"), false);
  assert.equal(sidecar.notebook.title, "Published notebook");
  assert.equal(sidecar.reflection.prompt, "What would change your view?");
  assert.equal(sidecar.reflection.modelReasoning, "Private instructor context.");
  assert.deepEqual(sidecar.references.courseIds, [COURSE_ID]);
});

test("legacy Markdown asset tokens remain stable without an asset_ids sidecar list", () => {
  const sidecar = buildTradeThesisSidecarReferences({
    id: LESSON_ID,
    content_markdown: "![Market structure](asset://" + ASSET_ID + ")",
    content_json: {},
  });
  assert.deepEqual(sidecar.assets[ASSET_ID], {
    id: ASSET_ID,
    title: "",
    alt: "",
    caption: "",
  });

  const resolved = resolveTradeThesisDocument({
    type: "doc",
    content: [{
      type: "paragraph",
      content: [{
        type: "image",
        attrs: { src: "asset://" + ASSET_ID, alt: "", title: null },
      }],
    }],
  }, sidecar);
  assert.deepEqual(resolved.diagnostics, []);
});

test("sidecar references never copy instructor answers or private video storage details", () => {
  const sidecar = buildTradeThesisSidecarReferences(sampleLesson());
  const question = sidecar.questions["question-01"];

  assert.equal(Object.hasOwn(question, "correctIndex"), false);
  assert.equal(Object.hasOwn(question, "explanation"), false);
  assert.equal(Object.hasOwn(sidecar.protectedVideo, "source_file"), false);
  assert.equal(Object.hasOwn(sidecar.protectedVideo, "stream_directory"), false);
  assert.equal(Object.hasOwn(sidecar.protectedVideo, "manifest_url"), false);
});

test("document resolver enriches assets and distinguishes comparison figures", () => {
  const sidecar = buildTradeThesisSidecarReferences(sampleLesson());
  const envelope = {
    format: "tradethesis.lesson-document",
    version: 1,
    document: {
      type: "doc",
      content: [{
        type: "paragraph",
        content: [
          { type: "image", attrs: { src: "asset://" + ASSET_ID, alt: "", title: null } },
          { type: "courseFigure", attrs: { figureId: "comparison-01", rawToken: "[[teaching-figure:comparison-01]]" } },
          { type: "imageGroup", attrs: { groupId: "group-01", rawToken: "[[image-group:group-01]]" } },
          { type: "lessonReference", attrs: { lessonId: RELATED_LESSON_ID, displayMode: "inline" } },
          { type: "courseCard", attrs: { courseId: COURSE_ID, comingSoon: false } },
          { type: "regionalBlock", attrs: { blockId: "india-note" } },
          { type: "regionalLessonVariant", attrs: { variantKey: "country:IN" } },
          { type: "tableReference", attrs: { tableId: "market-table" } },
          { type: "lessonTab", attrs: { tab: "practice" } },
        ],
      }],
    },
  };

  const resolved = resolveTradeThesisDocument(envelope, sidecar);
  const inline = resolved.document.document.content[0].content;

  assert.equal(resolved.document.format, "tradethesis.lesson-document");
  assert.equal(inline[0].attrs.assetId, ASSET_ID);
  assert.equal(inline[0].attrs.alt, "An annotated market structure chart");
  assert.equal(inline[0].attrs.title, "Market structure");
  assert.equal(inline[1].type, "comparisonFigure");
  assert.deepEqual(resolved.externalReferences.lessonIds, [RELATED_LESSON_ID]);
  assert.deepEqual(resolved.externalReferences.courseIds, [COURSE_ID]);
  assert.deepEqual(resolved.diagnostics, []);
});

test("image figures resolve and callouts remain blocked until learner-renderer parity exists", () => {
  const sidecar = buildTradeThesisSidecarReferences(sampleLesson());
  const resolved = resolveTradeThesisDocument({
    type: "doc",
    content: [{
      type: "paragraph",
      content: [{
        type: "courseFigure",
        attrs: { figureId: ASSET_ID, rawToken: "[[teaching-figure:" + ASSET_ID + "]]" },
      }],
    }, {
      type: "callout",
      attrs: { calloutId: "risk-note", tone: "warning", title: "Risk" },
    }],
  }, sidecar);

  assert.equal(resolved.document.content[0].content[0].type, "courseFigure");
  assert.deepEqual(resolved.diagnostics, [{
    nodeType: "callout",
    id: "risk-note",
    reason: "callout-renderer-not-supported",
  }]);
});

test("sidecar-backed blocks become typed ID-only document nodes and append idempotently", () => {
  const sidecar = buildTradeThesisSidecarReferences(sampleLesson());
  const nodes = createTradeThesisSidecarNodes(sidecar);
  const types = nodes.map(node => node.type);

  assert.deepEqual(types, [
    "practiceQuestion",
    "videoBlock",
    "notebookBlock",
    "reflectionBlock",
    "regionalLessonVariant",
    "regionalLessonVariant",
    "callout",
  ]);
  assert.equal(nodes[0].attrs.questionId, "question-01");
  assert.equal(nodes[1].attrs.videoId, VIDEO_ID);
  assert.equal(nodes[2].attrs.notebookId, "notebook-" + LESSON_ID);
  assert.equal(nodes[3].attrs.reflectionId, "reflection-" + LESSON_ID);
  assert.equal(nodes[4].attrs.variantKey, "country:IN");
  assert.equal(nodes[5].attrs.variantKey, "region:APAC");
  assert.equal(nodes[6].attrs.calloutId, "risk-note");

  const start = {
    type: "doc",
    content: [{ type: "paragraph", content: [{ type: "text", text: "Lesson body." }] }],
  };
  const once = appendTradeThesisSidecarNodes(start, sidecar);
  const twice = appendTradeThesisSidecarNodes(once, sidecar);

  assert.equal(once.content.length, 8);
  assert.deepEqual(twice, once);
  assert.deepEqual(
    once.content.slice(1).map(node => node.type),
    types,
  );
  for (const node of once.content.slice(1)) {
    assert.deepEqual(Object.keys(node.attrs).length, 1);
  }
});

test("missing sidecar records are reported without dropping their document nodes", () => {
  const document = {
    type: "doc",
    content: [{
      type: "paragraph",
      content: [{ type: "regionalBlock", attrs: { blockId: "missing-region" } }],
    }],
  };
  const resolved = resolveTradeThesisDocument(document, {
    format: "tradethesis.lesson-sidecar",
    version: 1,
    regionalBlocks: {},
  });

  assert.equal(resolved.document.content[0].content[0].type, "regionalBlock");
  assert.deepEqual(resolved.diagnostics, [{
    nodeType: "regionalBlock",
    id: "missing-region",
    reason: "regional-block-not-in-sidecar",
  }]);
});
