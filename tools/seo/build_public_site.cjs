'use strict';

const fs = require('node:fs');
const path = require('node:path');

const DEFAULT_PUBLIC_BASE_URL = 'https://tradethesis-public-staging.onrender.com';
const DEFAULT_ACADEMY_BASE_URL = 'https://tradethesis-academy-staging.onrender.com';

const PUBLIC_PAGES = [
  { file: 'index.html', route: '/', kind: 'home' },
  { file: 'courses.html', route: '/courses.html', kind: 'course-list' },
  { file: 'trading-path.html', route: '/trading-path.html', kind: 'trading-path' },
  { file: 'construct.html', route: '/construct.html', kind: 'construct' },
  { file: 'live-class.html', route: '/live-class.html', kind: 'live-class' },
  { file: 'community.html', route: '/community.html', kind: 'community' }
];

const COURSE_OFFERS = [
  {
    name: 'The TradeThesis Trading Path',
    description: 'A practical course in markets, chart reading, risk and review.',
    route: '/trading-path.html'
  },
  {
    name: 'CONSTRUCT: Trade Construction and Management',
    description: 'A guided programme for building and reviewing a trading process.',
    route: '/construct.html'
  },
  {
    name: 'Trade Construction and Management Live Classroom',
    description: 'Six live sessions on trade planning, risk and management.',
    route: '/live-class.html'
  }
];

function escapeHtml(value) {
  return String(value).replace(/&/g, '&amp;').replace(/"/g, '&quot;')
    .replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function normalizeBaseUrl(value, label) {
  const parsed = new URL(String(value));
  if (parsed.protocol !== 'https:' || parsed.username || parsed.password ||
      parsed.search || parsed.hash) {
    throw new Error(label + ' must be HTTPS without credentials, query or fragment.');
  }
  return parsed.toString().replace(/\/+$/, '');
}

function tagHasKey(tag, attribute, key) {
  const match = tag.match(/\b(name|property)\s*=\s*(["'])(.*?)\2/i);
  return Boolean(match && match[1].toLowerCase() === attribute && match[3] === key);
}

function removeMeta(head, attribute, key) {
  const tags = head.match(/<meta\b[^>]*>/gi) || [];
  for (const tag of tags) {
    if (tagHasKey(tag, attribute, key)) head = head.replace(tag, '');
  }
  return head;
}

function replaceMeta(head, attribute, key, content) {
  head = removeMeta(head, attribute, key);
  const tag = '<meta ' + attribute + '="' + escapeHtml(key) +
    '" content="' + escapeHtml(content) + '">';
  return head.replace(/<\/head>/i, '  ' + tag + '\n</head>');
}

function replaceCanonical(head, href) {
  head = head.replace(/<link\b(?=[^>]*\brel\s*=\s*(["'])canonical\1)[^>]*>\s*/gi, '');
  if (!href) return head;
  return head.replace(/<\/head>/i, '  <link rel="canonical" href="' +
    escapeHtml(href) + '">\n</head>');
}

function getMetaContent(head, name) {
  const tags = head.match(/<meta\b[^>]*>/gi) || [];
  const tag = tags.find(item => tagHasKey(item, 'name', name));
  if (!tag) return '';
  const match = tag.match(/\bcontent\s*=\s*(["'])([\s\S]*?)\1/i);
  return match ? match[2].replace(/&amp;/g, '&').trim() : '';
}

function getTitle(head) {
  const match = head.match(/<title\b[^>]*>([\s\S]*?)<\/title>/i);
  return match ? match[1].replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim()
    .replace(/&amp;/g, '&').replace(/&quot;/g, '"') : 'TradeThesis';
}

function safeJson(value) {
  return JSON.stringify(value).replace(/</g, '\\u003c')
    .replace(/>/g, '\\u003e').replace(/&/g, '\\u0026');
}

function structuredData(page, pageUrl, title, description, baseUrl) {
  const organizationId = baseUrl + '/#organization';
  const websiteId = baseUrl + '/#website';
  const graph = [
    {
      '@type': 'Organization',
      '@id': organizationId,
      name: 'TradeThesis',
      url: baseUrl + '/',
      logo: baseUrl + '/assets/tradethesis-horizontal.png'
    },
    {
      '@type': 'WebSite',
      '@id': websiteId,
      name: 'TradeThesis',
      url: baseUrl + '/',
      publisher: { '@id': organizationId }
    },
    {
      '@type': 'WebPage',
      '@id': pageUrl + '#webpage',
      url: pageUrl,
      name: title,
      description,
      isPartOf: { '@id': websiteId },
      about: { '@id': organizationId }
    }
  ];

  const course = COURSE_OFFERS.find(item => item.route === page.route);
  if (course) {
    graph.push({
      '@type': 'Course',
      name: course.name,
      description: course.description,
      url: pageUrl,
      provider: { '@id': organizationId }
    });
  }

  if (page.kind === 'course-list') {
    graph.push({
      '@type': 'ItemList',
      name: 'TradeThesis trading courses',
      itemListElement: COURSE_OFFERS.map((item, index) => ({
        '@type': 'ListItem',
        position: index + 1,
        url: baseUrl + item.route,
        item: {
          '@type': 'Course',
          name: item.name,
          description: item.description,
          provider: { '@id': organizationId },
          url: baseUrl + item.route
        }
      }))
    });
  }
  return { '@context': 'https://schema.org', '@graph': graph };
}

function walkHtml(directory) {
  const output = [];
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) output.push(...walkHtml(fullPath));
    else if (entry.isFile() && entry.name.toLowerCase().endsWith('.html')) output.push(fullPath);
  }
  return output;
}

function buildPublicSite(options = {}) {
  const siteDir = path.resolve(options.siteDir || path.join(__dirname, '../../site'));
  const rawPublicBaseUrl = options.publicBaseUrl || process.env.TRADETHESIS_PUBLIC_BASE_URL;
  const rawAcademyBaseUrl = options.academyBaseUrl || process.env.TRADETHESIS_ACADEMY_BASE_URL;
  const indexable = options.indexable !== undefined
    ? Boolean(options.indexable)
    : String(process.env.TRADETHESIS_SEO_INDEXABLE || '').toLowerCase() === 'true';

  if (indexable && !rawPublicBaseUrl) {
    throw new Error('Set TRADETHESIS_PUBLIC_BASE_URL before enabling search indexing.');
  }
  if (indexable && !rawAcademyBaseUrl) {
    throw new Error('Set TRADETHESIS_ACADEMY_BASE_URL before enabling search indexing.');
  }

  const publicBaseUrl = normalizeBaseUrl(rawPublicBaseUrl || DEFAULT_PUBLIC_BASE_URL,
    'TRADETHESIS_PUBLIC_BASE_URL');
  const academyBaseUrl = normalizeBaseUrl(rawAcademyBaseUrl || DEFAULT_ACADEMY_BASE_URL,
    'TRADETHESIS_ACADEMY_BASE_URL');

  const publicHost = new URL(publicBaseUrl).hostname.toLowerCase();
  if (indexable && (publicHost === 'localhost' || publicHost.endsWith('.onrender.com') ||
      publicHost === '127.0.0.1')) {
    throw new Error('Refusing to enable indexing on a local or Render staging hostname.');
  }

  const pageByFile = new Map(PUBLIC_PAGES.map(page => [page.file, page]));
  const allHtml = walkHtml(siteDir);
  for (const filePath of allHtml) {
    const relative = path.relative(siteDir, filePath).split(path.sep).join('/');
    const page = pageByFile.get(relative);
    const source = fs.readFileSync(filePath, 'utf8');
    const match = source.match(/<head\b[^>]*>[\s\S]*?<\/head>/i);
    if (!match) throw new Error('Missing HTML head in ' + relative);

    let head = match[0];
    const title = getTitle(head);
    const description = getMetaContent(head, 'description') ||
      'Practical trading education focused on chart reading, trade construction and risk management.';
    const shouldIndex = Boolean(indexable && page);

    head = replaceMeta(head, 'name', 'robots',
      shouldIndex ? 'index, follow' : 'noindex, nofollow');
    head = replaceMeta(head, 'name', 'tradethesis-academy-base-url', academyBaseUrl);

    if (shouldIndex) {
      const pageUrl = publicBaseUrl + page.route;
      const imageUrl = publicBaseUrl + '/assets/tradethesis-social-preview.jpg';
      head = replaceCanonical(head, pageUrl);
      head = replaceMeta(head, 'property', 'og:type', 'website');
      head = replaceMeta(head, 'property', 'og:site_name', 'TradeThesis');
      head = replaceMeta(head, 'property', 'og:title', title);
      head = replaceMeta(head, 'property', 'og:description', description);
      head = replaceMeta(head, 'property', 'og:url', pageUrl);
      head = replaceMeta(head, 'property', 'og:image', imageUrl);
      head = replaceMeta(head, 'property', 'og:image:secure_url', imageUrl);
      head = replaceMeta(head, 'property', 'og:image:width', '1200');
      head = replaceMeta(head, 'property', 'og:image:height', '630');
      head = replaceMeta(head, 'property', 'og:image:type', 'image/jpeg');
      head = replaceMeta(head, 'property', 'og:image:alt',
        'TradeThesis — practical trading education for chart reading, decision-making and risk management.');
      head = replaceMeta(head, 'name', 'twitter:card', 'summary_large_image');
      head = replaceMeta(head, 'name', 'twitter:title', title);
      head = replaceMeta(head, 'name', 'twitter:description', description);
      head = replaceMeta(head, 'name', 'twitter:image', imageUrl);

      head = head.replace(/<script\b(?=[^>]*\bid=["']tt-seo-jsonld["'])[^>]*>[\s\S]*?<\/script>\s*/gi, '');
      const jsonLd = safeJson(structuredData(page, pageUrl, title, description, publicBaseUrl));
      head = head.replace(/<\/head>/i,
        '  <script type="application/ld+json" id="tt-seo-jsonld">' + jsonLd + '</script>\n</head>');
    } else {
      head = replaceCanonical(head, '');
      head = removeMeta(head, 'property', 'og:url');
      head = head.replace(/<script\b(?=[^>]*\bid=["']tt-seo-jsonld["'])[^>]*>[\s\S]*?<\/script>\s*/gi, '');
    }

    fs.writeFileSync(filePath, source.replace(match[0], head));
  }

  const robotsLines = ['User-agent: *', 'Allow: /'];
  if (indexable) robotsLines.push('', 'Sitemap: ' + publicBaseUrl + '/sitemap.xml');
  fs.writeFileSync(path.join(siteDir, 'robots.txt'), robotsLines.join('\n') + '\n');

  const urlset = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
  ];
  if (indexable) {
    for (const page of PUBLIC_PAGES) {
      urlset.push('  <url><loc>' + escapeHtml(publicBaseUrl + page.route) + '</loc></url>');
    }
  }
  urlset.push('</urlset>');
  fs.writeFileSync(path.join(siteDir, 'sitemap.xml'), urlset.join('\n') + '\n');

  return { siteDir, publicBaseUrl, academyBaseUrl, indexable,
    htmlFilesProcessed: allHtml.length, sitemapUrls: indexable ? PUBLIC_PAGES.length : 0 };
}

if (require.main === module) {
  try {
    const result = buildPublicSite();
    process.stdout.write('TradeThesis SEO build complete: ' + result.htmlFilesProcessed +
      ' HTML files processed; indexing ' + (result.indexable ? 'enabled' : 'disabled') +
      '; ' + result.sitemapUrls + ' sitemap URLs.\n');
  } catch (error) {
    process.stderr.write('TradeThesis SEO build failed: ' + error.message + '\n');
    process.exitCode = 1;
  }
}

module.exports = { buildPublicSite, PUBLIC_PAGES };
