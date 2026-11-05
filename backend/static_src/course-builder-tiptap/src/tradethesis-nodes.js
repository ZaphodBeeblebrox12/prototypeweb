import { Node, mergeAttributes } from "@tiptap/core";

const UUID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
const SAFE_REFERENCE_PATTERN = /^[A-Za-z0-9_-]{1,120}$/;
const ASSET_SOURCE_PATTERN = /^asset:\/\/([0-9a-f-]{36})$/i;

function kebabCase(value) {
  return value.replace(/[A-Z]/g, letter => "-" + letter.toLowerCase());
}

function tokenFor(name, value) {
  return "[[" + name + ":" + value + "]]";
}

function createReferenceNode({ name, label, attributes, identifier, serialize }) {
  return Node.create({
    name,
    group: "inline",
    inline: true,
    atom: true,
    selectable: true,

    addAttributes() {
      return Object.fromEntries(
        attributes.map(attribute => [
          attribute,
          {
            default: null,
            renderHTML: () => ({}),
          },
        ]),
      );
    },

    parseHTML() {
      return [{
        tag: 'span[data-tt-node="' + name + '"]',
        getAttrs: element => Object.fromEntries(
          attributes.map(attribute => [
            attribute,
            element.getAttribute("data-tt-" + kebabCase(attribute)),
          ]),
        ),
      }];
    },

    renderHTML({ node, HTMLAttributes }) {
      const dataAttributes = { "data-tt-node": name };
      for (const attribute of attributes) {
        const value = node.attrs[attribute];
        if (value !== null && value !== undefined) {
          dataAttributes["data-tt-" + kebabCase(attribute)] =
            typeof value === "string" ? value : JSON.stringify(value);
        }
      }
      const reference = identifier ? identifier(node.attrs) : "";
      return [
        "span",
        mergeAttributes(HTMLAttributes, dataAttributes),
        label + (reference ? " · " + reference : ""),
      ];
    },

    renderMarkdown(node) {
      if (typeof node.attrs.rawToken === "string" && node.attrs.rawToken) {
        return node.attrs.rawToken;
      }
      const output = serialize ? serialize(node.attrs) : "";
      if (typeof output !== "string" || !output) {
        throw new Error(
          "TradeThesis " + name + " content has no lossless Markdown representation yet.",
        );
      }
      return output;
    },
  });
}

const imageNode = Node.create({
  name: "image",
  group: "inline",
  inline: true,
  atom: true,
  selectable: true,
  addAttributes() {
    return {
      src: { default: null, renderHTML: () => ({}) },
      alt: { default: "", renderHTML: () => ({}) },
      title: { default: null, renderHTML: () => ({}) },
      assetId: { default: null, renderHTML: () => ({}) },
    };
  },
  parseHTML() {
    return [
      {
        tag: "img[src]",
        getAttrs: element => {
          const src = element.getAttribute("src") || "";
          const asset = ASSET_SOURCE_PATTERN.exec(src);
          return {
            src,
            alt: element.getAttribute("alt") || "",
            title: element.getAttribute("title"),
            assetId: asset ? asset[1] : null,
          };
        },
      },
      {
        tag: 'span[data-tt-node="image"]',
        getAttrs: element => ({
          src: null,
          alt: element.textContent.replace(/^Image asset(?:\s*·\s*)?/, ""),
          title: null,
          assetId: element.getAttribute("data-tt-asset-id"),
        }),
      },
    ];
  },
  renderHTML({ node, HTMLAttributes }) {
    const src = node.attrs.src || (
      node.attrs.assetId ? "asset://" + node.attrs.assetId : ""
    );
    if (node.attrs.assetId || src.startsWith("asset://")) {
      const assetId = node.attrs.assetId || src.slice("asset://".length);
      return [
        "span",
        mergeAttributes(HTMLAttributes, {
          "data-tt-node": "image",
          "data-tt-asset-id": assetId,
        }),
        "Image asset" + (node.attrs.alt ? " · " + node.attrs.alt : ""),
      ];
    }
    return ["img", mergeAttributes(HTMLAttributes, {
      src,
      alt: node.attrs.alt || "",
      title: node.attrs.title || null,
    })];
  },
  markdownTokenName: "image",
  parseMarkdown(token) {
    const src = String(token.href || "");
    const asset = ASSET_SOURCE_PATTERN.exec(src);
    return {
      type: "image",
      attrs: {
        src,
        alt: String(token.text || ""),
        title: token.title || null,
        assetId: asset ? asset[1] : null,
      },
    };
  },
  renderMarkdown(node) {
    const src = String(node.attrs.src || (
      node.attrs.assetId ? "asset://" + node.attrs.assetId : ""
    ));
    if (!src) {
      throw new Error("An image without a source cannot be exported to Markdown.");
    }
    const alt = String(node.attrs.alt || "").replace(/([\[\]])/g, "\\$1");
    const title = node.attrs.title
      ? ' "' + String(node.attrs.title).replace(/"/g, '\\"') + '"'
      : "";
    return "![" + alt + "](" + src + title + ")";
  },
});

const courseFigure = createReferenceNode({
  name: "courseFigure",
  label: "Figure",
  attributes: ["figureId", "rawToken"],
  identifier: attrs => attrs.figureId,
  serialize: attrs => attrs.figureId
    ? tokenFor("teaching-figure", attrs.figureId)
    : "",
});

const imageGroup = createReferenceNode({
  name: "imageGroup",
  label: "Image group",
  attributes: ["groupId", "rawToken"],
  identifier: attrs => attrs.groupId,
  serialize: attrs => attrs.groupId ? tokenFor("image-group", attrs.groupId) : "",
});

const comparisonFigure = createReferenceNode({
  name: "comparisonFigure",
  label: "Comparison figure",
  attributes: ["figureId", "rawToken"],
  identifier: attrs => attrs.figureId,
  serialize: attrs => attrs.figureId
    ? tokenFor("teaching-figure", attrs.figureId)
    : "",
});

const courseCard = createReferenceNode({
  name: "courseCard",
  label: "Course card",
  attributes: ["courseId", "comingSoon", "rawToken"],
  identifier: attrs => attrs.courseId,
  serialize: attrs => {
    if (!UUID_PATTERN.test(String(attrs.courseId || ""))) return "";
    return tokenFor(
      "course-card",
      (attrs.comingSoon ? "coming-soon:" : "") + attrs.courseId,
    );
  },
});

const lessonReference = createReferenceNode({
  name: "lessonReference",
  label: "Lesson reference",
  attributes: ["lessonId", "displayMode", "rawToken"],
  identifier: attrs => attrs.lessonId,
  serialize: attrs => {
    if (!UUID_PATTERN.test(String(attrs.lessonId || ""))) return "";
    return tokenFor(
      attrs.displayMode === "card" ? "lesson-card" : "lesson",
      attrs.lessonId,
    );
  },
});

const regionalBlock = createReferenceNode({
  name: "regionalBlock",
  label: "Regional block",
  attributes: ["blockId", "rawToken"],
  identifier: attrs => attrs.blockId,
  serialize: attrs => SAFE_REFERENCE_PATTERN.test(String(attrs.blockId || ""))
    ? tokenFor("regional-block", attrs.blockId)
    : "",
});

const practiceQuestion = createReferenceNode({
  name: "practiceQuestion",
  label: "Practice question",
  attributes: ["questionId", "rawToken"],
  identifier: attrs => attrs.questionId,
});

const videoBlock = createReferenceNode({
  name: "videoBlock",
  label: "Protected video reference",
  attributes: ["videoId", "rawToken"],
  identifier: attrs => attrs.videoId,
});

const notebookBlock = createReferenceNode({
  name: "notebookBlock",
  label: "Notebook",
  attributes: ["notebookId", "rawToken"],
  identifier: attrs => attrs.notebookId,
});

const reflectionBlock = createReferenceNode({
  name: "reflectionBlock",
  label: "Reflection",
  attributes: ["reflectionId", "rawToken"],
  identifier: attrs => attrs.reflectionId,
});

const lessonTab = createReferenceNode({
  name: "lessonTab",
  label: "Lesson tab",
  attributes: ["tab", "rawToken"],
  identifier: attrs => attrs.tab,
  serialize: attrs => ["idea", "examples", "practice"].includes(attrs.tab)
    ? tokenFor("lesson-tab", attrs.tab)
    : "",
});

const tableReference = createReferenceNode({
  name: "tableReference",
  label: "Structured table",
  attributes: ["tableId", "rawToken"],
  identifier: attrs => attrs.tableId,
  serialize: attrs => SAFE_REFERENCE_PATTERN.test(String(attrs.tableId || ""))
    ? tokenFor("table-block", attrs.tableId)
    : "",
});

const callout = createReferenceNode({
  name: "callout",
  label: "Callout",
  attributes: ["tone", "title", "rawToken"],
  identifier: attrs => attrs.title || attrs.tone,
});

const legacyMarkdown = Node.create({
  name: "legacyMarkdown",
  group: "inline",
  inline: true,
  atom: true,
  selectable: true,
  addAttributes() {
    return {
      rawToken: { default: null, renderHTML: () => ({}) },
      tokenKind: { default: "unknown", renderHTML: () => ({}) },
    };
  },
  parseHTML() {
    return [{
      tag: 'span[data-tt-node="legacyMarkdown"]',
      getAttrs: element => ({
        rawToken: element.getAttribute("data-tt-raw-token"),
        tokenKind: element.getAttribute("data-tt-token-kind") || "unknown",
      }),
    }];
  },
  renderHTML({ node, HTMLAttributes }) {
    return [
      "span",
      mergeAttributes(HTMLAttributes, {
        "data-tt-node": "legacyMarkdown",
        "data-tt-token-kind": node.attrs.tokenKind || "unknown",
        "data-tt-raw-token": node.attrs.rawToken || "",
      }),
      "Unmapped lesson marker · " + (node.attrs.tokenKind || "unknown"),
    ];
  },
  renderMarkdown(node) {
    if (typeof node.attrs.rawToken !== "string" || !node.attrs.rawToken) {
      throw new Error("An unmapped lesson marker cannot be exported without its original token.");
    }
    return node.attrs.rawToken;
  },
});

export const TradeThesisExtensions = [
  imageNode,
  courseFigure,
  imageGroup,
  comparisonFigure,
  courseCard,
  lessonReference,
  regionalBlock,
  practiceQuestion,
  videoBlock,
  notebookBlock,
  reflectionBlock,
  lessonTab,
  tableReference,
  callout,
  legacyMarkdown,
];

function escapeHtmlAttribute(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function referencePlaceholder(name, attributes, rawToken) {
  const values = { ...attributes, rawToken };
  const htmlAttributes = { "data-tt-node": name };
  for (const [key, value] of Object.entries(values)) {
    if (value === null || value === undefined) continue;
    htmlAttributes["data-tt-" + kebabCase(key)] = String(value);
  }
  const markup = Object.entries(htmlAttributes)
    .map(([key, value]) => key + '="' + escapeHtmlAttribute(value) + '"')
    .join(" ");
  return "<span " + markup + "></span>";
}

function parseReferenceToken(rawToken) {
  const body = rawToken.slice(2, -2);
  const separator = body.indexOf(":");
  const kind = (separator < 0 ? body : body.slice(0, separator)).toLowerCase();
  const value = separator < 0 ? "" : body.slice(separator + 1).trim();

  if (kind === "teaching-figure" && SAFE_REFERENCE_PATTERN.test(value)) {
    return referencePlaceholder("courseFigure", { figureId: value }, rawToken);
  }
  if (kind === "image-group" && SAFE_REFERENCE_PATTERN.test(value)) {
    return referencePlaceholder("imageGroup", { groupId: value }, rawToken);
  }
  if ((kind === "lesson" || kind === "lesson-card") && UUID_PATTERN.test(value)) {
    return referencePlaceholder("lessonReference", {
      lessonId: value,
      displayMode: kind === "lesson-card" ? "card" : "inline",
    }, rawToken);
  }
  if (kind === "course-card") {
    const comingSoon = value.startsWith("coming-soon:");
    const courseId = comingSoon ? value.slice("coming-soon:".length) : value;
    if (UUID_PATTERN.test(courseId)) {
      return referencePlaceholder("courseCard", { courseId, comingSoon }, rawToken);
    }
  }
  if (kind === "regional-block" && SAFE_REFERENCE_PATTERN.test(value)) {
    return referencePlaceholder("regionalBlock", { blockId: value }, rawToken);
  }
  if (kind === "table-block" && SAFE_REFERENCE_PATTERN.test(value)) {
    return referencePlaceholder("tableReference", { tableId: value }, rawToken);
  }
  if (kind === "lesson-tab" && ["idea", "examples", "practice"].includes(value)) {
    return referencePlaceholder("lessonTab", { tab: value }, rawToken);
  }
  return referencePlaceholder("legacyMarkdown", {
    rawToken,
    tokenKind: kind || "unknown",
  }, rawToken);
}

function isEscapedAt(source, index) {
  let backslashes = 0;
  for (let cursor = index - 1; cursor >= 0 && source[cursor] === "\\"; cursor -= 1) {
    backslashes += 1;
  }
  return backslashes % 2 === 1;
}

function replaceMarkersOutsideInlineCode(line) {
  const tick = String.fromCharCode(96);
  let output = "";
  let cursor = 0;
  while (cursor < line.length) {
    const nextTick = line.indexOf(tick, cursor);
    const nextMarker = line.indexOf("[[", cursor);

    if (nextMarker >= 0 && (nextTick < 0 || nextMarker < nextTick)) {
      output += line.slice(cursor, nextMarker);
      const match = /^\[\[([^\]\r\n]{1,200})\]\]/.exec(line.slice(nextMarker));
      if (!match || isEscapedAt(line, nextMarker)) {
        output += "[[";
        cursor = nextMarker + 2;
        continue;
      }
      output += parseReferenceToken(match[0]);
      cursor = nextMarker + match[0].length;
      continue;
    }

    if (nextTick < 0) {
      output += line.slice(cursor);
      break;
    }

    output += line.slice(cursor, nextTick);
    let tickCount = 1;
    while (line[nextTick + tickCount] === tick) tickCount += 1;
    const delimiter = tick.repeat(tickCount);
    const closing = line.indexOf(delimiter, nextTick + tickCount);
    if (closing < 0) {
      output += delimiter;
      cursor = nextTick + tickCount;
      continue;
    }
    output += line.slice(nextTick, closing + tickCount);
    cursor = closing + tickCount;
  }
  return output;
}

export function prepareTradeThesisMarkdown(source) {
  const chunks = String(source || "").split(/(\r?\n)/);
  const output = [];
  let fence = null;

  for (const chunk of chunks) {
    if (chunk === "\n" || chunk === "\r\n") {
      output.push(chunk);
      continue;
    }
    if (fence) {
      output.push(chunk);
      const close = new RegExp("^ {0,3}" + fence.character + "{" + fence.length + ",}\\s*$");
      if (close.test(chunk)) fence = null;
      continue;
    }

    const tick = String.fromCharCode(96);
    const opener = new RegExp("^ {0,3}(" + tick + "{3,}|~{3,})").exec(chunk);
    if (opener) {
      fence = { character: opener[1][0], length: opener[1].length };
      output.push(chunk);
      continue;
    }

    output.push(replaceMarkersOutsideInlineCode(chunk));
  }

  return output.join("");
}
