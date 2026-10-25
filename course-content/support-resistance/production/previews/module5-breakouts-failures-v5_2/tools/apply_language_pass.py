from pathlib import Path
import json, re
ROOT = Path(__file__).resolve().parents[1]
JS = ROOT/'assets/module5-deep-content.js'
raw = JS.read_text(encoding='utf-8')
data = json.loads(re.search(r'window\.MODULE5_DEEP_CONTENT\s*=\s*(\{.*\})\s*;\s*$', raw, re.S).group(1))
P=lambda text:{'type':'p','text':text}
Q=lambda text:{'type':'quote','text':text}
F=lambda file,alt,caption:{'type':'figure','src':f'assets/figures/{file}','alt':alt,'caption':caption}
UL=lambda items:{'type':'ul','items':items}
TABLE=lambda headers,rows:{'type':'table','headers':headers,'rows':rows}
def section(lid,title):
    arr=data[str(lid)]['sections']
    found=[s for s in arr if s['title']==title]
    if len(found)!=1: raise ValueError(f'L{lid}: expected one section {title!r}, found {len(found)}')
    return found[0]
def set_blocks(lid,title,blocks): section(lid,title)['blocks']=blocks
def rename_section(lid,old,new):
    titles=[s['title'] for s in data[str(lid)]['sections']]
    if old in titles:
        section(lid,old)['title']=new
    elif new in titles:
        return
    else:
        raise ValueError(f'L{lid}: cannot find section to rename: {old!r} or {new!r}')

# LESSON 12 — explain from the learner's point of view and let the evidence do the work.
data['12']['summary'] = 'Learn to tell a brief move beyond a zone from a move that begins to hold outside it. We will compare the clues and their trade-offs.'
data['12']['hook'] = 'A close beyond a line is evidence. It is not a verdict.'
data['12']['takeaway'] = 'Describe what crossed the zone, say which rule you used, then watch what price does next.'
data['12']['objectives'] = [
 'Mark a useful zone using price behaviour that came before the move.',
 'Tell the difference between a wick beyond a zone and a candle close beyond it.',
 'Compare close, distance, time and volume as clues, including what each can miss.',
 'Keep a second possible explanation open while the chart develops.'
]
set_blocks(12,'Start with the question',[
 P("Imagine price has just moved above an area that stopped it several times before. Is that a breakout, or has price only poked above the area for now? The first candle rarely answers the whole question. We can make a better judgement by describing what happened, then watching what comes next."),
 Q('A close beyond a line is evidence. It is not a verdict.'),
 P('In this lesson, **continuation** simply means price keeps moving in the direction of the break. We will watch the later candles to see whether that happens.')
])
set_blocks(12,'First name the boundary',[
 P("Start with the chart before the move. Which earlier highs, lows or range edge make this area worth watching? Mark the area first, while the later candles are still hidden. That gives you a fair reference point for judging the move."),
 P("A **zone** is an area, not a price that must hold to the last tick. Once you have drawn it, keep it in place while you review the next candles. If you later decide the zone should be wider, narrower or somewhere else, that is allowed—just record the change and the reason for it."),
 P("A move outside the zone may be the start of a new direction. It may also be a brief move that returns to the old range. At first, call it a **breakout attempt**. Let the later candles help you decide how well the move held up.")
])
set_blocks(12,'Four kinds of evidence',[
 P("Four clues are easy to mix together, so let's keep them separate. A **wick** beyond the zone shows that price traded there during the candle. A **close** beyond it tells you where the candle finished. **Time or distance outside** tells you whether price stayed beyond the area and how far it travelled. **Follow-through** is what later candles do: they may keep moving away, stall, or come back through the zone."),
 P("Each clue adds something, but none predicts the next candle. A close just outside the band can fail. Several closes can fail too. That's not a reason to ignore the evidence; it's a reason to describe what each piece tells you—and what it leaves open."),
 P("Volume may add useful context when the feed is reliable and you know what it measures. We will look at that later. The historical example in this lesson shows price only, so use the candles that are actually on screen.")
])
set_blocks(12,'Every filter has a cost',[
 P("A **filter** is a rule you decide to use before judging a move. For example, you might require a candle to close outside the zone, a minimum distance beyond it, or two closes in a row. A clear rule helps you read similar situations in a similar way."),
 P("Every rule also has a cost. Waiting for a close can screen out some brief wicks, but a close just outside may still fail. Waiting for two closes adds another check, but you will recognise some moves later. A distance rule may ignore tiny crossings, yet the price can travel a long way before it meets your threshold."),
 P("I would write down the rule I used before looking at the ending. Then I would ask two questions: what kind of false start might this rule help me filter out, and what kind of real move might it make me recognise late? No filter catches everything.")
])
set_blocks(12,'The market state still matters',[
 P("Before you decide how important a break is, take one step back. The **timeframe** is the length of each candle—for example, five minutes or one day. A break on a short chart can still sit inside a much wider range on a daily chart."),
 P("Try looking at the same move on a nearby timeframe. Has price left the larger range, or has it only crossed a small local high? The answer can change how much weight you give the move. Neither view is automatically wrong; they are answering questions at different scales."),
 P("For this lesson, focus on describing the chart, not choosing a trade. Say what the move has shown so far, what it has not shown, and what you would watch next.")
])
set_blocks(12,'The range is a market state, not just a shape',[
 P("A range is a period when price moves back and forth between an upper area and a lower area without getting far beyond either one for long. The edges matter because price has reacted around them before. That history gives the next crossing some context, but it does not tell us which side will hold next."),
 P("When price leaves a range, two paths can begin with very similar candles. One move keeps travelling outside the range. Another slips back inside. At the start, they can look alike. The difference becomes clearer as later candles arrive."),
 F('FIG03_context_changes_the_question.png','Two schematic charts show a local breakout that looks decisive when zoomed in, while the same movement remains inside a higher-timeframe range.','A local break can be clear while the wider market is still ranging.')
])
set_blocks(12,'The evidence ladder: wick, close, acceptance, follow-through',[
 P("Here is a quick reference you can keep beside your chart. Read from left to right: what you can see, what it supports, and what it cannot promise. **Acceptance** simply means price spends time beyond the area and continues to hold there; it is a description, not a special signal."),
 TABLE(['What you see','What it tells you','What it does not tell you'],[
 ['A wick passes the edge','Price traded beyond the zone during the candle.','The candle may still close back inside.'],
 ['The candle closes outside','The candle ended beyond the chosen edge.','The next candle does not have to stay there.'],
 ['Price spends time outside','The move has remained beyond the zone for a while.','The move is not guaranteed to continue.'],
 ['Later candles hold or move farther away','The idea of a sustained break has more support.','The market can still return through the zone.'],
 ['Price returns into the old range','The claim that price is holding outside has weakened.','A move in the opposite direction is not guaranteed.']
 ]),
 F('FIG01_breakout_evidence_ladder.png','Three schematic price sequences compare intraday penetration, a candle close outside the zone, and follow-through in later candles.','The evidence can grow. Certainty does not grow at the same rate.'),
 P("For example, a daily close a little above resistance means the day ended beyond the area you chose. That's more information than a wick alone. But it is not the same as knowing that buyers will keep pushing price higher. That part has not happened yet.")
])
rename_section(12,'Confirmation filters move the decision point; they do not remove risk','Different rules recognise a move at different times')
set_blocks(12,'Different rules recognise a move at different times',[
 P("Compare what each rule asks you to wait for. A close-based rule uses where the candle finishes. A distance rule waits until price has moved farther beyond the zone. A two-close rule asks you to wait for another bar or session. The same price move may meet these rules at different times."),
 P("Waiting for more evidence can help you screen out brief crossings, but it usually means recognising a move later. A faster rule lets you assess the move sooner, but you will also see more attempts that return inside. Choose a rule you can explain, then keep using it long enough to review its trade-offs."),
 F('FIG02_filter_tradeoffs.png','Two schematic cases show a stricter rule recognising a move later and a price sequence that meets a filter but later reverses.','A rule changes when you recognise a move; it cannot choose the outcome.'),
 P("For the examples in this lesson, we will use a daily close beyond the marked zone as our working rule. It gives us one consistent way to compare the charts; it is not a rule every trader must use.")
])
set_blocks(12,'Volume: useful context, not a verdict',[
 P("Now that we have separated the wick, close and later follow-through, let's ask a different question: does volume add useful context? Sometimes it does. But volume is not a referee that declares a breakout valid or false."),
 P("In the figure, compare price behaviour first. Two sequences move away from the zone and two return through it. Then compare the volume panels. Expanding activity appears in a holding sequence and in a failing one; muted activity also appears in both. Volume and price outcome are different observations, and one cannot stand in for the other."),
 P("Before you call activity 'high', check the data feed. Listed shares and exchange-traded futures commonly report traded volume, though the source still matters. Spot FX and some CFDs may show tick volume or broker-specific activity instead of one consolidated exchange record. Compare like with like: the same instrument, similar sessions and a clear baseline. If you do not have that information, leave the volume claim out."),
 F('FIG08_volume_context_not_gate.png','Four longer price sequences are paired with volume panels: price holds or fails with expanding or muted volume.','Compare what price did with what volume adds. Keep the two observations separate.'),
 P("Here is how I would write it in a journal: 'Price closed above the zone and held there for three bars. Activity was higher than in the previous part of this chart, which adds context, but the later outcome is still open.' That says what you saw without guessing who traded or why. This lesson's historical case does not include volume, so volume cannot explain its ending.")
])
set_blocks(12,'What the historical case can teach—and what it cannot',[
 P("The NIFTY 50 chart gives us a useful practice case. At first, price has a candidate upper zone. Then several daily candles close above it. Later, price comes back below the same band. We will reveal those stages one at a time so you can write down what you think before seeing the ending."),
 P("At Stage 1, I would note the earlier highs that make the band worth watching and say what I will count as a break. At Stage 2, several closes above the band give the breakout attempt more support. At Stage 3, the move back below the band weakens the idea that price was holding above it."),
 P("Notice what has changed: the evidence, not the past. The closes above the zone really did happen. The later return really did happen too. A good review keeps both facts and updates the interpretation. It does not need to explain why the market moved or pretend the ending was obvious from the beginning."),
 F('FIG09_decision_record_timeline.png','A four-stage timeline shows why an area was selected, what changed at the break, what later challenged the first idea, and how to review it.','Keep the first view and the later revision so you can see why your thinking changed.')
])
set_blocks(12,'Acceptance is a useful description, not a secret confirmation rule',[
 P("You may hear traders say price has been 'accepted' above a level. In plain English, they mean it has spent time there and has not immediately fallen back through the area. That can be a helpful description of the chart."),
 P("The word does not turn the move into a guarantee. A price can hold above a zone for several candles and later return below it. When you use the term, explain what you mean: how many bars, which closes, and which area are you talking about? That lets another reader follow your reasoning."),
 F('FIG04_break_return_response.png','A schematic breakout sequence shows the break, later return and the response after the return.','Use the word acceptance only after you can point to the behaviour it describes.')
])
set_blocks(12,'Three questions to ask before keeping a breakout interpretation',[
 P("When the chart has given you a few more candles, pause and ask: (1) Is price still outside the zone I marked? (2) Are the closes and the surrounding structure consistent with a move holding beyond it? (3) What evidence would make me change my mind?"),
 P("Your current answer can be 'the break still looks plausible', 'the idea has weakened', or 'I cannot tell yet'. You do not need to force a confident label just because the lesson is about breakouts."),
 F('FIG12_after_failure_alternatives.png','A schematic branch illustrates possible paths after a breakout attempt is challenged.','A clear description can still leave more than one future path open.')
])
rename_section(12,'A filter is a personal convention that must be audited','How to review the rule you chose')
set_blocks(12,'How to review the rule you chose',[
 P("After you have reviewed several examples, look at more than the ones that worked. Ask what your rule helped you ignore, which moves it made you recognise late, and whether you applied it the same way each time. This is how you learn whether a rule suits the instrument and timeframe you are studying."),
 UL([
  '**It helped when:** which brief crossings did the rule screen out?',
  '**It cost me when:** which moves had already travelled before the rule was met?',
  '**I would keep or change it because:** what did you see across several examples, not just one?'
 ]),
 P("Here is what I would add to my journal: 'I waited for two closes. It helped me ignore one quick return inside, but on this example I recognised the move a bar later.' That is a useful review because it records both sides of the trade-off.")
])
set_blocks(12,'The note should preserve the rule you actually used',[
 P("A useful note is short and specific. It says which zone you marked, which rule you used, what price did, and what you would watch next. It does not need to sound technical to be good."),
 P("**Weak note:** 'Confirmed breakout. Strong move.'"),
 P("**A more useful note:** 'Price closed above the prior range ceiling on my daily-close rule. That supports a breakout attempt. I will reconsider if price closes back inside the range.'"),
 P("The second note is stronger because another person can see what you observed and what would change your view. That is the habit we are building. You can be wrong about the next move and still have made a careful read of the chart.")
])

# LESSON 13 — retain the simple-first visual progression while making the narration feel like a teacher.
data['13']['summary'] = 'Learn to separate the break, the return and the response. A retest gives you another clue, but it cannot tell you in advance whether the old area will hold.'
data['13']['hook'] = 'A retest gives you another clue, not a guarantee.'
data['13']['objectives'] = [
 'Separate the first break from a later return towards the zone.',
 'Describe how far price returns into the area and where the candle closes.',
 'Compare a response that holds, one that fails, and one that is still unclear.',
 'Explain why an old resistance area may act as support, without assuming it will.',
 'Keep your first read so you can compare it with later evidence.'
]
set_blocks(13,'Start with the question',[
 P("Price has moved above an area that held it back before. Later, it comes back towards that area. This return is often called a **retest**. Start by asking how far price came back, where the candle closed, and what happened next. The name describes the event; it does not tell us whether the area will hold."),
 Q('A retest gives you another clue, not a guarantee.')
])
set_blocks(13,'Three observations: break, return, response',[
 P("Let's slow this down. The **break** is the first move beyond the zone. The **return** is when price comes back towards it. The **response** is what price does after the return. Those are three separate events, even when traders use one word—'retest'—for the whole sequence."),
 P("On the first chart, point to the break. On the second, find the return. On the third, see how price reacts. A return can stop short, touch the edge, move deep into the band, close back in the old range, or cross the whole zone. The next bars may move away again or keep crossing back and forth."),
 F('FIG19_simple_break_return_response.png','A simple three-panel illustration separates the break beyond an old resistance area, the return towards it, and the response that follows.','Start simple: find the break, then the return, then the response.'),
 P("A good first note might be: 'Price closed above the old resistance area, later returned to its edge, and then moved away while staying above it.' That sentence describes a hold-like response. It does not promise that the area will hold on the next visit."),
 P("Keep this order in mind: the break tells you where price went; the return tells you it came back; the response tells you what happened next. You can only describe the last part after you have seen it.")
])
set_blocks(13,'The depth of the return matters—but does not settle the outcome',[
 P("A return can stop just above the band. It can touch the edge, enter a little, move deep into the area, or close back in the old range. Those are useful differences because they show how much of the earlier range price has moved back into."),
 P("Watch the wick and the close separately. A candle may dip into the band and still finish above it. Another may close well inside the old range. The second is a clearer challenge to the idea that the old resistance area is now holding price up—but the next bars still matter."),
 UL([
  '**No return:** price keeps moving away. There has not been a retest to judge.',
  '**Shallow touch:** price reaches the near edge and moves away. That may fit a hold, depending on the close and what follows.',
  '**Deep return:** price moves well into the band. Check whether later closes are moving back into the old range.',
  '**Close inside the old range:** the idea that price is holding outside the range has weakened.',
  '**Cross and reclaim:** price passes through the band, then moves back above it. Keep both events in your record.',
  '**Repeated overlap:** candles keep crossing the band. The answer may still be unclear.'
 ]),
 F('FIG16_retest_depth_and_closes.png','Four schematic examples distinguish a shallow touch, a deeper entry, a close back inside the range, and a move through the band.','The depth of the return and the closing price are two different clues.'),
 P("If you later redraw the zone, that's fine. Just keep the original one visible in your notes and explain what new evidence made you change it. This is how you can tell whether the idea improved—or whether the new drawing simply fits the ending better.")
])
set_blocks(13,'Three responses that share the same name',[
 P("Now look at the response after the return. In a **hold-like** response, price turns away from the zone and mostly stays on the new side. That supports the idea that the old area may be acting differently, at least in this part of the chart."),
 P("In a **failure-like** response, price moves back through the band and closes in the old range. If it then tries to reclaim the area and cannot stay above it, the role-reversal idea becomes harder to defend."),
 P("An **inconclusive** response is simply one that is not clear yet. Price may keep crossing the band, with candles closing on both sides. You have not missed a secret answer; the chart has not given a clear one."),
 F('FIG20_simple_retest_outcomes.png','Three simple candlestick examples compare a hold-like response, a failure-like response and an inconclusive return.','Three broad outcomes: holds for now, fails for now, or still unclear.'),
 P("The simple picture gives you the basic map. The longer examples add more candles and less tidy movement. As you look through them, keep asking the same questions: where was the boundary, how deep was the return, where did price close, and what did it do afterwards?"),
 F('FIG05_three_retest_outcomes.png','Three longer price sequences compare hold-like, failure-like and inconclusive retest outcomes.','Longer sequences can add evidence—or leave the answer mixed.')
])
set_blocks(13,'A four-stage view: before, break, return, response',[
 P("It can help to look at a chart in stages. First, study the old area without seeing the breakout. Then reveal the break. Next, look at the return. Only then look at the later response. This stops the final picture from colouring how you remember the beginning."),
 F('FIG04_break_return_response.png','A schematic sequence shows the break, return and response as separate moments in time.','Look at the same area through the sequence, not only at the final chart.'),
 P("When you do this, keep your first note. After the final stage, add a second note that says what changed. The aim is not to guess the last candle; it is to explain why your view became stronger, weaker, or stayed uncertain.")
])
rename_section(13,'The market does not owe you a retest','Some breakouts never retest the zone')
set_blocks(13,'Some breakouts never retest the zone',[
 P("Some moves continue without coming back to the old area. That is a normal possible path, not an incomplete chart. If your rule requires a retest, you are choosing to wait for that extra evidence. Sometimes it will arrive; sometimes price will keep moving without it."),
 P("A missing retest does not by itself prove that the breakout is valid or false. It simply means there is no return to assess in the window you are studying. You also do not need to chase a move just because the clean retest you hoped for never appeared."),
 F('FIG06_retest_is_not_owed.png','Several breakout paths show that some moves return while others continue without a retest.','A retest is one possible path, not a required step.')
])
rename_section(13,'Role reversal is a hypothesis, not a switch','Role reversal is possible, not automatic')
set_blocks(13,'Role reversal is possible, not automatic',[
 P("After price breaks above resistance, traders often watch to see whether that old ceiling may act as support. After a break below support, the reverse question is whether the old floor may act as resistance. This possible change in behaviour is called **role reversal**."),
 P("The key word is 'may'. The boundary does not change roles automatically because price crossed it once. If price returns and stays on the new side, the idea gets some support. If it closes back inside the old range and cannot reclaim the area, the idea weakens. If candles keep overlapping around the band, the answer may still be unclear."),
 F('FIG17_range_vs_trendline_failure.png','A horizontal range-boundary failure and a sloping trendline penetration/reclaim are shown as distinct structures.','The same question applies to a range edge or trendline: what happened after the break?'),
 P("A trendline deserves one extra check because it is drawn through earlier swing points and slopes across the chart. Ask whether those turning points were clear before the break. Then look at the wider swing structure. A line may break while the larger pattern of higher lows or lower highs remains in place."),
 P("I'd write what I can see before using a pattern name: 'Price moved below the rising trendline, then reclaimed it. The prior higher low is still intact.' Or: 'Price crossed the line, broke the prior swing low, and has not reclaimed it.' The two notes describe different evidence without pretending to know the next move.")
])
set_blocks(13,'A return gives you evidence, not a story about motive',[
 P("A boundary may matter because many people are watching the same area, but a chart does not show us what each person intended to do there. We can see the prices that traded, the highs and lows, and where the candle closed. We cannot tell from those bars alone whether someone deliberately defended the zone or set a trap."),
 P("You do not need to explain who was behind the move to read it well. Describe the return and the response. That gives you something another learner can check against the same chart.")
])
set_blocks(13,'What the historical case can teach—and what it cannot',[
 P("The staged NIFTY 50 example starts with an area that held back earlier advances. The next view shows price moving above it. Later, price comes back towards the area and then remains above it in the selected window."),
 P("That later behaviour supports a hold-like reading for this example. It does not prove the old area will always act as support, or that every breakout should be bought on a return. Another chart may show a deeper return or repeated closes back inside the range."),
 P("Some studies of named chart patterns have counted how often price returns towards a breakout area. Those results depend on the patterns, markets and timeframes they studied. They are not a reliable percentage for every zone we draw by hand. Use this example to practise describing the sequence, not to borrow a probability for a different chart."),
 F('FIG09_decision_record_timeline.png','A sequence of decision points shows how a view can be recorded and then updated as later evidence appears.','Preserve the first read so the revision has something real to compare with.')
])
set_blocks(13,'Your field note: keep the first read',[
 P("Here is what I would put in my own journal: first, what I saw; second, what I thought it might mean; third, what else could happen; and fourth, what would make me change my mind. You do not need elaborate language. Exact details are more useful than impressive-sounding labels."),
 P("**Weak note:** 'Retest successful. Resistance became support.'"),
 P("**A stronger note:** 'Price closed above the old resistance area, returned towards the band, and then moved higher while staying above it. That is consistent with a hold for now. Repeated closes back inside the old range would weaken this reading.'"),
 P("The stronger note is useful because it shows the sequence and keeps the claim limited. After the final reveal, compare it with your first answer. Which part still fits? Which part would you update? Getting the final direction right is not the test; explaining the evidence is.")
])

# LESSON 14 — reduce the intimidation factor while retaining the seven failure families and risk boundaries.
data['14']['summary'] = 'Learn to recognise different ways a breakout attempt can fail, describe the evidence in plain language, and keep more than one next path in mind.'
data['14']['takeaway'] = 'Name the original structure, describe the break attempt, point to the later evidence that changed the reading and ask what may happen next. If you study a stop, tie it to the price that would weaken your failure idea—not an arbitrary number.'
data['14']['objectives'] = [
 'Recognise several ways a move beyond a boundary can lose support.',
 'Point to the exact evidence that weakens the original idea.',
 'Compare an early warning with stronger evidence against the first idea.',
 'Explain why a failed breakout does not guarantee a move in the opposite direction.',
 'Use a hypothetical failure example to understand a price level that would undermine the idea, and know when passing may be safer.',
 'Review the first read without judging it only by the eventual outcome.'
]
set_blocks(14,'Start with the question',[
 P("Let's keep two moments apart. First, price moves beyond an area. We don't know yet whether it will hold there. Later, price may return through the area or fail to continue. That later behaviour is what can weaken the first idea."),
 Q('A failed breakout is not the first candle that crosses. It is the evidence that challenges the first idea.'),
 P("In this lesson, a **thesis** just means your current explanation of what the chart may be showing. If you think price is beginning to hold above resistance, that is your thesis. New candles may support it, weaken it, or leave you unsure. Changing your mind when the evidence changes is part of the job.")
])
rename_section(14,'Before we name the failure, define what price was trying to cross','First, name the boundary')
set_blocks(14,'First, name the boundary',[
 P("Start with a reference you could have marked before the move: the edge of a range; a prior swing high or low (a local turning point); a trendline; a continuation pause (a short rest after a move); or a neckline (an area used to judge a formation such as a double top or double bottom). Each is a different kind of boundary. The same candle can mean different things depending on which one price is crossing."),
 P("Then record the attempt. Did only the wick move outside? Did the candle close beyond the area? Did several bars stay there? Only after that should you look for evidence that challenges the first reading."),
 F('FIG10_failed_signal_family.png','Four schematic examples show a range break, trendline penetration, continuation-pause break and prior swing break that later lose follow-through.','These are different chart structures, but the same review question applies: what did price do after the break?'),
 P("If I were reviewing the chart with you, I'd keep four moments separate: the old structure, the move beyond it, the return or other challenge, and what price did next. We call it a failure when later candles challenge the first idea—not just because one candle crossed the line.")
])
# The seven structure sections were expanded in the package build. Apply modest, meaning-preserving voice cleanups.
for title, blocks in {
'1 · Range-edge upthrust or false upside break':[
 P("Let's start with a range, because the ceiling gives us a clear place to look. Before price moves, you should be able to point to an upper area that has slowed or stopped several advances. It need not be a perfect line; a band around the earlier highs is often more realistic."),
 P("When price first trades above the band, call it an upside-break attempt. Then check the close and the next few bars. A wick above the ceiling followed by a close back inside tells you the move did not finish outside. If price stays in the range and a later attempt to move above the ceiling also fails, the case for a false upside break becomes stronger."),
 F('FIG22_range_edge_upthrust.png','A schematic range shows repeated ceiling tests, an excursion above the range, a return inside and a later reclaim attempt that cannot hold.','The sequence matters: old ceiling, move above it, return, and later response.'),
 P("A useful journal note would be: 'Price traded above the range ceiling, then closed back inside. The next attempt to reclaim the area did not hold, so the continuation idea weakened.' Notice how much that tells us without guessing who bought or whether anyone was trapped."),
 P("There is another possible path. Price might close back inside for one bar and then reclaim the area, staying above it. If that happens, the failure reading needs to be reconsidered. Keep following the candles rather than getting attached to the name.")
],
'2 · Spring-like downside failure':[
 P("Now look at the lower edge of a range. Mark the floor from the lows that were visible before the move. If price trades below support, you have a downside-break attempt. The next question is whether price stays below or returns into the old range."),
 P("Compare the low with the close. The low shows how far price travelled below the floor; the close shows where the candle finished. If it closes back inside, the breakdown idea has weakened. If price stays in the range and another push below the floor cannot hold, the failure reading gets more support. If candles keep crossing the floor, leave the answer open."),
 F('FIG23_spring_downside_reclaim.png','A range-floor excursion moves below support, returns to the old range, and is followed by a recovery sequence.','A spring-like failure starts with a probe below the floor. The later bars tell you how the story develops.'),
 P("You may hear this called a 'spring' or a 'bear trap'. Treat those names as shorthand for the sequence, not an explanation of motive. The chart cannot prove that anyone deliberately set a trap, and the recovery may stall or fail again."),
 P("Keep the original range floor as your reference. The low of the failed move is important to record, but it does not replace the old floor simply because price later turned there.")
],
'3 · Trendline penetration and reclaim':[
 P("A trendline slopes through earlier turning points. A range ceiling is flatter; a trendline is a way of tracking the angle of the move. Before using it, ask whether the points that anchor the line were clear at the time. A line drawn only after price turns can make the past look neater than it felt in real time."),
 P("When price crosses the line, record the crossing first. A wick through it may be brief. A close through it adds evidence. If price later moves back across the line, that reclaim challenges the idea that the trendline break has held. If the reclaim fails again, the evidence shifts once more."),
 P("Now check the nearby swing structure as well. In a rising move, are the higher lows still intact, or has price also broken a prior swing low? A trendline can break while the wider structure still holds. A break of the line plus a lost swing low is a different picture."),
 F('FIG17_range_vs_trendline_failure.png','A horizontal range-boundary failure and a sloping trendline penetration/reclaim are shown as distinct structures.','A trendline break and a range break are different events. Name the reference first.'),
 P("For example: 'Price crossed below the rising line and later reclaimed it; the prior higher low is still intact.' Or: 'Price crossed the line, lost the prior swing low and has not reclaimed it.' Both notes stick to what happened, without forecasting the next move.")
],
'4 · A prior swing break that is quickly surrendered':[
 P("Now focus on one earlier turning point. A swing high or low is a local high or low that was visible before price tested it. Mark that point first. Then watch whether price moves beyond it and quickly gives the move back."),
 P("For an upside test, price may trade above the old swing high and then close back below it. That is a warning. If later bars continue lower and remain beneath the pivot, the failure-test reading becomes stronger. If price quickly reclaims the swing high, the failure label is challenged. The same logic works in reverse at a swing low."),
 F('FIG24_prior_swing_failure_test.png','Price advances through a pre-existing swing high, then closes back below the pivot and extends lower in the schematic example.','A pivot break needs a prior reference and a response that gives the break back.'),
 P("A swing break can happen inside a much wider range. It is still a real local event, but it may not change the larger structure. Also, mark the pivot from earlier candles—not just because it looks obvious after the reversal."),
 P("The useful question is: what happened after price moved beyond the swing? The move continuing and the move being quickly surrendered begin in the same way. The response separates them.")
],
'5 · A continuation pause breaks the wrong way':[
 P("A flag, pennant or short pause is often read as a rest before the earlier move continues. That's one possible interpretation, not a promise built into the shape. First look at the move leading into the pause. Then mark the pause edges and decide which side would fit the continuation idea."),
 P("If price breaks the expected edge and stays outside, that idea remains possible. If it breaks the other edge, the continuation explanation has lost support. If price briefly moves out and then returns into the pause, the result may still be unclear."),
 F('FIG25_continuation_pause_outcomes.png','Two similar compact pauses are shown resolving differently: one holds beyond the expected upper edge, while the other breaks through the lower edge.','A similar-looking pause can lead to different outcomes.'),
 P("Ask four simple questions: which way was price moving before the pause, which edge mattered to the continuation idea, where did the candle close, and what did the next bars do? A pause that breaks against the earlier move is evidence to review—not something to rename as a 'shakeout' before the chart supports that label."),
 P("Finally, zoom out. A clear break of a small pause may still be happening inside a larger range. Describe the local move and the wider structure if they tell different stories.")
],
'6 · The first pullback holds; a later pullback fails':[
 P("This sequence is easy to misread because the first return can look convincing. Price breaks above a range, comes back towards the old ceiling, stays mostly above it and then moves higher. You can reasonably call that first response hold-like. It only describes that visit, though; it does not promise that every later return will hold."),
 P("When price returns again, compare the second visit with the first. Did it move deeper into the zone? Where did the candle close? Was the next push away weaker? Did price lose a swing low that supported the earlier move? Those details help explain why the second return may change your view."),
 F('FIG11_first_pullback_later_failure.png','An initial return holds above the old boundary; a later return travels farther into the area and challenges the role-reversal interpretation.','One return holding does not guarantee the next return.'),
 P("A deeper return is not automatically a failure, and a shallow touch is not automatically strong. Look at the whole sequence. Keep both visits in your notes so that the later one does not erase what happened during the first."),
 P("For example: 'The first pullback stayed above the old ceiling and price moved higher. The second return closed inside the band, and price could not reclaim the edge; the role-reversal idea weakened.' That's much more helpful than simply writing 'support failed'.")
],
'7 · A neckline break in a top or bottom formation fails':[
 P("A neckline is the reference area in a formation such as a double top or double bottom. We don't need to learn every detail of those patterns here. We're using them to ask the same question as before: did price stay beyond the boundary it crossed, or did it come back through?"),
 P("In a top formation, price may break below the neckline. Check where the candle closes and whether later candles stay below. If price reclaims the neckline and remains above it, the breakdown idea is under pressure. For a bottom formation, reverse the direction: price breaks above the neckline, then closes back below and cannot reclaim it."),
 F('FIG18_neckline_formation_failures.png','A top-formation breakdown is reclaimed and a bottom-formation breakout returns beneath its neckline.','The pattern suggests a boundary to watch. The later candles show whether the break holds.'),
 P("A familiar pattern can make us expect a particular ending before the chart has earned that confidence. Keep the note simple: name the neckline, describe the break, point to the return or reclaim, and say what later price supports. A failed neckline break does not guarantee a move of a fixed distance in the opposite direction."),
 P("If candles keep crossing the neckline, say that the breakdown or breakout has not established itself yet. 'Unclear for now' is better than forcing the pattern into a success or failure label too early.")
]
}.items():
    set_blocks(14,title,blocks)
rename_section(14,'How strong is the contradiction?','How much has the evidence changed?')
set_blocks(14,'How much has the evidence changed?',[
 P("Not every return is equally important. A brief wick back into the zone is an early warning. A close back inside is a clearer challenge to the idea that price is holding outside. Several closes in the old range, especially when a reclaim attempt fails, make the continuation idea harder to support."),
 P("You can use the list below as a description guide. It is not a scoring system. The same number of candles can mean different things on a five-minute chart and a daily chart, especially when volatility changes."),
 UL([
  '**Early warning:** price briefly crosses back through the boundary, but the close and next response are still unknown.',
  '**Clearer warning:** a candle closes back inside the original zone.',
  '**Stronger evidence against the first idea:** later candles stay in the old range or a reclaim attempt fails.',
  '**The failure reading is challenged:** price later reclaims the area and holds outside again.',
  '**Still unclear:** price keeps overlapping the boundary, with closes on both sides.'
 ]),
 F('FIG15_failure_label_checklist.png','A structured checklist separates the original boundary, breakout attempt, later challenge and response.','Use the checklist to describe what you see, not to force a verdict.')
])
set_blocks(14,'Gaps and wide-range bars: sometimes the path is missing',[
 P("A gap is a jump between one candle's close and the next candle's open, with no trades shown between those prices in the chart. A wide-range bar covers much more ground than nearby bars. Both can make a breakout or failure harder to read because the chart gives you less detail about how price travelled."),
 P("If the market opens below a range after closing above it, you can describe the open and close that you can see. You cannot say that price traded smoothly back through every point inside the gap; those prices are not shown in the data. In the same way, a very wide bar may cross the zone and finish far away without showing how the move unfolded inside the period."),
 F('FIG13_gap_and_spike_failures.png','Schematic gaps and wide bars show how price may move from one side of a boundary to another without a detailed path in the supplied bars.','Describe the open, high, low and close you have. Leave the missing path unknown.')
])
set_blocks(14,'Volume: useful context, not proof of a trap',[
 P("Volume can help you compare activity around a break, but first check what the data source measures and what counts as normal for that instrument and session. An increase in activity can appear in a move that holds and in one that fails."),
 P("The candle and volume bar do not tell you who placed orders or why. **Causation** means what actually caused something to happen. Seeing high volume at the same time as a failed breakout does not prove that stop orders caused the reversal or that someone planned to trap traders."),
 P("A careful journal note might say: 'The break happened with higher reported volume than the previous bars, but price later closed back inside the range.' That's enough for the chart. You can mention volume as context without turning it into a story about hidden motives.")
])
set_blocks(14,'Where does a stop belong in a failed-breakout idea?',[
 P("A **stop-loss** is an order placed to exit a position if price reaches a chosen level. In this section it appears only in a hypothetical failed-breakout example, not as an instruction to enter a trade. We are using the marker to understand which price would make the failure idea harder to support."),
 P("Suppose price pushes above a range ceiling, then returns inside and closes below it. If you are studying a possible short-side idea based on that failure, the high of the failed move matters. A stop reference beyond that high says: if price climbs back through that extreme, the failure explanation may no longer fit."),
 P("The exact reference depends on how the failure developed. Sometimes the high appears on the same candle that closes back inside. Sometimes a later candle makes a higher high before the reversal becomes clear. Use the extreme that belongs to the sequence you are actually describing, not a neat-looking distance from the old zone."),
 P("For a possible long after a downside failure, the same idea works in reverse: the low of the failure move is the point that would challenge the recovery explanation."),
 P("Here is the important practical part. If that distance is too large for your risk limit, don't force the stop closer just to make the idea fit. You may reduce exposure, wait for a different structure, or pass. A stop is not a guaranteed execution price during a gap or a fast market. And the chart-reading idea alone is not a complete trading plan."),
 F('FIG21_failed_breakout_structural_stop.png','Two hypothetical failed-breakout sequences show the stop reference beyond the failure high for a possible short and beyond the failure low for a possible long.','The marker shows a price that would challenge the failure idea in this hypothetical example. It is not an entry signal.')
])
set_blocks(14,'After a failure, three paths remain possible',[
 P("Once a breakout attempt has failed to hold, it is tempting to expect a strong move the other way. That can happen, but it is only one path. Price may move back into the old range, drift sideways around the boundary, or reclaim the area and try the original direction again."),
 F('FIG07_failure_is_not_reverse_signal.png','A branch diagram shows a challenged continuation idea leading to three possible paths: a move into the prior range, choppy action around the zone, or a reclaim.','The failure changes the questions you ask. It does not choose the next path.'),
 P("A failed breakout makes other explanations worth considering. It does not tell you how far price will travel or whether a trade is suitable. Ask what the first idea no longer explains, what alternatives still fit, and what new evidence you would need before becoming more confident.")
])
set_blocks(14,'A failure can itself be challenged',[
 P("Imagine price moves above a range and then closes back inside. That return weakens the idea that the breakout is holding. Later, price climbs back above the ceiling and stays there. The new strength challenges the failure reading."),
 P("Both events still belong in your notes. The first return happened; the later reclaim happened too. You don't need to erase one to explain the other. Just update your current view as each new candle arrives."),
 F('FIG14_failed_failure_reclaim.png','A breakout attempt returns inside the range, then later reclaims the original boundary.','A later reclaim is new evidence. It does not erase the earlier return.')
])
set_blocks(14,'The failure review: preserve your original read',[
 P("A good review starts with the note you made before the ending was visible. Keep that note, then add what changed. I would check four things: what boundary I marked, what rule I used to call the break, which later bar challenged the idea, and whether the next move supported or weakened that revision."),
 UL([
  '**Original structure:** what earlier highs, lows, trendline or pattern made the zone relevant?',
  '**Break attempt:** what traded or closed beyond it, and under which rule?',
  '**What challenged the first idea:** which later wick, close, return or failed reclaim changed your reading?',
  '**Current read:** does the original idea still fit, has it weakened, or is the sequence unclear?',
  '**Next question:** what could happen next, and what visible evidence would change your view again?'
 ]),
 P("You can use the word **invalidation** for the event that would make your current idea no longer fit the chart. In plain language: what would show you that this explanation needs to be dropped or changed? It is a condition to watch, not a prediction that the event will happen."),
 F('FIG09_decision_record_timeline.png','A four-stage timeline for recording prior context, the break, later evidence and the review.','Use your first note as the starting point for the review, not something to hide.')
])
set_blocks(14,'Process and outcome are not the same thing',[
 P("Process means how you reached your view. Outcome means what price did later. They are related, but they are not the same thing. You can make a careful read using the evidence available and still have the move fail. You can also guess the ending correctly for weak reasons."),
 P("When you review your answer, ask whether you marked the area before the move, applied your stated rule, described the visible candles accurately, and named what could change your mind. That is a better test of your work than whether you guessed the final direction."),
 P("For this lesson, 'I am not sure yet' can be a strong answer when the candles point in different directions. The aim is not to sound certain. It is to explain what you see and update it when the evidence changes.")
])

# Keep terminology plain in the prompts as well as in the reading.
data['12']['notePrompts']['interpretation']['title'] = '2 · The rule I used'
data['12']['notePrompts']['interpretation']['prompt'] = 'Which rule are you using—close, distance, time outside, or a combination? What does the evidence show so far?'
data['13']['notePrompts']['revision']['prompt'] = 'Name an observable event that would strengthen or weaken the role-reversal idea. Keep the original zone visible and record any change you make.'
data['14']['notePrompts']['interpretation']['title'] = '2 · What challenged the idea?'
data['14']['notePrompts']['interpretation']['prompt'] = 'Point to the candle or sequence that weakened your first reading. What changed, and what remains uncertain?'
data['14']['notePrompts']['revision']['title'] = '4 · What would change your view?'
data['14']['notePrompts']['revision']['prompt'] = 'What later price action would make the failure idea harder to support? In the stop example, which price extreme would challenge the idea? If that level is too far away for your risk limit, passing is reasonable.'

# Light-touch phrase clean-up for any remaining paragraphs; preserve technical cautions but reduce scolding.
replacements = [
 ('Do not use the ending to claim the failure was obvious at Stage 1;', 'The ending does not make the failure obvious at Stage 1;'),
 ('Do not infer that institutions or stop hunters caused it.', 'The chart alone cannot tell us whether institutions or stop hunters caused it.'),
 ('Do not infer that institutions or stop hunters caused it. OHLC candles show prices and ranges; they do not reveal hidden intent.', 'OHLC candles show prices and ranges; they cannot reveal whether institutions or stop hunters caused the move.'),
 ('Do not rename every adverse move a', 'Avoid renaming every adverse move a'),
 ('Do not move the band after the outcome merely to make the chart look like a perfect test.', 'If you revise the band, record what new evidence led you to change it; that keeps the review fair.'),
 ('Do not move it silently so that every new candle appears to respect your first idea.', 'If you move it, show the revision and explain why the first band no longer works.'),
 ('Do not erase the earlier return;', 'Keep the earlier return in your notes;'),
 ('Do not edit the first note to make it sound as if you knew the outcome.', 'Keep the first note as it was, then add a new note explaining what the later candles changed.'),
 ('Do not grade yourself by whether you predicted the final path.', 'Judge your answer by how well you used the evidence available at that stage, not by whether you predicted the final path.'),
 ('The appropriate update is to weaken or invalidate a thesis whose conditions no longer hold—not to reverse automatically into a new trade.', 'A useful update is to weaken or drop an idea when its conditions no longer hold—not to reverse automatically into a new trade.'),
 ('A disciplined review therefore preserves four states.', 'In your review, keep four moments separate.'),
 ('The analyst’s job is not to name the transition too early;', 'Your job is to keep track of evidence for and against a change, rather than naming the transition too early;'),
 ('The task here is not to trade the break. It is to state exactly what the chart has established, what it has not established, and what future evidence would change your view.', 'For now, focus on reading the chart. State what it has shown, what remains uncertain, and what you would watch next.'),
 ('The correct sentence is not “the close confirms the breakout forever”; it is “the close adds evidence that price ended this period beyond the boundary”.', 'Try this wording: “The close adds evidence that price ended this period beyond the boundary.” It is more precise than saying the breakout is confirmed forever.'),
 ('A filter is valuable when it makes your observation repeatable and its trade-off is understood. It becomes dangerous when it is taught as a law.', 'A filter helps when it gives you a rule you can apply consistently. It still has a cost, so treat it as a working rule rather than a law.'),
 ('This is not permission to turn volume into a universal pass/fail switch.', 'That makes volume a useful question to ask, not a universal pass/fail rule.'),
 ('This distinction matters because a failure is always a failure **of a stated claim**.', 'This matters because we need to know what we expected price to do before we can say that the move failed.'),
 ('The original boundary should be defensible from the candles visible before the crossing, not drawn around the future candles after the event has happened.', 'Choose the boundary using candles you could see before the break. If you draw it around later candles, it becomes hard to tell whether the chart changed or the drawing did.'),
 ('The word retest must not do all three jobs.', 'The word retest covers too much when we use it for all three events.'),
 ('One defensible answer:', 'You could write:'),
 ('**A prior swing high or low** is a specific pivot.', '**A prior swing high or low** is a local turning point price made before the current move.'),
 ('A brief move through that line can be followed by a reclaim.', 'A brief move through that line can be followed by a **reclaim**—price moving back across the line after crossing it.'),
]
def soften(s):
    for a,b in replacements: s=s.replace(a,b)
    s=s.replace('The defensible summary is', 'A fair summary is')
    s=s.replace('The appropriate update is', 'A useful update is')
    s=s.replace('in the selected window', 'in the part of the chart we are studying')
    s=s.replace('the continuation thesis', 'the idea that the move would keep going') if False else s
    return s
for lid in ('12','13','14'):
    d=data[lid]
    for sec in d['sections']:
        for b in sec.get('blocks',[]):
            if 'text' in b: b['text']=soften(b['text'])
            if 'items' in b: b['items']=[soften(x) for x in b['items']]
    for k in ('summary','takeaway','hook'):
        if isinstance(d.get(k),str): d[k]=soften(d[k])

# First-use jargon: reserve the words until a plain-English explanation appears.
data['13']['sections'][2]['title']='The depth of the return matters—but does not settle the outcome'
data['14']['objectives']=[soften(x) for x in data['14']['objectives']]

JS.write_text('window.MODULE5_DEEP_CONTENT = '+json.dumps(data,ensure_ascii=False,indent=2)+';\n',encoding='utf-8')
print('Updated warm, plain-English long-form content in assets/module5-deep-content.js')
print('Sections:', {k:len(data[k]['sections']) for k in ('12','13','14')})
