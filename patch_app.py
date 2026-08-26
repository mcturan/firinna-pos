import re

with open("/opt/firinna-pos/app.py", "r") as f:
    content = f.read()

# 1. Modify api_tv_clients to include ping logic
old_clients = """def api_tv_clients():
    now_ts = time.time()
    # Purge entries older than 30 minutes
    for cid, info in list(_tv_clients.items()):
        if (now_ts - info.get('last_ping_ts', 0)) > 1800:
            del _tv_clients[cid]

    active_list = []
    for cid, info in list(_tv_clients.items()):
        is_online = (now_ts - info.get('last_ping_ts', 0)) < 45
        active_list.append({
            'client_id': cid,
            'ip': info.get('ip'),
            'device_type': info.get('device_type'),
            'name': info.get('name'),
            'last_ping': info.get('last_ping'),
            'is_online': is_online,
            'seconds_ago': int(now_ts - info.get('last_ping_ts', 0))
        })
    # Sort online first, then by most recent ping
    active_list.sort(key=lambda x: (not x['is_online'], x['seconds_ago']))
    return jsonify({"clients": active_list})"""

new_clients = """def api_tv_clients():
    now_ts = time.time()
    import subprocess
    import platform
    
    # We will temporarily keep known IPs forever so we can reboot them, 
    # instead of purging them after 30 mins, let's keep them up to 48 hours.
    for cid, info in list(_tv_clients.items()):
        if (now_ts - info.get('last_ping_ts', 0)) > 48 * 3600:
            del _tv_clients[cid]

    active_list = []
    for cid, info in list(_tv_clients.items()):
        is_online = (now_ts - info.get('last_ping_ts', 0)) < 45
        ip = info.get('ip')
        
        # Ping the device to see if it's alive on network
        is_device_on = False
        if ip and ip != '127.0.0.1':
            try:
                param = '-n' if platform.system().lower()=='windows' else '-c'
                ping_cmd = ['ping', param, '1', '-W', '1', ip]
                res = subprocess.run(ping_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                is_device_on = (res.returncode == 0)
            except:
                pass

        active_list.append({
            'client_id': cid,
            'ip': ip,
            'device_type': info.get('device_type'),
            'name': info.get('name'),
            'last_ping': info.get('last_ping'),
            'is_online': is_online,
            'is_device_on': is_device_on,
            'needs_attention': is_device_on and not is_online,
            'seconds_ago': int(now_ts - info.get('last_ping_ts', 0))
        })
    active_list.sort(key=lambda x: (not x['is_online'], x['seconds_ago']))
    return jsonify({"clients": active_list})"""

content = content.replace(old_clients, new_clients)

# 2. Modify api_tv_device_reboot to actually execute adb reboot
old_reboot = """def api_tv_device_reboot():
    data = request.json or {}
    target_ip = data.get('ip', '').strip()
    
    if not target_ip or target_ip.startswith('127.') or target_ip.startswith('localhost'):
        return jsonify({"status": "error", "message": "Geçersiz veya yerel IP adresi."}), 400
        
    import subprocess
    try:
        # Assuming Android ADB is available and configured
        subprocess.Popen(['adb', 'connect', target_ip])
        time.sleep(1)
        subprocess.Popen(['adb', '-s', f'{target_ip}:5555', 'reboot'])
        return jsonify({"status": "success", "message": f"{target_ip} cihazına yeniden başlatma sinyali gönderildi."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500"""

new_reboot = """def api_tv_device_reboot():
    data = request.json or {}
    target_ip = data.get('ip', '').strip()
    
    if not target_ip or target_ip.startswith('127.') or target_ip.startswith('localhost'):
        return jsonify({"status": "error", "message": "Geçersiz veya yerel IP adresi."}), 400
        
    import subprocess
    import threading
    
    def reboot_task():
        try:
            subprocess.run(['adb', 'connect', target_ip], timeout=5)
            subprocess.run(['adb', '-s', f'{target_ip}:5555', 'reboot'], timeout=5)
        except:
            pass
            
    threading.Thread(target=reboot_task).start()
    return jsonify({"status": "success", "message": f"{target_ip} cihazına yeniden başlatma sinyali gönderildi."})"""

content = content.replace(old_reboot, new_reboot)

with open("/opt/firinna-pos/app.py", "w") as f:
    f.write(content)
