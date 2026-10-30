/*
 * TradeThesis course catalogue content.
 * To add a micro-course, append one object to microCourses, keep priority=3, and set its order.
 * Set catalogueVisibility to "hidden" while it is still being developed; set to "visible" when it is ready to appear.
 * Visibility controls catalogue display only; it does not mean an offer has a live checkout or access policy.
 * The visual template and interactions live in courses-catalogue.js / courses.css.
 */
window.TRADETHESIS_COURSE_DATA = {
  programmePriority: 1,
  programmes: [
    {
      id: "trading-path",
      catalogueVisibility: "visible",
      priority: 1,
      order: 10,
      theme: "path",
      art: "beginner",
      kicker: "The beginner programme",
      badge: "Start here if you're new",
      title: "The TradeThesis Trading Path",
      promise: "Understand the screen before you risk the money.",
      description: "A guided introduction to markets, charts and trading decisions. Start with what price, orders and candles mean, then build towards chart reading, risk, planning and review.",
      facts: ["30 written lessons", "4 connected stages", "30-day guided sequence"],
      outcomes: [
        "Understand what markets are and how a trade works.",
        "Read basic chart structure and use tools as evidence, not automatic signals.",
        "Connect a trade idea to an entry, invalidation point and risk.",
        "Review decisions and build the habit of recording your reasoning."
      ],
      price: "Free",
      priceNote: "no payment required · permanent access",
      delivery: "15–20 min lesson + action step · written lessons · Telegram delivery",
      community: "Standalone course. Community access is not included.",
      href: "trading-path.html",
      cta: "Explore the free course"
    },
    {
      id: "construct",
      catalogueVisibility: "visible",
      priority: 1,
      order: 20,
      theme: "construct",
      art: "process",
      kicker: "The guided flagship programme",
      badge: "For a deeper process",
      title: "CONSTRUCT",
      subtitle: "Trade Construction & Management",
      promise: "Build a trading process you can explain—and defend.",
      description: "Turn market understanding into a repeatable process. Study at your own pace, complete paper-trading-led assignments, and improve your work through reviews, clinics and a capstone defence.",
      facts: ["70 days", "43 core lessons", "10 assignments", "8 Review Clinics"],
      outcomes: [
        "Turn market context and evidence into a clear trade thesis.",
        "Set invalidation, position size and risk before entry.",
        "Plan how to manage the trade after entry.",
        "Backtest, review and defend a written playbook of your own."
      ],
      price: "₹17,000",
      priceNote: "programme fee · guided practice",
      delivery: "Weekly lesson unlocks · paper trading · structured feedback",
      community: "Includes 12 months of The Wobbling Candle community access.",
      href: "construct.html",
      cta: "Explore CONSTRUCT"
    }
  ],
  supportingProgrammes: [{
    id: "live-classroom",
    catalogueVisibility: "visible",
    priority: 2,
    order: 10,
    title: "Trade Construction & Management — Live Classroom",
    description: "Six live weekend sessions connect context, thesis, entry, risk, management, exit and review. Guided worksheets and checkpoints build towards a written personal playbook.",
    facts: ["6 live weekend sessions", "Guided worksheets", "Personal playbook"],
    href: "live-class.html",
    cta: "Explore the Live Classroom"
  }],
  microCourses: [
    {
      id: "support-resistance",
      // The Builder draft is kept on a distinct database slug to avoid colliding
      // with the older seeded course row. Once published, merge it into this
      // existing curated card instead of rendering a second Support & Resistance tile.
      academySlug: "support-resistance-draft",
      catalogueVisibility: "visible",
      priority: 3,
      order: 10,
      title: "Support & Resistance",
      category: "Chart reading",
      art: "support-resistance",
      price: "₹599",
      level: "Foundational skill",
      hook: "Mark fewer zones. Give each one a reason.",
      problem: "For traders who see a possible level around every swing and need a reason to keep or discard it.",
      learningFocus: "Choose and defend relevant zones, read reactions and breaks, and identify invalidation.",
      tags: [],
      whyThisOne: "Treats zones as decision areas to justify, test and invalidate—not lines to collect.",
      description: "Learn to mark meaningful price zones, read reactions and avoid drawing lines without a reason.",
      outcome: "Read support and resistance as areas where price may react—not as guaranteed turning points.",
      complements: "Extends the chart-reading foundations in Trading Path.",
      modules: [
        { title: "The basic theory", count: "3 lessons", preview: "What support and resistance represent, why zones matter more than perfectly precise lines, and how to choose levels that deserve attention.", points: ["Price memory and areas of interest", "Zones versus single-price lines", "Choosing meaningful levels"] },
        { title: "Mark the chart with purpose", count: "3 lessons", preview: "Practise identifying a small number of useful levels and separating clear structure from chart clutter.", points: ["Swing highs and lows", "Repeated reactions", "When to remove a level"] },
        { title: "Read the reaction", count: "3 lessons", preview: "Look at how price behaves near a level instead of assuming the level will hold.", points: ["Rejection and acceptance", "Candle closes near a zone", "Context before confirmation"] },
        { title: "Understand trading ranges", count: "2 lessons", preview: "Identify the edges of a range and the conditions that make a reaction trade less clear.", points: ["Range boundaries", "Space to the next level", "When not to trade the middle"] },
        { title: "Breakouts and retests", count: "3 lessons", preview: "Study closes beyond a level, failed breaks and what a retest can—and cannot—tell you.", points: ["Break versus wick", "False breakout clues", "Retest as a new decision"] },
        { title: "Build a simple plan", count: "2 lessons", preview: "Bring the level, entry idea, invalidation and risk into one written plan before thinking about execution.", points: ["Define what would prove the idea wrong", "Plan the risk first", "A short chart-based practice"] }
      ]
    },
    {
      id: "bollinger-bands",
      catalogueVisibility: "visible",
      priority: 3,
      order: 20,
      title: "Understand Bollinger Bands",
      category: "Indicators",
      art: "bollinger",
      price: "₹599",
      level: "Indicator essentials",
      hook: "A band touch is not a trading plan.",
      problem: "For traders who treat every outer-band touch as a reversal or every squeeze as a signal to act.",
      learningFocus: "Read band width, compare trend and range behaviour, and assess price around the bands.",
      tags: [],
      whyThisOne: "Keeps volatility in context instead of turning the indicator into a buy-or-sell rule.",
      description: "Understand the bands, volatility and how to read them in market context instead of treating every touch as a signal.",
      outcome: "Explain what the bands show, what they do not show, and how to combine them with price structure.",
      complements: "A focused companion to the technical toolkit in Trading Path.",
      modules: [
        { title: "What the bands measure", count: "2 lessons", preview: "Understand the middle band, outer bands and the relationship between price and recent volatility.", points: ["The three parts of the indicator", "Standard settings and their meaning"] },
        { title: "Expansion and contraction", count: "2 lessons", preview: "Read changing band width as information about volatility, not a forecast by itself.", points: ["Band squeeze and expansion", "Why volatility can remain low or high"] },
        { title: "Price at the bands", count: "3 lessons", preview: "Compare trend and range conditions to understand why an outer-band touch can mean different things.", points: ["Walking the band", "Range reactions", "Avoiding automatic reversal assumptions"] },
        { title: "Combine with chart context", count: "2 lessons", preview: "Use structure and a clear question to decide whether the indicator adds anything useful.", points: ["Read the trend first", "Build a repeatable observation"] }
      ]
    },
    {
      id: "volume-price-analysis",
      catalogueVisibility: "visible",
      status: "in-development",
      priority: 3,
      order: 25,
      title: "Volume & Price Analysis",
      category: "Price & volume",
      art: "volume",
      price: "Coming soon",
      level: "Course in development",
      hook: "When activity rises, ask what price actually achieved.",
      problem: "For traders watching volume spikes without comparing effort with price progress, location and follow-through.",
      learningFocus: "Compare volume with candle results, assess breakouts and failures, and use Volume Profile to describe where activity concentrated.",
      tags: [],
      whyThisOne: "Uses volume as context and evidence—not as a standalone signal.",
      description: "Learn to read recorded volume alongside price, recognise potential trading situations, evaluate breakouts and failures, and build a structured trade plan.",
      outcome: "Interpret volume in price context, assess possible buying and selling pressure, evaluate breakouts and use Volume Profile as evidence rather than a standalone signal.",
      complements: "A natural companion to Bollinger Bands, chart structure and breakout study.",
      modules: [
        { title: "Read the Market Behind the Candles", count: "5 lessons", preview: "Understand what volume adds to candle reading and compare activity with price results across different data sources.", points: ["Unusual relative volume", "Candle range and close location", "Data-source limitations"] },
        { title: "Spot Buying and Selling Pressure", count: "5 lessons", preview: "Study effort versus result, retained progress, stalled moves and price/volume disagreement.", points: ["Activity and price progress", "Limited progress at key areas", "Alternative explanations"] },
        { title: "Find Trade Setups at the Levels That Matter", count: "5 lessons", preview: "Apply volume and price structure to trends, pullbacks, support/resistance and range boundaries.", points: ["Trend pullbacks", "Reactions around levels", "Setup quality and no-trade decisions"] },
        { title: "Spot False Breakouts Before You Chase Them", count: "5 lessons", preview: "Evaluate breakouts, failed moves, climactic activity, springs/upthrusts and the evidence needed after a break.", points: ["Breakout quality", "Failure and follow-through", "Climax activity"] },
        { title: "Find the Price Levels Worth Watching", count: "5 lessons", preview: "Use Volume Profile, Point of Control, Value Area and high/low-volume nodes to describe where activity concentrated.", points: ["Point of Control and Value Area", "High- and low-volume nodes", "Changes in value"] },
        { title: "Put It All Together: Build a Complete Trading Plan", count: "5 lessons", preview: "Combine context, price/volume evidence, alternative scenarios, trigger, invalidation, risk, execution and review.", points: ["Build a conditional thesis", "Plan entry and invalidation", "Review the process"] }
      ]
    },
    {
      id: "candlestick-patterns",
      catalogueVisibility: "visible",
      priority: 3,
      order: 30,
      title: "Candlestick Patterns",
      category: "Chart reading",
      art: "candlesticks",
      price: "₹499",
      level: "Chart reading",
      hook: "Read the candle. Then read where it formed.",
      problem: "For traders memorising pattern names without checking structure, location or what price does next.",
      learningFocus: "Read candle anatomy, compare common patterns, and test them against chart context and follow-through.",
      tags: [],
      whyThisOne: "Pairs pattern recognition with a repeatable observation checklist—not predictions.",
      description: "Read common candle patterns in context and learn why the same candle can mean different things in different places.",
      outcome: "Describe what a candle shows and test its significance against location, structure and follow-through.",
      complements: "Builds on the candle basics introduced in Trading Path.",
      modules: [
        { title: "Read one candle", count: "2 lessons", preview: "Understand the open, high, low, close, body and wick before memorising pattern names.", points: ["Bullish and bearish closes", "Body and wick proportions"] },
        { title: "Common two- and three-candle patterns", count: "3 lessons", preview: "Study engulfing candles, pin bars and reversal sequences without assuming they predict a reversal.", points: ["Pattern anatomy", "Confirmation and follow-through", "Context matters"] },
        { title: "Location changes meaning", count: "2 lessons", preview: "Compare patterns at meaningful levels, mid-range and after extended movement.", points: ["Support and resistance", "Trend and range context"] },
        { title: "Practice reading the chart", count: "2 lessons", preview: "Use a short checklist to record observation, interpretation and what would disprove it.", points: ["Separate fact from interpretation", "Chart review exercise"] }
      ]
    },
    {
      id: "risk-management-basics",
      catalogueVisibility: "visible",
      priority: 3,
      order: 40,
      title: "Risk Management Basics",
      category: "Risk & trade planning",
      art: "risk",
      price: "₹599",
      level: "Essential practice",
      hook: "Know what proves the trade wrong before you size it.",
      problem: "For traders choosing an entry first and working out the stop, quantity and possible loss afterward.",
      learningFocus: "Define invalidation, connect stop distance to position size, and estimate risk before entry.",
      tags: [],
      whyThisOne: "Makes risk part of the trade thesis, not a number added at the end.",
      description: "Understand invalidation, stop placement, position size and why a trade idea is incomplete without a risk plan.",
      outcome: "Define the possible loss before entry and connect position size to the risk you have chosen.",
      complements: "A practical companion to trading mechanics in Trading Path and CONSTRUCT.",
      modules: [
        { title: "Risk before reward", count: "2 lessons", preview: "Understand why the first question is what you can lose if the idea is wrong.", points: ["Define the risk budget", "Losses as part of trading"] },
        { title: "Invalidation and stops", count: "3 lessons", preview: "Place a stop in relation to the idea failing, not simply at an arbitrary distance.", points: ["What proves the idea wrong", "Stop distance and market structure", "Avoiding stop adjustments without a rule"] },
        { title: "Position size", count: "3 lessons", preview: "Connect account risk, entry-to-stop distance and quantity using worked examples.", points: ["Risk amount", "Distance and quantity", "Costs and slippage"] },
        { title: "Write a risk rule", count: "2 lessons", preview: "Turn the calculations into a short rule you can check before each trade.", points: ["Pre-trade check", "One-page risk note"] }
      ]
    },
    {
      id: "moving-averages",
      catalogueVisibility: "visible",
      priority: 3,
      order: 50,
      title: "Moving Averages",
      category: "Indicators",
      art: "moving-averages",
      price: "₹499",
      level: "Indicator essentials",
      hook: "A crossover can describe a chart. It cannot make the plan.",
      problem: "For traders treating moving-average crosses or line touches as complete trade signals.",
      learningFocus: "Compare simple and exponential averages, then read slope, spacing, lag and price location across trend and sideways conditions.",
      tags: [],
      whyThisOne: "Explains what the average summarises—and what extra evidence a decision still needs.",
      description: "Understand common moving averages, lag and trend context—and why a line crossing is not a plan by itself.",
      outcome: "Use moving averages as a way to summarise price behaviour while keeping price structure in view.",
      complements: "Extends technical-tool learning without replacing the full Trading Path.",
      modules: [
        { title: "What a moving average shows", count: "2 lessons", preview: "Learn how averaging smooths past prices and why the result lags current movement.", points: ["Simple and exponential averages", "Length and lag"] },
        { title: "Trend context", count: "2 lessons", preview: "Compare slope, spacing and price location without treating them as certainty.", points: ["Direction and slope", "Chop and sideways conditions"] },
        { title: "Crossovers and pullbacks", count: "3 lessons", preview: "Read popular signals critically and ask what extra evidence would be needed.", points: ["Crossover limitations", "Pullback context", "False starts"] },
        { title: "Put it on the chart", count: "2 lessons", preview: "Create a short observation checklist and review a few different market conditions.", points: ["Choose a purpose", "Review examples"] }
      ]
    },
    {
      id: "options-basics",
      catalogueVisibility: "visible",
      priority: 3,
      order: 60,
      title: "Options Basics",
      category: "Options",
      art: "options",
      price: "₹599",
      level: "New to options",
      hook: "Understand the contract before the strategy.",
      problem: "For new options traders who see CE/PE, strike, expiry and premium on screen but are still piecing together what they mean.",
      learningFocus: "Learn calls and puts, buyer and seller roles, strike, expiry, premium, time and volatility—and the risks each side carries.",
      tags: [],
      whyThisOne: "Builds the vocabulary and contract mechanics first, before moving on to strategies.",
      description: "Learn the language of calls, puts, strike prices, expiry and premium before exploring options strategies.",
      outcome: "Explain the basic contract terms and the key risks of buying or selling an option.",
      complements: "A standalone introduction; it does not replace a full trading or risk-management course.",
      modules: [
        { title: "What an option is", count: "2 lessons", preview: "Understand the contract, its underlying instrument and the difference between a call and a put.", points: ["Call and put", "Buyer and seller"] },
        { title: "Strike, expiry and premium", count: "3 lessons", preview: "Learn the terms that shape an option's price and lifespan.", points: ["Strike price", "Expiry and time value", "Premium and intrinsic value"] },
        { title: "What changes the premium", count: "2 lessons", preview: "Introduce price movement, time and volatility as key influences without relying on a single-factor explanation.", points: ["Underlying movement", "Time and volatility"] },
        { title: "Know the risks", count: "2 lessons", preview: "Compare the risks for option buyers and sellers and learn the contract details to check first.", points: ["Payoff and loss boundaries", "Expiry and position sizing"] }
      ]
    },
    {
      id: "market-structure",
      catalogueVisibility: "visible",
      priority: 3,
      order: 70,
      title: "Market Structure",
      category: "Chart reading",
      art: "structure",
      price: "₹599",
      level: "Read the bigger picture",
      hook: "Stop labelling every swing. Find the structure that matters.",
      problem: "For traders zooming into entries before deciding whether price is trending, ranging or changing behaviour.",
      learningFocus: "Identify meaningful swing points, read sequences of highs and lows, assess breaks, and connect structure to invalidation.",
      tags: [],
      whyThisOne: "Connects the bigger picture to a testable thesis and a clear reason to stand aside.",
      description: "Identify swings, higher highs, lower lows and changes in structure before zooming into an entry.",
      outcome: "Describe whether price is trending, ranging or changing behaviour using visible structure.",
      complements: "Supports chart context in Trading Path and thesis construction in CONSTRUCT.",
      modules: [
        { title: "Find the swings", count: "2 lessons", preview: "Identify meaningful highs and lows without labelling every small fluctuation.", points: ["Swing highs and lows", "Timeframe context"] },
        { title: "Trend and range", count: "3 lessons", preview: "Read sequences of highs and lows and recognise when the structure is less clear.", points: ["Higher highs and higher lows", "Lower highs and lower lows", "Sideways structure"] },
        { title: "Break of structure", count: "2 lessons", preview: "Study how a previous swing is crossed, and why one break alone does not settle the next direction.", points: ["Structural levels", "Confirmation and failure"] },
        { title: "Use structure in a thesis", count: "2 lessons", preview: "Connect the larger picture to a testable idea, an invalidation level and a reason to stand aside.", points: ["Context before entry", "A short thesis card"] }
      ]
    },
    {
      id: "understanding-adx",
      catalogueVisibility: "visible",
      priority: 3,
      order: 80,
      title: "Understanding ADX",
      category: "Indicators",
      art: "adx",
      price: "₹499",
      level: "Indicator essentials",
      hook: "Measure trend strength—without guessing direction.",
      problem: "For traders reading ADX as a bullish or bearish signal instead of a measure of trend strength.",
      learningFocus: "Understand what ADX measures, separate strength from direction, and read it alongside visible price structure.",
      tags: [],
      whyThisOne: "Draws a clear line between trend strength and directional bias, so the indicator is not asked to do both jobs.",
      description: "Understand what ADX says about trend strength, what it does not say about direction, and how to avoid reading it alone.",
      outcome: "Interpret ADX as one piece of information about trend strength, not a buy-or-sell signal.",
      complements: "A short technical-tool companion for chart readers.",
      modules: [
        { title: "What ADX measures", count: "2 lessons", preview: "Learn the purpose of the indicator and the relationship between ADX and directional movement.", points: ["Trend strength versus direction", "ADX and directional lines"] },
        { title: "Read rising and falling ADX", count: "2 lessons", preview: "Explore how the line behaves as a trend strengthens, weakens or remains unclear.", points: ["Rising ADX", "Falling ADX", "Low readings"] },
        { title: "Common interpretation mistakes", count: "2 lessons", preview: "Avoid treating a single threshold or reading as a full trade thesis.", points: ["Direction is not supplied by ADX", "Thresholds are context-dependent"] },
        { title: "Apply with price structure", count: "2 lessons", preview: "Bring price structure and the indicator together in a repeatable chart review.", points: ["Read context first", "Record what the indicator adds"] }
      ]
    }
  ]
};