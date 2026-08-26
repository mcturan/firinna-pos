import re

with open("/opt/firinna-pos/app.py", "r") as f:
    app_content = f.read()

# Instead of just _tv_clients = {}, let's save and load it
old_def = "_tv_clients = {}"
new_def = """import json, os

_TV_CLIENTS_DB = '/opt/firinna-pos/tv_clients.json'
_tv_clients = {}
try:
    if os.path.exists(_TV_CLIENTS_DB):
        with open(_TV_CLIENTS_DB, 'r') as f:
            _tv_clients = json.load(f)
except:
    pass

def save_tv_clients():
    try:
        with open(_TV_CLIENTS_DB, 'w') as f:
            json.dump(_tv_clients, f)
    except:
        pass"""

app_content = app_content.replace(old_def, new_def)

# In api_tv_ping, save the clients
old_ping = """            _tv_clients[client_id] = {
                'ip': ip,
                'last_ping': now_str,
                'last_ping_ts': now_ts,
                'device_type': device_type,
                'name': name
            }"""

new_ping = """            _tv_clients[client_id] = {
                'ip': ip,
                'last_ping': now_str,
                'last_ping_ts': now_ts,
                'device_type': device_type,
                'name': name
            }
            save_tv_clients()"""
app_content = app_content.replace(old_ping, new_ping)

with open("/opt/firinna-pos/app.py", "w") as f:
    f.write(app_content)
