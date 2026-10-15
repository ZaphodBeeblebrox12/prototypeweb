from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
raw=(ROOT/'assets'/'module5-deep-content.js').read_text(encoding='utf-8')
data=json.loads(re.search(r'window\.MODULE5_DEEP_CONTENT\s*=\s*(\{.*\})\s*;\s*$',raw,re.S).group(1))
interactions=json.loads((ROOT/'tools'/'lesson_interactions.json').read_text(encoding='utf-8'))
interactions={str(x['id']):x for x in interactions}

def render_block(b):
    typ=b['type']
    if typ=='p': return b['text']+'\n'
    if typ=='quote': return '> '+b['text']+'\n'
    if typ=='figure':
        return f"![{b.get('alt','')}](assets/figures/{Path(b['src']).name})\n\n*{b.get('caption','')}*\n"
    if typ=='caseChart':
        return f"![{b.get('alt','')}]({b.get('src','')})\n\n*{b.get('caption','')}*\n\n**Pause before the next reveal:** {b.get('question','')}\n\n*In the interactive preview, record your first read in the staged chart exercise before revealing later candles.*\n"
    if typ=='relatedCourse':
        return f"> **{b.get('label','RELATED COURSE IN THE CATALOGUE')} · {b.get('title','')}**\n>\n> {b.get('text','')}\n>\n> {b.get('note','')}\n"
    if typ in ('ol','ul'):
        marker='1.' if typ=='ol' else '-'
        return '\n'.join(f"{marker if typ=='ul' else str(i+1)+'.'} {item}" for i,item in enumerate(b.get('items',[])))+'\n'
    if typ=='table':
        headers=b.get('headers',[])
        rows=b.get('rows',[])
        out=['| '+' | '.join(headers)+' |','| '+' | '.join('---' for _ in headers)+' |']
        out += ['| '+' | '.join(row)+' |' for row in rows]
        return '\n'.join(out)+'\n'
    return ''

meta={
 '12':{'file':'LESSON_12_BREAKOUT_OR_TEMPORARY_PENETRATION.md','title':'Lesson 12 — Breakout or Temporary Penetration?','tag':'Read the crossing; do not predict the ending.'},
 '13':{'file':'LESSON_13_RETESTS_AND_ROLE_REVERSAL.md','title':'Lesson 13 — Retests and Role Reversal','tag':'Separate the break, the return and the response.'},
 '14':{'file':'LESSON_14_FAILED_BREAKOUTS_AND_ALTERNATE_OUTCOMES.md','title':'Lesson 14 — Failed Breakouts and Alternate Outcomes','tag':'Identify what failed before you consider what follows.'}}
for lid in ('12','13','14'):
    lesson=data[lid]; inter=interactions[lid]; m=meta[lid]
    out=[f"# {m['title']}", '', f"**Module:** 5 — Breakouts & Failures  ", f"**Estimated time:** {lesson['time']}  ", f"**Teaching hook:** *{lesson['hook']}*", '', lesson['summary'], '', '## What you will learn', '']
    out += [f"- {obj}" for obj in lesson['objectives']]
    out += ['', '## Read the idea', '']
    for sec in lesson['sections']:
        out += [f"### {sec['title']}", '']
        for block in sec.get('blocks',[]):
            out += [render_block(block), '']
    out += ['## Examine the evidence', '', 'The chart stages below are meant to be opened in order. Record what you can observe before you reveal the next stage. The NIFTY 50 material is temporary internal teaching data; the candidate bands are instructional choices, not official levels.', '']
    for stage in inter['stages']:
        out += [f"### {stage['title']}", '', f"![{stage['alt']}]({stage['image']})", '', f"**Question to consider:** {stage['prompt']}", '', f"**Write before revealing:** {stage.get('placeholder','Record the observation, interpretation, alternative and condition that would change your view.')}", '']
    out += ['## Model answers and self-check', '', 'Read these after you have recorded all three chart stages. They show one way to explain your thinking; your wording can be different if it points to the chart evidence.', '']
    for stage in inter['stages']:
        out += [f"### {stage['title']}", '', stage.get('modelAnswer',''), '', f"**Self-check:** {stage.get('selfCheck','')}", '']
    if inter.get('modelAnswerRubric'):
        out += ['### A quick rubric for your own answer', '']
        out += [f"- {item}" for item in inter['modelAnswerRubric']]
        out += ['']
    out += ['## Field notes', '', 'Use the four prompts below to preserve the development of your reasoning. Keep the first response; add a revision rather than rewriting history.', '']
    for key in ('observation','interpretation','alternative','revision'):
        p=lesson.get('notePrompts',{}).get(key)
        if p: out += [f"### {p['title']}", '', p['prompt'], '']
    out += ['## Knowledge check', '', 'Try the questions before reading the answer key below. In the interactive preview, the answers and automated explanations remain hidden until you submit all responses.', '']
    for qi,q in enumerate(inter['quiz'],1):
        out += [f"### {qi}. {q['q']}", '']
        for oi,option in enumerate(q['options']): out.append(f"- {chr(65+oi)}. {option}")
        out += ['']
    out += ['## Knowledge-check answer key and explanations', '', 'Use this section only after you have tried the questions.', '']
    for qi,q in enumerate(inter['quiz'],1):
        correct = q['options'][q['correct']]
        out += [f"### {qi}. Answer: {chr(65+q['correct'])}", '', correct, '', q['feedback'], '']
    out += ['## Take this with you', '', lesson['takeaway'], '', 'The historical chart extracts in this internal review package are temporary teaching examples. Replace them with user-owned or rights-cleared data before public release.', '']
    (ROOT/m['file']).write_text('\n'.join(out),encoding='utf-8')
print('Rebuilt three learner manuscripts from the exact preview content and interactions.')
