from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
data=json.loads((ROOT/'tools'/'lesson_interactions.json').read_text(encoding='utf-8'))
by_id={str(x['id']):x for x in data}
(ROOT/'assets'/'module5-interactions.js').write_text(
    'window.MODULE5_INTERACTIONS = '+json.dumps(by_id,ensure_ascii=False,indent=2)+';\n',
    encoding='utf-8'
)
print('Built assets/module5-interactions.js from tools/lesson_interactions.json')
