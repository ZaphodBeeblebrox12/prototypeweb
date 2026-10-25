const fs=require('fs'), vm=require('vm'), path=require('path');
const root=path.resolve(__dirname,'..');
const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
const deepSrc=fs.readFileSync(path.join(root,'assets/module5-deep-content.js'),'utf8');
const deepObj=JSON.parse(deepSrc.replace(/^window\.MODULE5_DEEP_CONTENT\s*=\s*/,'').replace(/;\s*$/,''));
const js=fs.readFileSync(path.join(root,'assets/module5.js'),'utf8');
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
let radioCache=[]; let radioHtmlLast=''; let lessonCache=[]; let lessonHtmlLast='';
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
   return [];
 }
};
const memory={};const storage={getItem:k=>memory[k]??null,setItem:(k,v)=>{memory[k]=v}};
const win={MODULE5_DEEP_CONTENT:deepObj};
new Function('document','window','localStorage','confirm','URL','Blob',js)(doc,win,storage,()=>true,{},function(){});
const checks=[];function check(name,ok,detail=''){checks.push({name,ok,detail});if(!ok)throw new Error('Failed '+name+' '+detail)}
check('startup lesson title',get('lesson-title').textContent.includes('Breakout or Temporary Penetration'));
check('long reading rendered',get('reading-sections').innerHTML.includes('FIG08_volume_context_not_gate.png') && get('reading-sections').innerHTML.includes('A fixed point buffer'));
check('L12 field-note prompt specific',get('note-observation-title').textContent.includes('What was crossed'));
check('stage starts gated',get('stage-next').disabled===true);
for(let i=0;i<3;i++){
 get('stage-response').value=`At this stage I observe price relative to the defined zone. My current interpretation is provisional, and I would reconsider it if later closes return inside the range. Stage ${i+1}.`;
 get('stage-response').fire('input');
 check(`stage ${i+1} unlocks after meaningful attempt`,get('stage-next').disabled===false);
 get('stage-next').fire('click');
}
check('final recap unlocked',get('final-recap').hidden===false);
check('L12 five quiz questions', (get('quiz-area').innerHTML.match(/class="quiz-item"/g)||[]).length===5);
// Select all five, submit, and confirm that feedback was unlocked.
for(const r of doc.querySelectorAll('#quiz-area input[type="radio"]')){r.fire('change')}
get('quiz-submit').fire('click');
check('quiz submission reveals explanations',get('quiz-area').innerHTML.includes('quiz-feedback') && get('quiz-status').textContent.includes('Explanations revealed'));
// Switch lessons using the dynamically generated list control.
const lessonLinks=doc.querySelectorAll('[data-lesson]');const l13=lessonLinks.find(x=>x.dataset.lesson==='13');l13.fire('click');
check('Lesson 13 title rendered',get('lesson-title').textContent.includes('Retests and Role Reversal'));
check('Lesson 13 specific notes',get('note-observation-title').textContent==='1 · Break and return');
check('Lesson 13 simple-to-complex figures rendered',get('reading-sections').innerHTML.includes('FIG19_simple_break_return_response.png') && get('reading-sections').innerHTML.includes('FIG20_simple_retest_outcomes.png') && get('reading-sections').innerHTML.includes('FIG05_three_retest_outcomes.png') && get('reading-sections').innerHTML.includes('FIG06_retest_is_not_owed.png'));
check('Lesson 13 simple diagrams precede complex diagrams',(()=>{const h=get('reading-sections').innerHTML;return h.indexOf('FIG19_simple_break_return_response.png')<h.indexOf('FIG16_retest_depth_and_closes.png') && h.indexOf('FIG20_simple_retest_outcomes.png')<h.indexOf('FIG05_three_retest_outcomes.png') && h.indexOf('FIG05_three_retest_outcomes.png')<h.indexOf('FIG04_break_return_response.png')})());
get('note-observation').value='The return entered the band; the bar closed outside it, which leaves the role-reversal read provisional.';get('note-observation').fire('input');
check('field notes persisted to local storage',memory['tradethesis.module5.internal-preview.v5']!==undefined && JSON.parse(memory['tradethesis.module5.internal-preview.v5']).notes['13'].observation.startsWith('The return entered'));
const l14=doc.querySelectorAll('[data-lesson]').find(x=>x.dataset.lesson==='14');l14.fire('click');
check('Lesson 14 expanded failure taxonomy',get('reading-sections').innerHTML.includes('FIG10_failed_signal_family.png') && get('reading-sections').innerHTML.includes('A failure can itself be challenged'));
check('Range-edge upthrust and downside failure diagrams rendered',get('reading-sections').innerHTML.includes('FIG22_range_edge_upthrust.png') && get('reading-sections').innerHTML.includes('FIG23_spring_downside_reclaim.png'));
check('Pivot and continuation-pause failure diagrams rendered',get('reading-sections').innerHTML.includes('FIG24_prior_swing_failure_test.png') && get('reading-sections').innerHTML.includes('FIG25_continuation_pause_outcomes.png'));
check('Instructor-led detail present for range and pivot failures',get('reading-sections').innerHTML.includes('Let’s start with the range because it gives us a clear object to study') && get('reading-sections').innerHTML.includes('A swing high or swing low is a local turning point'));
check('Lesson 14 failure-only stop illustration',get('reading-sections').innerHTML.includes('FIG21_failed_breakout_structural_stop.png') && get('reading-sections').innerHTML.includes('Where does a stop belong in a failed-breakout idea?'));
check('Lesson 14 stop-loss marker only in failure lesson',deepObj['14'].sections.some(x=>x.blocks?.some(b=>b.type==='figure' && b.src.includes('FIG21_'))) && !['12','13'].some(id=>deepObj[id].sections.some(x=>x.blocks?.some(b=>b.type==='figure' && b.src.includes('FIG21_')))));
check('Stop-loss language absent from Lessons 12 and 13',!JSON.stringify(deepObj['12']).match(/stop.loss|structural stop/i) && !JSON.stringify(deepObj['13']).match(/stop.loss|structural stop/i));
check('duplicate Lesson 12 volume section removed',deepObj['12'].sections.filter(x=>x.title.toLowerCase().includes('volume')).length===1);
check('lesson reading stays instructor-led, not bibliography-led',!JSON.stringify(deepObj).match(/author attribution|according to the author|according to a named source/i));
console.log(JSON.stringify({assertions:checks.length,passed:checks.filter(c=>c.ok).length,checks},null,2));
