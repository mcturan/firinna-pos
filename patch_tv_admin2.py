import re

# 1. Update app.py to 15 seconds timeout
with open("/opt/firinna-pos/app.py", "r") as f:
    app_content = f.read()

# is_online = (now_ts - info.get('last_ping_ts', 0)) < 45
app_content = re.sub(r"is_online = \(now_ts - info\.get\('last_ping_ts', 0\)\) < \d+", "is_online = (now_ts - info.get('last_ping_ts', 0)) < 15", app_content)

with open("/opt/firinna-pos/app.py", "w") as f:
    f.write(app_content)


# 2. Update tv_admin.html layout
with open("/opt/firinna-pos/templates/tv_admin.html", "r") as f:
    html_content = f.read()

# We will regex replace the whole html += div block for clients.
old_html_block = """                    let bgCol = c.is_online ? '#f0fdf4' : (c.needs_attention ? '#fffbeb' : '#f8fafc');
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
                            </div>
                            <div style="font-size:0.82rem; color:#64748b;">
                                <b>Cihaz ID:</b> <code style="background:#e2e8f0; padding:1px 5px; border-radius:3px; font-weight:bold; color:#0f172a;">${c.client_id}</code><br>
                                <b>IP:</b> ${c.ip} • <b>Ad:</b> ${c.name}
                            </div>
                            <div style="display:flex; gap:6px; margin-top:4px;">
                                <button type="button" onclick="pushInstantUpdate('reload', '${c.client_id}')" style="flex:1; background:#dc2626; color:white; border:none; padding:4px 8px; border-radius:4px; font-size:0.78rem; font-weight:bold; cursor:pointer;" title="Uygulamayı Yeniden Başlat">
                                    🔄 Uygulama
                                </button>
                                <button type="button" onclick="pushInstantUpdate('clear_cache', '${c.client_id}')" style="flex:1; background:#ea580c; color:white; border:none; padding:4px 8px; border-radius:4px; font-size:0.78rem; font-weight:bold; cursor:pointer;" title="Önbelleği Sil ve Yeniden Başlat">
                                    🧹 Cache Sil
                                </button>
                                <button type="button" onclick="rebootDeviceHardware('${c.ip}')" style="flex:1; background:#475569; color:white; border:none; padding:4px 8px; border-radius:4px; font-size:0.78rem; font-weight:bold; cursor:pointer;" title="Cihazı Komple Kapatıp Aç (Donanımsal Reboot)">
                                    🔌 Cihaz Reboot
                                </button>
                            </div>
                        </div>
                    `;"""

new_html_block = """                    let isAppOpen = c.is_online;
                    let isDeviceOn = c.is_device_on;
                    // If app is open, device must be on.
                    if (isAppOpen) isDeviceOn = true;

                    let bgCol = isAppOpen ? '#f0fdf4' : (isDeviceOn ? '#fffbeb' : '#fef2f2');
                    let borderCol = isAppOpen ? '#86efac' : (isDeviceOn ? '#fde047' : '#fca5a5');

                    let deviceStatusHtml = isDeviceOn 
                        ? `<span style="color:#15803d; font-weight:bold; background:#dcfce7; padding:2px 6px; border-radius:4px;">🟢 AÇIK</span>`
                        : `<span style="color:#b91c1c; font-weight:bold; background:#fee2e2; padding:2px 6px; border-radius:4px;">🔴 KAPALI</span>`;
                        
                    let appStatusHtml = isAppOpen
                        ? `<span style="color:#15803d; font-weight:bold; background:#dcfce7; padding:2px 6px; border-radius:4px;">🟢 AÇIK</span>`
                        : `<span style="color:#b91c1c; font-weight:bold; background:#fee2e2; padding:2px 6px; border-radius:4px;">🔴 KAPALI</span>`;

                    html += `
                        <div style="background:${bgCol}; border:2px solid ${borderCol}; border-radius:8px; padding:12px; display:flex; flex-direction:column; gap:8px; box-shadow:0 2px 4px rgba(0,0,0,0.02);">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <span style="font-weight:900; font-size:1rem; color:#1e293b;">${c.name || c.device_type}</span>
                                <span style="font-size:0.75rem; color:#64748b; font-weight:bold;">${Math.floor(c.seconds_ago/60)} dk önce görüldü</span>
                            </div>
                            
                            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; background:white; padding:8px; border-radius:6px; border:1px solid #e2e8f0;">
                                <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
                                    <span style="font-size:0.8rem; font-weight:bold; color:#475569;">Fiziksel Cihaz (Mi Stick)</span>
                                    ${deviceStatusHtml}
                                </div>
                                <div style="display:flex; flex-direction:column; align-items:center; gap:4px; border-left:1px solid #e2e8f0;">
                                    <span style="font-size:0.8rem; font-weight:bold; color:#475569;">Fırınna Uygulaması</span>
                                    ${appStatusHtml}
                                </div>
                            </div>

                            <div style="font-size:0.82rem; color:#64748b; text-align:center;">
                                <b>IP:</b> ${c.ip} &nbsp;•&nbsp; <b>ID:</b> <code>${c.client_id}</code>
                            </div>
                            
                            <div style="display:flex; gap:6px; margin-top:4px;">
                                <button type="button" onclick="pushInstantUpdate('reload', '${c.client_id}')" style="flex:1; background:${isAppOpen ? '#3b82f6' : '#94a3b8'}; color:white; border:none; padding:6px 8px; border-radius:4px; font-size:0.75rem; font-weight:bold; cursor:${isAppOpen ? 'pointer' : 'not-allowed'};" title="Uygulamayı Yeniden Başlat" ${!isAppOpen ? 'disabled' : ''}>
                                    🔄 Uygulama Yenile
                                </button>
                                <button type="button" onclick="pushInstantUpdate('clear_cache', '${c.client_id}')" style="flex:1; background:${isAppOpen ? '#ea580c' : '#94a3b8'}; color:white; border:none; padding:6px 8px; border-radius:4px; font-size:0.75rem; font-weight:bold; cursor:${isAppOpen ? 'pointer' : 'not-allowed'};" title="Önbelleği Sil ve Yeniden Başlat" ${!isAppOpen ? 'disabled' : ''}>
                                    🧹 Cache Sil
                                </button>
                                <button type="button" onclick="rebootDeviceHardware('${c.ip}')" style="flex:1; background:${isDeviceOn ? '#1e293b' : '#94a3b8'}; color:white; border:none; padding:6px 8px; border-radius:4px; font-size:0.75rem; font-weight:bold; cursor:${isDeviceOn ? 'pointer' : 'not-allowed'};" title="Cihazı Komple Kapatıp Aç (Donanımsal Reboot)" ${!isDeviceOn ? 'disabled' : ''}>
                                    🔌 Cihaz Reboot
                                </button>
                            </div>
                        </div>
                    `;"""

html_content = html_content.replace(old_html_block, new_html_block)

with open("/opt/firinna-pos/templates/tv_admin.html", "w") as f:
    f.write(html_content)
