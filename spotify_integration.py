import os
import json
import time
import base64
import requests
import urllib.parse
from flask import request, redirect, jsonify, Blueprint

spotify_bp = Blueprint('spotify_bp', __name__)

SPOTIFY_CLIENT_ID = "2ba926daf2054bce9cd76aff25fae899"
SPOTIFY_CLIENT_SECRET = "6fbe27d75ad2465da9e09bf1f55a96a2"
SPOTIFY_REDIRECT_URI = "https://google.com/callback"

SPOTIFY_TOKEN_FILE = os.path.join(os.path.dirname(__file__), 'spotify_tokens.json')

def load_spotify_tokens():
    if os.path.exists(SPOTIFY_TOKEN_FILE):
        try:
            with open(SPOTIFY_TOKEN_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_spotify_tokens(tokens):
    with open(SPOTIFY_TOKEN_FILE, 'w', encoding='utf-8') as f:
        json.dump(tokens, f)

def get_valid_access_token():
    tokens = load_spotify_tokens()
    if not tokens or 'refresh_token' not in tokens:
        return None

    if time.time() > tokens.get('expires_at', 0) - 60:
        auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
        b64_auth_str = base64.b64encode(auth_str.encode()).decode()
        headers = {
            'Authorization': f'Basic {b64_auth_str}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': tokens['refresh_token']
        }
        try:
            res = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data, timeout=10)
            if res.status_code == 200:
                new_data = res.json()
                tokens['access_token'] = new_data['access_token']
                tokens['expires_at'] = time.time() + new_data['expires_in']
                if 'refresh_token' in new_data:
                    tokens['refresh_token'] = new_data['refresh_token']
                save_spotify_tokens(tokens)
            else:
                return None
        except Exception:
            return None
            
    return tokens.get('access_token')

@spotify_bp.route('/api/spotify/login')
def spotify_login():
    scope = "user-read-playback-state user-modify-playback-state user-read-currently-playing playlist-read-private playlist-read-collaborative user-library-read streaming"
    auth_url = (
        f"https://accounts.spotify.com/authorize?response_type=code"
        f"&client_id={SPOTIFY_CLIENT_ID}"
        f"&scope={urllib.parse.quote(scope)}"
        f"&redirect_uri={urllib.parse.quote(SPOTIFY_REDIRECT_URI)}"
    )
    return redirect(auth_url)

@spotify_bp.route('/api/spotify/callback')
def spotify_callback():
    code = request.args.get('code')
    if not code:
        return "Error: No code provided", 400

    auth_str = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    b64_auth_str = base64.b64encode(auth_str.encode()).decode()

    headers = {
        'Authorization': f'Basic {b64_auth_str}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI
    }

    res = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
    if res.status_code == 200:
        token_data = res.json()
        token_data['expires_at'] = time.time() + token_data['expires_in']
        save_spotify_tokens(token_data)
        return redirect('/radio')
    else:
        return f"Error: {res.text}", 400

@spotify_bp.route('/api/spotify/status')
def spotify_status():
    tokens = load_spotify_tokens()
    return jsonify({
        "connected": 'refresh_token' in tokens
    })

@spotify_bp.route('/api/spotify/playlists')
def spotify_playlists():
    token = get_valid_access_token()
    if not token:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = requests.get('https://api.spotify.com/v1/me/playlists?limit=50', headers=headers, timeout=10)
        if res.status_code == 200:
            return jsonify({"success": True, "playlists": res.json().get('items', [])})
        else:
            return jsonify({"success": False, "error": res.text}), res.status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@spotify_bp.route('/api/spotify/playlist/<playlist_id>/tracks')
def spotify_playlist_tracks(playlist_id):
    token = get_valid_access_token()
    if not token:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = requests.get(f'https://api.spotify.com/v1/playlists/{playlist_id}/tracks?limit=100', headers=headers, timeout=10)
        if res.status_code == 200:
            items = res.json().get('items', [])
            tracks = []
            for it in items:
                tr = it.get('track')
                if tr:
                    tracks.append({
                        "id": tr.get('id'),
                        "name": tr.get('name'),
                        "uri": tr.get('uri'),
                        "artists": ", ".join([a.get('name') for a in tr.get('artists', [])]),
                        "duration_ms": tr.get('duration_ms'),
                        "image": tr.get('album', {}).get('images', [{}])[0].get('url') if tr.get('album', {}).get('images') else None
                    })
            return jsonify({"success": True, "tracks": tracks})
        else:
            return jsonify({"success": False, "error": res.text}), res.status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@spotify_bp.route('/api/spotify/devices')
def spotify_devices():
    token = get_valid_access_token()
    if not token:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = requests.get('https://api.spotify.com/v1/me/player/devices', headers=headers, timeout=10)
        if res.status_code == 200:
            return jsonify({"success": True, "devices": res.json().get('devices', [])})
        else:
            return jsonify({"success": False, "error": res.text}), res.status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@spotify_bp.route('/api/spotify/play', methods=['POST'])
def spotify_play():
    token = get_valid_access_token()
    if not token:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    req = request.json or {}
    context_uri = req.get('context_uri')
    uris = req.get('uris')
    offset = req.get('offset')
    device_id = req.get('device_id')

    headers = {'Authorization': f'Bearer {token}'}
    if not device_id:
        try:
            d_res = requests.get('https://api.spotify.com/v1/me/player/devices', headers=headers, timeout=5)
            if d_res.status_code == 200:
                devices = d_res.json().get('devices', [])
                firinna_dev = next((d for d in devices if 'firinna' in d.get('name', '').lower()), None)
                if firinna_dev:
                    device_id = firinna_dev.get('id')
                elif devices:
                    device_id = devices[0].get('id')
        except Exception:
            pass

    try:
        from app import _stop_all_audio_processes, load_radio_data, save_radio_data
        _stop_all_audio_processes()
        r_data = load_radio_data()
        r_data['state']['is_playing'] = False
        r_data['state']['source_type'] = 'spotify'
        save_radio_data(r_data)
    except Exception:
        pass

    url = 'https://api.spotify.com/v1/me/player/play'
    if device_id:
        url += f"?device_id={device_id}"

    body = {}
    if context_uri:
        body['context_uri'] = context_uri
    elif uris:
        body['uris'] = uris
    if offset is not None:
        body['offset'] = offset

    try:
        res = requests.put(url, headers=headers, json=body, timeout=10)
        if res.status_code in (200, 202, 204):
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": res.text}), res.status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@spotify_bp.route('/api/spotify/pause', methods=['POST'])
def spotify_pause():
    token = get_valid_access_token()
    if not token:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = requests.put('https://api.spotify.com/v1/me/player/pause', headers=headers, timeout=10)
        return jsonify({"success": res.status_code in (200, 202, 204)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@spotify_bp.route('/api/spotify/next', methods=['POST'])
def spotify_next():
    token = get_valid_access_token()
    if not token:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = requests.post('https://api.spotify.com/v1/me/player/next', headers=headers, timeout=10)
        return jsonify({"success": res.status_code in (200, 202, 204)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@spotify_bp.route('/api/spotify/previous', methods=['POST'])
def spotify_previous():
    token = get_valid_access_token()
    if not token:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = requests.post('https://api.spotify.com/v1/me/player/previous', headers=headers, timeout=10)
        return jsonify({"success": res.status_code in (200, 202, 204)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@spotify_bp.route('/api/spotify/current')
def spotify_current():
    token = get_valid_access_token()
    if not token:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = requests.get('https://api.spotify.com/v1/me/player', headers=headers, timeout=10)
        if res.status_code == 200 and res.text:
            data = res.json()
            item = data.get('item') or {}
            return jsonify({
                "success": True,
                "is_playing": data.get('is_playing', False),
                "device": data.get('device', {}).get('name'),
                "track": {
                    "id": item.get('id'),
                    "name": item.get('name'),
                    "artists": ", ".join([a.get('name') for a in item.get('artists', [])]),
                    "album": item.get('album', {}).get('name'),
                    "image": item.get('album', {}).get('images', [{}])[0].get('url') if item.get('album', {}).get('images') else None,
                    "duration_ms": item.get('duration_ms'),
                    "progress_ms": data.get('progress_ms')
                }
            })
        elif res.status_code == 204:
            return jsonify({"success": True, "is_playing": False, "track": None})
        else:
            return jsonify({"success": False, "error": res.text}), res.status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@spotify_bp.route('/api/spotify/search')
def spotify_search():
    token = get_valid_access_token()
    if not token:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify({"success": True, "tracks": [], "playlists": []})
    
    headers = {'Authorization': f'Bearer {token}'}
    try:
        res = requests.get(f'https://api.spotify.com/v1/search?q={urllib.parse.quote(q)}&type=track,playlist&limit=20', headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            tracks_raw = data.get('tracks', {}).get('items', [])
            playlists_raw = data.get('playlists', {}).get('items', [])
            
            tracks = []
            for tr in tracks_raw:
                if tr:
                    tracks.append({
                        "id": tr.get('id'),
                        "name": tr.get('name'),
                        "uri": tr.get('uri'),
                        "artists": ", ".join([a.get('name') for a in tr.get('artists', [])]),
                        "image": tr.get('album', {}).get('images', [{}])[0].get('url') if tr.get('album', {}).get('images') else None
                    })
            return jsonify({
                "success": True,
                "tracks": tracks,
                "playlists": [p for p in playlists_raw if p]
            })
        else:
            return jsonify({"success": False, "error": res.text}), res.status_code
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
