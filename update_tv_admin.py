import re

with open("/opt/firinna-pos/templates/tv_admin.html", "r") as f:
    content = f.read()

# Add GR and JP textareas in UI
es_block = """                <!-- 🇪🇸 İspanyolca (ES) -->
                <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-radius:8px; padding:12px; margin-bottom:12px;">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                        <span style="font-size:1.2rem;">🇪🇸</span>
                        <strong style="color:#0f172a; font-size:0.92rem;">Español:</strong>
                        <input type="text" id="ah_title_es" value="Actualmente estamos cerrados" style="flex:1; padding:6px 10px; border:1px solid #cbd5e1; border-radius:6px; font-weight:700;">
                    </div>
                    <textarea id="ah_text_es" rows="2" style="width:100%; padding:6px 10px; border:1px solid #cbd5e1; border-radius:6px; font-size:0.88rem; margin-bottom:6px; box-sizing:border-box;">Estimados clientes, actualmente estamos cerrados. Estaremos encantados de recibirles con nuestros deliciosos productos de panadería artesanal.</textarea>
                    <input type="text" id="ah_badge_es" value="☀️ Apertura: 08:00 (Todos los días)" placeholder="Açılış Rozeti" style="width:100%; padding:5px 10px; border:1px solid #86efac; background:#f0fdf4; border-radius:6px; font-size:0.85rem; font-weight:700; color:#15803d; box-sizing:border-box;">
                </div>"""

gr_jp_block = """
                <!-- 🇬🇷 Yunanca (EL) -->
                <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-radius:8px; padding:12px; margin-bottom:12px;">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                        <span style="font-size:1.2rem;">🇬🇷</span>
                        <strong style="color:#0f172a; font-size:0.92rem;">Ελληνικά:</strong>
                        <input type="text" id="ah_title_el" value="Αυτή τη στιγμή είμαστε κλειστά" style="flex:1; padding:6px 10px; border:1px solid #cbd5e1; border-radius:6px; font-weight:700;">
                    </div>
                    <textarea id="ah_text_el" rows="2" style="width:100%; padding:6px 10px; border:1px solid #cbd5e1; border-radius:6px; font-size:0.88rem; margin-bottom:6px; box-sizing:border-box;">Αγαπητοί επισκέπτες, είμαστε κλειστά. Ανυπομονούμε να σας καλωσορίσουμε με φρέσκα αρτοσκευάσματα και ζεστή φιλοξενία.</textarea>
                    <input type="text" id="ah_badge_el" value="☀️ Άνοιγμα: 08:00 (Καθημερινά)" placeholder="Açılış Rozeti" style="width:100%; padding:5px 10px; border:1px solid #86efac; background:#f0fdf4; border-radius:6px; font-size:0.85rem; font-weight:700; color:#15803d; box-sizing:border-box;">
                </div>

                <!-- 🇯🇵 Japonca (JA) -->
                <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-radius:8px; padding:12px; margin-bottom:12px;">
                    <div style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                        <span style="font-size:1.2rem;">🇯🇵</span>
                        <strong style="color:#0f172a; font-size:0.92rem;">日本語:</strong>
                        <input type="text" id="ah_title_ja" value="現在閉店しています" style="flex:1; padding:6px 10px; border:1px solid #cbd5e1; border-radius:6px; font-weight:700;">
                    </div>
                    <textarea id="ah_text_ja" rows="2" style="width:100%; padding:6px 10px; border:1px solid #cbd5e1; border-radius:6px; font-size:0.88rem; margin-bottom:6px; box-sizing:border-box;">お客様各位、現在閉店しております。焼き立てのパンと温かいおもてなしで皆様をお迎えできることを楽しみにしております。</textarea>
                    <input type="text" id="ah_badge_ja" value="☀️ 開店: 08:00 (毎日)" placeholder="Açılış Rozeti" style="width:100%; padding:5px 10px; border:1px solid #86efac; background:#f0fdf4; border-radius:6px; font-size:0.85rem; font-weight:700; color:#15803d; box-sizing:border-box;">
                </div>"""

content = content.replace(es_block, es_block + gr_jp_block)

# Add to getValues JS block
get_js = """                            lang: 'es',
                            flag: '🇪🇸',
                            tag: '🇪🇸 ESPAÑOL',
                            title: document.getElementById('ah_title_es') ? document.getElementById('ah_title_es').value : '',
                            text: document.getElementById('ah_text_es') ? document.getElementById('ah_text_es').value : '',
                            badge: document.getElementById('ah_badge_es') ? document.getElementById('ah_badge_es').value : ''
                        }"""

get_js_new = get_js + """,
                        {
                            lang: 'el',
                            flag: '🇬🇷',
                            tag: '🇬🇷 ΕΛΛΗΝΙΚΑ',
                            title: document.getElementById('ah_title_el') ? document.getElementById('ah_title_el').value : '',
                            text: document.getElementById('ah_text_el') ? document.getElementById('ah_text_el').value : '',
                            badge: document.getElementById('ah_badge_el') ? document.getElementById('ah_badge_el').value : ''
                        },
                        {
                            lang: 'ja',
                            flag: '🇯🇵',
                            tag: '🇯🇵 日本語',
                            title: document.getElementById('ah_title_ja') ? document.getElementById('ah_title_ja').value : '',
                            text: document.getElementById('ah_text_ja') ? document.getElementById('ah_text_ja').value : '',
                            badge: document.getElementById('ah_badge_ja') ? document.getElementById('ah_badge_ja').value : ''
                        }"""

content = content.replace(get_js, get_js_new)

# Add to setVal JS block
set_js = "const esMsg = msgs.find(m => m.lang === 'es') || {};"
set_js_new = set_js + """
                const elMsg = msgs.find(m => m.lang === 'el') || {};
                const jaMsg = msgs.find(m => m.lang === 'ja') || {};"""
content = content.replace(set_js, set_js_new)

set_js2 = """                setVal('ah_title_es', esMsg.title || 'Actualmente estamos cerrados');
                setVal('ah_text_es', esMsg.text || 'Estimados clientes, actualmente estamos cerrados. Estaremos encantados de recibirles con nuestros deliciosos productos de panadería artesanal.');
                setVal('ah_badge_es', esMsg.badge || esMsg.opening_badge || '☀️ Apertura: 08:00 (Todos los días)');"""

set_js2_new = set_js2 + """
                setVal('ah_title_el', elMsg.title || 'Αυτή τη στιγμή είμαστε κλειστά');
                setVal('ah_text_el', elMsg.text || 'Αγαπητοί επισκέπτες, είμαστε κλειστά. Ανυπομονούμε να σας καλωσορίσουμε με φρέσκα αρτοσκευάσματα και ζεστή φιλοξενία.');
                setVal('ah_badge_el', elMsg.badge || elMsg.opening_badge || '☀️ Άνοιγμα: 08:00 (Καθημερινά)');

                setVal('ah_title_ja', jaMsg.title || '現在閉店しています');
                setVal('ah_text_ja', jaMsg.text || 'お客様各位、現在閉店しております。焼き立てのパンと温かいおもてなしで皆様をお迎えできることを楽しみにしております。');
                setVal('ah_badge_ja', jaMsg.badge || jaMsg.opening_badge || '☀️ 開店: 08:00 (毎日)');"""

content = content.replace(set_js2, set_js2_new)

# Subtitle replacements (12 languages to 14 languages)
content = content.replace("12 Dilde", "14 Dilde").replace("12 Languages", "14 Languages").replace("12 языках", "14 языках").replace("12 Idiomas", "14 Idiomas").replace("12 لغة", "14 لغة")

with open("/opt/firinna-pos/templates/tv_admin.html", "w") as f:
    f.write(content)
