import assert from "node:assert/strict";
import test from "node:test";

import { TradeThesisExtensions } from "../src/tradethesis-nodes.js";

const ASSET_ID = "00000000-0000-4000-8000-000000000003";
const imageExtension = TradeThesisExtensions.find(extension => extension.name === "image");

test("asset-backed Markdown images retain stable IDs and export the original reference", () => {
  assert.ok(imageExtension, "The TradeThesis image extension must be registered");

  const source = "asset://" + ASSET_ID;
  const parsed = imageExtension.config.parseMarkdown({
    href: source,
    text: "Market structure",
    title: null,
  });

  assert.equal(parsed.type, "image");
  assert.equal(parsed.attrs.src, source);
  assert.equal(parsed.attrs.assetId, ASSET_ID);
  assert.equal(parsed.attrs.alt, "Market structure");
  assert.equal(
    imageExtension.config.renderMarkdown({ attrs: parsed.attrs }),
    "![Market structure](" + source + ")",
  );
});

test("asset-backed image extension renders a safe placeholder instead of fetching a private URL", () => {
  const attrs = {
    src: "asset://" + ASSET_ID,
    assetId: ASSET_ID,
    alt: "Market structure",
    title: null,
  };
  const element = imageExtension.config.renderHTML({
    node: { attrs },
    HTMLAttributes: {},
  });

  assert.equal(element[0], "span");
  assert.equal(element[1]["data-tt-node"], "image");
  assert.equal(element[1]["data-tt-asset-id"], ASSET_ID);
  assert.match(element[2], /Market structure/);
});


test("asset-backed image renders its authenticated Academy preview without serializing that URL", () => {
  const previewUrl = "/staff/course-builder/assets/draft/00000000-0000-4000-8000-000000000003/";
  const attrs = {
    src: "asset://" + ASSET_ID,
    assetId: ASSET_ID,
    previewUrl,
    alt: "Market structure",
    title: "Market structure",
  };
  const element = imageExtension.config.renderHTML({
    node: { attrs },
    HTMLAttributes: {},
  });

  assert.equal(element[0], "img");
  assert.equal(element[1].src, previewUrl);
  assert.equal(element[1]["data-tt-asset-id"], ASSET_ID);
  assert.equal(element[1].alt, "Market structure");
  assert.equal(
    imageExtension.config.renderMarkdown({ attrs }),
    "![Market structure](asset://" + ASSET_ID + ' "Market structure")',
  );
});
