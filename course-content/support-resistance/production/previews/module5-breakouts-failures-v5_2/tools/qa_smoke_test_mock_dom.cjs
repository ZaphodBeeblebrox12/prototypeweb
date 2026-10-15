const fs=require('fs'), vm=require('vm'), path=require('path');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const deepSrc=fs.readFileSync(path.join(root,'assets/module5-deep-content.js'),'utf8');
const deepObj=JSON.parse(deepSrc.replace(/^window\.MODULE5_DEEP_CONTENT\s*=\s*/,'').replace(/;\s*$/,''));
const js=fs.readFileSync(path.join(root,'assets/module5.js'),'utf8');
const interactionSrc=fs.readFileSync(path.join(root,'assets/module5-interactions.js'),'utf8');
const interactionObj=JSON.parse(interactionSrc.replace(/^window\.MODULE5_INTERACTIONS\s*=\s*/,'').replace(/;\s*$/,''));
const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
class El {
  constructor(id=''){this.id=id;this.value='';this.textContent='';this.innerHTML='';this.hidden=false;this.disabled=false;this.checked=false;this.dataset={};this.style={};this.listeners={};this.attributes={};this.className='';this.src='';this.alt='';this.placeholder='';this.download='';this.href='';this._html='';}
  set innerHTML(v){this._html=String(v)} get innerHTML(){return this._html}
  addEventListener(t,fn){(this.listeners[t] ||= []).push(fn)}
  fire(t,extra={}){for(const fn of this.listeners[t]||[])fn({target:this,currentTarget:this,preventDefault(){},...extra})}
  setAttribute(k,v){this.attributes[k]=String(v)} getAttribute(k){return this.attributes[k]}
  scrollIntoView(){}
  click(){this.fire('click')}
}
const els=new Map(ids.map(id=>[id,new El(id)]));
let radioCache=[]; let radioHtmlLast=''; let lessonCache=[]; let lessonHtmlLast=''; let chartButtonCache=[]; let chartMarkupLast='';
function get(id){if(!els.has(id))els.set(id,new El(id));return els.get(id)}
const doc={
 getElementById:get,
 createElement(tag){const e=new El(tag);e.tagName=tag;return e},
 querySelectorAll(selector){
   if(selector==='[data-lesson]'){
     const markup=get('lesson-list').innerHTML;
     if(markup!==lessonHtmlLast){lessonHtmlLast=markup;lessonCache=[...markup.matchAll(/data-lesson="(\d+)"/g)].map(m=>{const e=new El('lesson-link');e.dataset.lesson=m[1];e.tagName='button';return e});}
     return lessonCache;
   }
   if(selector==='#quiz-area input[type="radio"]'){
     const markup=get('quiz-area').innerHTML;
     if(markup!==radioHtmlLast){radioHtmlLast=markup;radioCache=[...markup.matchAll(/<input type="radio" name="([^"]+)" value="(\d+)"/g)].map(m=>{const e=new El('radio');e.name=m[1];e.value=m[2];e.tagName='input';return e});}
     return radioCache;
   }
   if(selector==='[data-open-chart]'){
     const markup=get('reading-sections').innerHTML;
     if(markup!==chartMarkupLast){chartMarkupLast=markup;chartButtonCache=[...markup.matchAll(/<button class="button secondary" type="button" data-open-chart="([^"]+)">/g)].map(m=>{const e=new El('case-chart-button');e.dataset.openChart=m[1];e.tagName='button';return e});}
     return chartButtonCache;
   }
   return [];
 }
};
const memory={};const storage={getItem:k=>memory[k]??null,setItem:(k,v)=>{memory[k]=v}};
const win={MODULE5_DEEP_CONTENT:deepObj,MODULE5_INTERACTIONS:interactionObj};
let activeTab='read';const mockSetTab=(name)=>{activeTab=name;};
new Function('document','window','localStorage','confirm','URL','Blob','setTab',js)(doc,win,storage,()=>true,{},function(){},mockSetTab);
const checks=[];function check(name,ok,detail=''){checks.push({name,ok,detail});if(!ok)throw new Error('Failed '+name+' '+detail)}
check('startup lesson title',get('lesson-title').textContent.includes('Breakout or Temporary Penetration'));
check('long reading and evidence table rendered',get('reading-sections').innerHTML.includes('FIG08_volume_context_not_gate.png') && get('reading-sections').innerHTML.includes('reading-table') && get('reading-sections').innerHTML.includes('What it does not tell you'));
check('Lesson 12 historical chart appears beside the first-read question',get('reading-sections').innerHTML.includes('case-chart-block') && get('reading-sections').innerHTML.includes('charts/L12-01-before-break.png') && get('reading-sections').innerHTML.includes('PAUSE BEFORE THE NEXT REVEAL') && !get('reading-sections').innerHTML.includes('charts/L12-02-outside-zone.png'));
const inlineChartButton=doc.querySelectorAll('[data-open-chart]')[0];inlineChartButton.fire('click');check('inline chart control opens the staged evidence tab',activeTab==='chart');activeTab='read';
check('Volume is presented as an existing catalogue course',get('reading-sections').innerHTML.includes('related-course-card') && get('reading-sections').innerHTML.includes('RELATED COURSE IN THE TRADETHESIS CATALOGUE') && get('reading-sections').innerHTML.includes('Volume'));
check('Volume section explains spot FX, CFD and tick volume',get('reading-sections').innerHTML.includes('Spot FX') && get('reading-sections').innerHTML.includes('CFD (contract for difference)') && get('reading-sections').innerHTML.includes('tick volume') && get('reading-sections').innerHTML.includes('not interchangeable'));
check('first chart stage has an instrument/date/zone-specific caption',get('chart-note').textContent.includes('NIFTY 50 · daily OHLC · 15 July–2 September 2016') && get('chart-note').textContent.includes('8,810–8,850'));
check('L12 field-note prompt specific',get('note-observation-title').textContent.includes('What was crossed'));
check('stage starts gated',get('stage-next').disabled===true);
for(let i=0;i<3;i++){
 get('stage-response').value=`At this stage I observe price relative to the defined zone. My current interpretation is provisional, and I would reconsider it if later closes return inside the range. Stage ${i+1}.`;
 get('stage-response').fire('input');
 check(`stage ${i+1} unlocks after meaningful attempt`,get('stage-next').disabled===false);
 get('stage-next').fire('click');
 if(i===0) check('stage 2 updates the caption to its own visible date range',get('chart-note').textContent.includes('15 July–8 September 2016'));
}
check('final recap unlocked',get('final-recap').hidden===false);
check('L12 seven quiz questions', (get('quiz-area').innerHTML.match(/class="quiz-item"/g)||[]).length===7);
// Select one valid response for each of the seven Lesson 12 questions.
for(const r of doc.querySelectorAll('#quiz-area input[type="radio"]')){r.fire('change')}
get('quiz-submit').fire('click');
check('quiz submission reveals automated feedback',get('quiz-area').innerHTML.includes('quiz-feedback') && get('quiz-status').textContent.includes('Automated feedback shown'));
// Switch lessons using the dynamically generated list control.
const lessonLinks=doc.querySelectorAll('[data-lesson]');const l13=lessonLinks.find(x=>x.dataset.lesson==='13');l13.fire('click');
check('Lesson 13 title rendered',get('lesson-title').textContent.includes('Retests and Role Reversal'));
check('Lesson 13 specific notes',get('note-observation-title').textContent==='1 · Break and return');
check('Lesson 13 simple-to-complex figures rendered',get('reading-sections').innerHTML.includes('FIG19_simple_break_return_response.png') && get('reading-sections').innerHTML.includes('FIG20_simple_retest_outcomes.png') && get('reading-sections').innerHTML.includes('FIG05_three_retest_outcomes.png') && get('reading-sections').innerHTML.includes('FIG06_retest_is_not_owed.png'));
check('Lesson 13 historical chart and question appear together without exposing later stages',get('reading-sections').innerHTML.includes('charts/L13-01-before-break.png') && get('reading-sections').innerHTML.includes('What reactions support drawing this area?') && !get('reading-sections').innerHTML.includes('charts/L13-02-return-toward-area.png'),`stage1=${get('reading-sections').innerHTML.includes('charts/L13-01-before-break.png')}; question=${get('reading-sections').innerHTML.includes('What reactions support drawing this area?')}; stage2Hidden=${!get('reading-sections').innerHTML.includes('charts/L13-02-return-toward-area.png')}`);
check('Lesson 13 simple diagrams precede complex diagrams',(()=>{const h=get('reading-sections').innerHTML;return h.indexOf('FIG19_simple_break_return_response.png')<h.indexOf('FIG16_retest_depth_and_closes.png') && h.indexOf('FIG20_simple_retest_outcomes.png')<h.indexOf('FIG05_three_retest_outcomes.png') && h.indexOf('FIG05_three_retest_outcomes.png')<h.indexOf('FIG04_break_return_response.png')})());
get('note-observation').value='The return entered the band; the bar closed outside it, which leaves the role-reversal read provisional.';get('note-observation').fire('input');
check('field notes persisted to local storage',memory['tradethesis.module5.internal-preview.v5']!==undefined && JSON.parse(memory['tradethesis.module5.internal-preview.v5']).notes['13'].observation.startsWith('The return entered'));
const l14=doc.querySelectorAll('[data-lesson]').find(x=>x.dataset.lesson==='14');l14.fire('click');
check('Lesson 14 expanded failure taxonomy',get('reading-sections').innerHTML.includes('FIG10_failed_signal_family.png') && get('reading-sections').innerHTML.includes('A failure can itself be challenged'));
check('Lesson 14 historical chart is placed beside the applied review question',get('reading-sections').innerHTML.includes('charts/L14-01-before-break.png') && get('reading-sections').innerHTML.includes('Which earlier highs make this an area worth watching?') && !get('reading-sections').innerHTML.includes('charts/L14-02-initial-return.png'));
check('Range-edge upthrust and downside failure diagrams rendered',get('reading-sections').innerHTML.includes('FIG22_range_edge_upthrust.png') && get('reading-sections').innerHTML.includes('FIG23_spring_downside_reclaim.png'));
check('Pivot and continuation-pause failure diagrams rendered',get('reading-sections').innerHTML.includes('FIG24_prior_swing_failure_test.png') && get('reading-sections').innerHTML.includes('FIG25_continuation_pause_outcomes.png'));
check('Plain-language detail present for range and pivot failures',get('reading-sections').innerHTML.includes('start with a range') && get('reading-sections').innerHTML.includes('A swing high or low is a local high or low'));
check('Lesson 14 failure-only stop illustration',get('reading-sections').innerHTML.includes('FIG21_failed_breakout_structural_stop.png') && get('reading-sections').innerHTML.includes('Where does a stop belong in a failed-breakout idea?'));
check('Lesson 14 stop-loss marker only in failure lesson',deepObj['14'].sections.some(x=>x.blocks?.some(b=>b.type==='figure' && b.src.includes('FIG21_'))) && !['12','13'].some(id=>deepObj[id].sections.some(x=>x.blocks?.some(b=>b.type==='figure' && b.src.includes('FIG21_')))));
check('Stop-loss language absent from Lessons 12 and 13',!JSON.stringify(deepObj['12']).match(/stop.loss|structural stop/i) && !JSON.stringify(deepObj['13']).match(/stop.loss|structural stop/i));
check('duplicate Lesson 12 volume section removed',deepObj['12'].sections.filter(x=>x.title.toLowerCase().includes('volume')).length===1);
check('lesson reading stays instructor-led, not bibliography-led',!JSON.stringify(deepObj).match(/author attribution|according to the author|according to a named source/i));
check('model answers shown after final chart stage',get('model-stage-answers').innerHTML.includes('You could write:') && get('model-stage-answers').innerHTML.includes('Quick self-check'));
check('dynamic lesson 13 quiz count',interactionObj['13'].quiz.length===7);
check('dynamic lesson 14 quiz count',interactionObj['14'].quiz.length===8);
check('staged response includes learner model answers',interactionObj['12'].stages.every(x=>x.modelAnswer && x.selfCheck));
console.log(JSON.stringify({assertions:checks.length,passed:checks.filter(c=>c.ok).length,checks},null,2));
