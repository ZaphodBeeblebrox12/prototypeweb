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
    if typ in ('ol','ul'):
        marker='1.' if typ=='ol' else '-'
        return '\n'.join(f"{marker if typ=='ul' else str(i+1)+'.'} {item}" for i,item in enumerate(b.get('items',[])))+'\n'
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
        out += [f"### {stage['title']}", '', f"![{stage['alt']}]({stage['image']})", '', f"**Instructor prompt:** {stage['prompt']}", '', f"**Write before revealing:** {stage.get('placeholder','Record the observation, interpretation, alternative and condition that would change your view.')}", '']
    out += ['## Field notes', '', 'Use the four prompts below to preserve the development of your reasoning. Keep the first response; add a revision rather than rewriting history.', '']
    for key in ('observation','interpretation','alternative','revision'):
        p=lesson.get('notePrompts',{}).get(key)
        if p: out += [f"### {p['title']}", '', p['prompt'], '']
    out += ['## Knowledge check', '', 'Answer before reading the feedback. In the interactive preview, explanations remain hidden until the answers are submitted.', '']
    for qi,q in enumerate(inter['quiz'],1):
        out += [f"### {qi}. {q['q']}", '']
        for oi,option in enumerate(q['options']): out.append(f"- {'**' if oi==q['correct'] else ''}{chr(65+oi)}. {option}{'**' if oi==q['correct'] else ''}")
        out += ['', f"**Instructor feedback:** {q['feedback']}", '']
    out += ['## Instructor close', '', lesson['takeaway'], '', 'The historical chart extracts in this internal review package are temporary teaching examples. Replace them with user-owned or rights-cleared data before public release.', '']
    (ROOT/m['file']).write_text('\n'.join(out),encoding='utf-8')
print('Rebuilt three learner manuscripts from the exact preview content and interactions.')
