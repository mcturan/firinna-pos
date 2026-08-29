import re
import json

with open('/opt/firinna-pos/web/i18n_dump.txt', 'r') as f:
    text = f.read()

def get_keys_for_lang(lang_code):
    # Very rough regex to extract keys for a block
    # Find the block for the language
    pattern = rf'{lang_code}:\s*{{(.*?)}}'
    matches = re.finditer(pattern, text, re.DOTALL)
    keys = set()
    for match in matches:
        block = match.group(1)
        # Find all keys
        for line in block.split('\n'):
            line = line.strip()
            if not line: continue
            if ':' in line:
                key = line.split(':')[0].strip().strip('\'"')
                keys.add(key)
    return keys

en_keys = get_keys_for_lang('en')
el_keys = get_keys_for_lang('el')
ja_keys = get_keys_for_lang('ja')

print(f"EN keys: {len(en_keys)}")
print(f"EL keys: {len(el_keys)}")
print(f"JA keys: {len(ja_keys)}")

missing_in_el = en_keys - el_keys
print("Missing in EL:", missing_in_el)
