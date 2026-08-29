import json, re

with open('en_full.json', 'r', encoding='utf-8') as f:
    en_dict = json.load(f)

el_dict = {}
ja_dict = {}

# Dummy AI translation for now, wait I should do real translation.
