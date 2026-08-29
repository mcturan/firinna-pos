import re

with open("/opt/firinna-pos/app.py", "r") as f:
    app_content = f.read()

old_ping = """            try:
                param = '-n' if platform.system().lower()=='windows' else '-c'
                ping_cmd = ['ping', param, '1', '-W', '1', ip]
                res = subprocess.run(ping_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                is_device_on = (res.returncode == 0)
            except:
                pass"""

new_ping = """            try:
                param = '-n' if platform.system().lower()=='windows' else '-c'
                ping_path = 'ping' if platform.system().lower()=='windows' else '/usr/bin/ping'
                ping_cmd = [ping_path, param, '1', '-W', '1', ip]
                res = subprocess.run(ping_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                is_device_on = (res.returncode == 0)
            except:
                pass"""

app_content = app_content.replace(old_ping, new_ping)

with open("/opt/firinna-pos/app.py", "w") as f:
    f.write(app_content)
