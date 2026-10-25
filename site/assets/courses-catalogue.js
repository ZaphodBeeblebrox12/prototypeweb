/* TradeThesis Courses templates and interactions. Content lives in course-catalogue-data.js. */
(() => {
  'use strict';

  const data = window.TRADETHESIS_COURSE_DATA;
  if (!data) return;

  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));
  // Hidden records remain available as drafts but are excluded from public cards and counts.
  const isCatalogueVisible = item => item && item.catalogueVisibility !== 'hidden';
  const escapeHTML = value => String(value ?? '').replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[char]));

  const chartArt = type => {
    const base = `
      <g stroke="#cbd3c5" stroke-dasharray="3 5" opacity=".82"><path d="M10 20H210M10 42H210M10 64H210M10 86H210"/><path d="M54 10V92M100 10V92M146 10V92M192 10V92"/></g>
      <g stroke-linecap="round" stroke-width="1.6"><path d="M29 47V79M49 35V60M69 43V72M89 27V52M109 32V61M129 18V45M149 24V55M169 13V38M189 19V47" stroke="#355a46"/><rect x="25" y="54" width="8" height="17" rx="1" fill="#658568"/><rect x="45" y="39" width="8" height="15" rx="1" fill="#c96f50"/><rect x="65" y="49" width="8" height="16" rx="1" fill="#658568"/><rect x="85" y="31" width="8" height="15" rx="1" fill="#658568"/><rect x="105" y="39" width="8" height="14" rx="1" fill="#c96f50"/><rect x="125" y="23" width="8" height="15" rx="1" fill="#658568"/><rect x="145" y="31" width="8" height="17" rx="1" fill="#c96f50"/><rect x="165" y="18" width="8" height="15" rx="1" fill="#658568"/><rect x="185" y="24" width="8" height="14" rx="1" fill="#658568"/></g>`;
    const drawings = {
      'volume': `${base}<g opacity=".95"><rect x="25" y="69" width="10" height="21" rx="1" fill="#8ea98b"/><rect x="47" y="57" width="10" height="33" rx="1" fill="#8ea98b"/><rect x="69" y="64" width="10" height="26" rx="1" fill="#8ea98b"/><rect x="91" y="42" width="10" height="48" rx="1" fill="#8ea98b"/><rect x="113" y="27" width="10" height="63" rx="1" fill="#c96f50"/><rect x="135" y="51" width="10" height="39" rx="1" fill="#8ea98b"/><rect x="157" y="62" width="10" height="28" rx="1" fill="#8ea98b"/><rect x="179" y="70" width="10" height="20" rx="1" fill="#8ea98b"/></g><path d="M15 48L39 43L61 49L83 31L105 39L127 21L149 34L171 25L205 31" fill="none" stroke="#355a46" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"/>`,
      'support-resistance': `<rect x="8" y="61" width="204" height="20" rx="3" fill="#b8cbae" opacity=".76"/><path d="M12 66H208M12 81H208" stroke="#789277" stroke-width="1.4" stroke-dasharray="4 4"/>${base}<path d="M15 75L39 65L62 72L86 44L109 55L132 29L156 41L179 21L204 31" fill="none" stroke="#355a46" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>`,
      'bollinger': `${base}<path d="M12 50C35 12 56 14 78 28S119 70 145 40S181 16 208 23" fill="none" stroke="#c96f50" stroke-width="1.8"/><path d="M12 26C35 2 56 4 78 11S119 34 145 17S181 5 208 7" fill="none" stroke="#728f70" stroke-width="1.7"/><path d="M12 75C35 58 56 60 78 69S119 89 145 73S181 59 208 65" fill="none" stroke="#728f70" stroke-width="1.7"/>`,
      'candlesticks': `${base}<g stroke-width="1.8" stroke-linecap="round"><path d="M36 19V74M64 31V82M92 14V53M120 24V69M148 13V62M176 20V48" stroke="#355a46"/><rect x="30" y="34" width="12" height="22" rx="1" fill="#658568"/><rect x="58" y="46" width="12" height="20" rx="1" fill="#c96f50"/><rect x="86" y="20" width="12" height="23" rx="1" fill="#658568"/><rect x="114" y="39" width="12" height="18" rx="1" fill="#c96f50"/><rect x="142" y="24" width="12" height="26" rx="1" fill="#658568"/><rect x="170" y="28" width="12" height="13" rx="1" fill="#c96f50"/></g>`,
      'risk': `${base}<rect x="20" y="18" width="180" height="23" rx="3" fill="#a9c4a4" opacity=".64"/><rect x="20" y="41" width="180" height="21" rx="3" fill="#d9bf7a" opacity=".56"/><rect x="20" y="62" width="180" height="23" rx="3" fill="#dba28d" opacity=".62"/><g fill="#355a46" font-family="system-ui,sans-serif" font-size="7" font-weight="750" letter-spacing=".8"><text x="26" y="32">TARGET</text><text x="26" y="55">ENTRY</text><text x="26" y="77">INVALIDATION</text></g>`,
      'moving-averages': `${base}<path d="M12 73C34 71 40 52 61 53S94 62 115 43S150 34 174 26S196 33 208 19" fill="none" stroke="#c96f50" stroke-width="2"/><path d="M12 83C38 81 54 70 76 68S111 59 135 49S178 42 208 35" fill="none" stroke="#d0ad51" stroke-width="2"/>`,
      'options': `${base}<path d="M16 84Q42 83 61 75T104 51T148 28T205 12" fill="none" stroke="#355a46" stroke-width="2.2"/><path d="M16 84Q45 84 70 79T118 73T161 74T205 77" fill="none" stroke="#c96f50" stroke-width="2.2"/><path d="M16 84Q42 83 61 75T104 51T148 28T205 12V87H16Z" fill="#a8bea0" opacity=".15"/>`,
      'structure': `${base}<path d="M13 77L38 61L60 69L82 42L104 52L128 28L149 43L172 23L205 35" fill="none" stroke="#355a46" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><g fill="#f6e9c7" stroke="#c96f50" stroke-width="1.5"><circle cx="38" cy="61" r="3.5"/><circle cx="82" cy="42" r="3.5"/><circle cx="128" cy="28" r="3.5"/><circle cx="172" cy="23" r="3.5"/></g>`,
      'adx': `${base}<path d="M12 83C35 78 50 59 74 65S111 41 135 50S172 24 208 26" fill="none" stroke="#355a46" stroke-width="2.1"/><path d="M12 66C36 65 47 75 74 69S113 61 135 63S173 56 208 54" fill="none" stroke="#c96f50" stroke-width="1.6"/><path d="M12 51C35 41 48 50 72 43S110 54 136 35S174 41 208 31" fill="none" stroke="#d0ad51" stroke-width="1.6"/>`,
    };
    return `<svg viewBox="0 0 220 100" aria-hidden="true" focusable="false">${drawings[type] || drawings['support-resistance']}</svg>`;
  };

  const programmeArt = kind => {
    if (kind === 'process') {
      return `<svg class="cc-programme-art" viewBox="0 0 175 95" aria-hidden="true"><rect x="3" y="7" width="169" height="81" rx="8" fill="#1f3b2c" stroke="#789176"/><g stroke="#52735b" stroke-dasharray="3 5"><path d="M14 25H161M14 46H161M14 67H161"/></g><path d="M14 71L34 57L52 64L73 38L92 49L112 26L132 38L159 15" fill="none" stroke="#f0d38a" stroke-width="2.5" stroke-linecap="round"/><path d="M14 71L34 57L52 64L73 38L92 49L112 26L132 38L159 15V79H14Z" fill="#f0d38a" opacity=".08"/><path d="M14 77H161" stroke="#c96f50" stroke-width="1.5" stroke-dasharray="4 3"/><circle cx="112" cy="26" r="4" fill="#f0d38a"/></svg>`;
    }
    return `<svg class="cc-programme-art" viewBox="0 0 175 95" aria-hidden="true"><rect x="3" y="7" width="169" height="81" rx="8" fill="#f6f1e3" stroke="#d7ddcb"/><g stroke="#d3d8c9" stroke-dasharray="3 4"><path d="M13 27H162M13 47H162M13 67H162"/></g><rect x="13" y="58" width="148" height="14" rx="2" fill="#c3d3b8" opacity=".7"/><path d="M13 66L32 58L47 63L64 42L81 51L98 32L116 44L136 20L160 29" fill="none" stroke="#355a46" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/><g stroke="#355a46" stroke-width="1.4"><path d="M31 51V70M48 53V72M65 35V57M82 45V65M99 25V44M116 37V57M137 13V34M154 18V38"/></g><g fill="#c96f50"><rect x="27" y="56" width="8" height="9" rx="1"/><rect x="44" y="57" width="8" height="9" rx="1"/><rect x="61" y="42" width="8" height="10" rx="1"/><rect x="78" y="48" width="8" height="10" rx="1"/><rect x="95" y="29" width="8" height="10" rx="1"/><rect x="112" y="41" width="8" height="10" rx="1"/><rect x="133" y="17" width="8" height="10" rx="1"/><rect x="150" y="24" width="8" height="9" rx="1"/></g></svg>`;
  };

  const renderEditorialProgramme = (course, variant) => {
    const isConstruct = variant === 'construct';
    const outcomes = (course.outcomes || []).slice(0, isConstruct ? 3 : 3).map((item, index) => '<li><span>0' + (index + 1) + '</span>' + escapeHTML(item) + '</li>').join('');
    const factSource = isConstruct ? (course.facts || []) : (course.facts || []).filter(fact => !/connected stages|guided sequence/i.test(fact));
    const facts = factSource.map(fact => '<span>' + escapeHTML(fact) + '</span>').join('');
    const price = '<div class="ed-offer-price"><strong>' + escapeHTML(course.price) + '</strong><span>' + escapeHTML(course.priceNote) + '</span></div>';
    const action = '<a class="ed-action ' + (isConstruct ? 'ed-action-gold' : 'ed-action-primary') + '" href="' + escapeHTML(course.href) + '">' + escapeHTML(course.cta) + ' <span aria-hidden="true">↗</span></a>';
    if (!isConstruct) {
      return '<div class="ed-offer-inner ed-offer-inner--path">' +
        '<div class="ed-primary-main"><div class="ed-offer-topline"><span>Flagship programme · start here</span><span class="ed-offer-number">01 / FOUNDATIONS</span></div>' +
        '<h2 class="ed-offer-title">' + escapeHTML(course.title) + '</h2>' +
        '<p class="ed-offer-promise">' + escapeHTML(course.promise) + '</p>' +
        '<p class="ed-offer-description">' + escapeHTML(course.description) + '</p>' +
        '<div class="ed-offer-facts">' + facts + '</div>' +
        '<ul class="ed-offer-outcomes">' + outcomes + '</ul>' +
        '<div class="ed-offer-bottom">' + price + action + '</div></div>' +
        '<aside class="offer-side"><div><span class="eyebrow">The foundation</span><p class="ed-side-route">Market language <i>→</i> chart reading <i>→</i> risk <i>→</i> planning <i>→</i> review</p></div><div class="ed-side-note">Four connected stages<br>30-day guided sequence</div></aside>' +
      '</div>';
    }
    return '<div class="ed-offer-inner ed-offer-inner--construct">' +
      '<div class="ed-offer-topline"><span>Flagship programme · guided process</span><span class="ed-offer-number">02 / CONSTRUCT</span></div>' +
      '<h2 class="ed-offer-title">CONSTRUCT</h2><p class="ed-offer-subtitle">' + escapeHTML(course.subtitle || 'Trade Construction & Management') + '</p>' +
      '<p class="ed-offer-promise">' + escapeHTML(course.promise) + '</p>' +
      '<p class="ed-offer-description">' + escapeHTML(course.description) + '</p>' +
      '<div class="ed-offer-facts">' + facts + '</div>' +
      '<ul class="ed-offer-outcomes">' + outcomes + '</ul>' +
      '<div class="ed-offer-bottom">' + price + action + '</div>' +
      '<p class="ed-offer-note">' + escapeHTML(course.community) + '</p>' +
    '</div>';
  };
  const microGrid = $('#cc-micro-grid');
  const developmentRail = $('#cc-development-rail');
  const orderedProgrammes = data.programmes.filter(isCatalogueVisible).sort((a, b) => a.priority - b.priority || (a.order ?? 0) - (b.order ?? 0));
  const primaryProgramme = orderedProgrammes.find(course => course.id === 'trading-path');
  const secondaryProgramme = orderedProgrammes.find(course => course.id === 'construct');
  const primaryHost = $('#ed-trading-path');
  const secondaryHost = $('[data-offer="construct"]');
  if (primaryHost && primaryProgramme) primaryHost.innerHTML = renderEditorialProgramme(primaryProgramme, 'path');
  if (secondaryHost && secondaryProgramme) secondaryHost.innerHTML = renderEditorialProgramme(secondaryProgramme, 'construct');

  const supportingProgrammes = [...(data.supportingProgrammes || [])].filter(isCatalogueVisible).sort((a, b) => a.priority - b.priority || (a.order ?? 0) - (b.order ?? 0));
  const supportHost = $('#cc-supporting-programme');
  if (supportHost && supportingProgrammes.length) {
    supportHost.innerHTML = supportingProgrammes.map(support => '<article class="ed-live-card" id="' + escapeHTML(support.id) + '">' +
      '<div class="ed-live-stamp">LIVE /<br>CLASSROOM</div>' +
      '<div class="ed-live-copy"><span class="eyebrow">A separate delivery format</span><h2>' + escapeHTML(support.title) + '</h2><p>' + escapeHTML(support.description) + '</p><div class="ed-live-facts">' + support.facts.map(fact => '<span>' + escapeHTML(fact) + '</span>').join('') + '</div></div>' +
      '<a class="ed-action ed-action-outline" href="' + escapeHTML(support.href) + '">' + escapeHTML(support.cta) + ' <span aria-hidden="true">↗</span></a></article>').join('');
  }

  const modal = $('#cc-course-modal');
  const modalDialog = $('.cc-modal-dialog', modal);
  const modalScroll = $('#cc-modal-scroll');
  const modalFooter = $('#cc-modal-footer');
  const toast = $('#cc-toast');
  const searchInput = $('#cc-course-search');
  const filterHost = $('#cc-course-filters');
  const countLabel = $('#cc-result-count');
  const noResults = $('#cc-no-results');
  let activeFilter = 'all';
  let activeCourse = null;
  let lastFocus = null;
  let toastTimer = null;

  let microCourses = data.microCourses.filter(isCatalogueVisible).sort((a, b) => a.priority - b.priority || (a.order ?? 0) - (b.order ?? 0));

  function renderMicroCard(course, index) {
    const hook = course.hook || course.description || '';
    const problem = course.problem || '';
    const learningFocus = course.learningFocus || course.outcome || '';
    const whyThisOne = course.whyThisOne || '';
    const serial = String(index + 1).padStart(2, '0');
    const artLabels = {
      'support-resistance': 'MARK THE ZONE',
      'bollinger-bands': 'READ VOLATILITY',
      'candlestick-patterns': 'READ THE CANDLE',
      'risk-management-basics': 'DEFINE INVALIDATION',
      'moving-averages': 'READ THE TREND',
      'options-basics': 'UNDERSTAND THE CONTRACT',
      'market-structure': 'FIND THE SWING',
      'understanding-adx': 'MEASURE STRENGTH'
    };
    const artLabel = artLabels[course.id] || 'CHART STUDY';
    const status = course.status === 'coming-soon' ? '<span class="ed-course-status">Coming soon</span>' : '';
    return '<article class="ed-micro-tile" data-course-id="' + escapeHTML(course.id) + '">' +
      '<div class="ed-tile-art"><span class="ed-tile-serial">FIELD STUDY <i>/</i> ' + serial + '</span>' + chartArt(course.art) + '<span class="ed-tile-art-caption">' + escapeHTML(artLabel) + '</span></div>' +
      '<div class="ed-tile-body"><div class="ed-tile-meta"><span>' + escapeHTML(course.category || 'Focused study') + '</span><span>' + escapeHTML(course.level || 'Self-paced') + '</span></div>' +
      '<h3 class="ed-tile-title">' + escapeHTML(course.title) + '</h3>' + status +
      '<div class="ed-tile-problem-label">The trader’s question</div><p class="ed-tile-hook cc-card-hook">' + escapeHTML(hook) + '</p>' +
      (problem ? '<p class="ed-tile-problem">' + escapeHTML(problem) + '</p>' : '') +
      '<div class="ed-tile-focus"><span>What you will work on</span><p>' + escapeHTML(learningFocus) + '</p></div>' +
      (whyThisOne ? '<p class="ed-tile-why"><b>Why this one</b><span>' + escapeHTML(whyThisOne) + '</span></p>' : '') +
      '<div class="ed-tile-footer"><div class="ed-tile-price"><strong>' + escapeHTML(course.price || '') + '</strong></div><button class="ed-tile-action" type="button" data-open-course="' + escapeHTML(course.id) + '">See what is inside <i aria-hidden="true">↗</i></button></div></div></article>';
  }
  function renderFilterButtons() {
    if (!filterHost) return;
    const availableCourses = microCourses.filter(course => course.status !== 'in-development');
    const categories = [...new Set(availableCourses.map(course => course.category).filter(Boolean))]
      .sort((a, b) => a.localeCompare(b));
    const categoryButtons = categories.map(category => {
      const count = availableCourses.filter(course => course.category === category).length;
      return `<button type="button" data-filter="${escapeHTML(category)}" aria-pressed="false">${escapeHTML(category)} <span data-filter-count="true">${count}</span></button>`;
    }).join('');
    filterHost.innerHTML = `<button type="button" class="is-active" data-filter="all" aria-pressed="true">All topics <span data-count="all">${availableCourses.length}</span></button>${categoryButtons}`;
  }

  function renderMicroCourses() {
    if (!microGrid) return;
    const query = (searchInput?.value || '').trim().toLocaleLowerCase();
    const publishedTiles = microCourses.filter(course => course.status !== 'in-development');
    const shown = publishedTiles.filter(course => {
      const categoryMatches = activeFilter === 'all' || course.category === activeFilter;
      const searchBlob = [course.title, course.category, course.level, course.status, course.description, course.outcome, course.complements, course.hook, course.problem, course.learningFocus, course.whyThisOne].join(' ').toLocaleLowerCase();
      return categoryMatches && (!query || searchBlob.includes(query));
    });
    microGrid.innerHTML = shown.map(renderMicroCard).join('');
    if (countLabel) countLabel.textContent = shown.length + ' focused course' + (shown.length === 1 ? '' : 's');
    if (noResults) noResults.hidden = shown.length !== 0;
    microGrid.hidden = shown.length === 0;
    if (filterHost) {
      $$('.cc-filter-list button', filterHost).forEach(button => {
        const key = button.dataset.filter;
        const filteredCount = key === 'all' ? publishedTiles.length : publishedTiles.filter(course => course.category === key).length;
        let badge = $('[data-filter-count]', button);
        if (key === 'all') { const allCount = $('[data-count="all"]', button); if (allCount) allCount.textContent = String(filteredCount); }
        else if (filteredCount > 0) { if (!badge) { badge = document.createElement('span'); badge.dataset.filterCount = 'true'; button.appendChild(badge); } badge.textContent = String(filteredCount); }
        else if (badge) badge.remove();
        button.classList.toggle('is-active', key === activeFilter);
        button.setAttribute('aria-pressed', String(key === activeFilter));
      });
    }
    if (developmentRail) {
      const inDevelopment = microCourses.filter(course => course.status === 'in-development');
      developmentRail.hidden = inDevelopment.length === 0;
      developmentRail.innerHTML = inDevelopment.map(course => '<div class="ed-development-inner"><div><span class="eyebrow">In development · no enrolment yet</span><h3>' + escapeHTML(course.title) + '</h3><p>' + escapeHTML(course.description) + '</p></div><button type="button" class="ed-development-action" data-open-development-course="' + escapeHTML(course.id) + '">Preview course outline <span aria-hidden="true">↗</span></button></div>').join('');
    }
  }
  function cataloguePresentationModalMarkup(course) {
    const tags = Array.isArray(course.tags) ? course.tags.filter(tag => String(tag || '').trim()) : [];
    if (!(course.problem || course.hook || course.learningFocus || course.whyThisOne || tags.length)) return '';
    let html = '<section class="cc-modal-presentation"><span class="cc-modal-presentation-label">THE PROBLEM IT HELPS WITH</span>';
    if (course.hook) html += '<h3>' + escapeHTML(course.hook) + '</h3>';
    if (course.problem) html += '<p class="cc-modal-presentation-problem">' + escapeHTML(course.problem) + '</p>';
    if (course.learningFocus) html += '<p class="cc-modal-presentation-focus"><b>Learning focus:</b> ' + escapeHTML(course.learningFocus) + '</p>';
    if (tags.length) html += '<div class="cc-card-tags">' + tags.map(tag => '<span class="cc-card-tag">' + escapeHTML(tag) + '</span>').join('') + '</div>';
    if (course.whyThisOne) html += '<p class="cc-modal-presentation-why"><b>Why this one:</b> ' + escapeHTML(course.whyThisOne) + '</p>';
    return html + '</section>';
  }

  function renderModal(course) {
    const lessonCount = course.modules.reduce((sum, item) => sum + (parseInt(item.count, 10) || 0), 0);
    modalScroll.innerHTML = `<div class="cc-modal-top">
      <div><div class="cc-modal-kicker">Micro-course · ${escapeHTML(course.category)}</div><h2 id="cc-modal-title">${escapeHTML(course.title)}</h2><p id="cc-modal-description" class="cc-modal-deck">${escapeHTML(course.description)}</p><div class="cc-modal-facts"><span>Focused topic</span><span>${course.modules.length} sections</span>${course.status === 'coming-soon' ? '<span>Full outline to be announced</span>' : `<span>Approx. ${lessonCount} short lessons</span>`}${course.status === 'coming-soon' ? '<span>Coming soon · no enrolment yet</span>' : (course.status === 'in-development' ? '<span>Course in development</span>' : '')} </div></div>
      <div class="cc-modal-art">${chartArt(course.art)}</div>
    </div>
    <div class="cc-modal-outcome"><span aria-hidden="true">✳</span><span><b>What you'll take away</b><br>${escapeHTML(course.outcome)}</span></div>
    ${cataloguePresentationModalMarkup(course)}
    <div class="cc-outline-header"><h3>Inside the course</h3><span>Open a section to preview it</span></div>
    <div class="cc-outline" id="cc-outline">${course.modules.map((module, index) => `<section class="cc-outline-item ${index === 0 ? 'is-open' : ''}"><button class="cc-outline-toggle" type="button" aria-expanded="${index === 0 ? 'true' : 'false'}" aria-controls="cc-outline-preview-${escapeHTML(course.id)}-${index}"><span class="cc-outline-num">${String(index + 1).padStart(2, '0')}</span><span class="cc-outline-title">${escapeHTML(module.title)}</span><span class="cc-outline-count">${escapeHTML(module.count)}</span><span class="cc-outline-sign" aria-hidden="true">+</span></button><div class="cc-outline-preview" id="cc-outline-preview-${escapeHTML(course.id)}-${index}" ${index === 0 ? '' : 'hidden'}><p>${escapeHTML(module.preview)}</p><ul>${module.points.map(point => `<li>${escapeHTML(point)}</li>`).join('')}</ul></div></section>`).join('')}</div>
    <p class="cc-modal-fit"><b>Where it fits:</b> ${escapeHTML(course.complements)} This is designed as a standalone micro-course; community access is not included.</p>`;
    modalFooter.innerHTML = `<div class="cc-modal-price-wrap"><span class="cc-modal-price">${escapeHTML(course.price)}</span><span class="cc-modal-price-note">${course.status === 'coming-soon' ? 'No enrolment yet · launch details to follow' : (course.status === 'in-development' ? 'Development outline only · no enrolment yet' : 'Indicative price · preview only')}</span></div>${course.status === 'coming-soon' ? '<button class="button cc-modal-cta" type="button" disabled aria-disabled="true">Coming soon</button>' : (course.status === 'in-development' ? '<button class="button cc-modal-cta" type="button" disabled aria-disabled="true">Course in development</button>' : `<button class="button cc-modal-cta" type="button" data-get-course="${escapeHTML(course.id)}">Preview only <span aria-hidden="true">↗</span></button>`)}`;
  }

  function openModal(course, opener) {
    activeCourse = course;
    lastFocus = opener || document.activeElement;
    renderModal(course);
    modal.hidden = false;
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('cc-no-scroll');
    modalScroll.scrollTop = 0;
    $('.cc-modal-close', modal).focus();
  }

  function closeModal() {
    if (!modal || modal.hidden) return;
    modal.hidden = true;
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('cc-no-scroll');
    activeCourse = null;
    if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus();
  }

  function showToast(message) {
    if (!toast) return;
    toast.textContent = message;
    toast.hidden = false;
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(() => { toast.hidden = true; }, 4800);
  }

  renderFilterButtons();
  if (microGrid) renderMicroCourses();
  // Published Academy courses are fetched from Django; curated static content remains unchanged.
  const baseRenderModal = renderModal;
  renderModal = function(course) {
    baseRenderModal(course);
    if (course && course.academyUrl) {
      const link = document.createElement('a');
      link.className = 'button cc-modal-cta';
      link.href = course.academyUrl;
      link.textContent = 'Open in Academy ↗';
      modalFooter.replaceChildren(link);
      const note = document.createElement('span');
      note.className = 'cc-modal-price-note';
      note.textContent = 'Published in the Academy · access and pricing configured separately';
      modalFooter.prepend(note);
    }
  };
  fetch("https://tradethesis-academy-staging.onrender.com/api/academy/catalogue/", {headers: {"Accept":"application/json"}})
    .then(response => { if (!response.ok) throw new Error("Academy catalogue unavailable"); return response.json(); })
    .then(payload => {
      const academyEntries = (payload.courses || []).filter(course => course && (
        (course.status === "published" && course.academyUrl) || course.status === "coming-soon"
      ));
      let catalogueChanged = false;
      for (const incoming of academyEntries) {
        const existing = microCourses.find(course =>
          String(course.id) === String(incoming.id) ||
          (incoming.slug && (String(course.slug || "") === String(incoming.slug) || String(course.id) === String(incoming.slug)))
        );
        const normalized = {
          ...incoming, priority: 3, order: 1000 + microCourses.length,
          category: incoming.category || "TradeThesis courses", level: incoming.level || "Self-paced",
          art: incoming.art || "structure", modules: Array.isArray(incoming.modules) ? incoming.modules : [],
          tags: Array.isArray(incoming.tags) ? incoming.tags : [],
          outcome: incoming.outcome || incoming.description || "",
          complements: incoming.complements || (incoming.status === "coming-soon"
            ? "This course is being prepared. Full details will be shared closer to launch."
            : "Explore this published course in the TradeThesis Academy."),
          price: incoming.price || ""
        };
        if (existing) {
          existing.slug = existing.slug || normalized.slug;
          existing.academyUrl = normalized.academyUrl || existing.academyUrl;
          if (normalized.modules.length) existing.modules = normalized.modules;
          if (!existing.outcome && normalized.outcome) existing.outcome = normalized.outcome;
          if (!existing.complements && normalized.complements) existing.complements = normalized.complements;
          if (normalized.price && (!existing.price || existing.price === "Coming soon")) existing.price = normalized.price;
          if (normalized.cataloguePresentationConfigured) {
            existing.hook = normalized.hook; existing.problem = normalized.problem;
            existing.learningFocus = normalized.learningFocus; existing.tags = normalized.tags;
            existing.whyThisOne = normalized.whyThisOne;
          } else {
            for (const key of ["hook", "problem", "learningFocus", "whyThisOne"]) if (!existing[key] && normalized[key]) existing[key] = normalized[key];
            if ((!Array.isArray(existing.tags) || !existing.tags.length) && normalized.tags.length) existing.tags = normalized.tags;
          }
          catalogueChanged = true;
        } else {
          microCourses.push(normalized); catalogueChanged = true;
        }
      }
      if (catalogueChanged) { renderFilterButtons(); renderMicroCourses(); }
    })
    .catch(() => {
      // The curated catalogue remains usable if Academy is temporarily unavailable.
    });

  microGrid?.addEventListener('click', event => {
    const opener = event.target.closest('[data-open-course]');
    if (!opener) return;
    const course = microCourses.find(item => item.id === opener.dataset.openCourse);
    if (course) openModal(course, opener);
  });

  developmentRail?.addEventListener('click', event => {
    const opener = event.target.closest('[data-open-development-course]');
    if (!opener) return;
    const course = microCourses.find(item => item.id === opener.dataset.openDevelopmentCourse);
    if (course) openModal(course, opener);
  });

  filterHost?.addEventListener('click', event => {
    const button = event.target.closest('[data-filter]');
    if (!button) return;
    activeFilter = button.dataset.filter;
    renderMicroCourses();
  });

  searchInput?.addEventListener('input', renderMicroCourses);
  $('.cc-clear-search')?.addEventListener('click', () => {
    if (searchInput) { searchInput.value = ''; searchInput.focus(); }
    activeFilter = 'all';
    renderMicroCourses();
  });

  modal?.addEventListener('click', event => {
    const dismiss = event.target.closest('[data-modal-dismiss]');
    if (dismiss) { closeModal(); return; }
    const outlineToggle = event.target.closest('.cc-outline-toggle');
    if (outlineToggle) {
      const item = outlineToggle.closest('.cc-outline-item');
      const wasOpen = item.classList.contains('is-open');
      $$('.cc-outline-item', modal).forEach(section => {
        section.classList.remove('is-open');
        const button = $('.cc-outline-toggle', section);
        const panel = $('.cc-outline-preview', section);
        button.setAttribute('aria-expanded', 'false');
        panel.hidden = true;
      });
      if (!wasOpen) {
        item.classList.add('is-open');
        outlineToggle.setAttribute('aria-expanded', 'true');
        $('.cc-outline-preview', item).hidden = false;
      }
      return;
    }
    const buyButton = event.target.closest('[data-get-course]');
    if (buyButton && activeCourse) {
      showToast(`Preview only: ${activeCourse.title} is not connected to checkout yet. The final course data and payment flow can be connected without changing this reusable layout.`);
    }
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && modal && !modal.hidden) closeModal();
    if (event.key === 'Tab' && modal && !modal.hidden) {
      const focusables = $$('button:not([disabled]), a[href], input:not([disabled]), [tabindex]:not([tabindex="-1"])', modalDialog).filter(el => el.offsetParent !== null);
      if (!focusables.length) return;
      const first = focusables[0];
      const last = focusables[focusables.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
})();