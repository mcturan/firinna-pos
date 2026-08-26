import re

with open("/opt/firinna-pos/templates/tv_admin.html", "r") as f:
    content = f.read()

old_html = """                let html = '';
                clients.forEach(c => {
                    html += `
                        <div style="background:${c.is_online ? '#f0fdf4' : '#f8fafc'}; border:1.5px solid ${c.is_online ? '#86efac' : '#e2e8f0'}; border-radius:8px; padding:10px 12px; display:flex; flex-direction:column; gap:6px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-weight:bold; font-size:0.95rem; color:#1e293b;">${c.device_type}</span>
                                <span style="font-size:0.78rem; font-weight:bold; color:${c.is_online ? '#15803d' : '#94a3b8'};">
                                    ${c.is_online ? '🟢 Canlı' : `⚪ ${Math.floor(c.seconds_ago/60)}dk önce`}
                                </span>
                            </div>"""

new_html = """                let html = '';
                clients.forEach(c => {
                    
                    let bgCol = c.is_online ? '#f0fdf4' : (c.needs_attention ? '#fffbeb' : '#f8fafc');
                    let borderCol = c.is_online ? '#86efac' : (c.needs_attention ? '#fde047' : '#e2e8f0');
                    let statText = c.is_online ? '🟢 Canlı' : (c.needs_attention ? '⚠️ Cihaz Açık, Uygulama Kapalı!' : `⚪ ${Math.floor(c.seconds_ago/60)}dk önce (Kapalı)`);
                    let statCol = c.is_online ? '#15803d' : (c.needs_attention ? '#ca8a04' : '#94a3b8');

                    html += `
                        <div style="background:${bgCol}; border:1.5px solid ${borderCol}; border-radius:8px; padding:10px 12px; display:flex; flex-direction:column; gap:6px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-weight:bold; font-size:0.95rem; color:#1e293b;">${c.device_type}</span>
                                <span style="font-size:0.78rem; font-weight:bold; color:${statCol};">
                                    ${statText}
                                </span>
                            </div>"""

content = content.replace(old_html, new_html)

# Add Warning to the upload input
old_upload = """<input type="file" id="videoUploadInput" accept="video/mp4, video/webm, video/ogg" style="display:block; width:100%; font-size:0.9rem;">"""
new_upload = """<input type="file" id="videoUploadInput" accept="video/mp4, video/webm, video/ogg" style="display:block; width:100%; font-size:0.9rem;" onchange="if(this.files[0] && this.files[0].size > 500*1024*1024) { alert('UYARI: Seçtiğiniz dosya 500 MB\\'dan büyük (' + (this.files[0].size/1024/1024).toFixed(1) + ' MB). TV Stick\\'te donmalara veya uygulamadan atma sorunlarına (RAM dolması) yol açabilir. Lütfen bu dosyayı yüklemeden önce sıkıştırınız (Önerilen: Maks 500 MB).'); }">"""
content = content.replace(old_upload, new_upload)

with open("/opt/firinna-pos/templates/tv_admin.html", "w") as f:
    f.write(content)
