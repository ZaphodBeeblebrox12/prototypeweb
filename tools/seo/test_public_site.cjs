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
  assert.match(read(production, 'robots.txt'), /Sitemap: https://tradethesis\.example/sitemap\.xml/);
  assert.match(read(production, 'index.html'), /name="robots" content="index, follow"/);
  assert.match(read(production, 'index.html'), /rel="canonical" href="https://tradethesis\.example/"/);
  assert.match(read(production, 'index.html'), /tradethesis-social-preview\.jpg/);
  assert.match(read(production, 'index.html'), /tradethesis-academy-base-url/);
  assert.match(read(production, 'member-area-preview.html'), /noindex, nofollow/);
  const sitemap = read(production, 'sitemap.xml');
  assert.equal((sitemap.match(/<url>/g) || []).length, PUBLIC_PAGES.length);
  assert.doesNotMatch(sitemap, /member-area-preview|00_OPEN_INTERACTIVE_PREVIEW|support-resistance-room/);
  const schema = read(production, 'courses.html');
  assert.match(schema, /"@type":"ItemList"/);
  assert.equal((schema.match(/"@type":"Course"/g) || []).length, 3);
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
