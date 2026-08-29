import re

with open('/opt/firinna-pos/web/script.js', 'r') as f:
    text = f.read()

i18n_start = text.find('const i18n = {')
i18n_end = text.find('document.addEventListener', i18n_start)
i18n_text = text[i18n_start:i18n_end]

start = i18n_text.find('en: {')
start += len('en: {')
depth = 1
end = start
for i in range(start, len(i18n_text)):
    if i18n_text[i] == '{': depth += 1
    elif i18n_text[i] == '}': depth -= 1
    if depth == 0:
        end = i
        break
        
en_block = i18n_text[start:end]

en_dict = {}
for line in en_block.split('\n'):
    line = line.strip()
    if not line or line.startswith('//'): continue
    if ':' in line:
        key = line.split(':', 1)[0].strip().strip('\'"')
        val = line.split(':', 1)[1].strip().rstrip(',').strip('\'"')
        if not ' ' in key and key != '':
            en_dict[key] = val

import json
with open('en_full.json', 'w') as f:
    json.dump(en_dict, f, indent=2, ensure_ascii=False)
