(() => {
  'use strict';
  const STORAGE_KEY = 'tradethesis.module5.internal-preview.v5';
  const $ = (id) => document.getElementById(id);
  const lessons = [
    {
      id:12, title:'Breakout or Temporary Penetration?', short:'Breakout or penetration', time:'30–35 min', hook:'A close beyond a line is evidence. It is not a verdict.',
      summary:'Learn to describe the break precisely, compare confirmation choices and keep their limitations visible.',
      notePrompts:{observation:{title:'Observation · What crossed?',prompt:'Name the prior zone, timeframe, wick/close and current sequence. Use only candles visible at this stage.'},interpretation:{title:'Rule & interpretation',prompt:'Which confirmation convention are you applying, and what does the current evidence support so far?'},alternative:{title:'Filter cost / alternative',prompt:'Could the move hold, return into the band, or remain unclear? What cost does your filter create?'},revision:{title:'What would change the read?',prompt:'State an observable event—such as a close back inside or absent follow-through—that would weaken your view.'}},
      objectives:[
        'Define the prior zone using evidence visible before the move.',
        'Distinguish an intraday excursion from a close outside the zone.',
        'Explain the trade-offs of close, distance, time and volume filters.',
        'Describe alternatives without turning the chart into a buy/sell instruction.'
      ],
      sections:[
        {title:'First name the boundary', paragraphs:[
          'A breakout begins with a claim about a boundary. Before price moves through it, identify the previous highs, lows or range edge that make the area relevant. Keep the zone fixed while you inspect what happens next. If the zone needs to change, record the revision rather than pretending you drew it that way originally.',
          'A move outside a zone can be a transition from a range into a directional phase. It can also be a temporary excursion or an unresolved transition. The label breakout should describe what price has done—not quietly predict what it must do next.'
        ]},
        {title:'Four kinds of evidence', paragraphs:[
          'A wick beyond the area shows that price traded there; it does not show that the session finished there. A close outside the area adds a different piece of evidence. Distance beyond the zone and time spent outside it can provide further information, while follow-through shows whether the move continues to hold up. These are related but distinct observations.',
          'Volume may provide context when the instrument and data source make it meaningful. Some analysts use it as a central confirmation tool; others do not require a volume surge before they interpret a price move. In this course, volume is supporting evidence—not a universal pass/fail switch. The example chart deliberately isolates price behaviour and does not plot volume.'
        ]},
        {title:'Every filter has a cost', paragraphs:[
          'Waiting for a close can filter out some intraday penetrations, but a close just outside the zone may still fail. Requiring a larger percentage distance can reduce borderline cases, but the market may already have moved far by the time the condition is met. Requiring two closes can avoid some one-bar excursions, but it can also recognise a move late—and it still cannot guarantee continuation.',
          'A filter helps when you can apply the rule consistently and understand what it may cause you to miss. It cannot make the next move certain.'
        ]},
        {title:'The market state still matters', paragraphs:[
          'A breakout attempt is a transition between structures. A move above a nearby high on a short chart may remain inside a much broader range. Conversely, a boundary that caps a long period of overlapping price may be more consequential than a tiny local swing. Change the viewing scale and ask what remains true. The local break is not automatically the larger story.',
          'Your task here is not to trade the break. It is to state exactly what the chart has established, what it has not established, and what future evidence would change your view.'
        ]}
      ],
      stages:[
        {image:'charts/L12-01-before-break.png', alt:'NIFTY 50 daily candles through 2 September 2016. The prior upper zone is highlighted; subsequent candles are hidden.', title:'Stage 1 · Before the break', prompt:'What makes this a plausible prior upper area, and what would count as a break on this daily chart?', placeholder:'Name the prior evidence, your breakout convention, and one thing that would remain uncertain.'},
        {image:'charts/L12-02-outside-zone.png', alt:'The same NIFTY 50 chart through 8 September 2016, now showing several closes above the highlighted zone.', title:'Stage 2 · The move closes outside', prompt:'Price has now closed above the zone for several sessions. What is better supported now—and what is still not guaranteed?', placeholder:'State your revised view, the evidence for it, and a specific condition that would weaken it.'},
        {image:'charts/L12-03-later-failure.png', alt:'The complete teaching window through 16 September 2016, showing price later returning below the original zone.', title:'Stage 3 · Later evidence', prompt:'How should you revise your earlier view now that price has moved back below the original zone?', placeholder:'Explain which earlier evidence still mattered, what changed, and what you would avoid claiming in hindsight.'}
      ],
      reveal:'The sequence is intentionally uncomfortable: multiple closes beyond the chosen band did not prevent a later failure. A closing-price or time filter can make a rule more consistent; it cannot make the next move certain. The defensible summary is that a breakout attempt occurred and later lost support from the subsequent evidence. The ending was not knowable at Stage 1.',
      takeaway:'Describe the break using an explicit convention, then keep judging what happens afterwards.',
      quiz:[
        {q:'A wick crosses above resistance but the candle closes back inside the zone. What is the most precise description?',options:['The breakout is confirmed.','Price penetrated the area intraday but did not close beyond the chosen boundary.','The level has become support.'],correct:1,feedback:'The high records an excursion; the close records where the session finished. They are not identical observations.'},
        {q:'Two closes beyond a zone guarantee continuation.',options:['True','False'],correct:1,feedback:'A time filter is a convention, not a guarantee. The historical example later closes back below its zone.'},
        {q:'No volume surge appears on the chart. Does that alone prove the breakout is false?',options:['Yes, volume is mandatory in every market.','No. Volume is one possible contextual input; assess the price sequence and chart context too.','Yes, unless the next candle gaps.'],correct:1,feedback:'Practitioners differ on how volume should be used. The course should not turn it into a universal pass/fail rule.'},
        {q:'A fixed 20-point buffer has the same meaning on every instrument and in every market condition.',options:['True; points always have the same significance.','False; its meaning depends on instrument scale and current movement.','True, if the zone is drawn horizontally.'],correct:1,feedback:'Fixed-distance, percentage and volatility-scaled conventions have different trade-offs. None is universal.'},
        {q:'After two closes beyond the zone, price later returns inside it. What is the best review?',options:['The earlier closes were not real observations.','The rule was consistent, but later evidence weakened the continuation interpretation.','A short trade is automatically required.'],correct:1,feedback:'Later evidence changes the current interpretation; it does not erase what was observable at the earlier stage.'}
      ]
    },
    {
      id:13,title:'Retests and Role Reversal',short:'Retests & role reversal',time:'35–40 min',hook:'A retest gives you another clue, not a guarantee.',
      summary:'Separate the original zone, the move beyond it and the response after a return.',
      notePrompts:{observation:{title:'1 · Break and return',prompt:'Name the original boundary, how price crossed it, how far the return went into the band, and where the relevant bar closed.'},interpretation:{title:'2 · Response so far',prompt:'Does the response look hold-like, failure-like or inconclusive? Point to the actual closes and later bars that support your wording.'},alternative:{title:'3 · What else remains possible?',prompt:'Include a no-retest path, a deeper return, a full move back into the old range, or a reclaim that challenges your current view.'},revision:{title:'4 · What would change your read?',prompt:'Name the observable next event that would strengthen or weaken your role-reversal hypothesis. Keep the original zone visible.'}},
      objectives:[
        'Distinguish the break from a later return.',
        'Describe whether the return touches, enters, crosses or stays outside the band.',
        'Explain why former resistance may become support without treating that as a rule.',
        'State what would strengthen or weaken the idea that the old area may have changed roles.'
      ],
      sections:[
        {title:'Three events, not one pattern name',paragraphs:[
          'First ask what happened at the break. Did price close beyond the area or only wick through it? Next, ask what happened on the return. Did price enter the zone, touch its edge, stop just short, or never return? Finally, examine the later response. Did price remain on the new side, pass through the band or leave mixed evidence?',
          'When all of this is called simply “a retest”, the label hides the information needed for analysis. A retest describes a return to an area after a break; it does not tell you whether that return succeeded.'
        ]},
        {title:'Role reversal is possible, not automatic',paragraphs:[
          'A previous resistance area may become relevant as support after price moves above it. The reverse may occur after a break below support. This is a way to describe a possible change in how the area behaves—not a switch that turns on automatically when price crosses the line.',
          'Keep the original zone visible while you assess the return. If the band no longer describes the behaviour, you can revise it—just record what changed and why.'
        ]},
        {title:'Some breakouts never retest the zone',paragraphs:[
          'Some moves continue without returning to the old zone. The absence of a tidy pullback does not invalidate the breakout. It also does not create an obligation to chase a move that has already travelled a long distance. This lesson is about interpreting price, not prescribing a universal entry trigger.',
          'A return that initially holds above the area may still fail later. Conversely, a brief penetration of the area may be followed by a recovery. Record the timeframe, where the candles closed, and what subsequent evidence would change your view.'
        ]},
        {title:'Read the historical example without hindsight',paragraphs:[
          'The chart stages use NIFTY 50 daily data and a candidate former-resistance band around 7,795–7,865. In Stage 1, inspect the earlier reactions and decide whether the band is a reasonable area to watch. In Stage 2, the move beyond the area and the first return become visible. Stage 3 reveals the later sequence only after you have recorded a view.',
          'Judge your answer by how well you used the evidence available at that stage, not by whether you guessed the ending. Describe where price traded and closed, what that makes more plausible, and what remains uncertain. The final stage adds evidence; it does not prove the zone caused the move.'
        ]}
      ],
      stages:[
        {image:'charts/L13-01-before-break.png',alt:'NIFTY 50 daily candles through 14 August 2014, with the candidate former-resistance zone highlighted.',title:'Stage 1 · The old upper area',prompt:'Which visible reactions support this candidate band, and what alternative boundary could another careful analyst defend?',placeholder:'Record the reactions you rely on and what your band excludes.'},
        {image:'charts/L13-02-return-toward-area.png',alt:'The same chart through 22 August 2014, showing the break and a later candle whose low approaches the zone edge.',title:'Stage 2 · The return approaches',prompt:'Did price enter the chosen band, touch its edge or just approach it? What does the close add?',placeholder:'Describe the low and close relative to the zone; do not call the outcome confirmed yet.'},
        {image:'charts/L13-03-later-evidence.png',alt:'The full selected NIFTY 50 window through 18 September 2014, with later price remaining above the candidate area.',title:'Stage 3 · Later evidence',prompt:'What does the later sequence support, and what claim would go beyond the evidence?',placeholder:'Explain how your interpretation changed and what remains unproven.'}
      ],
      reveal:'In this selected window, price remains above the candidate area following the return. That supports, but does not prove, the idea that the old area may have changed roles. The close and later follow-through matter; neither the label “retest” nor the zone itself supplies a guaranteed outcome.',
      takeaway:'A retest is one possible path, not a required step.',
      quiz:[
        {q:'Does every breakout need to return to its origin?',options:['Yes, a retest is required.','No. Price may continue without returning.','Only if the first candle closes outside the zone.'],correct:1,feedback:'A retest can offer additional evidence, but it is not mandatory.'},
        {q:'Former resistance definitely becomes support after price returns from above.',options:['True','False'],correct:1,feedback:'Role reversal is possible, not automatic; price can hold, cross through or remain ambiguous.'},
        {q:'What should you do if the zone seems to need a new boundary after later candles appear?',options:['Move it silently to fit the outcome.','Record the revision and the new evidence that justified it.','Pretend the original boundary always included the new candles.'],correct:1,feedback:'Revising a zone is possible, but the revision should be explicit to avoid hindsight-fitting.'},
        {q:'A return touches the band but the sequence then closes repeatedly inside the old range. What is the safest description?',options:['The retest succeeded because it touched the band.','The role-reversal hypothesis is weakened by the later closes inside the prior range.','The next move must reach the opposite range edge.'],correct:1,feedback:'Touching the area is not enough to determine the response; the later closes matter.'},
        {q:'A move continues without a return to the original zone. What does that establish?',options:['The breakout was invalid.','Only that the return did not happen in this window; it is not a required step.','You must chase the move.'],correct:1,feedback:'The market does not owe a retest. Missing one is not evidence that every breakout is invalid.'}
      ]
    },
    {
      id:14,title:'Failed Breakouts and Alternate Outcomes',short:'Failed breakouts',time:'45–55 min including Wider Neckline',hook:'A failed breakout can tell you more than the breakout attempt—but it is not an automatic reverse signal.',
      summary:'Treat a failed signal as new evidence, not an excuse to predict the opposite with certainty.',
      notePrompts:{observation:{title:'1 · Original signal & contradiction',prompt:'Name the original structure, the break attempt and the precise later event that challenged it. Record only what was visible at each stage.'},interpretation:{title:'2 · What failed, exactly?',prompt:'Did the continuation claim weaken, remain inconclusive or get reclaimed? Point to the close and subsequent response rather than using only a label.'},alternative:{title:'3 · After the failure',prompt:'Could price travel into the old range, stall, reclaim the boundary or remain mixed? Keep at least one credible alternative.'},revision:{title:'4 · Invalidation & process',prompt:'What observable event would invalidate your failure interpretation? If considering a hypothetical failed-breakout setup, identify the failure extreme; do not force a trade if the structural distance is too large.'}},
      objectives:[
        'Identify a move beyond the zone followed by contradictory evidence.',
        'Distinguish a setback from a sustained return into the prior range.',
        'Explain why a failure may increase the relevance of an opposite scenario without guaranteeing it.',
        'Use the Wider Neckline ChartLab to defend reasoning, not a perfect drawing.'
      ],
      sections:[
        {title:'The anatomy of a failure',paragraphs:[
          'The review has four parts: the old boundary, the attempt to move beyond it, the later candle or sequence that challenged the move, and what happened next. Did price continue, move sideways, or recover?',
          'A failed breakout is not just a move that looks poor after we know the ending. It means the move did not keep going in the direction first suggested by the break. The more price stays in the old range, the harder it is to keep the original idea unchanged.'
        ]},
        {title:'Failure is information, not a command',paragraphs:[
          'A failure test occurs when price moves beyond a prior pivot or support/resistance area and then reverses quickly. When the move does not follow through, the original continuation claim is challenged and an alternative may deserve more attention.',
          'But “more relevant” is not “guaranteed”. After a failed upside break, price may move down, settle into a range, or recover and try again. A failed downside break may recover, but it can also fail again. When the evidence no longer supports your first idea, weaken it or set it aside. That does not mean you must immediately trade in the opposite direction.'
        ]},
        {title:'What counts as contradiction?',paragraphs:[
          'An intraday dip into the zone is different from a close back inside it. A single close back inside can weaken the claim without completing a full reversal. A return through the boundary followed by further closes in the old range adds more contradictory evidence. There is no single percentage or candle count that is correct in every market and timeframe.',
          'Look at how price behaved after crossing the zone, rather than relying on a candle name. The candles show where price traded and closed; they cannot tell us whether institutions or stop hunters caused the move.'
        ]},
        {title:'Read the historical case without hindsight',paragraphs:[
          'The staged NIFTY 50 example begins with a candidate former-resistance band and a move beyond it. The next view includes a return that still leaves the close above the band. This is the point at which many learners become attached to the continuation idea.',
          'Write your view before revealing later candles. At the end, point to the evidence that supports or changes your view. The ending does not make the failure obvious at Stage 1; judge your first answer by what you could see then.'
        ]},
        {title:'Keep the existing Wider Neckline ChartLab',paragraphs:[
          'This is the third and final ChartLab in the course; it remains in Lesson 14. Use the existing clean Wider Neckline chart from the course asset set. Ask the learner to choose and defend a useful zone, explain which nearby reactions it includes or excludes, then name two possible outcomes after a break. The reference shows one reasonable approach, not the only acceptable drawing.',
          'This expanded module adds more explanation and counterexamples around the existing lab. It does not add another ChartLab or move Clear W from Lesson 5 and Uneven Lows from Lesson 8.'
        ]},
        {title:'The disciplined response',paragraphs:[
          'Write down the idea you started with, the evidence available at the time, what challenged it, and the condition that changed your view. If an alternative becomes more relevant, state what evidence would still be needed. “Failed breakout” is not a complete note unless you explain which part of the sequence failed and what that means for your interpretation.',
          'This course does not provide a universal entry, stop or position-size rule. Those would require a separate trading plan and risk-control framework. Here, the learning outcome is a more honest reading of the chart.'
        ]}
      ],
      stages:[
        {image:'charts/L14-01-before-break.png',alt:'NIFTY 50 daily candles through 19 January 2018, showing the candidate former-resistance band before the breakout.',title:'Stage 1 · Before the breakout attempt',prompt:'Which visible reactions define your candidate area? What would count as contradictory evidence later?',placeholder:'State the initial hypothesis, prior evidence, and a specific invalidation condition.'},
        {image:'charts/L14-02-initial-return.png',alt:'The same NIFTY 50 chart through 1 February 2018, showing a move above the band and a return that still closes above it.',title:'Stage 2 · The return looks acceptable',prompt:'At this point, what interpretation is plausible? What evidence is still missing?',placeholder:'Write the provisional view before you see the next sessions.'},
        {image:'charts/L14-03-failed-follow-through.png',alt:'The same NIFTY 50 series through 20 February 2018, showing the close below the band and later weakness.',title:'Stage 3 · The thesis is challenged',prompt:'Which specific new evidence weakens the idea that the move would keep going? Does it guarantee an opposite trade?',placeholder:'Record the contradiction, your revised view, and what remains uncertain.'}
      ],
      reveal:'The return on 1 February did not establish a durable change of role. The 2 February close back below the prior band was a clear contradiction to the idea that the move would keep going, and subsequent weakness added context. This makes the original bullish interpretation weaker; it does not by itself prescribe a short trade or prove hidden trader intent.',
      takeaway:'When the chart contradicts your idea, update the idea before inventing an excuse for it.',
      quiz:[
        {q:'Price breaks above a zone and later closes back inside the prior range. What is the most careful conclusion?',options:['The next move must be lower.','The return is contradictory evidence against sustained continuation; assess the later sequence.','The original area was drawn incorrectly.'],correct:1,feedback:'The failure weakens the original thesis. It does not guarantee direction or prove that the original zone was invalid.'},
        {q:'What distinguishes a failure test from a single wick beyond a zone?',options:['Any wick is enough to prove the failure test.','The sequence includes a move beyond a prior pivot or area and a quick reversal that challenges the initial move.','A volume surge is mandatory.'],correct:1,feedback:'The sequence and the response matter. One wick beyond a boundary does not establish the complete pattern.'},
        {q:'Price fails to hold beyond resistance, then later reclaims the original boundary and remains above it. What should you record?',options:['The first failure never happened.','The reclaim is new evidence that may weaken the failure interpretation; preserve both events.','The original continuation thesis is guaranteed to succeed now.'],correct:1,feedback:'The sequence changes as new candles appear. A reclaim challenges the current label without erasing earlier observations.'},
        {q:'Does high volume on a failed breakout prove stop hunting?',options:['Yes; high volume proves that stops were triggered intentionally.','No. Volume describes activity in the feed; it does not prove hidden motive.','Only if the candle closes outside the zone.'],correct:1,feedback:'The data feed and its baseline matter, but OHLCV alone cannot establish who acted or why.'},
        {q:'In a hypothetical failed-upside-break setup, what is a defensible structural reference for an initial stop?',options:['A fixed line just above the old zone, regardless of the failure high.','Beyond the failure extreme that would undermine the failure thesis, with appropriate room; if that distance is too large, reduce exposure or pass.','Exactly one fixed tick amount on every instrument.'],correct:1,feedback:'The structural reference is the extreme that would invalidate the failed-breakout interpretation. It is not a universal buffer, and stop orders may fill worse than the stop price during gaps or fast markets.'}
      ]
    }
  ];
  // Long-form canonical lesson text is loaded as a separate data file so the same content can be reviewed without duplicating it in the interaction code.
  const deepPack = window.MODULE5_DEEP_CONTENT || {};
  const interactionPack = window.MODULE5_INTERACTIONS || {};
  lessons.forEach((l) => {
    const d = deepPack[String(l.id)];
    if (d) {
      l.sections = d.sections;
      l.objectives = d.objectives;
      l.time = d.time;
      l.hook = d.hook;
      l.summary = d.summary;
      l.takeaway = d.takeaway;
      l.notePrompts = d.notePrompts || l.notePrompts;
    }
    const inter = interactionPack[String(l.id)];
    if (inter) {
      l.stages = inter.stages || l.stages;
      l.reveal = inter.reveal || l.reveal;
      l.quiz = inter.quiz || l.quiz;
      l.modelAnswerRubric = inter.modelAnswerRubric || [];
    }
  });

  const blankState = () => ({activeLesson:12,stage:{},stageResponses:{},notes:{},quizAnswers:{},quizSubmitted:{}});
  let state = loadState();
  const requestedLesson = Number(new URLSearchParams(window.location.search).get("lesson"));
  if ([12,13,14].includes(requestedLesson)) state.activeLesson = requestedLesson;
  function loadState(){ try {return {...blankState(),...JSON.parse(localStorage.getItem(STORAGE_KEY)||'{}')}} catch(e){return blankState()} }
  function saveState(){try{localStorage.setItem(STORAGE_KEY,JSON.stringify(state));$('save-indicator').textContent='Saved in this browser only';}catch(e){$('save-indicator').textContent='Browser storage is unavailable';}}
  const lesson = () => lessons.find(l=>l.id===state.activeLesson)||lessons[0];
  const stageIndex = () => Math.min(state.stage[state.activeLesson]||0, lesson().stages.length-1);
  function escapeText(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  function renderLessonList(){
    $('lesson-list').innerHTML=lessons.map(l=>`<button class="lesson-link ${l.id===state.activeLesson?'active':''}" data-lesson="${l.id}" type="button"><span class="lesson-num">${l.id}</span><span>${escapeText(l.short)}</span><span class="lesson-dot" aria-hidden="true"></span></button>`).join('');
    document.querySelectorAll('[data-lesson]').forEach(b=>b.addEventListener('click',()=>selectLesson(Number(b.dataset.lesson))));
    $('active-lesson-meta').textContent=`Lesson ${lesson().id} of 18 · Module 5 of 6`;
  }
  function selectLesson(id){state.activeLesson=id;saveState();renderAll();$('lesson-main').scrollIntoView({behavior:'smooth',block:'start'});}
  function renderInline(text){
    return escapeText(text)
      .replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>')
      .replace(/\*([^*]+)\*/g,'<em>$1</em>');
  }
  function renderReadingBlock(block){
    if(block.type==='p') return `<p>${renderInline(block.text)}</p>`;
    if(block.type==='quote') return `<blockquote class="reading-quote">${renderInline(block.text)}</blockquote>`;
    if(block.type==='ul' || block.type==='ol') {
      const tag=block.type==='ol'?'ol':'ul';
      return `<${tag} class="reading-bullets">${block.items.map(item=>`<li>${renderInline(item)}</li>`).join('')}</${tag}>`;
    }
    if(block.type==='figure') return `<figure class="reading-figure"><img src="${escapeText(block.src)}" alt="${escapeText(block.alt)}" loading="lazy"><figcaption>${escapeText(block.caption || block.alt)}</figcaption></figure>`;
    if(block.type==='caseChart') return `<div class="case-chart-block"><div class="case-chart-question case-chart-rights-note"><span>PAUSE BEFORE THE NEXT REVEAL</span><strong>Original historical chart visual withheld pending data-redistribution rights review</strong><p>The accompanying lesson text explains the historical case, but its original chart image is not included in this public preview until redistribution rights are confirmed. The staged chart exercise uses synthetic illustrative candles to practise the same observation-and-revision process.</p><p>${renderInline(block.question)}</p><p class="case-chart-hint">Use only the synthetic candles shown in the staged exercise; they are not the historical case data.</p><button class="button secondary" type="button" data-open-chart="chart">Open the staged chart exercise →</button></div></div>`;
    if(block.type==='relatedCourse') return `<aside class="related-course-card"><div class="related-course-label">${escapeText(block.label || 'RELATED COURSE IN THE CATALOGUE')}</div><div class="related-course-body"><p class="related-course-kicker">Continue learning</p><h4>${escapeText(block.title)}</h4><p>${renderInline(block.text)}</p><p class="related-course-note">${renderInline(block.note || '')}</p></div></aside>`;
    if(block.type==='table') return `<div class="reading-table-wrap"><table class="reading-table"><thead><tr>${block.headers.map(h=>`<th scope="col">${renderInline(h)}</th>`).join('')}</tr></thead><tbody>${block.rows.map(row=>`<tr>${row.map(cell=>`<td>${renderInline(cell)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
    return '';
  }
  function renderReading(l){
    $('lesson-title').textContent=`${l.id}. ${l.title}`;
    $('lesson-time').textContent=l.time;
    $('lesson-hook').textContent=l.hook;
    $('lesson-summary').textContent=l.summary;
    $('objectives').innerHTML=l.objectives.map(x=>`<li>${escapeText(x)}</li>`).join('');
    $('reading-sections').innerHTML=l.sections.map(s=>`<section class="reading-section"><h3>${escapeText(s.title)}</h3>${(s.blocks||[]).map(renderReadingBlock).join('')}</section>`).join('');
    document.querySelectorAll('[data-open-chart]').forEach(button=>button.addEventListener('click',()=>{setTab('chart');$('panel-chart').scrollIntoView({behavior:'smooth',block:'start'});}));
    $('takeaway').textContent=l.takeaway;
  }
  function renderChartStage(l){
    const i=stageIndex(),s=l.stages[i];
    $('stage-label').textContent=`STAGE ${i+1} OF ${l.stages.length}`;
    $('stage-title').textContent=s.title;
    $('stage-prompt').textContent=s.prompt;
    $('stage-image').src=s.image;
    $('stage-image').alt=s.alt;
    $('stage-count').textContent=`${i+1} / ${l.stages.length}`;
    const key=`${l.id}-${i}`;
    $('stage-response').value=state.stageResponses[key]||'';
    $('stage-response').placeholder=s.placeholder;
    $('stage-response-state').textContent=(state.stageResponses[key]||'').trim().length>=45?'Your view is saved in this browser':'Add a little more detail before moving on (45 characters minimum)';
    $('stage-next').disabled=(state.stageResponses[key]||'').trim().length<45;
    $('stage-next').textContent=i<l.stages.length-1?'Record this view & reveal the next stage →':'Record final view & compare answers';
    $('stage-reset').hidden=(i===0 && !state.stageResponses[`${l.id}-0`]);
    $('final-recap').hidden=!(state.stage[l.id]===l.stages.length);
    $('final-recap-text').textContent=l.reveal;
    const answerCards=l.stages.map((stage,idx)=>`<section class="model-answer"><h4>${escapeText(stage.title || `Stage ${idx+1}`)}</h4><p>${escapeText(stage.modelAnswer || 'Compare your response with the visible evidence and explain any difference.')}</p><p class="model-self-check"><strong>Self-check:</strong> ${escapeText(stage.selfCheck || '')}</p></section>`).join('');
    $('model-stage-answers').innerHTML=`<h3>One possible answer for each stage</h3><p class="model-intro">These are examples, not exact wording to copy. Your answer can differ if it is tied to the candles you could see at that stage.</p>${answerCards}<h4>Quick self-check</h4><ul class="model-rubric">${(l.modelAnswerRubric||[]).map(x=>`<li>${escapeText(x)}</li>`).join('')}</ul>`;
    $('chart-note').textContent=s.caption || 'Historical NIFTY 50 daily OHLC · temporary internal teaching chart · later candles are revealed in sequence.';
    $('notes-hook').textContent=l.hook;
    renderQuiz(l);
    renderProgress();
  }
  function renderNotes(l){
    const note=state.notes[l.id]||{};
    const defaults={observation:{title:'1 · Observation',prompt:'What did price actually do? Mention wick, close, zone and timeframe.'},interpretation:{title:'2 · Interpretation',prompt:'What does the evidence make more plausible, without making it certain?'},alternative:{title:'3 · Alternative',prompt:'What else could happen while remaining consistent with the evidence so far?'},revision:{title:'4 · Revision condition',prompt:'What specific event would make you weaken, abandon or revise the current view?'}};
    const prompts=l.notePrompts||defaults;
    ['observation','interpretation','alternative','revision'].forEach(k=>{if(prompts[k]){$('note-'+k+'-title').textContent=prompts[k].title;$('note-'+k+'-prompt').textContent=prompts[k].prompt;}});
    $('note-observation').value=note.observation||'';
    $('note-interpretation').value=note.interpretation||'';
    $('note-alternative').value=note.alternative||'';
    $('note-revision').value=note.revision||'';
    $('notes-lesson-title').textContent=`Field notes · Lesson ${l.id}`;
  }
  function renderQuiz(l){
    if((state.stage[l.id]||0)<l.stages.length){
      $('quiz-area').innerHTML='<div class="reader-takeaway"><span>COMPLETE THE EVIDENCE SEQUENCE FIRST</span><p>Record your view at each chart stage before checking the answers. The explanations are designed to follow the evidence, not reveal the ending in advance.</p></div>';
      $('quiz-submit').hidden=true;$('quiz-reset').hidden=true;$('quiz-status').textContent='Unlocks after all three chart stages have been recorded.';return;
    }
    $('quiz-area').innerHTML=l.quiz.map((q,qi)=>`<fieldset class="quiz-item"><legend>${qi+1}. ${escapeText(q.q)}</legend>${q.options.map((o,oi)=>`<label class="quiz-choice"><input type="radio" name="quiz-${l.id}-${qi}" value="${oi}" ${state.quizAnswers[`${l.id}-${qi}`]===oi?'checked':''} ${state.quizSubmitted[l.id]?'disabled':''}><span>${escapeText(o)}</span></label>`).join('')}<p class="quiz-feedback" ${state.quizSubmitted[l.id]?'':'hidden'}>${state.quizSubmitted[l.id]?(state.quizAnswers[`${l.id}-${qi}`]===q.correct?'Good reading. ':'Compare the evidence again. ')+escapeText(q.feedback):''}</p></fieldset>`).join('');
    if(!state.quizSubmitted[l.id]){
      $('quiz-submit').hidden=false;$('quiz-reset').hidden=true;
      $('quiz-status').textContent=`Answer all ${l.quiz.length}, then submit to see the feedback.`;
      document.querySelectorAll(`#quiz-area input[type="radio"]`).forEach(inp=>inp.addEventListener('change',()=>{const qi=Number(inp.name.split('-').pop());state.quizAnswers[`${l.id}-${qi}`]=Number(inp.value);saveState();}));
    } else {$('quiz-submit').hidden=true;$('quiz-reset').hidden=false;$('quiz-status').textContent='Automated feedback shown. Revisit any answer you want to reconsider.';}
  }
  function renderProgress(){
    const l=lesson(),i=stageIndex();
    $('progress-value').textContent=`Lesson ${l.id} · Stage ${i+1} of ${l.stages.length}`;
    $('progress-bar').style.width=`${((l.id-12)*100/3)+((i+1)/l.stages.length)*(100/3)}%`;
  }
  function renderAll(){const l=lesson();renderLessonList();renderReading(l);renderChartStage(l);renderNotes(l);}
  $('stage-response').addEventListener('input',()=>{
    const key=`${state.activeLesson}-${stageIndex()}`;state.stageResponses[key]=$('stage-response').value;saveState();
    $('stage-response-state').textContent=state.stageResponses[key].trim().length>=45?'Your view is saved in this browser':'Add a little more detail before moving on (45 characters minimum)';
    $('stage-next').disabled=state.stageResponses[key].trim().length<45;
  });
  $('stage-next').addEventListener('click',()=>{
    const l=lesson(),i=stageIndex(),key=`${l.id}-${i}`;
    if((state.stageResponses[key]||'').trim().length<45)return;
    state.stage[l.id]=Math.min(i+1,l.stages.length);saveState();renderChartStage(l);
  });
  $('stage-reset').addEventListener('click',()=>{
    const l=lesson();if(!confirm('Reset this lesson’s chart reveal sequence? Your field notes will be kept.'))return;
    state.stage[l.id]=0;for(let i=0;i<l.stages.length;i++)delete state.stageResponses[`${l.id}-${i}`];saveState();renderChartStage(l);
  });
  ['observation','interpretation','alternative','revision'].forEach(key=>$('note-'+key).addEventListener('input',()=>{
    const l=lesson();state.notes[l.id]={...(state.notes[l.id]||{}),[key]:$('note-'+key).value};saveState();
  }));
  $('quiz-submit').addEventListener('click',()=>{
    const l=lesson();const missing=l.quiz.some((q,qi)=>!Number.isInteger(state.quizAnswers[`${l.id}-${qi}`]));
    if(missing){$('quiz-status').textContent='Please answer every question before viewing feedback.';return;}
    state.quizSubmitted[l.id]=true;saveState();renderQuiz(l);$('quiz-status').textContent='Automated feedback shown. Revisit any answer you want to reconsider.';
  });
  $('quiz-reset').addEventListener('click',()=>{const id=lesson().id;delete state.quizSubmitted[id];saveState();renderQuiz(lesson());$('quiz-status').textContent='';});
  $('export-notes').addEventListener('click',()=>{
    const l=lesson();const data={lesson:l.id,title:l.title,stages:l.stages.map((s,i)=>({stage:s.title,response:state.stageResponses[`${l.id}-${i}`]||''})),fieldNotes:state.notes[l.id]||{},fieldNotePrompts:l.notePrompts||{},quizAnswers:l.quiz.map((q,i)=>({question:q.q,answerIndex:state.quizAnswers[`${l.id}-${i}`]??null,submitted:!!state.quizSubmitted[l.id]}))};
    const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=`TradeThesis-L${l.id}-field-notes.json`;a.click();URL.revokeObjectURL(url);
  });
  renderAll();
})();
