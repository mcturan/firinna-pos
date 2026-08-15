import re
import js2py
html = open('templates/index.html').read()
scripts = re.findall(r'<script.*?>([\s\S]*?)</script>', html, re.IGNORECASE)
for idx, s in enumerate(scripts):
    try:
        js2py.parse_js(s)
    except Exception as e:
        print(f"Error in script {idx}: {e}")
