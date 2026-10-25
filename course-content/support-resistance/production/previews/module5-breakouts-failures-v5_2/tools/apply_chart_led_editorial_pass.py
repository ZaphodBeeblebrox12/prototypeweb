from pathlib import Path
import json, re
ROOT = Path(__file__).resolve().parents[1]
JS = ROOT / 'assets' / 'module5-deep-content.js'
raw = JS.read_text(encoding='utf-8')
m = re.search(r'window\.MODULE5_DEEP_CONTENT\s*=\s*(\{.*\})\s*;\s*$', raw, re.S)
if not m:
    raise SystemExit('Unable to parse module5-deep-content.js')
data = json.loads(m.group(1))
P = lambda text: {'type': 'p', 'text': text}
Q = lambda text: {'type': 'quote', 'text': text}
F = lambda file, alt, caption: {'type':'figure','src':f'assets/figures/{file}','alt':alt,'caption':caption}
CASE = lambda src, alt, caption, question: {'type':'caseChart','src':src,'alt':alt,'caption':caption,'question':question}
COURSE = lambda title, label, text, note: {'type':'relatedCourse','title':title,'label':label,'text':text,'note':note}

def section(lid, title):
    matches = [x for x in data[lid]['sections'] if x['title'] == title]
    if len(matches) != 1:
        raise ValueError(f'{lid}: expected one section {title!r}; found {len(matches)}')
    return matches[0]

# Lesson 12: define product/feed terminology at the point it matters and offer Volume as an existing catalogue course.
l12 = data['12']
vol = section('12', 'Volume: useful context, not a verdict')
vol['blocks'] = [
    P("Now that we have separated the wick, close and later follow-through, let's ask a different question: can volume add useful context? Sometimes it can. But volume does not decide whether a breakout is valid or false."),
    P("In the figure, compare price first. Two sequences keep moving away from the zone and two return through it. Now compare the volume panels. Higher activity appears in a sequence that holds and in one that fails. The same is true of quieter activity. That is why I read price and volume as two clues, not as one verdict."),
    P("Before interpreting volume, check what your chart is measuring. For listed shares and exchange-traded futures, volume usually refers to shares or contracts traded, as reported by the relevant venue or data provider. **Spot FX** means currency trading at the current exchange rate. Retail spot FX is generally handled through a network of dealers and brokers rather than one central exchange, so a chart may not have one consolidated volume total. A **CFD (contract for difference)** is a contract with a provider whose value follows an instrument's price; trading it does not mean you own the underlying share, index or commodity. Some FX and CFD charts show **tick volume**—a count of price updates used as a rough measure of activity—or provider-specific data instead of a count of all traded contracts or shares. These measures are not interchangeable."),
    P("Here is a useful check: if the platform does not clearly tell you what its volume figure represents, do not treat it as confirmed traded size. Compare like with like: the same instrument, similar sessions and a clear baseline. If you cannot verify those things, leave the volume claim out."),
    F('FIG08_volume_context_not_gate.png','Four longer price sequences are paired with volume panels: price holds or fails with expanding or muted volume.','Compare the price result with the volume bars. The same kind of activity can appear in different outcomes.'),
    P("Here is how I would record it in a journal: 'Price closed above the zone and held there for three bars. The volume shown is higher than in the previous section of this chart, which adds context, but the later outcome is still open.' That is enough. We do not need to guess who traded or why."),
    COURSE('Volume','RELATED COURSE IN THE TRADETHESIS CATALOGUE',"For a fuller look at how to read volume, continue with the separate **Volume** course in the TradeThesis catalogue. Here, we only need to know what volume can add to a breakout reading—and what it cannot prove.","Keep this lesson focused on price structure. The Volume course explores the volume question in its own right."),
    P("One important detail before the NIFTY example: the historical NIFTY 50 chart below is an index-price chart and has no volume bars. We will use it to study price only. Volume cannot be used to explain the outcome of this particular example.")
]

hist12 = section('12', 'What the historical case can teach—and what it cannot')
hist12['blocks'] = [
    P("Let's put the idea to work on a real chart. This is a temporary internal NIFTY 50 daily-price example. The shaded band is a candidate upper area drawn for this exercise; it is not an official level. We'll start with the candles that were visible before the move, then reveal later sessions only after you have recorded your first read."),
    CASE('charts/L12-01-before-break.png', 'NIFTY 50 daily candles from 15 July through 2 September 2016. A candidate upper area between 8,810 and 8,850 is shaded; later sessions are not shown.', 'NIFTY 50 · daily OHLC · 15 July–2 September 2016. The shaded 8,810–8,850 band is the candidate upper area for this exercise. Later sessions are hidden. Temporary internal teaching data; the band is an instructional choice, not an official level.', 'Before seeing any later candles, point to the earlier highs near the shaded band. Why is this a reasonable area to watch? What rule will you use to count a break?'),
    P("Take a moment with the chart before opening the next stage. A useful first note might be: 'Price has turned away from this upper area before, so I will treat it as a candidate ceiling. I will count a daily close above the band as a break for this exercise. I do not yet know whether price will stay above it.' Your wording can differ; the important thing is to name the evidence and the rule you chose."),
    P("Use **Examine the evidence** to record that first read. The next two chart views will reveal what happened after this date. When they appear, keep the earlier closes as facts and update only the interpretation that the new evidence changes."),
    F('FIG09_decision_record_timeline.png','A four-stage timeline shows the prior area, the crossing, later evidence and a review that preserves the earlier view.','Keep the first view and the later revision so you can see why your thinking changed.')
]

# Lesson 13: clarify the chart that demonstrates the return; avoid stating the final result before the staged reveal.
hist13 = section('13', 'What the historical case can teach—and what it cannot')
hist13['blocks'] = [
    P("Let's work through a second NIFTY 50 daily-price example. The shaded band marks a candidate former-resistance area around 7,795–7,865. It was chosen for this exercise from earlier reactions; it is not an official level. The first chart stops before the move we want to study, so you can decide what the earlier structure tells you without hindsight."),
    CASE('charts/L13-01-before-break.png', 'NIFTY 50 daily candles from 26 June through 14 August 2014. The candidate former-resistance band around 7,795–7,865 is highlighted; later candles are hidden.', 'NIFTY 50 · daily OHLC · 26 June–14 August 2014. The shaded 7,795–7,865 band is the candidate former-resistance area. Later candles are hidden; the zone is an instructional choice, not an official level.', 'Look at the earlier approaches to the band. What reactions support drawing this area? Would a careful reader be justified in drawing the band slightly differently?'),
    P("For now, do not try to predict whether the area will hold if price returns to it. First decide whether the original band is defensible and what you will inspect on a return: the low, the amount of overlap with the band, the close, and the candles that follow."),
    P("Open **Examine the evidence** and record your first read. The next stages will let you inspect the crossing, the return and the later response separately. A hold-like outcome in one selected window is an example to study, not a probability you can transfer to every zone you draw."),
    F('FIG09_decision_record_timeline.png','A four-stage timeline shows the prior area, the crossing, later evidence and a review that preserves the earlier view.','Keep the first view and the later revision so you can see why your thinking changed.')
]

# Lesson 14: place a real price chart next to the first historical case explanation, without giving away its ending.
# Append as a final applied example after process/outcome teaching, keeping the existing failure-family sequence intact.
l14 = data['14']
chart_section = {
    'title':'Put the failure review to work on a chart',
    'blocks':[
        P("Now let's apply the questions to a historical chart. The NIFTY 50 daily chart below reaches a candidate upper area after a sustained rise. The band is drawn for this teaching exercise, not supplied as an official index level. At this first stage, the breakout attempt and its outcome are not yet visible."),
        CASE('charts/L14-01-before-break.png', 'NIFTY 50 daily candles from 1 December 2017 through 19 January 2018. The candidate upper band around 10,875–10,920 is highlighted; later candles are hidden.', 'NIFTY 50 · daily OHLC · 1 December 2017–19 January 2018. The shaded 10,875–10,920 band is a candidate prior upper area selected for this exercise. Later sessions are hidden; it is not an official level.', 'Look at the rise into the shaded band. Which earlier highs make this an area worth watching? What would count as a break, and what later event would make you question the idea that price is holding above it?'),
        P("You do not need to label this a failure yet. It is the starting picture. Write down the area, your rule for a break, and one kind of evidence that could weaken the first interpretation. Then open **Examine the evidence** to reveal the later candles in order."),
        P("When the later bars appear, notice the difference between a reasonable first read and a read that can no longer stand unchanged. The exercise is not to guess the final candle path; it is to identify what the chart adds at each stage and revise the explanation when that evidence changes.")
    ]
}
existing_chart_section = next((i for i, item in enumerate(l14['sections']) if item['title'] == chart_section['title']), None)
if existing_chart_section is None:
    l14['sections'].append(chart_section)
else:
    l14['sections'][existing_chart_section] = chart_section

# Slightly improve first-use plain-language hooks in course-wide objectives and titles where it aids beginner comprehension.
data['12']['summary'] = 'Learn to tell a brief move beyond a zone from a move that begins to hold outside it. We will compare the clues and their trade-offs.'
data['13']['summary'] = 'Separate the break, the return and what price does next. A retest gives you another clue, but it cannot tell you in advance whether the old area will hold.'
data['14']['summary'] = 'Learn to recognise different ways a breakout attempt can fail, describe what the chart shows in plain language, and keep more than one next path in mind.'

JS.write_text('window.MODULE5_DEEP_CONTENT = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')

# Update staged prompts and captions so the chart UI teaches the learner how to inspect the visible evidence.
inter_path=ROOT/'tools'/'lesson_interactions.json'
inter=json.loads(inter_path.read_text(encoding='utf-8'))
updates={
12:[
 ('NIFTY 50 · daily OHLC · 15 July–2 September 2016. The shaded 8,810–8,850 band is the candidate upper area. Look at earlier highs near the band; later sessions are hidden.', 'Look at the earlier highs near the shaded band. What makes this a reasonable upper area to watch, and what rule will you use to call a break?'),
 ('NIFTY 50 · daily OHLC · 15 July–8 September 2016. The same band remains fixed; several daily candles have now closed above it. The later sessions are still hidden.', 'Compare the latest candle closes with the same band. What has been added to the evidence, and what would still make you reconsider?'),
 ('NIFTY 50 · daily OHLC · 15 July–16 September 2016. The original band is unchanged; later price has returned below it and moved back into the earlier range.', 'Now compare the final sequence with your first note. Which observations remain true, which interpretation needs updating, and what still cannot be concluded?')],
13:[
 ('NIFTY 50 · daily OHLC · 26 June–14 August 2014. The shaded 7,795–7,865 band marks the candidate former-resistance area; later candles are hidden.', 'Look at the earlier approaches to the band. Which reactions support the area, and could another careful reader draw it slightly differently?'),
 ('NIFTY 50 · daily OHLC · 26 June–22 August 2014. The same band remains fixed. The visible sequence includes the move above the area and a return towards it.', 'Find the bar whose low returns towards the band. Does its low enter, touch or stop short of the zone? Where does that bar close, and what happened after it?'),
 ('NIFTY 50 · daily OHLC · 26 June–18 September 2014. The same band remains fixed; after the return, later candles move farther above it, followed by a pullback that remains above the band in this selected window.', 'What does the later sequence support in this window? Which claim would go too far—for example, that the band must always hold or that every breakout should be bought on a return?')],
14:[
 ('NIFTY 50 · daily OHLC · 1 December 2017–19 January 2018. The candidate upper area around 10,875–10,920 is shaded; later sessions are hidden.', 'Look at the rise into the shaded area. Which earlier highs make it relevant, and what would count as contradictory evidence after a break?'),
 ('NIFTY 50 · daily OHLC · 1 December 2017–1 February 2018. Price has moved above the original band and returned towards it; the relevant close remains above the zone.', 'At this point, the close is still above the band after a return. What interpretation remains plausible, and what evidence is still missing?'),
 ('NIFTY 50 · daily OHLC · 1 December 2017–20 February 2018. The unchanged band is shown with a later close below it and subsequent weakness.', 'Find the close that moves back below the original band. How does it challenge the continuation idea, and what does it still not prove?')]
}
for item in inter:
    lid=item['id']
    for idx,stage in enumerate(item['stages']):
        caption,prompt=updates[lid][idx]
        stage['caption']=caption
        stage['prompt']=prompt
# Correct a lesson 13 stage 3 model answer to keep its claim limited to this window.
inter[1]['stages'][2]['modelAnswer'] = 'You could write: “In this selected window, price moves above the candidate area after the return, then pulls back while staying above the band. That supports a hold-like reading for now. It does not prove the area will always hold or that every breakout needs a retest. Later price could still return through it.”'
# Store all revisions
inter_path.write_text(json.dumps(inter,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated chart-led reading sections, Volume course signpost, and staged captions/prompts.')
