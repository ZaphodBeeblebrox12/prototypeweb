/**
 * Lossless bridge between the current Academy lesson sidecars and Tiptap nodes.
 *
 * Lesson prose is represented by the versioned Tiptap document. Existing figures,
 * tables, questions, regional variants, notebook/reflection data and protected-video
 * records remain in their existing sidecar stores. Nodes carry stable references only.
 * This module does not fetch media, resolve private URLs, or copy instructor answers
 * into the learner document.
 */

export const TRADETHESIS_SIDECAR_FORMAT = "tradethesis.lesson-sidecar";
export const TRADETHESIS_SIDECAR_VERSION = 1;

const SAFE_ID = /^[A-Za-z0-9_-]{1,120}$/;
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const COURSE_REF = /\[\[course-card:(?:(coming-soon):)?([0-9a-f-]{36})\]\]/gi;
const LESSON_REF = /\[\[(lesson|lesson-card):([0-9a-f-]{36})\]\]/gi;
const ASSET_REF = /asset:\/\/([0-9a-f-]{36})/gi;
const FIGURE_REF = /\[\[teaching-figure:([A-Za-z0-9_-]{1,120})\]\]/g;
const IMAGE_GROUP_REF = /\[\[image-group:([A-Za-z0-9_-]{1,120})\]\]/g;
const REGIONAL_REF = /\[\[regional-block:([A-Za-z0-9_-]{1,120})\]\]/g;
const TABLE_REF = /\[\[table-block:([A-Za-z0-9_-]{1,120})\]\]/g;

function asObject(value) {
  return value && typeof value === "object" && !Array.isArray(value) ? value : {};
}

function asArray(value) {
  return Array.isArray(value) ? value : [];
}

function cloneJSON(value) {
  if (value === undefined) return undefined;
  return JSON.parse(JSON.stringify(value));
}

function safeId(value) {
  const candidate = String(value ?? "").trim();
  return SAFE_ID.test(candidate) || UUID.test(candidate) ? candidate : "";
}

function collectMatches(source, pattern, pick) {
  const matches = [];
  const regex = new RegExp(pattern.source, pattern.flags);
  let match;
  while ((match = regex.exec(source)) !== null) {
    const value = pick(match);
    if (value && !matches.includes(value)) matches.push(value);
    if (match[0] === "") regex.lastIndex += 1;
  }
  return matches;
}

function mapEntries(value) {
  return Object.entries(asObject(value));
}

function firstObject(...values) {
  for (const value of values) {
    if (value && typeof value === "object" && !Array.isArray(value)) return value;
  }
  return {};
}

/**
 * Build a detached, safe reference index from the builder lesson shape or the
 * published Lesson.content_json shape. The index intentionally omits video paths,
 * stream URLs, encryption details, and question answer keys/explanations.
 */
export function buildTradeThesisSidecarReferences(lessonValue = {}) {
  const lesson = asObject(lessonValue);
  const contentJson = firstObject(lesson.contentJson, lesson.content_json);
  const lessonId = safeId(lesson.id || lesson.lessonId || lesson.lesson_id);
  const markdown = String(
    lesson.content ?? lesson.content_markdown ?? lesson.markdown ?? "",
  );

  const assets = {};
  const builderImageIds = new Map();

  for (const image of asArray(lesson.images)) {
    const item = asObject(image);
    const id = safeId(item.assetUuid || item.assetId || item.asset_id || item.id);
    if (!id) continue;
    assets[id] = {
      id,
      title: String(item.title || "").slice(0, 240),
      alt: String(item.alt || item.altText || item.alt_text || "").slice(0, 500),
      caption: String(item.caption || "").slice(0, 500),
    };
    for (const key of [item.id, item.assetUuid, item.assetId, item.asset_id]) {
      const builderId = safeId(key);
      if (builderId) builderImageIds.set(builderId, id);
    }
  }

  for (const rawId of asArray(contentJson.asset_ids)) {
    const id = safeId(rawId);
    if (id && !assets[id]) assets[id] = { id, title: "", alt: "", caption: "" };
  }

  const resolveAssetId = rawId => {
    const candidate = safeId(rawId);
    if (!candidate) return "";
    return builderImageIds.get(candidate) || candidate;
  };

  const figures = {};
  for (const [rawId, rawFigure] of mapEntries(contentJson.figures)) {
    const id = safeId(rawId);
    const figure = asObject(rawFigure);
    if (!id) continue;
    const type = figure.type === "image-group"
      ? "image-group"
      : figure.type === "comparison-cards"
        ? "comparison-cards"
        : "image";
    const imageIds = asArray(figure.image_ids || figure.imageIds)
      .map(resolveAssetId)
      .filter(Boolean);
    figures[id] = {
      id,
      type,
      title: String(figure.title || "").slice(0, 240),
      alt: String(figure.alt || "").slice(0, 500),
      caption: String(figure.caption || "").slice(0, 500),
      imageIds,
      description: String(figure.description || figure.note || "").slice(0, 1500),
      cards: asArray(figure.cards).slice(0, 4).map(cardValue => {
        const card = asObject(cardValue);
        return {
          kicker: String(card.kicker || "").slice(0, 100),
          title: String(card.title || "").slice(0, 240),
          body: String(card.body || "").slice(0, 1000),
        };
      }),
      note: String(figure.note || "").slice(0, 1500),
    };
  }

  for (const groupValue of asArray(lesson.imageGroups)) {
    const group = asObject(groupValue);
    const id = safeId(group.id);
    if (!id) continue;
    figures[id] = {
      id,
      type: "image-group",
      title: String(group.title || "").slice(0, 240),
      imageIds: asArray(group.imageIds || group.image_ids).map(resolveAssetId).filter(Boolean).slice(0, 4),
      description: String(group.description || group.note || "").slice(0, 1500),
      cards: [],
      note: String(group.note || group.description || "").slice(0, 1500),
    };
  }

  for (const figureValue of asArray(lesson.teachingFigures)) {
    const figure = asObject(figureValue);
    const id = safeId(figure.id);
    if (!id) continue;
    figures[id] = {
      id,
      type: "comparison-cards",
      title: String(figure.title || "Comparison").slice(0, 240),
      imageIds: [],
      description: "",
      cards: asArray(figure.cards).slice(0, 4).map(cardValue => {
        const card = asObject(cardValue);
        return {
          kicker: String(card.kicker || "").slice(0, 100),
          title: String(card.title || "").slice(0, 240),
          body: String(card.body || "").slice(0, 1000),
        };
      }),
      note: String(figure.note || "").slice(0, 1500),
    };
  }

  // Preserve figure metadata for assets even when the builder only supplied a
  // content_json figures map and no separate images array.
  for (const [id, figure] of Object.entries(figures)) {
    if (figure.type === "image" && !assets[id]) {
      assets[id] = {
        id,
        title: figure.title,
        alt: figure.alt || "",
        caption: figure.caption || "",
      };
    }
  }

  const lessonTables = asObject(lesson.tables);
  const tablesSource = Object.keys(lessonTables).length ? lessonTables : asObject(contentJson.tables);
  const tables = {};
  for (const [rawId, rawTable] of mapEntries(tablesSource)) {
    const id = safeId(rawId);
    const table = asObject(rawTable);
    if (!id) continue;
    tables[id] = {
      id,
      title: String(table.title || "Lesson table").slice(0, 240),
      columnWidths: asArray(table.columnWidths).slice(0, 12).map(Number),
      rows: asArray(table.rows).slice(0, 60).map(rowValue => {
        const row = asObject(rowValue);
        return {
          section: row.section === "head" ? "head" : "body",
          cells: asArray(row.cells).slice(0, 12).map(cellValue => {
            const cell = asObject(cellValue);
            return {
              text: String(cell.text || "").slice(0, 2000),
              colspan: Math.max(1, Math.min(12, Number(cell.colspan) || 1)),
              rowspan: Math.max(1, Math.min(12, Number(cell.rowspan) || 1)),
              header: Boolean(cell.header),
            };
          }),
        };
      }),
    };
  }

  const builderRegionalBlocks = asArray(lesson.regionalBlocks);
  const regionalSource = builderRegionalBlocks.length
    ? builderRegionalBlocks
    : contentJson.regional_blocks;
  const regionalBlocks = {};
  const regionalEntries = Array.isArray(regionalSource)
    ? regionalSource.map(block => [asObject(block).id, block])
    : mapEntries(regionalSource);
  for (const [rawId, rawBlock] of regionalEntries) {
    const id = safeId(rawId || asObject(rawBlock).id);
    const block = asObject(rawBlock);
    if (!id) continue;
    regionalBlocks[id] = {
      id,
      title: String(block.title || "Regional content").slice(0, 240),
      baseContent: String(block.baseContent ?? block.base_content ?? ""),
      variants: asArray(block.variants).slice(0, 30).map(variantValue => {
        const variant = asObject(variantValue);
        return {
          id: safeId(variant.id),
          scope: variant.scope === "region" ? "region" : "country",
          code: String(variant.code || variant.country || variant.region || "").toUpperCase().slice(0, 12),
          content: String(variant.content || ""),
          hidden: Boolean(variant.hidden),
        };
      }),
    };
  }

  // Whole-lesson regional alternatives are stored separately from inline blocks.
  // Keep each complete Markdown body outside the learner document and reference it
  // by its validated country/region key.
  const regionalLessonSource = lesson.regionalContent
    ?? contentJson.regional_lesson_content
    ?? contentJson.regionalLessonContent;
  const regionalLessonContent = {};
  for (const [rawKey, rawContent] of mapEntries(regionalLessonSource)) {
    if (typeof rawContent !== "string") continue;
    const match = /^(country|region):([A-Za-z0-9-]{2,12})$/i.exec(rawKey.trim());
    if (!match) continue;
    const scope = match[1].toLowerCase();
    const code = match[2].toUpperCase();
    if (scope === "country" && !/^[A-Z]{2}$/.test(code)) continue;
    if (scope === "region" && !["APAC", "EU", "NA", "LATAM", "MENA", "SSA"].includes(code)) continue;
    regionalLessonContent[scope + ":" + code] = rawContent;
  }

  const questionSource = Array.isArray(lesson.questions) && lesson.questions.length
    ? lesson.questions
    : contentJson.questions;
  const questions = {};
  asArray(questionSource).forEach((questionValue, index) => {
    const question = asObject(questionValue);
    const id = safeId(question.id) || (
      lessonId ? "question-" + lessonId + "-" + (index + 1) : ""
    );
    if (!id) return;
    const imageId = resolveAssetId(
      question.imageId || question.image_asset_id || question.imageAssetId,
    );
    questions[id] = {
      id,
      prompt: String(question.prompt || "").slice(0, 2000),
      options: asArray(question.options).slice(0, 12).map(value => String(value).slice(0, 500)),
      imageId,
    };
  });

  const builderNotebook = asObject(lesson.notebook);
  const notebookValue = Object.keys(builderNotebook).length
    ? builderNotebook
    : asObject(contentJson.notebook);
  const notebookPrompts = asArray(notebookValue.prompts).slice(0, 30).map(promptValue => {
    const prompt = asObject(promptValue);
    return {
      label: String(prompt.label || "").slice(0, 100),
      text: String(prompt.text || "").slice(0, 1000),
    };
  });
  const notebook = (
    lessonId && (Object.keys(notebookValue).length || notebookPrompts.length)
  ) ? {
    id: "notebook-" + lessonId,
    title: String(notebookValue.title || "Your Trading Notebook").slice(0, 160),
    prompts: notebookPrompts,
  } : null;

  const builderReflection = asObject(lesson.reflection);
  const reflectionValue = Object.keys(builderReflection).length
    ? builderReflection
    : asObject(contentJson.reflection);
  const reflectionPrompt = String(
    lesson.reflectionPrompt ?? lesson.reflection_prompt ?? reflectionValue.prompt ?? "",
  ).slice(0, 1000);
  const reflectionReasoning = String(
    lesson.reflectionModelReasoning ?? lesson.reflection_model_reasoning
      ?? reflectionValue.model_reasoning ?? "",
  ).slice(0, 3000);
  const reflectionChartNotes = String(
    lesson.reflectionChartNotes ?? lesson.reflection_chart_notes
      ?? reflectionValue.chart_notes ?? "",
  ).slice(0, 3000);
  const reflection = (
    lessonId && (reflectionPrompt || reflectionReasoning || reflectionChartNotes)
  ) ? {
    id: "reflection-" + lessonId,
    prompt: reflectionPrompt,
    modelReasoning: reflectionReasoning,
    chartNotes: reflectionChartNotes,
  } : null;

  const rawVideo = firstObject(lesson.protectedVideo, lesson.protected_video);
  const videoId = safeId(rawVideo.id || rawVideo.videoId || rawVideo.video_id);
  const protectedVideo = videoId ? {
    id: videoId,
    kind: rawVideo.kind === "staged" ? "staged" : "protected",
    status: String(rawVideo.status || "unknown").slice(0, 32),
  } : null;

  const callouts = {};
  const builderCallouts = asArray(lesson.callouts);
  const calloutSource = builderCallouts.length ? builderCallouts : contentJson.callouts;
  asArray(calloutSource).forEach((calloutValue, index) => {
    const callout = asObject(calloutValue);
    const id = safeId(callout.id) || (
      lessonId ? "callout-" + lessonId + "-" + (index + 1) : ""
    );
    if (!id) return;
    callouts[id] = {
      id,
      tone: String(callout.tone || "note").slice(0, 32),
      title: String(callout.title || "").slice(0, 240),
      body: String(callout.body || callout.content || "").slice(0, 3000),
    };
  });

  const referencedLessonIds = collectMatches(
    markdown,
    LESSON_REF,
    match => UUID.test(match[2]) ? match[2].toLowerCase() : "",
  );
  const referencedCourseIds = collectMatches(
    markdown,
    COURSE_REF,
    match => UUID.test(match[2]) ? match[2].toLowerCase() : "",
  );
  const referencedAssetIds = collectMatches(
    markdown,
    ASSET_REF,
    match => UUID.test(match[1]) ? match[1].toLowerCase() : "",
  );
  const referencedFigureIds = collectMatches(markdown, FIGURE_REF, match => safeId(match[1]));
  const referencedImageGroupIds = collectMatches(markdown, IMAGE_GROUP_REF, match => safeId(match[1]));
  const referencedRegionalBlockIds = collectMatches(markdown, REGIONAL_REF, match => safeId(match[1]));
  const referencedTableIds = collectMatches(markdown, TABLE_REF, match => safeId(match[1]));

  const relatedCourseIds = asArray(lesson.relatedCourseIds || contentJson.related_course_ids)
    .map(value => String(value || "").toLowerCase())
    .filter(value => UUID.test(value));

  return {
    format: TRADETHESIS_SIDECAR_FORMAT,
    version: TRADETHESIS_SIDECAR_VERSION,
    lessonId,
    assets,
    figures,
    tables,
    regionalBlocks,
    regionalLessonContent,
    questions,
    notebook,
    reflection,
    protectedVideo,
    callouts,
    references: {
      assetIds: [...new Set([...Object.keys(assets), ...referencedAssetIds])],
      figureIds: referencedFigureIds,
      imageGroupIds: referencedImageGroupIds,
      regionalBlockIds: referencedRegionalBlockIds,
      regionalLessonVariantKeys: Object.keys(regionalLessonContent).sort(),
      tableIds: referencedTableIds,
      lessonIds: referencedLessonIds,
      courseIds: [...new Set([...relatedCourseIds, ...referencedCourseIds])],
    },
  };
}

function getDocumentRoot(value) {
  const envelope = asObject(value);
  if (envelope.document && asObject(envelope.document).type === "doc") {
    return { root: envelope.document, envelope: true };
  }
  return { root: envelope, envelope: false };
}

/**
 * Resolve editor node types and presentation hints against the sidecar index.
 * It never fetches records or replaces IDs with mutable titles/slugs.
 */
export function resolveTradeThesisDocument(documentValue, sidecarValue) {
  const sidecar = asObject(sidecarValue);
  const { root: sourceRoot, envelope } = getDocumentRoot(documentValue);
  const root = cloneJSON(sourceRoot);
  const diagnostics = [];
  const externalReferences = { lessonIds: [], courseIds: [] };

  function visit(node) {
    if (!node || typeof node !== "object") return;
    const attrs = asObject(node.attrs);
    const idFor = {
      image: attrs.assetId || String(attrs.src || "").replace(/^asset:\/\//i, ""),
      courseFigure: attrs.figureId,
      comparisonFigure: attrs.figureId,
      imageGroup: attrs.groupId,
      courseCard: attrs.courseId,
      lessonReference: attrs.lessonId,
      regionalBlock: attrs.blockId,
      regionalLessonVariant: attrs.variantKey,
      tableReference: attrs.tableId,
      practiceQuestion: attrs.questionId,
      videoBlock: attrs.videoId,
      notebookBlock: attrs.notebookId,
      reflectionBlock: attrs.reflectionId,
      callout: attrs.calloutId || attrs.id,
    }[node.type];

    if (node.type === "image") {
      const asset = asObject(asObject(sidecar.assets)[safeId(idFor)]);
      if (asset.id) {
        if (!attrs.alt) attrs.alt = asset.alt || "";
        if (!attrs.title) attrs.title = asset.title || "";
        if (!attrs.assetId) attrs.assetId = asset.id;
      } else if (idFor) {
        diagnostics.push({ nodeType: "image", id: String(idFor), reason: "asset-reference-not-in-sidecar" });
      }
    } else if (node.type === "courseFigure" || node.type === "comparisonFigure") {
      const figure = asObject(asObject(sidecar.figures)[safeId(idFor)]);
      if (figure.id && figure.type === "comparison-cards") {
        node.type = "comparisonFigure";
      } else {
        diagnostics.push({
          nodeType: node.type,
          id: String(idFor || ""),
          reason: figure.id ? "figure-reference-type-mismatch" : "figure-reference-not-in-sidecar",
        });
      }
    } else if (node.type === "imageGroup") {
      const figure = asObject(asObject(sidecar.figures)[safeId(idFor)]);
      if (!figure.id || figure.type !== "image-group") {
        diagnostics.push({ nodeType: "imageGroup", id: String(idFor || ""), reason: "image-group-reference-not-in-sidecar" });
      }
    } else if (node.type === "courseCard") {
      if (UUID.test(String(idFor || ""))) {
        externalReferences.courseIds.push(String(idFor).toLowerCase());
      } else {
        diagnostics.push({ nodeType: "courseCard", id: String(idFor || ""), reason: "invalid-course-reference-id" });
      }
    } else if (node.type === "lessonReference") {
      if (UUID.test(String(idFor || ""))) {
        externalReferences.lessonIds.push(String(idFor).toLowerCase());
      } else {
        diagnostics.push({ nodeType: "lessonReference", id: String(idFor || ""), reason: "invalid-lesson-reference-id" });
      }
    } else if (node.type === "regionalBlock" && !asObject(sidecar.regionalBlocks)[safeId(idFor)]?.id) {
      diagnostics.push({ nodeType: "regionalBlock", id: String(idFor || ""), reason: "regional-block-not-in-sidecar" });
    } else if (node.type === "regionalLessonVariant" && !Object.hasOwn(asObject(sidecar.regionalLessonContent), String(idFor || ""))) {
      diagnostics.push({ nodeType: "regionalLessonVariant", id: String(idFor || ""), reason: "regional-lesson-variant-not-in-sidecar" });
    } else if (node.type === "tableReference" && !asObject(sidecar.tables)[safeId(idFor)]?.id) {
      diagnostics.push({ nodeType: "tableReference", id: String(idFor || ""), reason: "table-not-in-sidecar" });
    } else if (node.type === "practiceQuestion" && !asObject(sidecar.questions)[safeId(idFor)]?.id) {
      diagnostics.push({ nodeType: "practiceQuestion", id: String(idFor || ""), reason: "question-not-in-sidecar" });
    } else if (node.type === "videoBlock" && asObject(sidecar.protectedVideo).id !== safeId(idFor)) {
      diagnostics.push({ nodeType: "videoBlock", id: String(idFor || ""), reason: "protected-video-not-in-sidecar" });
    } else if (node.type === "notebookBlock" && asObject(sidecar.notebook).id !== String(idFor || "")) {
      diagnostics.push({ nodeType: "notebookBlock", id: String(idFor || ""), reason: "notebook-not-in-sidecar" });
    } else if (node.type === "reflectionBlock" && asObject(sidecar.reflection).id !== String(idFor || "")) {
      diagnostics.push({ nodeType: "reflectionBlock", id: String(idFor || ""), reason: "reflection-not-in-sidecar" });
    } else if (node.type === "callout" && !asObject(sidecar.callouts)[safeId(idFor)]?.id) {
      diagnostics.push({ nodeType: "callout", id: String(idFor || ""), reason: "callout-not-in-sidecar" });
    } else if (node.type === "legacyMarkdown") {
      diagnostics.push({ nodeType: "legacyMarkdown", id: String(attrs.rawToken || ""), reason: "preserved-opaque-marker" });
    }

    for (const child of asArray(node.content)) visit(child);
  }

  visit(root);
  externalReferences.lessonIds = [...new Set(externalReferences.lessonIds)];
  externalReferences.courseIds = [...new Set(externalReferences.courseIds)];

  if (envelope) {
    return {
      document: { ...cloneJSON(asObject(documentValue)), document: root },
      diagnostics,
      externalReferences,
    };
  }
  return { document: root, diagnostics, externalReferences };
}

/**
 * Return top-level typed nodes for the sidecar-backed lesson tools. These nodes
 * contain only stable IDs; authoring/learner data remains in the sidecar.
 */
export function createTradeThesisSidecarNodes(sidecarValue) {
  const sidecar = asObject(sidecarValue);
  const nodes = [];

  for (const id of Object.keys(asObject(sidecar.questions)).sort()) {
    nodes.push({ type: "practiceQuestion", attrs: { questionId: id } });
  }
  if (asObject(sidecar.protectedVideo).id) {
    nodes.push({ type: "videoBlock", attrs: { videoId: sidecar.protectedVideo.id } });
  }
  if (asObject(sidecar.notebook).id) {
    nodes.push({ type: "notebookBlock", attrs: { notebookId: sidecar.notebook.id } });
  }
  if (asObject(sidecar.reflection).id) {
    nodes.push({ type: "reflectionBlock", attrs: { reflectionId: sidecar.reflection.id } });
  }
  for (const variantKey of Object.keys(asObject(sidecar.regionalLessonContent)).sort()) {
    nodes.push({ type: "regionalLessonVariant", attrs: { variantKey } });
  }
  for (const id of Object.keys(asObject(sidecar.callouts)).sort()) {
    nodes.push({ type: "callout", attrs: { calloutId: id } });
  }
  return nodes;
}

/**
 * Append missing sidecar references to a document without embedding their data.
 * A second call is idempotent, so editor save/reopen cycles do not duplicate blocks.
 */
export function appendTradeThesisSidecarNodes(documentValue, sidecarValue) {
  const { root: sourceRoot, envelope } = getDocumentRoot(documentValue);
  const root = cloneJSON(sourceRoot);
  if (root.type !== "doc") throw new Error("A TradeThesis document root must be a doc node.");
  if (!Array.isArray(root.content)) root.content = [];

  const existing = new Set();
  const collect = node => {
    if (!node || typeof node !== "object") return;
    const attrs = asObject(node.attrs);
    for (const key of ["questionId", "videoId", "notebookId", "reflectionId", "variantKey", "calloutId"]) {
      if (attrs[key]) existing.add(node.type + ":" + attrs[key]);
    }
    for (const child of asArray(node.content)) collect(child);
  };
  collect(root);

  for (const node of createTradeThesisSidecarNodes(sidecarValue)) {
    const attrs = asObject(node.attrs);
    const refId = attrs.questionId || attrs.videoId || attrs.notebookId
      || attrs.reflectionId || attrs.variantKey || attrs.calloutId;
    const key = node.type + ":" + refId;
    if (!existing.has(key)) {
      root.content.push(cloneJSON(node));
      existing.add(key);
    }
  }

  if (envelope) {
    return { ...cloneJSON(asObject(documentValue)), document: root };
  }
  return root;
}
