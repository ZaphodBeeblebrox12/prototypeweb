window.MODULE5_INTERACTIONS = {
  "12": {
    "id": 12,
    "title": "Breakout or Temporary Penetration?",
    "time": "30–35 min",
    "stages": [
      {
        "image": "charts/L12-A-01-first-crossing.png",
        "alt": "Synthetic illustrative candles move beyond a candidate upper zone. Later response is not shown.",
        "title": "Stage 1 · The first move beyond the zone",
        "prompt": "What has price done relative to the prior zone, and what remains unknown about whether it can stay outside?",
        "placeholder": "Record the visible move, the rule you are using, and one event that could change your view.",
        "modelAnswer": "Price has moved beyond the candidate zone. That is an observable event, but it does not establish that price will remain outside. I will keep the boundary fixed and review the later candles before deciding whether the move held.",
        "selfCheck": "Name the visible move, keep the confirmation convention explicit, and avoid claiming continuation.",
        "caption": "Synthetic illustrative OHLC — not historical market data. First move beyond a candidate zone; later bars remain hidden."
      },
      {
        "image": "charts/L12-B-02-follow-through.png",
        "alt": "Synthetic illustrative candles continue to operate beyond the candidate zone, adding evidence of follow-through.",
        "title": "Stage 2 · Later bars hold outside",
        "prompt": "What does the additional time outside the zone support, and what could still weaken the continuation reading?",
        "placeholder": "Record the new evidence, then state what would make you reconsider.",
        "modelAnswer": "Later bars continue to operate outside the zone, so the sustained-move interpretation has more support than it did at the first crossing. That still does not guarantee continuation; a later return into the prior range would weaken it.",
        "selfCheck": "Describe the later follow-through, retain uncertainty, and name contradictory evidence.",
        "caption": "Synthetic illustrative OHLC — not historical market data. Later bars remain beyond the zone, but the next outcome is not guaranteed."
      },
      {
        "image": "charts/L12-A-02-return-inside.png",
        "alt": "Synthetic illustrative candles show an earlier move beyond a zone followed by a return into the prior range.",
        "title": "Stage 3 · A return inside challenges the move",
        "prompt": "Which new evidence challenges the continuation idea, and what should your revised note avoid claiming?",
        "placeholder": "Keep the earlier crossing as a fact, identify the contradiction, and revise your interpretation.",
        "modelAnswer": "The earlier crossing still happened, but price later returned into the old range. That weakens the claim that the move held outside. The chart does not prove hidden motive or prescribe an automatic trade in the opposite direction.",
        "selfCheck": "Preserve both observations, point to the return inside, and avoid hindsight certainty.",
        "caption": "Synthetic illustrative OHLC — not historical market data. Later price returns inside the earlier range."
      }
    ],
    "quiz": [
      {
        "q": "A candle wicks above resistance but closes back inside the zone. Which description fits?",
        "options": [
          "The session closed and stayed above the resistance zone.",
          "Price traded above, then closed back inside the zone.",
          "The upper band has become support after this first test."
        ],
        "correct": 1,
        "feedback": "The high shows where price travelled during the candle; the close shows where it finished. This is an intraday move beyond the zone, not a close outside it."
      },
      {
        "q": "One daily candle closes just above a marked area. What can you say now?",
        "options": [
          "The session finished above the chosen boundary.",
          "The close suggests buyers kept control into the end.",
          "The close tells us the next session will rise."
        ],
        "correct": 0,
        "feedback": "The close is an observation. It tells you where this session ended, not what the next session must do."
      },
      {
        "q": "Two closes are above the zone, but later price closes back inside. How would you review it?",
        "options": [
          "The earlier closes no longer count after price comes back.",
          "The return proves the zone was drawn too low from the start.",
          "The rule was met, then later evidence weakened the move."
        ],
        "correct": 2,
        "feedback": "The earlier closes remain valid observations. The later return changes the current reading, but it does not create an automatic opposite-side trade."
      },
      {
        "q": "A chart shows higher volume on both a move that holds and one that fails. What does that suggest?",
        "options": [
          "More volume makes a failed move more likely than a hold.",
          "Volume adds context, but does not settle the outcome alone.",
          "Less volume confirms that price will return inside the zone."
        ],
        "correct": 1,
        "feedback": "Volume and price behaviour are two separate clues. Activity can rise in moves that continue and in moves that fail."
      },
      {
        "q": "A fixed 20-point buffer is used on two different instruments. What is the main concern?",
        "options": [
          "The same buffer can mean different things across markets.",
          "The buffer may miss some moves, but works the same across markets.",
          "A fixed buffer matters only after the candle closes outside."
        ],
        "correct": 0,
        "feedback": "Instrument scale and normal price movement differ. A fixed distance is a convention to test, not a universal threshold."
      },
      {
        "q": "A five-minute break occurs while price remains inside a broad daily range. Which note is clearest?",
        "options": [
          "The local break means the daily range has already ended.",
          "The local break is clear; the wider range still matters.",
          "Keep the daily chart for review only if the break fails."
        ],
        "correct": 1,
        "feedback": "Both statements can be true: a local boundary was crossed, while the wider structure remains a range."
      },
      {
        "q": "Which journal note would be most useful to review later?",
        "options": [
          "Strong breakout; I expect price to keep moving higher from here.",
          "Price moved quickly, so continuation seems more likely now.",
          "Close above the zone; reconsider if it closes back inside."
        ],
        "correct": 2,
        "feedback": "A useful note gives the area, the rule, the observation and a condition that would change your view."
      }
    ],
    "reveal": "The rule was applied consistently: several daily closes appeared above the chosen band. Later, price returned below it. A fair review keeps both facts and updates the interpretation. The ending was not available at Stage 1.",
    "modelAnswerRubric": [
      "Points to price behaviour visible at that stage.",
      "Separates the observation from what it may mean.",
      "Names one uncertainty or alternative path.",
      "Says what new evidence could strengthen or weaken the view."
    ]
  },
  "13": {
    "id": 13,
    "title": "Retests and Role Reversal",
    "time": "35–40 min",
    "stages": [
      {
        "image": "charts/L13-A-01-break-beyond.png",
        "alt": "Synthetic illustrative candles move beyond a former resistance area; no return is visible yet.",
        "title": "Stage 1 · The break",
        "prompt": "Which earlier reactions support this candidate area, and what should remain open after the first break?",
        "placeholder": "Describe the prior reactions, keep the chosen area fixed, and name one uncertainty.",
        "modelAnswer": "Earlier reactions make the band a reasonable candidate area. Price has now moved beyond it, but the crossing does not prove that the old resistance will become support or that a return will occur.",
        "selfCheck": "Describe the zone, distinguish the break from the later response, and leave the outcome open.",
        "caption": "Synthetic illustrative OHLC — not historical market data. Break beyond a candidate former-resistance area."
      },
      {
        "image": "charts/L13-B-01-return-to-area.png",
        "alt": "Synthetic illustrative candles return toward the same former resistance area after moving beyond it.",
        "title": "Stage 2 · The return",
        "prompt": "Does price stop short of, touch, enter or cross the band? Where does the candle close, and what can you say before seeing its response?",
        "placeholder": "Describe the return depth and close separately; do not call the retest successful yet.",
        "modelAnswer": "Price has returned toward the zone. I will describe the low and the close separately, because a wick that enters the band and a close back inside the old range are different observations. The return alone does not prove a role reversal.",
        "selfCheck": "Describe return depth and close as separate facts; do not treat proximity as confirmation.",
        "caption": "Synthetic illustrative OHLC — not historical market data. Price returns toward the unchanged area."
      },
      {
        "image": "charts/L13-C1-hold.png",
        "alt": "Synthetic illustrative candles return toward the former area, remain on the new side and move away again.",
        "title": "Stage 3 · A hold-like response",
        "prompt": "What makes a hold-like interpretation plausible here, and what does this response not guarantee?",
        "placeholder": "Point to the return and the later response, then name one possible contradiction.",
        "modelAnswer": "Price returned toward the area and then remained on the new side before moving away. That is consistent with a hold-like response in this example, but it does not prove that the area will hold on another visit.",
        "selfCheck": "Point to the return and response, use conditional language, and retain a possible alternative.",
        "caption": "Synthetic illustrative OHLC — not historical market data. One possible hold-like response after a return."
      },
      {
        "image": "charts/L13-C2-fail.png",
        "alt": "Synthetic illustrative candles move back through the former area and re-enter the old range.",
        "title": "Stage 4 · A return can fail",
        "prompt": "Which new evidence challenges the role-reversal idea, and why does it not guarantee an opposite move?",
        "placeholder": "Compare with the hold-like stage and revise the interpretation without forecasting a certain direction.",
        "modelAnswer": "Price has moved back through the former area and into the old range, which challenges the idea that the band is holding as support here. It does not prove that price must keep falling; it could pause, reclaim the zone or remain mixed.",
        "selfCheck": "Describe the contradiction and keep the next path conditional.",
        "caption": "Synthetic illustrative OHLC — not historical market data. An alternative outcome returns through the old area."
      }
    ],
    "quiz": [
      {
        "q": "Price breaks above a range and continues higher without returning. What can you conclude?",
        "options": [
          "No return appeared here; a retest was not required.",
          "Without a return, the breakout is still incomplete for review.",
          "A retest is usually needed before a move can continue."
        ],
        "correct": 0,
        "feedback": "Some moves continue without returning. A retest is an additional event to assess, not a step every breakout must complete."
      },
      {
        "q": "After an upside break, what does “role reversal” mean?",
        "options": [
          "The former ceiling can still resist price on a return.",
          "One close above confirms support for future visits.",
          "The old resistance area may now act as support."
        ],
        "correct": 2,
        "feedback": "Role reversal is a possibility to test. Price may hold above the area, cross back through it, or remain mixed."
      },
      {
        "q": "The wick dips into the band, but the candle closes above it. What should you record?",
        "options": [
          "The low places price inside the band for the full candle.",
          "The wick entered the area; the close remained above it.",
          "The zone no longer matters after the candle closes."
        ],
        "correct": 1,
        "feedback": "The low and close give different information. Record both, then look at the later response."
      },
      {
        "q": "Three later candles close on alternating sides of the band. What is the fairest label?",
        "options": [
          "The hold is clear enough to call the role change complete.",
          "The break has changed into a complete reversal now.",
          "The response remains mixed; more candles are needed."
        ],
        "correct": 2,
        "feedback": "When candles keep crossing the band without moving away clearly, the answer is still unclear. You can leave it there for now."
      },
      {
        "q": "Price closes inside the old range and a later reclaim attempt fails. What changed?",
        "options": [
          "The failed reclaim weakens the role-reversal idea.",
          "The boundary must be moved around the newest candles.",
          "The opposite range edge is now the most likely target."
        ],
        "correct": 0,
        "feedback": "Closes in the old range and a failed reclaim are evidence against the idea that the old ceiling is holding as support."
      },
      {
        "q": "You decide the band needs to be wider after seeing more candles. What is the best practice?",
        "options": [
          "Replace the old band after each new high or low.",
          "Keep both versions and record why you revised it.",
          "Choose the wider band because the final chart looks cleaner."
        ],
        "correct": 1,
        "feedback": "A revision can be reasonable. Keeping the old boundary and noting the reason helps you avoid fitting the drawing to the ending."
      },
      {
        "q": "Which note best describes a return that holds for now?",
        "options": [
          "The old area worked, so future visits should hold too.",
          "A long position is justified on the next test of the band.",
          "Price returned, moved away, and stayed above the band."
        ],
        "correct": 2,
        "feedback": "The third note describes the visible sequence and keeps the conclusion limited to this visit."
      }
    ],
    "reveal": "In the selected window, price returns towards the candidate area and later remains above it. That supports a hold-like reading here. A different sequence could close back inside the old range or remain mixed; the area does not become permanent support just because it held once.",
    "modelAnswerRubric": [
      "Names the original area and how price moved relative to it.",
      "Separates the return (low or wick) from the candle close.",
      "Describes the later response rather than guessing in advance.",
      "Keeps the claim limited and names what could change it."
    ]
  },
  "14": {
    "id": 14,
    "title": "Failed Breakouts and Alternate Outcomes",
    "time": "45–55 min including Wider Neckline",
    "stages": [
      {
        "image": "charts/L14-A-01-area-before-break.png",
        "alt": "Synthetic illustrative candles approach a candidate upper zone; the attempted move beyond it is hidden.",
        "title": "Stage 1 · Before the break",
        "prompt": "Which earlier reactions make this area worth watching, and what later evidence would challenge a continuation idea?",
        "placeholder": "Record the prior structure, a provisional hypothesis and a condition that would make you reconsider.",
        "modelAnswer": "I can point to the earlier reactions that make the zone a reasonable candidate. Before seeing later bars, I will state a confirmation convention and the evidence that would weaken a future move beyond the area.",
        "selfCheck": "Use only the visible prior structure; preserve uncertainty about what happens next.",
        "caption": "Synthetic illustrative OHLC — not historical market data. The candidate area is shown before a break attempt."
      },
      {
        "image": "charts/L14-B-01-first-move-beyond.png",
        "alt": "Synthetic illustrative candles show an initial move beyond the prior zone; later response is hidden.",
        "title": "Stage 2 · The first move beyond",
        "prompt": "What has happened so far, and what has not yet been established about the move?",
        "placeholder": "State the event without prematurely labelling it a sustained breakout or failure.",
        "modelAnswer": "Price has moved beyond the prior zone, so a breakout attempt can be recorded. The move has not yet demonstrated that it will hold outside, and it cannot yet be labelled a failed breakout without later contradictory evidence.",
        "selfCheck": "Name the event first and keep the final outcome open.",
        "caption": "Synthetic illustrative OHLC — not historical market data. Initial move beyond the prior area."
      },
      {
        "image": "charts/L14-C-01-return-through.png",
        "alt": "Synthetic illustrative candles return through the original zone and into the prior range.",
        "title": "Stage 3 · The thesis is challenged",
        "prompt": "Which new evidence weakens the initial continuation thesis, and what can you not conclude from that evidence alone?",
        "placeholder": "Preserve the first view, point to the contradiction and write a careful revision.",
        "modelAnswer": "The return through the original area challenges the idea that price is holding beyond it. The earlier crossing remains a valid observation, but the interpretation needs revision. This does not establish hidden intent or make a reverse trade automatic.",
        "selfCheck": "Identify the contradiction and distinguish the event from a guaranteed next direction.",
        "caption": "Synthetic illustrative OHLC — not historical market data. Later price returns through the original area."
      },
      {
        "image": "charts/L14-D-01-pullback-holds.png",
        "alt": "Synthetic illustrative candles break beyond a zone, return toward it, remain outside and then move away.",
        "title": "Stage 4 · A contrasting pullback that holds",
        "prompt": "How does this contrasting sequence differ from the prior return-through example, and what could still weaken the hold-like interpretation?",
        "placeholder": "Compare the close and later response while keeping the original zone fixed.",
        "modelAnswer": "This sequence returns toward the prior area but then remains beyond it and moves away, making a hold-like interpretation plausible. A later close back inside or a failed reclaim would still challenge that interpretation.",
        "selfCheck": "Compare the response after the return, not just the fact that a return occurred.",
        "caption": "Synthetic illustrative OHLC — not historical market data. A contrasting pullback holds beyond the prior area."
      }
    ],
    "quiz": [
      {
        "q": "A candle has just closed above a range ceiling. How should you label it at this point?",
        "options": [
          "Price has confirmed a move that should continue higher.",
          "The break has failed before any return inside appears.",
          "A breakout attempt; its next response is unknown."
        ],
        "correct": 2,
        "feedback": "At the first close you can record the attempt. A failure label needs later evidence that challenges the move."
      },
      {
        "q": "One candle then closes back inside the old range. What does that tell you?",
        "options": [
          "The next move lower is now the more likely outcome.",
          "The close now challenges the idea of holding above.",
          "The original zone may have been set too high or low."
        ],
        "correct": 1,
        "feedback": "A close back inside is a clear contradiction to the idea that price is holding outside, but one close does not guarantee the next direction."
      },
      {
        "q": "After a failed upside break, which paths may still happen?",
        "options": [
          "Price may return, move sideways, or reclaim the zone.",
          "Price should reach the opposite edge after a failed break.",
          "Only a strong reversal remains possible from here."
        ],
        "correct": 0,
        "feedback": "Failure makes alternatives worth reviewing. It does not select a single outcome."
      },
      {
        "q": "For a hypothetical short after an upside failure, which price point matters structurally?",
        "options": [
          "Use a fixed number of points above the old zone.",
          "Use the midpoint of the prior range as the reference.",
          "Use the extreme that would challenge the failure idea."
        ],
        "correct": 2,
        "feedback": "The structural reference should relate to the move that failed. It is not a universal buffer or an entry instruction; if the risk is too large, passing may be appropriate."
      },
      {
        "q": "A market gaps from above a zone to below it. What can the candles tell you?",
        "options": [
          "The candle data lets us reconstruct every price inside the gap.",
          "We see the open and range, not the path inside the gap.",
          "The market crossed the gap without any missing prices."
        ],
        "correct": 1,
        "feedback": "The chart does not show trades inside the gap. Describe the prices the data supplies and leave the missing path unknown."
      },
      {
        "q": "High volume appears during a failed breakout. What does that prove?",
        "options": [
          "Volume shows activity, but not who traded or why.",
          "It shows that stops were targeted around the level.",
          "It makes a move in the opposite direction more likely."
        ],
        "correct": 0,
        "feedback": "Volume can describe reported activity, but it does not establish hidden motive or guarantee follow-through."
      },
      {
        "q": "Price returns into the range, then later reclaims the ceiling and stays above. What should the review say?",
        "options": [
          "The earlier return should now be removed from the written record.",
          "The first failure proves any later breakout will hold.",
          "The reclaim adds new evidence against the failure reading."
        ],
        "correct": 2,
        "feedback": "Both events matter. Keep the earlier return, then note that the later reclaim challenges your current label."
      },
      {
        "q": "A neckline break fails and later candles cross the neckline repeatedly. Which description fits best?",
        "options": [
          "The pattern points to a move in the opposite direction now.",
          "The break is not established; the result is still unclear.",
          "The first crossing completes the pattern without more evidence."
        ],
        "correct": 1,
        "feedback": "A pattern name does not settle the result. Repeated overlap can leave the interpretation unresolved."
      }
    ],
    "reveal": "The return on 1 February still closed above the band, so a hold-like reading remained plausible at that stage. The 2 February close back below the band then challenged that idea, and later weakness added context. The first view was not foolish; the evidence changed. This does not prove hidden intent or prescribe a short trade.",
    "modelAnswerRubric": [
      "Names the boundary and the original breakout convention.",
      "Points to the new candle or sequence that changed the reading.",
      "Explains what the evidence weakens without claiming certainty.",
      "Does not infer hidden motive or turn the failure into an automatic trade."
    ]
  }
};
