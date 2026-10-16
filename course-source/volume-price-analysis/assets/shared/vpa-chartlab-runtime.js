(function(){
"use strict";
const cfg=JSON.parse(document.getElementById("lab-config").textContent);
const $=id=>document.getElementById(id);
const esc=s=>String(s==null?"":s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&#39;");
let stage=0,submitted=false;
const stages=[$("stage1"),$("stage2"),$("stage3"),$("review")];
const prog=[$("progress1"),$("progress2"),$("progress3")];
const seed=parseInt(cfg.id.replace(/\D/g,""),10)||1;
function reduced(){return window.matchMedia&&window.matchMedia("(prefers-reduced-motion: reduce)").matches}
function focusStage(i){const title=stages[i].querySelector("h2");if(title){title.setAttribute("tabindex","-1");title.focus({preventScroll:true})}window.scrollTo({top:0,behavior:reduced()?"auto":"smooth"})}
function showStage(i){stage=i;stages.forEach((el,n)=>el.hidden=n!==i);prog.forEach((el,n)=>{el.classList.toggle("current",n===i&&i<3);el.classList.toggle("done",n<i||i===3);if(n===i&&i<3)el.setAttribute("aria-current","step");else el.removeAttribute("aria-current")});focusStage(i)}
function seeded(seed){let x=(seed>>>0)||1;return()=>{x=(1664525*x+1013904223)>>>0;return x/4294967296}}
const shapes={
 volume_surge:{cl:[100,101,100.5,101.2,100.8,101.5,101,101.8,101.4,101.6,101.2,102.1],v:[80,90,86,92,88,95,89,91,90,94,87,260]},
 candle_shape:{cl:[100,101,100.6,101.4,100.9,101.6,101.1,101.8,101.3,101.8,101.5,102],v:[80,95,85,100,93,102,90,97,96,105,91,128]},
 low_volume:{cl:[100,100.5,101.1,101.7,102.1,102.5,102.7,102.9,103.1,103.25,103.35,103.6],v:[150,142,138,130,124,118,112,106,99,91,85,78]},
 pressure:{cl:[100,101.1,100.7,101.8,100.8,101.2,100.5,101.4,100.9,101.3,101,101.4],v:[95,105,110,108,120,118,135,129,140,138,152,165]},
 progress:{cl:[100,101,102,102.6,103.6,104.1,105,105.6,106.1,107.2,107.6,108.6],v:[80,90,87,97,93,110,105,118,112,130,120,150]},
 effort_result:{cl:[100,101,100.6,101.7,101.1,101.5,101,101.8,101.2,101.4,101.1,101.3],v:[80,90,86,96,92,100,95,108,102,115,104,300]},
 weakening:{cl:[100,101,102,103,103.6,104.1,104.4,104.55,104.4,104.1,104.2,103.8],v:[95,98,102,105,110,115,118,120,128,137,148,175]},
 divergence:{cl:[100,100.9,101.7,102.2,102.9,103.5,104,104.4,105,105.2,105.7,106],v:[220,210,198,190,180,170,160,148,139,130,121,110]},
 trend_pullback:{cl:[100,101,102,103.1,104,105,104.2,103.5,102.9,103.2,103.5,104.2],v:[90,98,95,105,103,118,90,83,77,86,92,120]},
 range:{cl:[100,102,101,99.8,101.5,102.2,100.5,99.7,101.1,102.1,100.6,101.2],v:[100,105,98,110,103,112,100,118,106,121,102,145]},
 setup:{cl:[100,100.8,101.7,102.5,103.3,104.1,103.5,102.9,103.1,103.5,103.7,104.4],v:[85,90,92,97,98,110,95,82,80,88,92,118]},
 breakout:{cl:[100,101,100.5,101.3,100.7,101.5,100.8,101.6,101,101.4,101.6,104],v:[90,96,89,98,92,103,91,100,95,105,98,300]},
 failed_breakout:{cl:[100,101,100.5,101.4,100.8,101.7,100.6,101.3,100.9,102.5,101.8,101.4],v:[90,96,89,98,92,103,91,100,95,185,210,300]},
 climax:{cl:[100,101,102,103,104,105,106,106.8,107.4,108.1,108.5,107.9],v:[90,96,98,105,110,120,125,134,145,158,170,390]},
 spring:{cl:[100,101.5,100.6,102,100.5,101.8,100.3,101.5,100.8,101.7,100.9,102.2],v:[90,95,88,102,91,108,94,110,100,118,105,220]},
 upthrust:{cl:[100,101.4,100.6,102,100.7,101.8,100.5,101.7,100.9,101.8,102.1,101.5],v:[90,95,88,102,91,108,94,110,100,118,125,245]},
 reversal:{cl:[100,101,102,103,104,105,104.3,103.5,102.8,102.1,101.5,100.8],v:[90,95,100,103,108,110,115,125,140,165,185,205]},
 profile:{cl:[100,101,103,102,104,103,105,104,102,101,103,104],v:[90,150,230,190,285,230,160,125,205,250,215,140]},
 migration:{cl:[100,101,102,101.5,102.5,103.4,104,103.5,104.8,105.3,106,106.5],v:[90,105,130,118,155,180,190,170,205,220,235,250]},
 context:{cl:[100,101,100.2,101.4,99.9,101.1,100.5,102,100.7,101.3,100.9,101.6],v:[95,120,110,130,105,145,115,155,120,140,125,175]},
 evidence:{cl:[100,101.1,101.7,102.4,103,102.3,102.8,103.7,103.2,104,104.4,104.1],v:[90,100,115,130,125,165,150,190,185,210,230,260]},
 scenario:{cl:[100,101,100.6,101.5,100.8,101.6,100.7,101.8,101.1,101.5,101.6,103],v:[90,100,92,108,95,115,97,120,101,124,109,240]},
 pullback:{cl:[100,101.2,102.3,103.4,104.4,105.2,104.4,103.7,103.2,103.6,103.9,104.5],v:[90,98,105,112,120,130,105,93,86,95,102,138]}
};
function getBars(pattern,seed,phase){
 const s=seeded(seed),shape=shapes[pattern]||shapes.context,base=100;
 const bars=[];
 for(let i=0;i<shape.cl.length;i++){
   const close=shape.cl[i],open=i===0?close-(s()>.5?.6:-.6):bars[i-1].close;
   let hi=Math.max(open,close)+.25+s()*.5,lo=Math.min(open,close)-.25-s()*.5;
   if(pattern==="candle_shape"&&i===shape.cl.length-1){hi=Math.max(open,close)+1.8;lo=Math.min(open,close)-.35}
   if(pattern==="spring"&&i===shape.cl.length-1){lo=97.8;hi=Math.max(open,close)+.35}
   if(pattern==="upthrust"&&i===shape.cl.length-1){hi=104.5;lo=Math.min(open,close)-.3}
   if(pattern==="climax"&&i===shape.cl.length-1){hi=110.0;lo=Math.min(open,close)-.25}
   const vol=Math.max(30,shape.v[i]*(.96+s()*.08));
   bars.push({open,high:hi,low:lo,close,volume:vol});
 }
 if(phase==="hold"||phase==="fail"){
   const last=bars[bars.length-1].close;
   const ds=phase==="hold"?[.7,1.05,.45,1.15]:[-.55,-1.05,-.7,-1.25];
   for(let i=0;i<ds.length;i++){
     const open=bars[bars.length-1].close;
     const delta=ds[i];
     const close=open+delta;
     const wig=.25+s()*.55;
     bars.push({open,high:Math.max(open,close)+wig,low:Math.min(open,close)-wig,close,volume:(phase==="hold"?115:155)*(0.88+s()*.26)});
   }
 }
 return bars;
}
function svgChart(vis){
 if(vis.view==="feeds")return feedCards(vis);
 const bars=getBars(vis.pattern||cfg.pattern,seed+(vis.seed||0),vis.phase||"initial");
 const profile=vis.view==="profile";
 const W=900,H=profile?470:450,px=65,py=62,pw=profile?440:770,ph=220,vy=315,vh=70;
 let min=Math.min(...bars.map(b=>b.low)),max=Math.max(...bars.map(b=>b.high));
 if(vis.level!=null){min=Math.min(min,vis.level-.5);max=Math.max(max,vis.level+.5)}
 const pad=(max-min)*.09;min-=pad;max+=pad;
 const y=v=>py+ph-(v-min)/(max-min)*ph;
 const n=bars.length,step=pw/n,cw=Math.min(25,step*.46),vols=bars.slice(0,10).map(b=>b.volume),base=vols.reduce((a,b)=>a+b,0)/vols.length;
 const vmax=Math.max(...bars.map(b=>b.volume))*1.08;
 let out='<svg class="chart-svg" viewBox="0 0 '+W+' '+H+'" role="img" aria-labelledby="ct cd"><title id="ct">'+esc(vis.title||"Synthetic price and recorded volume chart")+'</title><desc id="cd">'+esc(vis.caption||"Synthetic price bars and recorded activity. All values are illustrative, not historical market data.")+'</desc><rect width="'+W+'" height="'+H+'" rx="8" fill="#fffefa"/>';
 for(let k=0;k<5;k++){const val=min+(max-min)*k/4,yy=y(val);out+='<line x1="'+px+'" y1="'+yy+'" x2="'+(px+pw)+'" y2="'+yy+'" stroke="#e4e2da"/><text x="'+(px-9)+'" y="'+(yy+4)+'" text-anchor="end" font-size="12" fill="#777870">'+val.toFixed(1)+'</text>'}
 out+='<text x="'+px+'" y="34" font-size="14" font-weight="700" fill="#62645f">PRICE</text>';
 const level=vis.level!=null?vis.level:((cfg.pattern==="breakout"||cfg.pattern==="failed_breakout"||cfg.pattern==="scenario")?102:(cfg.pattern==="spring"?99:(cfg.pattern==="upthrust"?103.5:null)));
 if(level!=null){const yy=y(level);out+='<line x1="'+px+'" y1="'+yy+'" x2="'+(px+pw)+'" y2="'+yy+'" stroke="#7f867b" stroke-width="1.5" stroke-dasharray="6 5"/><rect x="'+(px+pw-148)+'" y="'+(yy-19)+'" width="145" height="17" fill="#fffefa"/><text x="'+(px+pw-5)+'" y="'+(yy-7)+'" text-anchor="end" font-size="11" fill="#62645f">'+esc(vis.levelLabel||"Reference level")+'</text>'}
 bars.forEach((b,i)=>{
  const x=px+step*i+step/2,up=b.close>=b.open,col=up?"#27725f":"#b85f55",top=y(Math.max(b.open,b.close)),bottom=y(Math.min(b.open,b.close)),body=Math.max(2,bottom-top);
  if(i===11)out+='<rect x="'+(x-step*.42)+'" y="'+(py-7)+'" width="'+(step*.84)+'" height="'+(ph+14)+'" fill="none" stroke="#b28a23" stroke-dasharray="4 4" rx="4"/>';
  out+='<line x1="'+x+'" y1="'+y(b.high)+'" x2="'+x+'" y2="'+y(b.low)+'" stroke="'+col+'" stroke-width="2.1"/><rect x="'+(x-cw/2)+'" y="'+top+'" width="'+cw+'" height="'+body+'" fill="'+col+'" rx="1"/>';
 });
 out+='<text x="'+px+'" y="299" font-size="13" font-weight="700" fill="#62645f">RECORDED VOLUME</text><line x1="'+px+'" y1="'+(vy+vh-(base/vmax)*vh)+'" x2="'+(px+pw)+'" y2="'+(vy+vh-(base/vmax)*vh)+'" stroke="#62645f" stroke-dasharray="5 5" stroke-width="1.5"/>';
 bars.forEach((b,i)=>{const x=px+step*i+step/2,h=b.volume/vmax*vh,col=i===11?"#b28a23":"#bec2ba";out+='<rect x="'+(x-cw/2)+'" y="'+(vy+vh-h)+'" width="'+cw+'" height="'+h+'" fill="'+col+'" rx="1"/>'});
 out+='<text x="'+px+'" y="414" font-size="12" fill="#62645f">Dashed line: average of previous 10 bars</text><text x="'+(px+pw)+'" y="414" text-anchor="end" font-size="12" font-weight="700" fill="#62645f">Outlined candle: event under review</text>';
 if(profile){
  const x0=548,profW=285,bins=9,counts=new Array(bins).fill(0);
  bars.forEach(b=>{const idx=Math.max(0,Math.min(bins-1,Math.round((b.close-min)/(max-min)*(bins-1))));counts[idx]+=b.volume});
  const maxC=Math.max(...counts),binH=ph/bins,top=py;
  out+='<text x="'+x0+'" y="34" font-size="14" font-weight="700" fill="#62645f">ACTIVITY BY PRICE</text>';
  counts.forEach((v,i)=>{const idx=bins-1-i,yy=top+i*binH,w=v/maxC*profW,highlight=idx===counts.indexOf(maxC),c=highlight?"#b28a23":"#bfc4bc";out+='<rect x="'+x0+'" y="'+yy+'" width="'+w+'" height="'+(binH-2)+'" fill="'+c+'" rx="2"/>';if(highlight)out+='<text x="'+(x0+Math.min(w,profW)-6)+'" y="'+(yy+binH*.65)+'" text-anchor="end" font-size="11" font-weight="700" fill="#252923">POC</text>'});
  out+='<text x="'+x0+'" y="'+(py+ph+24)+'" font-size="11" fill="#62645f">Illustrative profile from this window</text>';
 }
 out+='</svg>';
 return '<div class="visual-title">'+esc(vis.title||"Synthetic chart")+'</div>'+out+'<p class="visual-caption">'+esc(vis.caption||"Illustrative synthetic data. Compare visible price behaviour with recorded activity; do not treat this as a signal.")+'</p>';
}
function feedCards(vis){if(vis&&vis.phase){return '<div class="feed-grid"><article class="feed-card"><strong>'+esc(vis.title||"Outcome") + '</strong><p>'+esc(vis.caption||"A data-source scenario to evaluate.")+'</p><p><b>Review:</b> Check whether the measure and coverage stayed comparable.</p></article><article class="feed-card"><strong>What changed?</strong><p>'+esc(vis.phase==="hold"?"The source/measurement stayed consistent, so the relative comparison remains interpretable.":"The provider or coverage changed, so the apparent volume shift may partly be a data difference.")+'</p><p>Do not compare unlike measures as if they were interchangeable.</p></article></div>'}return '<div class="feed-grid"><article class="feed-card"><strong>Exchange-traded futures</strong><p><b>Measure:</b> contract volume reported by the exchange feed.</p><p><b>Limit:</b> confirm the contract, session and data provider; do not mix unlike contracts without a method.</p></article><article class="feed-card"><strong>Retail spot FX</strong><p><b>Measure:</b> often tick volume, a count of price updates from that feed.</p><p><b>Limit:</b> not a consolidated count of every global currency transaction.</p></article><article class="feed-card"><strong>Crypto spot</strong><p><b>Measure:</b> trading activity reported by a particular venue or aggregation provider.</p><p><b>Limit:</b> venues differ; coverage and units may not be directly comparable.</p></article></div>'}
function renderVisual(id,vis){const el=$(id);if(!el)return;el.innerHTML=svgChart(vis)}
function renderChecks(){const host=$("noticeCheck");host.innerHTML='<fieldset class="choices"><legend>'+esc(cfg.check.q)+'</legend>'+cfg.check.options.map((o,i)=>'<label><input type="radio" name="checkAnswer" value="'+esc(o.value)+'" '+(i===-1?"checked":"")+'><span>'+esc(o.label)+'</span></label>').join("")+'</fieldset>'}
function field(id,label,placeholder,min){return '<div class="field"><label for="'+id+'">'+esc(label)+'</label><textarea id="'+id+'" minlength="'+(min||35)+'" placeholder="'+esc(placeholder||"Use visible evidence, then explain your reasoning.")+'"></textarea><p class="hint">Write enough for another learner to follow your reasoning. This prototype does not semantically grade free text.</p></div>'}
function validateFields(ids,feedbackId){const missing=ids.find(id=>$(id).value.trim().length<Number($(id).getAttribute("minlength")||30));const f=$(feedbackId);f.hidden=false;f.className="feedback bad";if(missing){f.textContent="Add a specific observation before continuing. Point to the visible price/volume or profile evidence and state what remains uncertain.";$(missing).focus();return false}f.className="feedback good";f.textContent="Response recorded in this page. This checks completion, not the meaning or quality of the answer.";return true}
function checkLevel1(){const f=$("feedback1"),answer=document.querySelector('input[name="checkAnswer"]:checked');f.hidden=false;f.className="feedback bad";if(!answer){f.textContent="Choose the answer that matches the chart before continuing.";document.querySelector('input[name="checkAnswer"]')?.focus();return false}if(answer.value!==cfg.check.correct){f.textContent=cfg.check.retry||"That choice does not match the visible evidence. Recheck the chart and try again.";document.querySelector('input[name="checkAnswer"]:checked')?.focus();return false}if($("noticeResponse").value.trim().length<25){f.textContent="Correct observation. Now add one written detail from the chart before advancing.";f.className="feedback good";$("noticeResponse").focus();return false}f.className="feedback good";f.textContent=cfg.check.feedback||"Correct. Keep this observation separate from an interpretation of what may happen next.";return true}
function modelHtml(){const m=cfg.model;return '<details id="modelReasoning"><summary>Reveal model reasoning and feedback</summary><div class="answer"><h3>Level 1 — Notice</h3><p>'+esc(m.notice)+'</p></div><div class="answer"><h3>Level 2 — Compare</h3><p>'+esc(m.compare)+'</p></div><div class="answer"><h3>Level 3 — Apply</h3><p>'+esc(m.apply)+'</p></div><div class="answer"><h3>Possible outcome A</h3><p>'+esc(m.hold)+'</p></div><div class="answer"><h3>Possible outcome B</h3><p>'+esc(m.fail)+'</p></div><div class="answer"><h3>Counterexample / limit</h3><p>'+esc(cfg.counterexample)+'</p></div></details>'}
function boot(){
 $("eyebrow").textContent="Read Volume. Find Trade Setups. · Module "+cfg.module+" · Lesson "+cfg.id;
 $("title").textContent=cfg.title;
 $("intro").textContent=cfg.aim;
 $("learningOutcome").textContent=cfg.objective;
 $("noticeTitle").textContent=cfg.l1Title||"First, identify the visible facts";
 $("noticeIntro").textContent=cfg.l1Intro||"Observe before you interpret. This chart uses synthetic data, not a historical market.";
 $("compareTitle").textContent=cfg.l2Title||"Compare two situations";
 $("compareIntro").textContent=cfg.compareIntro;
 $("applyTitle").textContent=cfg.l3Title||"Apply the idea to a new case";
 $("applyIntro").textContent=cfg.applyIntro;
 $("noticePrompt").textContent=cfg.l1Prompt||"State one visible fact not already captured by the selected answer.";
 $("compareTask").textContent=cfg.compareTask;
 $("alternativeTask").textContent=cfg.alternativeTask;
 $("applyTask").textContent=cfg.applyTask;
 $("scenarioTask").textContent=cfg.scenarioTask;
 $("outcomeReviewLabel").textContent=cfg.outcomeReviewLabel||"What later evidence changed or strengthened your reading?";
 $("noticeResponseLabel").textContent=cfg.noticeResponseLabel||"Add one more observation";
 $("compareResponseLabel").textContent=cfg.compareResponseLabel||"Compare the two cases";
 $("alternativeResponseLabel").textContent=cfg.alternativeResponseLabel||"Give an alternative explanation";
 $("applyResponseLabel").textContent=cfg.applyResponseLabel||"What can you conclude from the new case?";
 $("scenarioResponseLabel").textContent=cfg.scenarioResponseLabel||"Write two possible outcomes and what would distinguish them";
 $("counterexampleText").textContent=cfg.counterexample;
 $("modelBlock").innerHTML=modelHtml();
 $("rubric").innerHTML=(cfg.rubric||[]).map(x=>'<li>'+esc(x)+'</li>').join("");
 $("noticeResponse").placeholder=cfg.noticePlaceholder||"Name a visible feature, using the chart labels where relevant.";
 $("compareResponse").placeholder=cfg.comparePlaceholder||"Compare location, structure and the evidence displayed.";
 $("alternativeResponse").placeholder=cfg.alternativePlaceholder||"Another plausible explanation is...";
 $("applyResponse").placeholder=cfg.applyPlaceholder||"Describe what is visible, what it may mean, and what remains uncertain.";
 $("scenarioResponse").placeholder=cfg.scenarioPlaceholder||"If price does X, that would support... If price does Y, that would weaken...";
 $("outcomeReview").placeholder=cfg.reviewPlaceholder||"Say exactly what later evidence changed your reading.";
 renderChecks();
 renderVisual("noticeVisual",{view:cfg.view,pattern:cfg.pattern,title:cfg.visualTitle,caption:cfg.visualCaption,level:cfg.level,levelLabel:cfg.levelLabel});
 renderVisual("applyVisual",{view:cfg.view,pattern:cfg.pattern,title:cfg.applyVisualTitle||"New case · initial evidence only",caption:cfg.applyVisualCaption||"Later bars are withheld until your initial reading is recorded.",level:cfg.level,levelLabel:cfg.levelLabel,seed:41});
 $("outcomeATitle").textContent=cfg.outcomeA.title;$("outcomeBTitle").textContent=cfg.outcomeB.title;
 $("compareVisualA").innerHTML=svgChart({view:cfg.view,pattern:cfg.compareA.pattern,title:cfg.compareA.title,caption:cfg.compareA.caption,level:cfg.compareA.level,levelLabel:cfg.compareA.levelLabel,seed:17});
 $("compareVisualB").innerHTML=svgChart({view:cfg.view,pattern:cfg.compareB.pattern,title:cfg.compareB.title,caption:cfg.compareB.caption,level:cfg.compareB.level,levelLabel:cfg.compareB.levelLabel,seed:29});
 if(cfg.riskCalc){
  $("riskCalc").hidden=false;
  $("riskCalc").innerHTML='<h3>Hypothetical risk calculator</h3><p>Use the supplied teaching values first. These are illustrative units, not a real contract recommendation.</p><div class="ticket-grid"><div class="field"><label for="riskBudget">Maximum planned risk</label><input id="riskBudget" type="number" min="0" step="1" value="250"></div><div class="field"><label for="stopDistance">Entry-to-invalidation distance</label><input id="stopDistance" type="number" min="0" step=".1" value="2.5"></div><div class="field"><label for="pointValue">Value per unit per point</label><input id="pointValue" type="number" min="0" step=".1" value="10"></div><div class="field"><label for="extraCost">Extra cost/slippage per unit (points)</label><input id="extraCost" type="number" min="0" step=".1" value="0"></div></div><div class="ticket-output" id="riskOutput" role="status" aria-live="polite">Complete the fields to see the calculation.</div>';
  const calc=()=>{const risk=Number($("riskBudget").value),dist=Number($("stopDistance").value),val=Number($("pointValue").value),cost=Number($("extraCost").value),per=(dist+cost)*val;const n=per>0?Math.floor(risk/per):0;$("riskOutput").textContent="Estimated risk per unit: "+per.toFixed(2)+" · Maximum whole units within the supplied risk budget: "+n+" · Estimated total risk: "+(n*per).toFixed(2)+". Reassess if execution costs or invalidation distance change.";};["riskBudget","stopDistance","pointValue","extraCost"].forEach(id=>$(id).addEventListener("input",calc));calc();
 }
 $("noticeResponse").addEventListener("input",()=>{if(!$("feedback1").hidden)$("feedback1").hidden=true});
 $("next1").addEventListener("click",()=>{if(checkLevel1())showStage(1)});
 $("back2").addEventListener("click",()=>showStage(0));
 $("next2").addEventListener("click",()=>{if(validateFields(["compareResponse","alternativeResponse"],"feedback2"))showStage(2)});
 $("back3").addEventListener("click",()=>showStage(1));
 $("revealOutcomes").addEventListener("click",()=>{
  if(!validateFields(["applyResponse","scenarioResponse"],"feedback3"))return;
  submitted=true;
  $("initialRead").hidden=true;$("outcomes").hidden=false;
  $("outcomeA").innerHTML=svgChart({view:cfg.view,pattern:cfg.pattern,title:cfg.outcomeA.title,caption:cfg.outcomeA.caption,level:cfg.level,levelLabel:cfg.levelLabel,phase:"hold"});
  $("outcomeB").innerHTML=svgChart({view:cfg.view,pattern:cfg.pattern,title:cfg.outcomeB.title,caption:cfg.outcomeB.caption,level:cfg.level,levelLabel:cfg.levelLabel,phase:"fail",seed:4});
  $("outcomeAtext").textContent=cfg.model.hold;$("outcomeBtext").textContent=cfg.model.fail;
  $("outcomesTitle").focus({preventScroll:true});$("outcomesTitle").scrollIntoView({behavior:reduced()?"auto":"smooth",block:"start"});
 });
 $("complete").addEventListener("click",()=>{if(!submitted)return;if(validateFields(["outcomeReview"],"feedbackReview"))showStage(3)});
 $("openModel").addEventListener("click",()=>{$("modelReasoning").open=true;$("modelReasoning").scrollIntoView({behavior:reduced()?"auto":"smooth",block:"nearest"})});
 $("restart").addEventListener("click",()=>{["noticeResponse","compareResponse","alternativeResponse","applyResponse","scenarioResponse","outcomeReview"].forEach(id=>$(id).value="");document.querySelectorAll('input[name="checkAnswer"]').forEach(el=>el.checked=false);document.querySelectorAll(".checks input").forEach(el=>el.checked=false);["feedback1","feedback2","feedback3","feedbackReview"].forEach(id=>{const el=$(id);el.hidden=true;el.className="feedback"});$("initialRead").hidden=false;$("outcomes").hidden=true;$("modelReasoning").open=false;submitted=false;if(cfg.riskCalc){$("riskBudget").value=250;$("stopDistance").value=2.5;$("pointValue").value=10;$("extraCost").value=0;$("riskBudget").dispatchEvent(new Event("input"))}showStage(0)});
 $("dateNote").textContent="Synthetic teaching examples · not historical data, investment advice or trade signals. Responses remain in this browser page; they are not sent to a server or saved to a member account.";
}
document.addEventListener("DOMContentLoaded",boot);
})();