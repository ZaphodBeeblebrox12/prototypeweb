'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { buildPublicSite, PUBLIC_PAGES } = require('./build_public_site.cjs');
const sourceSite = path.resolve(__dirname, '../../site');

function temporarySite() {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'tradethesis-seo-'));
  fs.cpSync(sourceSite, directory, { recursive: true });
  return directory;
}
function read(directory, file) {
  return fs.readFileSync(path.join(directory, file), 'utf8');
}
function clean(directory) {
  fs.rmSync(directory, { recursive: true, force: true });
}
function jsonLd(directory, file) {
  const html = read(directory, file);
  const match = html.match(/<script\\b(?=[^>]*\\bid=["']tt-seo-jsonld["'])[^>]*>([\\s\\S]*?)<\\/script>/i);
  assert.ok(match, file + ' must include generated JSON-LD.');
  return JSON.parse(match[1]);
}
function metaDescription(html) {
  const tag = (html.match(/<meta\\b[^>]*\\bname=["']description["'][^>]*>/i) || [])[0] || '';
  const match = tag.match(/\\bcontent\\s*=\\s*(["'])([\\s\\S]*?)\\1/i);
  return match ? match[2].trim() : '';
}

const staging = temporarySite();
try {
  const result = buildPublicSite({
    siteDir: staging,
    publicBaseUrl: 'https://tradethesis-public-staging.onrender.com',
    academyBaseUrl: 'https://tradethesis-academy-staging.onrender.com',
    indexable: false
  });
  assert.equal(result.indexable, false);
  assert.equal(result.sitemapUrls, 0);
  assert.match(read(staging, 'robots.txt'), /Allow: \//);
  assert.doesNotMatch(read(staging, 'robots.txt'), /Sitemap:/);
  assert.doesNotMatch(read(staging, 'sitemap.xml'), /<url>/);
  assert.match(read(staging, 'index.html'), /name="robots" content="noindex, nofollow"/);
  assert.doesNotMatch(read(staging, 'index.html'), /rel="canonical"/);
  assert.match(read(staging, 'member-area-preview.html'), /noindex, nofollow/);
} finally {
  clean(staging);
}

const production = temporarySite();
try {
  const result = buildPublicSite({
    siteDir: production,
    publicBaseUrl: 'https://tradethesis.example',
    academyBaseUrl: 'https://academy.tradethesis.example',
    indexable: true
  });
  assert.equal(result.indexable, true);
  assert.equal(result.sitemapUrls, PUBLIC_PAGES.length);
  assert.ok(read(production, 'robots.txt').includes('Sitemap: https://tradethesis.example/sitemap.xml'));
  assert.match(read(production, 'index.html'), /name="robots" content="index, follow"/);
  assert.ok(read(production, 'index.html').includes('rel="canonical" href="https://tradethesis.example/'));
  assert.match(read(production, 'index.html'), /tradethesis-social-preview\.jpg/);
  assert.match(read(production, 'index.html'), /tradethesis-academy-base-url/);
  assert.match(read(production, 'member-area-preview.html'), /noindex, nofollow/);
  const indexedMetadata = PUBLIC_PAGES.map(page => {
    const html = read(production, page.file);
    const titleMatch = html.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i);
    const descriptionTag = (html.match(/<meta\b[^>]*\bname=["']description["'][^>]*>/i) || [])[0] || '';
    const descriptionMatch = descriptionTag.match(/\bcontent\s*=\s*(["'])([\s\S]*?)\1/i);
    const title = titleMatch ? titleMatch[1].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim() : '';
    const description = descriptionMatch ? descriptionMatch[2].trim() : '';
    assert.ok(title, page.file + ' must have a page title.');
    assert.ok(description.length >= 90 && description.length <= 180,
      page.file + ' must have a useful, concise meta description (90–180 characters).');
    return title;
  });
  assert.equal(new Set(indexedMetadata).size, indexedMetadata.length,
    'Each indexable public page must have a distinct title.');

  const sitemap = read(production, 'sitemap.xml');
  assert.equal((sitemap.match(/<url>/g) || []).length, PUBLIC_PAGES.length);
  assert.doesNotMatch(sitemap, /member-area-preview|00_OPEN_INTERACTIVE_PREVIEW|support-resistance-room/);
  const catalogueSchema = jsonLd(production, 'courses.html');
  const catalogueList = catalogueSchema['@graph'].find(item => item['@type'] === 'ItemList');
  assert.ok(catalogueList, 'The catalogue must describe its three primary learning offers.');
  assert.equal(catalogueList.itemListElement.length, COURSE_OFFERS.length);
  for (const offer of COURSE_OFFERS) {
    const page = PUBLIC_PAGES.find(item => item.route === offer.route);
    const pageHtml = read(production, page.file);
    const listed = catalogueList.itemListElement.find(item => item.item.url === 'https://tradethesis.example' + offer.route);
    assert.ok(listed, offer.route + ' must appear in the catalogue ItemList.');
    assert.equal(listed.item.description, metaDescription(pageHtml),
      offer.route + ' schema description must stay synchronized with visible page metadata.');
    const pageSchema = jsonLd(production, page.file);
    const courseSchema = pageSchema['@graph'].find(item => item['@type'] === 'Course');
    assert.ok(courseSchema, offer.route + ' must retain its Course structured data.');
    assert.equal(courseSchema.description, metaDescription(pageHtml));
  }

  for (const page of PUBLIC_PAGES) {
    const pageSchema = jsonLd(production, page.file);
    const webPage = pageSchema['@graph'].find(item => item['@type'] === 'WebPage');
    assert.ok(Array.isArray(webPage.about) && webPage.about.length > 0,
      page.file + ' must identify its actual subject topics.');
    assert.ok(webPage.about.every(topic => topic['@type'] === 'Thing' && topic.name),
      page.file + ' must express topical about values as named Things.');
    if (page.breadcrumbs) {
      const breadcrumbSchema = pageSchema['@graph'].find(item => item['@type'] === 'BreadcrumbList');
      assert.ok(breadcrumbSchema, page.file + ' must expose its visible breadcrumb hierarchy.');
      assert.deepEqual(
        breadcrumbSchema.itemListElement.map(item => item.name),
        page.breadcrumbs.map(item => item.name)
      );
      assert.deepEqual(
        breadcrumbSchema.itemListElement.map(item => item.item),
        page.breadcrumbs.map(item => 'https://tradethesis.example' + item.route)
      );
    }
  }

  const tradingPath = read(production, 'trading-path.html');
  assert.doesNotMatch(tradingPath, /<a href="construct\\.html">CONSTRUCT<\\/a>/,
    'The Trading Path must not show CONSTRUCT as a parent breadcrumb.');
  const construct = read(production, 'construct.html');
  assert.match(construct, /<a href="trading-path\\.html">Trading Path<\\/a>/,
    'CONSTRUCT must link to its stated preceding learning path in the breadcrumb.');
} finally {
  clean(production);
}

assert.throws(() => buildPublicSite({
  siteDir: sourceSite,
  publicBaseUrl: 'https://tradethesis-public-staging.onrender.com',
  academyBaseUrl: 'https://tradethesis-academy-staging.onrender.com',
  indexable: true
}), /Refusing to enable indexing/);

process.stdout.write('TradeThesis SEO build tests passed.\n');
