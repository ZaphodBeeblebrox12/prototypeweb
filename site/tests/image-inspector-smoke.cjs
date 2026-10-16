const assert = require("node:assert/strict");
const fs = require("node:fs");
const { chromium } = require("playwright");

(async () => {
  const screenshotDir = "/tmp/tradethesis-image-inspector";
  fs.mkdirSync(screenshotDir, { recursive: true });
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const pageErrors = [];
  page.on("pageerror", error => pageErrors.push(error.message));

  await page.goto("http://127.0.0.1:4173/support-resistance-room.html?lesson=14", { waitUntil: "networkidle" });
  await page.waitForSelector("#sr-v52-longform:not([hidden])");
  await page.waitForFunction(() => {
    const img = document.querySelector("#sr-chart-image");
    return img && img.complete && img.naturalWidth > 0;
  });
  const coreChart = page.locator("#sr-chart-image");
  const desktopGridTracks = await page.locator("#sr-work-grid").evaluate(el => getComputedStyle(el).gridTemplateColumns);
  assert.equal(desktopGridTracks.trim().split(/\s+/).length, 1,
    "Instructional chart should get the full reading width, with the response panel beneath it");
  const chartSource = await coreChart.evaluate(img => img.currentSrc || img.src);
  assert.ok(chartSource.endsWith(".svg"), "Core lesson charts should prefer vector sources when available: " + chartSource);
  assert.ok((await coreChart.getAttribute("data-chart-canonical-file") || "").endsWith(".png"),
    "The chart should preserve its canonical PNG stage key for answer-gate mapping");
  const panel = page.locator("#sr-v52-longform .sr-v52-figure-panel").first();
  await panel.waitFor({ state: "visible" });
  const firstPanelViewBox = (await panel.getAttribute("viewBox")).trim().split(/\s+/).map(Number);
  assert.equal(firstPanelViewBox[0], 0,
    "The first comparative panel must retain its left-side price-axis labels in the crop");
  await panel.screenshot({ path: screenshotDir + "/first-panel-crop.png" });
  const sixPanelStack = page.locator(".sr-v52-figure-set").filter({
    has: page.locator('.sr-v52-figure-panel[aria-label^="Panel 1 of 6"]')
  }).first();
  await sixPanelStack.waitFor({ state: "visible" });
  await sixPanelStack.screenshot({ path: screenshotDir + "/six-panel-stack.png" });
  assert.equal(await panel.getAttribute("role"), "button", "Inline chart crops should be keyboard-accessible buttons");
  assert.ok(await panel.getAttribute("aria-label"), "Chart crops should have an accessible description");

  const finalReview = page.locator("#sr-v52-final-review");
  const reviewWasHidden = await finalReview.evaluate(el => el.hidden);
  const triggerTop = await panel.evaluate(el => el.getBoundingClientRect().top);
  await panel.scrollIntoViewIfNeeded();
  const expectedScroll = await page.evaluate(() => window.scrollY);
  await panel.click();
  const dialog = page.locator("dialog.tt-image-inspector[open]");
  await dialog.waitFor();
  assert.ok(await dialog.isVisible(), "The image inspector should open from a teaching figure");

  const zoom = dialog.locator("[data-tt-zoom]");
  const beforeZoom = await zoom.innerText();
  for (let i = 0; i < 5; i++) await dialog.locator('[data-tt-action="zoom-in"]').click();
  const mediaWidth = await dialog.locator(".tt-image-inspector-media").evaluate(el => parseFloat(el.style.width));
  assert.ok(mediaWidth > 0, "Zoom controls should size the image explicitly");
  assert.notEqual(await zoom.innerText(), beforeZoom, "Zoom status should update after zooming");
  await dialog.screenshot({ path: screenshotDir + "/desktop-viewer-zoom.png" });

  const stage = dialog.locator("[data-tt-stage]");
  const stageBox = await stage.boundingBox();
  const beforePan = await stage.evaluate(el => ({ left: el.scrollLeft, top: el.scrollTop }));
  await page.mouse.move(stageBox.x + Math.min(300, stageBox.width / 2), stageBox.y + Math.min(260, stageBox.height / 2));
  await page.mouse.down();
  await page.mouse.move(stageBox.x + Math.min(160, stageBox.width / 3), stageBox.y + Math.min(240, stageBox.height / 2), { steps: 4 });
  await page.mouse.up();
  const afterPan = await stage.evaluate(el => ({ left: el.scrollLeft, top: el.scrollTop }));
  assert.ok(afterPan.left !== beforePan.left || afterPan.top !== beforePan.top, "Dragging should pan a zoomed image");

  await dialog.locator('[data-tt-action="fit"]').click();
  assert.match(await zoom.innerText(), /^Fit/, "Fit control should reset the image to the viewport");
  await page.keyboard.press("Escape");
  await page.waitForFunction(() => !document.querySelector("dialog.tt-image-inspector").open);
  assert.ok(await panel.evaluate(el => document.activeElement === el), "Closing should return keyboard focus to the source chart");
  const scrollAfterClose = await page.evaluate(() => window.scrollY);
  assert.ok(Math.abs(scrollAfterClose - expectedScroll) < 3, "Closing should preserve the reader's scroll position");
  assert.equal(await finalReview.evaluate(el => el.hidden), reviewWasHidden, "Image inspection must not change the lesson review gate");

  await page.setViewportSize({ width: 390, height: 844 });
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForSelector("#sr-v52-longform:not([hidden])");
  const mobilePanel = page.locator("#sr-v52-longform .sr-v52-figure-panel").first();
  await mobilePanel.scrollIntoViewIfNeeded();
  await mobilePanel.click();
  const mobileDialog = page.locator("dialog.tt-image-inspector[open]");
  await mobileDialog.waitFor();
  await page.waitForFunction(() => {
    const el = document.querySelector("dialog.tt-image-inspector [data-tt-zoom]");
    return el && el.textContent.startsWith("Detail ·");
  });
  assert.match(await mobileDialog.locator("[data-tt-zoom]").innerText(), /^Detail · 200%$/,
    "Mobile image inspection should open enlarged instead of starting with tiny fit-to-screen annotations");
  assert.match(await mobileDialog.locator("[data-tt-image-source]").innerText(), /raster chart/i,
    "The inspector should explain when a panel is cropped from a raster source");
  const mobileStage = mobileDialog.locator("[data-tt-stage]");
  const mobileMediaWidth = await mobileDialog.locator(".tt-image-inspector-media").evaluate(el => parseFloat(el.style.width));
  const mobileStageWidth = await mobileStage.evaluate(el => el.clientWidth);
  assert.ok(mobileMediaWidth > mobileStageWidth * 1.4,
    "The initial mobile detail view should enlarge the image beyond the viewport width for closer reading");
  const mobileStartPosition = await mobileStage.evaluate(el => ({ left: el.scrollLeft, top: el.scrollTop }));
  assert.deepEqual(mobileStartPosition, { left: 0, top: 0 },
    "The initial enlarged view should keep the title and left-side price labels in view");
  await mobileDialog.screenshot({ path: screenshotDir + "/mobile-viewer.png" });
  const mobileLayout = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    pageWidth: document.documentElement.scrollWidth,
    viewerWidth: Math.round(document.querySelector("dialog.tt-image-inspector").getBoundingClientRect().width)
  }));
  assert.ok(mobileLayout.pageWidth <= mobileLayout.viewport + 1, "Opening the inspector must not introduce mobile page overflow");
  assert.ok(mobileLayout.viewerWidth <= mobileLayout.viewport + 1, "The viewer should fit the mobile viewport");
  await mobileDialog.locator('[data-tt-action="close"]').click();
  await page.waitForFunction(() => !document.querySelector("dialog.tt-image-inspector").open);
  assert.deepEqual(pageErrors, [], "Image inspection should not introduce browser JavaScript errors");
  console.log(JSON.stringify({
    result: "PASS",
    desktop: "open, zoom, pan, fit/reset, Escape-close, focus and scroll restoration",
    lessonState: "review gate unchanged",
    mobile: "viewport fit and no document-level horizontal overflow",
    pageErrors: pageErrors.length
  }, null, 2));
  await browser.close();
})().catch(error => {
  console.error(error);
  process.exit(1);
});