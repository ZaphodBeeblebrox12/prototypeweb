from pathlib import Path
import json, re
ROOT=Path(__file__).resolve().parents[1]
JS=ROOT/'assets/module5-deep-content.js'
s=JS.read_text(encoding='utf-8')
m=re.search(r'window\.MODULE5_DEEP_CONTENT\s*=\s*(\{.*\})\s*;\s*$',s,re.S)
if not m: raise SystemExit('Could not parse deep content')
data=json.loads(m.group(1))
P=lambda text:{'type':'p','text':text}
Q=lambda text:{'type':'quote','text':text}
F=lambda file,alt,caption:{'type':'figure','src':f'assets/figures/{file}','alt':alt,'caption':caption}
UL=lambda items:{'type':'ul','items':items}
OL=lambda items:{'type':'ol','items':items}

def section(lid, title):
    arr=data[lid]['sections']
    found=[x for x in arr if x['title']==title]
    if len(found)!=1: raise ValueError(f'{lid}: expected one section {title!r}, got {len(found)}')
    return found[0]

# Lesson 12: preserve one volume section, but make its transition and teaching voice explicit.
l12=data['12']
l12['time']='30–35 min'
vols=[x for x in l12['sections'] if 'volume' in x['title'].lower()]
if len(vols)!=1: raise ValueError(f'Lesson 12 should have exactly one volume section, found {len(vols)}')
vol=vols[0]
# Keep its figure and overall substance; make a more direct bridge from price evidence to volume context.
vol['blocks']=[
 P("Now that you have separated the wick, close and later follow-through, let’s ask a different question: does volume add useful context? It sometimes does. But volume is not a referee that declares a breakout valid or false."),
 P("In the figure, compare price behaviour first. Two sequences move away from the zone and two return through it. Then compare the volume panels. Expanding activity appears in a holding sequence and in a failing one; muted activity also appears in both. That does not make volume useless. It means volume and price outcome are different observations, and one cannot substitute for the other."),
 P("Before you call activity ‘high’, check the feed. Listed equities and exchange-traded futures commonly report traded volume, but the aggregation still depends on the data source. Spot FX and some CFDs may show tick volume or broker-specific activity rather than one consolidated exchange tape. Compare like with like: the same instrument, comparable sessions and an explicit baseline. If that information is absent, say so instead of inventing certainty."),
 F('FIG08_volume_context_not_gate.png','Four longer price sequences are paired with volume panels: price holds or fails with expanding or muted volume.','Read price outcome and volume context as separate dimensions.'),
 P("Here is the discipline I want you to practise: describe what price did, then state what volume adds to that description. Do not infer who traded, why they traded, or whether a deliberate trap was set. The staged historical case in this lesson does not include volume, so volume is not evidence you may use to explain its ending.")
]

# Lesson 13: detailed, calm instructor voice; retain simple overview first, then richer illustrations.
l13=data['13']
l13['time']='38–45 min'
l13['summary']='Separate the break, the return and the response; describe how price revisits an area before deciding what the sequence supports.'
l13['hook']='A retest is not confirmation. It is the next test of a claim.'
l13['takeaway']='Name the break, describe the return, then judge the response. The word retest must not do all three jobs.'
l13['objectives']=[
 'Separate the initial break from the later return towards the area.',
 'Describe return depth, closing location and the response after the return.',
 'Distinguish hold-like, failure-like and inconclusive sequences.',
 'Explain why a role reversal is a hypothesis to test, not an automatic switch.',
 'Keep the first interpretation intact so later evidence can be compared with it.'
]
l13['notePrompts']={
 'observation':{'title':'1 · Break and return','prompt':'Name the original boundary, how price crossed it, how far the return travelled into the band, and where the relevant bar closed.'},
 'interpretation':{'title':'2 · Response so far','prompt':'Does the sequence look hold-like, failure-like or inconclusive? Point to the actual closes and later bars that support your wording.'},
 'alternative':{'title':'3 · What else remains possible?','prompt':'Consider no retest, a shallow touch, a deeper return, a close back inside the old range, or a reclaim that challenges your current view.'},
 'revision':{'title':'4 · What would change your read?','prompt':'Name an observable event that would strengthen or weaken your role-reversal hypothesis. Keep the original zone visible and do not move it silently.'}
}
s13_2=section('13','Three observations: break, return, response')
s13_2['blocks']=[
 P("Let’s slow the sequence down. Price has moved beyond an area that mattered before. Later, price comes back towards it. What do we know? We know a crossing occurred under the convention we chose, and we can now describe the return. We do not yet know whether the old area will matter from the new side."),
 Q('A retest is not confirmation. It is the next test of a claim.'),
 P("I want you to separate three things that are often bundled into one word. First, the **break**: what moved beyond the boundary—the wick, the close, or several closes? Second, the **return**: did price stop short, touch the near edge, travel into the band, close back inside the old range, or cross through the whole area? Third, the **response**: what did price do after the return? It may move away while staying on the new side, continue back through the area, or overlap around it without making the answer clear."),
 P("If you label all three stages ‘a successful retest’, you have jumped to the conclusion before describing the evidence. Start with this simple three-panel view. Point to the break first. Then the return. Only the third panel asks how price responds."),
 F('FIG19_simple_break_return_response.png','A simple three-panel illustration separates the break beyond an old resistance area, the return towards it, and the response that follows.','Start simple: identify three separate observations before deciding what the whole sequence means.'),
 P("Keep one sentence in mind while you read: **a break tells you where price went; a retest tells you it came back; the response tells you what happened next.** Those statements are not interchangeable.")
]
s13_3=section('13','The depth of the return matters—but does not settle the outcome')
s13_3['blocks']=[
 P("A return can stop just above the area. It can touch the upper boundary and turn away. It can enter the band shallowly or deeply. It can close inside the old range, cross through the opposite edge, and later reclaim the area. These are not cosmetic differences. They tell you how much of the old range has been re-entered and how strong the claim ‘the former ceiling is now supporting price’ still looks."),
 P("Pay attention to the close as well as the extreme. A wick that dips into the band and a candle that finishes deep inside it are different observations. A close back in the old range challenges the role-reversal idea more directly than a wick that touches the near edge and closes above. Even then, one close is not a prophecy: later bars may extend the return, stall, or reclaim the zone."),
 UL([
  '**No return:** price keeps moving away. That is not a failed retest; there has been no retest to judge.',
  '**Shallow touch:** price reaches the near edge and moves away. This may be consistent with a hold, but inspect the close and what follows.',
  '**Deep entry:** price trades well into the band. The original role-reversal claim needs closer scrutiny, especially if closes move towards the old range.',
  '**Close inside the old range:** this is a clearer contradiction to the claim that price is sustaining itself outside the range.',
  '**Cross through and reclaim:** price passes through the area, then recovers. Record both events; a reclaim can challenge an earlier failure interpretation.',
  '**Repeated overlap:** bars keep crossing the area with closes on both sides. The sequence may still be unresolved; do not force a binary answer.'
 ]),
 F('FIG16_retest_depth_and_closes.png','Four schematic examples distinguish a shallow touch, a deeper entry, a close back inside the range, and a move through the band.','Describe depth and closing location separately. Neither one alone guarantees the next move.'),
 P("Keep the original band fixed while you make this comparison. If later evidence convinces you that the band was drawn badly, revise it openly and record why. Do not shift it silently so that every new candle appears to respect your first idea.")
]
s13_4=section('13','Three responses that share the same name')
s13_4['blocks']=[
 P("Now compare the response, not just the return. In a **hold-like response**, price returns towards the band and then moves away while staying mostly on the new side. That is consistent with the area remaining relevant in this sequence. It does not mean the zone has become a permanent floor or that the next visit must work."),
 P("In a **failure-like response**, price returns through the band and closes back in the old range. If it then cannot reclaim the area, the idea that the old ceiling is now support becomes harder to defend. In an **inconclusive response**, candles overlap around the band and close on alternating sides. The market has not provided enough separation for a confident label. ‘Inconclusive for now’ is a proper analytical conclusion, not a failure to answer."),
 F('FIG20_simple_retest_outcomes.png','Three simple candlestick examples compare a hold-like response, a failure-like response and an inconclusive return.','Start with the three broad outcomes: hold-like, failure-like, or not yet resolved.'),
 P("The simple examples give you the map. Now inspect the more developed sequences below. Notice that the response includes more bars and more uneven movement. Real analysis often becomes less tidy as the window grows, because you see more evidence that may support different interpretations."),
 F('FIG05_three_retest_outcomes.png','Three longer price sequences compare hold-like, failure-like and inconclusive retest outcomes.','The same question with fuller context: what does price do after it returns?'),
 P("Your wording should match the strength of the evidence. ‘It touched the zone and closed above’ is an observation. ‘That is consistent with a hold’ is an interpretation. ‘It will now rally’ is a forecast and requires much more support than a retest label by itself provides.")
]
s13_7=section('13','Role reversal is a hypothesis, not a switch')
s13_7['blocks']=[
 P("It is tempting to think that once resistance is broken, it automatically becomes support. But a line has no permanent role of its own. The role is a description of how price behaves around that area in the sequence you are studying."),
 P("Before the break, the upper area may have capped several advances. Price then trades above it. Only after a return and the response that follows can you assess whether buyers or sellers are behaving differently around that area. If price returns and stays mostly above it, ‘former resistance is acting as support in this window’ is a fair, limited description. If price closes back inside and cannot reclaim it, the new-role hypothesis weakens. If closes keep alternating across the band, leave it unresolved."),
 P("There is a subtle but important difference between saying **‘the area has reversed roles’** and **‘the area is holding from the other side so far’**. The first sounds permanent; the second tells the reader exactly what the current evidence establishes. I want you to practise the second form until later evidence justifies stronger wording."),
 F('FIG03_context_changes_the_question.png','A local breakout appears different when viewed in the wider chart context.','Role reversal is always a claim about a specific area, timeframe and developing sequence.'),
 P("Also keep the no-retest path alive. Price may never return to the old area. Do not chase it simply because the clean retest you wanted did not appear. The absence of a retest is a missing event, not proof that the breakout is invalid or valid.")
]

# Lesson 14: instructor voice and deliberate elaboration of the failure families, each with observable sequence.
l14=data['14']
l14['time']='55–65 min including Wider Neckline'
l14['summary']='Learn to name the exact claim that failed, identify the contradiction, and decide what remains uncertain without treating every failure as an opposite-side trade.'
l14['hook']='A failed breakout can tell you more than the breakout attempt—but it is not an automatic reverse signal.'
l14['takeaway']='Define the original structure, describe the attempt, point to the contradiction and reassess what remains possible. Keep any stop reference tied to structural invalidation, not an arbitrary distance.'
l14['objectives']=[
 'Distinguish seven common failed-signal structures by the boundary and sequence involved.',
 'Separate an attempted break from later evidence that contradicts the continuation claim.',
 'Compare brief penetration, close back inside, failed reclaim and unresolved overlap.',
 'Describe how gaps, wide bars, pullbacks and volume complicate interpretation.',
 'For a hypothetical failed-breakout idea, identify the structural invalidation extreme and recognise when passing is the better decision.',
 'Review a first interpretation against later evidence without rewriting the original note.'
]
l14['notePrompts']={
 'observation':{'title':'1 · Original structure & attempt','prompt':'Was the boundary a range edge, pivot, trendline or formation edge? Describe the attempted break using only the bars visible at that stage.'},
 'interpretation':{'title':'2 · What contradicted the claim?','prompt':'Point to the exact close or later sequence that weakened the continuation idea. Was it a brief warning, sustained contradiction or still inconclusive?'},
 'alternative':{'title':'3 · What may happen next?','prompt':'Could price continue into the old range, stall, reclaim the boundary or remain mixed? Keep at least one credible alternative alive.'},
 'revision':{'title':'4 · Invalidation & process','prompt':'What observable event would undermine the failure interpretation? For the hypothetical failed-breakout example, identify the failure extreme; if the structural distance is too large, passing is valid.'}
}
# Replace sections 3 through 9 with expanded one-on-one teaching text and new detail figures.
replacements={
'1 · Range-edge upthrust or false upside break':[
 P("Let’s start with the range because it gives us a clear object to study. Before price makes the move, you should be able to point to an upper area that has stopped or slowed several advances. It need not be a perfect horizontal line. Think of it as a band around the cluster of prior highs. Draw it from the evidence available then—not around the highest candle you can find after the move has already happened."),
 P("When price first trades above that band, do **not** call it a failure. You have an upside breakout attempt. Watch three things next: where the bar closes, whether later bars can remain outside, and what happens if price returns to the band. An upper wick above the ceiling followed by a close back inside is a warning that the move did not finish outside. It becomes a stronger failure-like sequence if later price remains in the old range and an attempt to reclaim the ceiling cannot hold."),
 P("Look closely at the chart. First notice the repeated tests near the ceiling; these explain why the area mattered. Then look at the excursion above it. The next bars return into the range. Finally, price tries to approach the upper edge again but cannot establish itself above it. That is the sequence you are describing—not a magical candle shape."),
 F('FIG22_range_edge_upthrust.png','A schematic range shows repeated ceiling tests, an excursion above the range, a return inside and a later reclaim attempt that cannot hold.','A false upside break is identified by the sequence: prior ceiling, excursion, return inside, and subsequent response.'),
 P("Here is a useful way to word the note: ‘Price traded above the prior range ceiling, then closed back inside. The next attempt to reclaim the area failed, so the continuation claim weakened.’ Notice what the sentence does not say: it does not claim to know who bought, who sold, or whether anyone was deliberately trapped."),
 P("Now protect yourself from the opposite mistake. If price closes back inside for one bar and the next bars reclaim the area and remain above it, the failure interpretation has been challenged. Keep that possibility open. The label should follow the sequence, not become a story you defend after new evidence appears.")
],
'2 · Spring-like downside failure':[
 P("Now mirror the same reasoning at the lower edge. First, identify the prior range floor using lows that were visible before the move. Price then trades below support. At that instant, you have a downside-break attempt. The later response tells you whether the break is sustaining itself or whether price has returned to the old range."),
 P("Watch the low and the close separately. The low records how far the excursion travelled below the floor. The close tells you where that bar finished. If the close returns inside the range, the breakdown claim has weakened; if later bars remain inside and a renewed push below support cannot hold, the failure-like interpretation becomes stronger. If price keeps overlapping around the floor, do not force the label."),
 F('FIG23_spring_downside_reclaim.png','A range-floor excursion moves below support, returns to the old range, and is followed by a recovery sequence.','A spring-like downside failure is described by the probe below support and the return; the later response determines how convincing the interpretation is.'),
 P("You may hear this pattern called a ‘spring’ or a ‘bear trap’. Use the short name only after you can describe the bars that justify it. The name does not prove that anyone set a trap, and it does not guarantee a rally. After returning inside, price may advance, stall, or later break the range floor for real. The same discipline applies as on the upside: observe the excursion, the close, the return and what happens next."),
 P("One extra caution: the lowest wick is not automatically the best boundary for every analysis. The floor should come from the prior structure. Do not redraw support around the failure low just to make the story look neat. That lower extreme belongs in your note as part of the event, not as a replacement for the original range edge.")
],
'3 · Trendline penetration and reclaim':[
 P("A trendline is different from the range ceiling you just studied. It is a sloping reference drawn through prior swing points, so it describes the angle of a sequence rather than a flat boundary. Before reading a break, ask yourself which pivots anchor the line and whether those pivots were reasonably clear at the time. A line drawn only after price turns can explain the past in a convincing way without having been a useful reference beforehand."),
 P("When price crosses the line, record the event—but do not immediately declare the trend dead. A wick through the line may be an excursion. A close through it adds evidence. A later reclaim may challenge the idea that the trend has broken. Conversely, a reclaim that immediately fails again adds a different kind of evidence. You need to look at how price behaves around the line, not only whether one candle crossed it."),
 P("Then widen the question from the line to the swing structure. In an advancing sequence, are the higher lows still intact? Has price also broken a prior swing low? Is the broader structure still rising even though the local line failed? If the line is broken but the key swing structure remains intact, describe that distinction. If important pivots also give way and later attempts to recover them fail, you have a stronger case that more than the line has changed."),
 F('FIG17_range_vs_trendline_failure.png','A horizontal range-boundary failure and a sloping trendline penetration/reclaim are shown as distinct structures.','A trendline break and a range break are different observations. Describe the reference before naming the failure.'),
 P("Try to write the narrowest defensible sentence first: ‘Price crossed below the rising trendline and later reclaimed it; the prior higher-low structure remains intact.’ Or: ‘Price crossed below the line, broke the prior swing low and could not reclaim it.’ Those two sentences describe different evidence. Neither requires you to predict the next move.")
],
'4 · A prior swing break that is quickly surrendered':[
 P("Now forget the full range for a moment and focus on one prior pivot. A swing high or swing low is a local turning point that was visible before the test. Mark it before the later candles arrive. The idea here is simple: price moves beyond that pivot but quickly gives the break back. The pivot break is the attempt; the reversal through the level is the contradiction."),
 P("For an upside test, watch price trade above the prior swing high. If the bar closes back below the pivot, the breakout attempt has not held through the close. If the following bar then moves lower and the market continues to trade beneath the pivot, the failure-test interpretation gains weight. If price immediately reclaims the pivot and remains above it, the failure label has itself been challenged. The downside version is the mirror image: price trades below a prior swing low, then returns and closes back above it."),
 F('FIG24_prior_swing_failure_test.png','Price advances through a pre-existing swing high, then closes back below the pivot and extends lower in the schematic example.','A pivot failure needs a visible prior reference and a reversal that surrenders the break; a wick alone is not the full sequence.'),
 P("Do not confuse this with a broad range-edge failure. A pivot can be crossed while price remains inside a much larger range. That still matters as a local event, but its significance depends on the surrounding structure. Also, be wary of pivots that become obvious only after the reversal. A level should be identifiable from earlier bars; otherwise you may be explaining the chart after the fact."),
 P("The useful question is not ‘Did the market take the high?’ It is ‘What happened after the high was taken?’ A break that continues to hold and a break that is quickly surrendered start with the same event and develop into different sequences.")
],
'5 · A continuation pause breaks the wrong way':[
 P("A flag, pennant or compact pause is often read as a rest before the prior move continues. That is a reasonable hypothesis to test, not a promise built into the shape. First identify the movement leading into the pause. Then outline the pause boundaries using the bars already visible. Ask which side would represent the expected continuation and which side would challenge it."),
 P("Now follow the actual close at the edge. If price breaks in the expected direction and remains outside, the continuation idea is still viable. If it moves through the opposite edge, the expected direction has lost support. If it briefly breaks one side and returns into the pause, you may have an unresolved or failed attempt rather than a clean resolution. A name like ‘flag’ does not rescue the thesis from evidence that goes the other way."),
 F('FIG25_continuation_pause_outcomes.png','Two similar compact pauses are shown resolving differently: one holds beyond the expected upper edge, while the other breaks through the lower edge.','Compare the outcome with the original continuation idea. A pause can resolve in more than one direction.'),
 P("Let’s make the review concrete. What was the direction of the move before the pause? Which edge was the expected continuation edge? Where did the relevant bar close? Did later price remain outside or return? If price breaks the opposite edge, write that the continuation interpretation was challenged. Do not rename every adverse move a ‘shakeout’ unless the later sequence actually supports a renewed continuation."),
 P("This is also where the wider market state matters. A small pause may be only a minor interruption inside a larger range. A break of the pause can be locally clear without being a breakout from the larger market structure. Describe both scales if they disagree.")
],
'6 · The first pullback holds; a later pullback fails':[
 P("This is one of the easiest situations to misread because the first return can look persuasive. Price breaks above the range ceiling, returns towards the old area, holds mostly above it and then advances. You can reasonably describe that first sequence as hold-like. But do not turn one visit into a universal rule that the former ceiling will always behave as support."),
 P("When price comes back again, treat it as a new test. Compare the second return with the first. Did it penetrate deeper? Did the relevant bar close inside the band or the old range? Was the next push away weaker? Did price break the swing low that supported the earlier continuation? Those are concrete differences you can point to. A later pullback that closes back inside the old range and cannot reclaim the ceiling weakens the role-reversal idea, even though the first pullback genuinely held."),
 F('FIG11_first_pullback_later_failure.png','An initial return holds above the old boundary; a later return travels farther into the area and challenges the role-reversal interpretation.','One holding response describes one visit. It does not guarantee the next return.'),
 P("Avoid the opposite oversimplification too. A deeper retest is not automatically a failure, and a shallow touch is not automatically strong. The full candle sequence matters: depth, close, the reaction after the return, and the surrounding swing structure. Keep both visits in view so that the second one does not erase your record of what happened during the first."),
 P("A useful note might read: ‘The first pullback stayed above the prior ceiling and price moved higher. The second return closed inside the band, then failed to reclaim the old edge; the role-reversal interpretation weakened.’ That is a better review than saying ‘support failed’ without showing what changed.")
],
'7 · A neckline break in a top or bottom formation fails':[
 P("A neckline is the reference boundary in a formation such as a double top or double bottom. You do not need to turn this lesson into a full course on those patterns. Use the neckline to study the same question you have been asking throughout this module: did price stay beyond the boundary it broke, or did it return through it?"),
 P("For a top formation, suppose price breaks below the neckline. First ask where the bar closed, then whether subsequent bars stayed below. If price reclaims the neckline and remains above it, the breakdown interpretation has been challenged. For a bottom formation, reverse the direction: price breaks above the neckline, but later closes back beneath it and cannot reclaim it. The original pattern label is not enough to settle the event."),
 F('FIG18_neckline_formation_failures.png','A top-formation breakdown is reclaimed and a bottom-formation breakout returns beneath its neckline.','The formation supplies the boundary; the response still determines whether the break is holding.'),
 P("Why include this example? Because a named pattern can create confidence before the evidence has earned it. You may recognise a familiar shape and start anticipating its expected outcome. Instead, state the pattern boundary, the break attempt, the reclaim or reversal, and whether later bars support the original direction. A failed neckline break is another instance of a claim being contradicted—not proof that the opposite move must travel a measured distance."),
 P("If the bars are mixed around the neckline, stay with the mixed description. You can say ‘the breakdown attempt has not established itself below the neckline’. That is more precise than either ‘the top is confirmed’ or ‘the pattern has failed’ when the chart has not yet made the answer clear.")
]
}
for title, blocks in replacements.items():
    sec=section('14',title)
    sec['blocks']=blocks

# Expand contradiction grading and stop placement, ensuring the only stop-loss teaching/markers live in Lesson 14.
sec=section('14','How strong is the contradiction?')
sec['blocks']=[
 P("Let’s not stamp every return with the same word. Evidence has degrees. A brief wick back inside the zone is a warning. A close back inside is a clearer contradiction to a claim that price is sustaining itself outside. Several closes inside, followed by a reclaim attempt that cannot hold, make the continuation interpretation harder to defend. If price later reclaims the area and remains outside again, the failure interpretation is challenged in turn."),
 P("Use this as a description ladder, not a universal scoring rule. The relevant timeframe, volatility and session all matter. One daily candle is not interchangeable with one five-minute candle. Your task is to state the rule you are using and identify the event that changed the interpretation—not invent a magic candle count that makes all markets behave alike."),
 UL([
  '**Warning:** a wick or brief excursion returns through the boundary, but the close and next response are not yet clear.',
  '**Contradiction:** the bar closes back inside the original area, challenging the claim that price is sustaining itself outside.',
  '**Stronger contradiction:** later closes remain in the old range or repeated reclaim attempts fail.',
  '**Reassessment required:** a subsequent reclaim and renewed holding action challenges the failure label itself.',
  '**Still unresolved:** price overlaps around the boundary, with closes alternating and no sustained response.'
 ]),
 F('FIG15_failure_label_checklist.png','A structured checklist distinguishes the original signal, breakout attempt, contradiction and subsequent response.','Use the checklist to discipline the description, not to produce a mechanical verdict.')
]
sec=section('14','Where does a stop belong in a failed-breakout idea?')
sec['blocks']=[
 P("This is the only lesson in this module where I mark a stop-loss on the chart, because we are discussing a specific hypothetical failed-breakout idea—not an ordinary breakout, retest or role-reversal diagram. The principle is structural: if the setup depends on price failing beyond an extreme, ask what price level would contradict that failure interpretation."),
 P("Consider a possible short after an upside failure. Price pushes above a prior range ceiling, then returns and closes back inside. If the short-side idea is based on that excursion failing, the high of the failure move is important. A stop reference just beyond that high is intended to say: ‘If price reclaims and exceeds the failure extreme, the reason for this short-side interpretation is under pressure.’ Placing the stop just over the original zone without checking the failure high may leave it inside the very move that created the failure."),
 P("Sometimes the failed move is evident on the same bar: price trades above resistance, then closes back below it. Sometimes the first bar closes outside and only the following bar reverses back into the range. In the second case, the new extreme made during that sequence may be the more relevant structural reference. The drawing shows the principle, not a required entry trigger or a one-size-fits-all buffer."),
 P("For a possible long after a downside failure, reverse the logic. Price probes below the prior floor and then reclaims it; the low of that failure move is the point the idea must survive. A stop reference beyond that low expresses the invalidation. In either direction, choose the reference because it changes the technical explanation—not because a standard number of ticks sounds tidy."),
 P("Now the practical limitation: if the distance to that structural point is too large for your risk limit, the answer is not to squeeze the stop into ordinary noise just to make the trade fit. You may reduce exposure, wait for a different structure, or pass. A stop order is not a guaranteed fill at the stop price; gaps and fast markets can result in worse execution. And a failure interpretation by itself is not a complete trade plan."),
 F('FIG21_failed_breakout_structural_stop.png','Two hypothetical failed-breakout sequences show the stop reference beyond the failure high for a possible short and beyond the failure low for a possible long.','Stop markers appear only in failed-breakout examples. They illustrate structural invalidation, not a trade signal.')
]

# Keep the v2 simple retest diagrams before the v3 complex views and one volume lesson in L12.
assert sum('volume' in x['title'].lower() for x in l12['sections'])==1
assert section('13','Three observations: break, return, response')['blocks'][-2]['src'].endswith('FIG19_simple_break_return_response.png')
assert section('14','Where does a stop belong in a failed-breakout idea?')['blocks'][-1]['src'].endswith('FIG21_failed_breakout_structural_stop.png')
assert not any('stop-loss' in (b.get('text','').lower()) or 'stop loss' in (b.get('text','').lower()) for lid in ('12','13') for sec in data[lid]['sections'] for b in sec['blocks'])
# Keep the reading voice direct: no bibliography or named-source attribution is inserted into student copy.
learner_text=json.dumps({k:data[k] for k in ('12','13','14')},ensure_ascii=False).lower()
if re.search(r'\baccording to (?:the author|the book|a named source)\b|author attribution', learner_text):
    raise ValueError('Source attribution language belongs in the separate internal research note.')
JS.write_text('window.MODULE5_DEEP_CONTENT = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print('Prepared expanded instructor-led v5 lesson content.')
print('Sections:', {k:len(data[k]['sections']) for k in ('12','13','14')})
