import re

with open('/opt/firinna-pos/web/script.js', 'r') as f:
    text = f.read()

# Find the full i18n object definition. It goes on until document.addEventListener or similar
i18n_start = text.find('const i18n = {')
i18n_end = text.find('document.addEventListener', i18n_start)
i18n_text = text[i18n_start:i18n_end]

def get_keys(lang):
    # Find "{lang}: {"
    start = i18n_text.find(f'{lang}: {{')
    if start == -1: return set()
    start += len(f'{lang}: {{')
    
    # We will count braces to find the end
    depth = 1
    end = start
    for i in range(start, len(i18n_text)):
        if i18n_text[i] == '{': depth += 1
        elif i18n_text[i] == '}': depth -= 1
        
        if depth == 0:
            end = i
            break
            
    block = i18n_text[start:end]
    keys = set()
    for line in block.split('\n'):
        line = line.strip()
        if not line or line.startswith('//'): continue
        if ':' in line:
            key = line.split(':')[0].strip().strip('\'"')
            if not ' ' in key and key != '':
                keys.add(key)
    return keys

en_keys = get_keys('en')
tr_keys = get_keys('tr')
el_keys = get_keys('el')
ja_keys = get_keys('ja')

print(f"EN keys: {len(en_keys)}")
print(f"TR keys: {len(tr_keys)}")
print(f"EL keys: {len(el_keys)}")
print(f"JA keys: {len(ja_keys)}")

missing = en_keys - el_keys
print("Missing in EL (first 10):", list(missing)[:10])

# Output all missing keys and their EN values as JSON for translation
missing_dict = {}
for line in i18n_text[i18n_text.find('en: {'):].split('\n'):
    line = line.strip()
    if not line: continue
    if ':' in line:
        key = line.split(':')[0].strip().strip('\'"')
        if key in missing:
            val = line[line.find(':')+1:].strip().rstrip(',').strip('\'"')
            missing_dict[key] = val

import json
with open('missing.json', 'w') as f:
    json.dump(missing_dict, f, indent=2, ensure_ascii=False)

