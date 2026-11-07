/* TradeThesis Courses — exact approved catalogue layout, wired to the curated catalogue and Academy API. */
(() => {
  'use strict';
  const source = window.TRADETHESIS_COURSE_DATA || {};
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => Array.from(root.querySelectorAll(selector));
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const normalise = value => String(value || '').trim().toLowerCase().replace(/[^a-z0-9]+/g, '');
  const visible = item => item && item.catalogueVisibility !== 'hidden';
  const academyBase = String(window.TRADETHESIS_ACADEMY_CONFIG?.baseUrl || '').trim().replace(/\/+$/, '');

  const asModule = module => typeof module === 'string'
    ? {title:module,count:'',preview:'',points:[]}
    : {title:module?.title || 'Course section',count:module?.count || '',preview:module?.preview || '',points:Array.isArray(module?.points) ? module.points : []};
  const normaliseCourse = course => ({
    ...course,
    focus:course.learningFocus || course.focus || '',
    why:course.whyThisOne || course.why || '',
    modules:(Array.isArray(course.modules) ? course.modules : []).map(asModule),
    status:course.status || 'curated'
  });

  let programmes = (source.programmes || []).filter(visible).slice().sort((a,b)=>(a.order||0)-(b.order||0));
  let supporting = (source.supportingProgrammes || []).filter(visible).slice();
  let dynamicFlagships = [];
  let dynamicSupporting = [];
  let courses = (source.microCourses || []).filter(visible).map(normaliseCourse).sort((a,b)=>(a.order||0)-(b.order||0));
  let activeFilter = 'All topics';
  let activeCourse = null;
  let activeShareCourse = null;
  let lastCourseTrigger = null;
  let lastShareTrigger = null;

  const flagshipGrid = $('#flagshipGrid');
  const liveHost = $('#liveClassroomLine');
  const developmentRail = $('#developmentRail');
  const grid = $('#courseGrid');
  const searchInput = $('#courseSearch');
  const filtersHost = $('#courseFilters');
  const resultCount = $('#courseResultCount');
  const emptyState = $('#courseEmpty');
  const modalBackdrop = $('#courseModal');
  const shareBackdrop = $('#shareBackdrop');

  function flagshipFacts(course) {
    if (course.id === 'trading-path') return [['30','Written lessons'],['4','Connected stages'],['30 days','Guided sequence']];
    if (course.id === 'construct') return [['70 days','Guided programme'],['43','Core lessons'],['10','Assignments'],['8','Review Clinics']];
    return (course.facts || []).slice(0,4).map(fact => {
      const match = String(fact).match(/^(\S+)\s+(.*)$/);
      return match ? [match[1],match[2]] : [fact,''];
    });
  }
  function reflectionNote() {
    return '<aside class="construct-reflection" aria-label="A thought worth keeping">' +
      '<p class="construct-reflection-kicker">A thought worth keeping</p>' +
      '<h4>Before the<br><em>chart answered.</em></h4>' +
      '<div class="construct-reflection-quote"><p class="construct-reflection-question">What did you believe then?</p>' +
      '<p class="construct-reflection-reminder">Don\'t let the ending answer for you.</p></div></aside>';
  }
  function renderFlagshipCard(course,index) {
    const isConstruct = course.id === 'construct' || /construct/i.test(course.title || '');
    const isDark = isConstruct || (course.price && course.price !== 'Free');
    const isPath = course.id === 'trading-path';
    const heading = isPath ? 'The TradeThesis<br>Trading Path' : esc(course.title || '');
    const badge = isConstruct ? 'Guided flagship · ' + esc(course.price || '₹17,000')
      : (course.price === 'Free' || course.isFree ? 'Free · Permanent access' :
        (course.price ? 'Flagship · ' + esc(course.price) : 'Full course'));
    const facts = flagshipFacts(course).map(item =>
      '<div><strong>' + esc(item[0]) + '</strong><span>' + esc(item[1]) + '</span></div>'
    ).join('');
    const href = isConstruct ? 'construct.html' : (isPath ? 'trading-path.html' : (course.href || course.academyUrl || '#'));
    const className = 'flagship-card ' + (isDark ? 'flagship-card--construct' : 'flagship-card--path');
    const serialText = isConstruct ? 'APPLICATION' : (isPath ? 'FOUNDATIONS' : 'FULL PROGRAMME');
    const serial = String(index+1).padStart(2,'0') + ' <i>/</i> ' + serialText;
    const kicker = course.kicker || (isConstruct ? 'THE GUIDED FLAGSHIP PROGRAMME' : (isPath ? 'THE BEGINNER PROGRAMME' : 'TRADETHESIS FLAGSHIP PROGRAMME'));
    const subtitle = (isConstruct || course.subtitle)
      ? '<p class="flagship-subtitle">' + esc(course.subtitle || 'Trade Construction &amp; Management') + '</p>' : '';
    const reflection = isConstruct ? reflectionNote() : '';
    const footer = isConstruct ? 'Guided practice · 12-month community access'
      : (isPath ? 'Complete self-paced course' : (course.community || 'Complete flagship programme'));
    const cta = isConstruct ? 'Explore CONSTRUCT' : (isPath ? 'Explore Trading Path' : (course.cta || 'Explore course'));
    const aria = isConstruct ? 'Explore CONSTRUCT, the guided flagship course, priced at 17,000 rupees'
      : (isPath ? 'Explore The TradeThesis Trading Path, free full course' : 'Explore ' + (course.title || 'TradeThesis flagship course'));
    return '<a class="' + className + '" href="' + esc(href) + '" aria-label="' + esc(aria) + '">' +
      '<div class="flagship-card-top"><span class="flagship-serial">' + serial + '</span><span class="flagship-badge">' + badge + '</span></div>' +
      '<div class="flagship-card-main"><p class="flagship-card-kicker">' + esc(kicker) + '</p><h3>' + heading + '</h3>' + subtitle +
      '<p class="flagship-promise">' + esc(course.promise || course.hook || '') + '</p><p class="flagship-description">' + esc(course.description || '') + '</p>' + reflection + '</div>' +
      '<div class="flagship-facts ' + (isPath ? 'flagship-facts--three' : '') + '" aria-label="Course format">' + facts + '</div>' +
      '<div class="flagship-card-footer"><span>' + esc(footer) + '</span><strong>' + esc(cta) + ' <i aria-hidden="true">↗</i></strong></div></a>';
  }
  function renderFlagships() {
    if (!flagshipGrid) return;
    const entries = [...programmes,...dynamicFlagships].sort((a,b) =>
      (a.catalogueOrder ?? a.order ?? 0) - (b.catalogueOrder ?? b.order ?? 0));
    flagshipGrid.innerHTML = entries.map(renderFlagshipCard).join('');
    const count = $('.flagship-count strong');
    if (count) count.textContent = String(entries.length).padStart(2,'0');
    const countLabel = $('.flagship-count');
    if (countLabel) countLabel.setAttribute('aria-label',entries.length + ' flagship courses');
  }
  function renderLiveClassroom() {
    if (!liveHost) return;
    const entries = [...supporting,...dynamicSupporting].sort((a,b) =>
      (a.catalogueOrder ?? a.order ?? 0) - (b.catalogueOrder ?? b.order ?? 0));
    liveHost.hidden = !entries.length;
    liveHost.innerHTML = entries.map(course => {
      const isLiveClassroom = course.id === 'live-classroom';
      const title = isLiveClassroom ? 'Trade Construction &amp; Management — Live Classroom' : esc(course.title || 'Supporting programme');
      const description = isLiveClassroom
        ? 'Six live weekend sessions, guided worksheets and checkpoints that lead towards a written personal playbook.'
        : esc(course.description || '');
      const href = course.href || course.academyUrl || 'live-class.html';
      const cta = isLiveClassroom ? 'Explore the live programme' : (course.cta || 'Explore programme');
      return '<div class="live-classroom-line"><div class="live-classroom-copy">' +
        '<p class="live-classroom-kicker">LIVE CLASSROOM</p><h3>' + title + '</h3><p>' + description +
        '</p></div><a href="' + esc(href) + '">' + esc(cta) + ' <span aria-hidden="true">↗</span></a></div>';
    }).join('');
  }
  function renderDevelopmentRail() {
    if (!developmentRail) return;
    const items = courses.filter(item => item && item.status === 'in-development');
    developmentRail.hidden = !items.length;
    developmentRail.innerHTML = items.map(item =>
      '<div><span class="development-label">In development</span><h3>' + esc(item.title) + '</h3><p>' +
      esc(item.description || item.learningFocus || '') + '</p></div><span class="development-status">Coming soon</span>'
    ).join('');
  }

  function sharePageUrl() {
    const url = new URL(window.location.href);
    url.hash = 'courses';
    return url.href;
  }
  function shareUrlFor(course) { return course.shareUrl || sharePageUrl(); }
  function shareMessageFor(course) {
    return course.shareMessage || 'I came across this TradeThesis course and thought it might be useful for anyone looking to develop a more structured approach to trading.\n\nExplore ' +
      course.title + ' and learn at your own pace.\n\nTradeThesis — Conviction before Execution.';
  }
  function renderShareButton(course) {
    return '<button type="button" class="share-trigger" data-share-course="' + esc(course.id) +
      '" aria-label="Share ' + esc(course.title) + '">Share ↗</button>';
  }
  function renderFilters() {
    if (!filtersHost) return;
    const allowed = courses.filter(course => course.status !== 'in-development' && course.catalogueVisibility !== 'hidden');
    const categories = [...new Set(allowed.map(course => course.category).filter(Boolean))].sort((a,b)=>a.localeCompare(b));
    filtersHost.innerHTML = '<button type="button" data-filter="All topics" aria-pressed="true">All topics <span>' + allowed.length + '</span></button>' +
      categories.map(category => '<button type="button" data-filter="' + esc(category) + '" aria-pressed="false">' + esc(category) +
        ' <span>' + allowed.filter(course => course.category === category).length + '</span></button>').join('');
    if (!categories.includes(activeFilter)) activeFilter = 'All topics';
    $$('[data-filter]',filtersHost).forEach(button => {
      button.classList.toggle('is-active',button.dataset.filter===activeFilter);
      button.setAttribute('aria-pressed',String(button.dataset.filter===activeFilter));
    });
  }
  function renderCourses() {
    if (!grid) return;
    const query = String(searchInput?.value || '').trim().toLocaleLowerCase();
    const published = courses.filter(course => course.status !== 'in-development' && course.catalogueVisibility !== 'hidden');
    const shown = published.filter(course => {
      const categoryMatches = activeFilter === 'All topics' || course.category === activeFilter;
      const blob = [course.title,course.category,course.level,course.hook,course.problem,course.focus,course.description,course.outcome,course.why,course.complements].join(' ').toLocaleLowerCase();
      return categoryMatches && (!query || blob.includes(query));
    });
    grid.innerHTML = shown.map(course => {
      const topic = [course.category,course.level].filter(Boolean).join(' · ');
      return '<article class="course-tile" id="course-' + esc(course.id) + '" data-course-card="' + esc(course.id) +
        '" tabindex="0" aria-label="Open course details for ' + esc(course.title) + '. You can also share this course.">' +
        '<div class="tile-top"><span class="tile-topic">' + esc(topic) + '</span><span class="price-chip">' + esc(course.price || 'Details soon') + '</span></div>' +
        '<h3>' + esc(course.title) + '</h3><p class="course-hook">' + esc(course.hook || course.description || '') + '</p>' +
        '<div class="tile-bottom"><span>Course details</span><div class="tile-actions"><button type="button" data-open-course="' + esc(course.id) +
        '"><strong>Explore ↗</strong></button>' + renderShareButton(course) + '</div></div></article>';
    }).join('');
    if (resultCount) resultCount.textContent = shown.length + ' focused course' + (shown.length===1?'':'s');
    if (emptyState) emptyState.hidden = shown.length !== 0;
    grid.hidden = shown.length === 0;
    $$('[data-filter]',filtersHost).forEach(button => {
      const active = button.dataset.filter === activeFilter;
      button.classList.toggle('is-active',active);
      button.setAttribute('aria-pressed',String(active));
    });
  }
  function openCourse(id, trigger) {
    const course = courses.find(item => String(item.id) === String(id));
    if (!course || !modalBackdrop) return;
    activeCourse = course;
    lastCourseTrigger = trigger || document.activeElement;
    $('#modalTopic').textContent = [course.category,course.level].filter(Boolean).join(' · ') || 'Focused course';
    $('#modalTitle').textContent = course.title || 'Course title';
    $('#modalHook').textContent = course.hook ? '“' + course.hook + '”' : '';
    $('#modalDescription').textContent = course.description || course.problem || '';
    $('#modalPrice').textContent = course.price || 'Details to follow';
    const outcomes = [course.outcome,course.focus,course.why].filter(value => String(value||'').trim());
    $('#modalOutcomes').innerHTML = outcomes.map(item => '<li>' + esc(item) + '</li>').join('');
    $('#modalOutline').innerHTML = (course.modules || []).map((module,index) =>
      '<li><strong>' + String(index+1).padStart(2,'0') + '</strong> &nbsp; ' + esc(module.title) +
      (module.count ? ' <span>· ' + esc(module.count) + '</span>' : '') + '</li>'
    ).join('');
    const enrol = $('#enrolButton');
    if (course.academyUrl && course.status !== 'coming-soon' && course.status !== 'in-development') {
      enrol.disabled = false;
      enrol.textContent = 'Open in Academy ↗';
      enrol.onclick = () => window.open(course.academyUrl,'_blank','noopener,noreferrer');
    } else {
      enrol.disabled = true;
      enrol.textContent = course.status === 'coming-soon' ? 'Coming soon' : 'Academy link not returned';
      enrol.onclick = null;
    }
    $('.modal-note').textContent = 'Course descriptions and outlines come from the TradeThesis catalogue. Published Academy links are supplied by the live catalogue when available.';
    modalBackdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
    $('.modal-close',modalBackdrop).focus();
  }
  function closeCourse() {
    if (!modalBackdrop?.classList.contains('open')) return;
    modalBackdrop.classList.remove('open');
    document.body.style.overflow = '';
    if (lastCourseTrigger?.isConnected) lastCourseTrigger.focus();
  }
  function openShare(id, trigger) {
    const course = courses.find(item => String(item.id) === String(id));
    if (!course || !shareBackdrop) return;
    activeShareCourse = course;
    lastShareTrigger = trigger || document.activeElement;
    const message = shareMessageFor(course);
    const url = shareUrlFor(course);
    const full = message + '\n\n' + url;
    $('#shareCourseTitle').textContent = course.shareTitle || course.title;
    $('#shareMessage').textContent = message;
    $('#shareUrl').textContent = url;
    $('#shareStatus').textContent = course.shareUrl ? '' : 'The individual course link is not available yet. This link opens the TradeThesis course catalogue.';
    const targets = [
      ['WhatsApp','wa','https://wa.me/?text=' + encodeURIComponent(full)],
      ['Telegram','tg','https://t.me/share/url?url=' + encodeURIComponent(url) + '&text=' + encodeURIComponent(message)],
      ['LinkedIn','in','https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(url)],
      ['Facebook','fb','https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(url)],
      ['X','xx','https://twitter.com/intent/tweet?text=' + encodeURIComponent(message) + '&url=' + encodeURIComponent(url)]
    ];
    const symbols = {wa:'W',tg:'➤',in:'in',fb:'f',xx:'𝕏'};
    const options = $('#shareOptions');
    options.innerHTML = targets.map(([label,kind,href]) =>
      '<a href="' + href + '" target="_blank" rel="noopener noreferrer"><span class="share-channel-icon ' + kind + '">' +
      symbols[kind] + '</span><span>' + label + '</span><span style="margin-left:auto;color:#9a9a8d">↗</span></a>'
    ).join('');
    if (typeof navigator.share === 'function') {
      const more = document.createElement('button');
      more.type = 'button';
      more.innerHTML = '<span class="share-channel-icon more">↗</span><span>More options</span>';
      more.addEventListener('click', async () => {
        try { await navigator.share({title:course.shareTitle || course.title,text:message,url:url}); }
        catch (error) { if (error?.name !== 'AbortError') $('#shareStatus').textContent = 'Your device could not open its share sheet. Choose an app above instead.'; }
      });
      options.append(more);
    }
    $('#shareCopy').textContent = 'Copy link';
    shareBackdrop.classList.add('open');
    document.body.style.overflow = 'hidden';
    $('#shareClose').focus();
  }
  function closeShare() {
    if (!shareBackdrop?.classList.contains('open')) return;
    shareBackdrop.classList.remove('open');
    document.body.style.overflow = '';
    if (lastShareTrigger?.isConnected) lastShareTrigger.focus();
  }
  async function copyShareLink() {
    const url = activeShareCourse ? shareUrlFor(activeShareCourse) : '';
    try {
      if (navigator.clipboard?.writeText) await navigator.clipboard.writeText(url);
      else {
        const area = document.createElement('textarea');
        area.value = url; area.style.position = 'fixed'; area.style.opacity = '0';
        document.body.append(area); area.select();
        const copied = document.execCommand('copy'); area.remove();
        if (!copied) throw new Error('Clipboard copy was blocked.');
      }
      $('#shareCopy').textContent = 'Copied ✓';
      $('#shareStatus').textContent = 'The course link is ready to pass along.';
    } catch (_error) {
      $('#shareStatus').textContent = 'Copy was blocked by your browser. You can select the link above.';
    }
  }

  function sameCourse(left,right) {
    const leftKeys = [left?.id,left?.slug,left?.academySlug,left?.title].filter(Boolean).map(normalise);
    const rightKeys = [right?.id,right?.slug,right?.title].filter(Boolean).map(normalise);
    return rightKeys.some(key => leftKeys.includes(key));
  }
  function syncAcademyCatalogue() {
    if (!academyBase) return;
    fetch(academyBase + '/api/academy/catalogue/',{headers:{Accept:'application/json'}})
      .then(response => { if (!response.ok) throw new Error('Academy catalogue unavailable'); return response.json(); })
      .then(payload => {
        let changed = false;
        (Array.isArray(payload.courses) ? payload.courses : []).forEach(incoming => {
          if (!incoming || !incoming.slug) return;
          const prior = [...programmes,...supporting,...courses,...dynamicFlagships,...dynamicSupporting]
            .find(item => sameCourse(item,incoming));
          const role = ['flagship','supporting','mini','hidden'].includes(incoming.catalogueRole)
            ? incoming.catalogueRole : 'mini';

          if (role === 'hidden' || incoming.status === 'hidden') {
            programmes = programmes.filter(item => !sameCourse(item,incoming));
            supporting = supporting.filter(item => !sameCourse(item,incoming));
            courses = courses.filter(item => !sameCourse(item,incoming));
            dynamicFlagships = dynamicFlagships.filter(item => !sameCourse(item,incoming));
            dynamicSupporting = dynamicSupporting.filter(item => !sameCourse(item,incoming));
            changed = true;
            return;
          }
          if (incoming.status !== 'published' && incoming.status !== 'coming-soon') return;

          const target = normaliseCourse({
            ...(prior || {}),
            ...incoming,
            id:(prior && prior.id) || incoming.slug,
            slug:incoming.slug,
            category:incoming.category || (prior && prior.category) || 'Focused study',
            level:incoming.level || (prior && prior.level) || 'Self-paced',
            art:(prior && prior.art) || incoming.art || 'structure',
            modules:Array.isArray(incoming.modules) && incoming.modules.length
              ? incoming.modules : ((prior && prior.modules) || []),
            status:incoming.status
          });
          target.academyUrl = incoming.academyUrl || '';
          target.shareUrl = incoming.shareUrl || '';
          target.shareTitle = incoming.shareTitle || target.title;
          target.shareMessage = incoming.shareMessage || '';
          target.price = incoming.priceConfigured
            ? (incoming.price || '')
            : ((prior && prior.price) || incoming.price || '');
          target.priceNote = incoming.priceNote || (prior && prior.priceNote) || '';
          target.catalogueRole = role;
          target.catalogueOrder = Number.isFinite(Number(incoming.catalogueOrder))
            ? Number(incoming.catalogueOrder) : ((prior && prior.catalogueOrder) || (prior && prior.order) || 0);
          target.priority = role === 'flagship' ? 1 : role === 'supporting' ? 2 : 3;
          if (incoming.cataloguePresentationConfigured) {
            target.hook = incoming.hook || '';
            target.problem = incoming.problem || '';
            target.focus = incoming.learningFocus || '';
            target.why = incoming.whyThisOne || '';
          } else if (prior) {
            target.hook = prior.hook || target.hook || '';
            target.problem = prior.problem || target.problem || '';
            target.focus = prior.focus || target.focus || '';
            target.why = prior.why || target.why || '';
          }

          programmes = programmes.filter(item => !sameCourse(item,incoming));
          supporting = supporting.filter(item => !sameCourse(item,incoming));
          courses = courses.filter(item => !sameCourse(item,incoming));
          dynamicFlagships = dynamicFlagships.filter(item => !sameCourse(item,incoming));
          dynamicSupporting = dynamicSupporting.filter(item => !sameCourse(item,incoming));

          if (role === 'flagship') {
            if (prior && (source.programmes || []).some(item => sameCourse(item,incoming))) {
              programmes.push(target);
            } else dynamicFlagships.push(target);
          } else if (role === 'supporting') {
            if (prior && (source.supportingProgrammes || []).some(item => sameCourse(item,incoming))) {
              supporting.push(target);
            } else dynamicSupporting.push(target);
          } else {
            courses.push(target);
          }
          changed = true;
        });
        if (changed) {
          courses.sort((a,b)=>(a.priority||3)-(b.priority||3) ||
            (a.order||a.catalogueOrder||0)-(b.order||b.catalogueOrder||0) ||
            String(a.title||'').localeCompare(String(b.title||'')));
          renderFlagships();
          renderLiveClassroom();
          renderDevelopmentRail();
          renderFilters();
          renderCourses();
        }
      })
      .catch(() => { /* Keep the checked-in catalogue usable if Academy is offline. */ });
  }

  grid?.addEventListener('click',event => {
    const share = event.target.closest('[data-share-course]');
    if (share) { event.preventDefault(); event.stopPropagation(); openShare(share.dataset.shareCourse,share); return; }
    const open = event.target.closest('[data-open-course]');
    if (open) { event.preventDefault(); event.stopPropagation(); openCourse(open.dataset.openCourse,open); return; }
    const card = event.target.closest('[data-course-card]');
    if (card && grid.contains(card)) openCourse(card.dataset.courseCard,card);
  });
  grid?.addEventListener('keydown',event => {
    const card = event.target.closest('[data-course-card]');
    if (card && card === event.target && (event.key === 'Enter' || event.key === ' ')) {
      event.preventDefault(); openCourse(card.dataset.courseCard,card);
    }
  });
  filtersHost?.addEventListener('click',event => {
    const button = event.target.closest('[data-filter]');
    if (!button) return;
    activeFilter = button.dataset.filter; renderCourses();
  });
  searchInput?.addEventListener('input',renderCourses);
  $('#clearSearch')?.addEventListener('click',() => {
    if (searchInput) { searchInput.value = ''; searchInput.focus(); }
    activeFilter = 'All topics'; renderFilters(); renderCourses();
  });
  $('.modal-close',modalBackdrop)?.addEventListener('click',closeCourse);
  modalBackdrop?.addEventListener('click',event => { if (event.target === modalBackdrop) closeCourse(); });
  $('#shareClose')?.addEventListener('click',closeShare);
  shareBackdrop?.addEventListener('click',event => { if (event.target === shareBackdrop) closeShare(); });
  $('#shareCopy')?.addEventListener('click',copyShareLink);
  document.addEventListener('keydown',event => {
    if (event.key === 'Escape') {
      if (shareBackdrop?.classList.contains('open')) closeShare();
      else if (modalBackdrop?.classList.contains('open')) closeCourse();
    }
  });

  renderFlagships();
  renderLiveClassroom();
  renderDevelopmentRail();
  renderFilters();
  renderCourses();
  syncAcademyCatalogue();
})();
