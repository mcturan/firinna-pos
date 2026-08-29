import json
import re

with open('/opt/firinna-pos/translations.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)

with open('/opt/firinna-pos/web/script.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Helper to format dict as JS object block (unquoted keys)
def format_js_dict(d, indent=8):
    lines = [" {"]
    for k, v in d.items():
        v_str = json.dumps(v, ensure_ascii=False)
        lines.append(" " * indent + f"{k}: {v_str},")
    lines.append(" " * (indent - 4) + "}")
    return "\n".join(lines)

el_js = "el:" + format_js_dict(translations['el'])
ja_js = "ja:" + format_js_dict(translations['ja'])

# replace el block
content = re.sub(r'el:\s*\{[\s\S]*?\},(?=\s*ja:\s*\{)', el_js + ",\n\n", content, count=1)
# replace ja block
content = re.sub(r'ja:\s*\{[\s\S]*?\},(?=\s*tr:\s*\{)', ja_js + ",\n\n", content, count=1)

with open('/opt/firinna-pos/web/script.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated script.js successfully")
