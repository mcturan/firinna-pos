from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, make_response
import database as db
import telegram_notify
from printer import ThermalPrinter
import os
import json
import subprocess
import threading
import time
import fcntl
import signal
from datetime import datetime
import urllib.request
import re
import xml.etree.ElementTree as ET
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

from spotify_integration import spotify_bp
app.register_blueprint(spotify_bp)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["5000 per hour", "100 per minute"],
    storage_uri="memory://"
)

APP_VERSION = "1.5.5"
APP_BUILD   = "2026-08-10"

# DB migration — __name__ kontrolü olmadan her başlangıçta çalışır
try:
    db.init_db()
    db.migrate_product_stock_link()
    db.migrate_expenses_columns()
    db.migrate_kitchen_ready()
except Exception as _e:
    print(f"Startup migration warning: {_e}")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.after_request
def add_no_cache_headers(response):
    # Allow Android WebView & local app origins (CORS)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With'

    if request.path.startswith('/static/tv_media/'):
        response.headers['Cache-Control'] = 'public, max-age=86400'
        response.headers['Accept-Ranges'] = 'bytes'
        if 'Pragma' in response.headers:
            del response.headers['Pragma']
        if 'Expires' in response.headers:
            del response.headers['Expires']
        return response
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=3600'
        return response
    if request.path.startswith('/api/web/analytics') or 'admin' in request.path or 'yonetim' in request.path or request.path.startswith('/api/tv') or request.path == '/tv':
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# Ana sayfa (masalar görünümü)
@app.route('/api/mobile_version')
def api_mobile_version():
    return jsonify({
        'version': APP_VERSION,
        'apk_url': '/download_apk',
        'tv_version': '1.1.32',
        'tv_apk_url': '/static/Firinna-TV-1.1.32.apk'
    })

@app.route('/download_apk')
def download_apk():
    return send_from_directory('mobile_app', 'Firinna-Garson.apk', as_attachment=True)

@app.route('/static/Firinna-TV-<path:filename>.apk')
@app.route('/download_tv_apk')
def download_tv_apk(filename=None):
    # Always serve TV APK with 200 OK (ignore Range header) so older clients don't get 416
    apk_path = '/opt/firinna-pos/static/Firinna-TV-1.1.32.apk'
    if not os.path.exists(apk_path):
        return jsonify({"error": "APK not found"}), 404
    with open(apk_path, 'rb') as f:
        data = f.read()
    response = app.response_class(
        response=data,
        status=200,
        mimetype='application/vnd.android.package-archive'
    )
    response.headers['Content-Disposition'] = 'attachment; filename="Firinna-TV-1.1.32.apk"'
    response.headers['Content-Length'] = str(len(data))
    response.headers['Accept-Ranges'] = 'none'
    return response

import threading

_tv_log_lock = threading.Lock()
_tv_settings_lock = threading.Lock()

@app.route('/api/tv/upload_logs', methods=['POST'])
def upload_logs():
    try:
        data = request.json if request.is_json else request.form
        logs = (data.get('logs', '') if data else '') or ''
        client_id = (data.get('client_id', '') if data else '') or 'tv'
        now = datetime.now()
        timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
        today_str = now.strftime('%Y-%m-%d')
        
        if logs and logs.strip():
            log_entry = f"[{timestamp}] [{client_id}]\n{logs.strip()}\n"
            logs_file = '/opt/firinna-pos/tv_logs.txt'
            
            with _tv_log_lock:
                existing_lines = []
                if os.path.exists(logs_file):
                    try:
                        with open(logs_file, 'r', encoding='utf-8', errors='ignore') as f:
                            existing_lines = f.readlines()
                    except:
                        pass
                
                # Split incoming multi-line string to individual lines for consistent truncation
                entry_lines = [l + '\n' for l in log_entry.strip().split('\n')]
                new_lines = (existing_lines + entry_lines)[-500:]
                with open(logs_file, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                
                logs_dir = '/opt/firinna-pos/tv_logs'
                os.makedirs(logs_dir, exist_ok=True)
                daily_file = os.path.join(logs_dir, f"tv_log_{today_str}.txt")
                with open(daily_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/tv/clear_logs', methods=['POST'])
def api_clear_tv_logs():
    try:
        logs_file = '/opt/firinna-pos/tv_logs.txt'
        with _tv_log_lock:
            with open(logs_file, 'w', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] [admin]\n[LOGS CLEARED BY ADMIN]\n")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/tv/logs', methods=['GET'])
def api_get_tv_logs():
    try:
        content = ""
        if os.path.exists('/opt/firinna-pos/tv_logs.txt'):
            with open('/opt/firinna-pos/tv_logs.txt', 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        return jsonify({"success": True, "logs": content})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/version')
def api_version():
    import sqlite3
    db_path = 'pos_data.db'
    try:
        conn = sqlite3.connect(db_path)
        pv = conn.execute('PRAGMA user_version').fetchone()[0]
        conn.close()
    except:
        pv = 0
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    return jsonify({
        'app_version': APP_VERSION,
        'build_date':  APP_BUILD,
        'db_version':  pv,
        'db_size_kb':  round(db_size / 1024, 1)
    })


@app.route('/')
def index():
    response = make_response(render_template('index.html'))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route('/web')
@app.route('/web/')
def web_home():
    return send_from_directory('web', 'index.html')

@app.route('/yeni_menu.json')
def yeni_menu_json():
    return send_from_directory('web', 'yeni_menu.json')

@app.route('/menu')
@app.route('/menu.html')
def menu_web_page():
    return send_from_directory('web', 'menu.html')

@app.route('/gezi')
@app.route('/gezi/')
@app.route('/gezi.html')
def gezi_web_page():
    return send_from_directory('web', 'gezi.html')

@app.route('/admin')
@app.route('/admin.html')
@app.route('/yonetim')
@app.route('/yonetim/')
@app.route('/yonetim/index.html')
def admin_web_page():
    return send_from_directory('web', 'admin.html')

# Yönetim sayfaları
@app.route('/products')
def products_page():
    return render_template('products.html')

@app.route('/tables')
def tables_page():
    return render_template('tables.html')

@app.route('/kasa')
def kasa_page():
    return render_template('kasa.html')

@app.route('/stok')
def stok_page():
    return render_template('stok.html')

@app.route('/recete')
def recete_page():
    return render_template('recete.html')

@app.route('/api/kasa/summary', methods=['GET'])
def api_kasa_summary():
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    return jsonify(db.get_kasa_summary(date))


@app.route('/api/kasa/data', methods=['GET'])
def api_kasa_data():
    from datetime import timedelta
    period = request.args.get('period', 'daily')
    today = datetime.now().date()
    if period == 'daily':
        start = end = request.args.get('date', str(today))
    elif period == 'weekly':
        start = str(today - timedelta(days=today.weekday()))
        end = str(today)
    elif period == 'monthly':
        start = str(today.replace(day=1))
        end = str(today)
    elif period == 'custom':
        start = request.args.get('start', str(today))
        end = request.args.get('end', str(today))
    else:
        start = '2000-01-01'
        end = str(today)
    method = request.args.get('method', None)
    return jsonify(db.get_kasa_data(start, end, method))

@app.route('/api/transactions', methods=['GET'])
def api_transactions():
    start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
    end = request.args.get('end', datetime.now().strftime('%Y-%m-%d'))
    method = request.args.get('method', None)
    return jsonify(db.get_kasa_data(start, end, method))

@app.route('/api/transactions', methods=['POST'])
def api_add_transaction():
    data = request.json
    db.add_transaction(
        data['type'], data['amount'], data.get('category','masraf'),
        data.get('payment_method','cash'), data.get('description',''),
        date=data.get('date', None),
        created_at=data.get('datetime', None)
    )
    return jsonify({'success': True})


@app.route('/api/kasa/transactions', methods=['GET'])
def api_kasa_transactions():
    today = datetime.now().strftime('%Y-%m-%d')
    start    = request.args.get('date_from', today)
    end      = request.args.get('date_to', today)
    type_    = request.args.get('type', None)
    category = request.args.get('category', None)
    method   = request.args.get('method', None)
    page     = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 30))
    fmt      = request.args.get('format', 'json')

    if fmt == 'csv':
        from flask import Response
        data = db.get_transactions_paginated(start, end, type_, category, method,
                                             page=1, per_page=100000)
        lines = ['\uFEFFTarih,Tür,Kategori,Kasa,Açıklama,Tutar']
        for r in data['rows']:
            lines.append(','.join([
                r['date'],
                'Giriş' if r['type'] == 'in' else 'Çıkış',
                r['category'] or '',
                r['payment_method'] or '',
                (r['description'] or '').replace(',', ';'),
                str(r['amount'])
            ]))
        csv_text = '\n'.join(lines)
        return Response(csv_text, mimetype='text/csv',
                        headers={'Content-Disposition':
                                 f'attachment; filename=kasa_{start}_{end}.csv'})
    return jsonify(db.get_transactions_paginated(start, end, type_, category,
                                                 method, page, per_page))

@app.route('/api/transactions/<int:tid>', methods=['PUT'])
def api_update_transaction(tid):
    data = request.json
    ok = db.update_transaction(
        tid,
        data['amount'], data.get('description', ''),
        data.get('category', 'masraf'), data.get('payment_method', 'cash'),
        data.get('date'), data.get('datetime')
    )
    return jsonify({'success': ok})

@app.route('/api/transactions/<int:tid>', methods=['DELETE'])
def api_delete_transaction(tid):
    db.delete_transaction(tid)
    return jsonify({'success': True})

# STOK
@app.route('/api/stock', methods=['GET'])
def api_stock_list():
    return jsonify(db.get_stock_items())

@app.route('/api/stock', methods=['POST'])
def api_add_stock():
    d = request.json
    db.add_stock_item(d['name'], d.get('unit','adet'), d.get('min_quantity',0),
                      d.get('cost_per_unit',0), d.get('category','Genel'))
    return jsonify({'success': True})

@app.route('/api/stock/<int:item_id>', methods=['PATCH'])
def api_update_stock(item_id):
    d = request.json
    db.update_stock_item(item_id, d['name'], d.get('unit','adet'),
                         d.get('min_quantity',0), d.get('cost_per_unit',0), d.get('category','Genel'))
    return jsonify({'success': True})

@app.route('/api/stock/<int:item_id>', methods=['DELETE'])
def api_delete_stock(item_id):
    ok, msg = db.delete_stock_item(item_id)
    return jsonify({'success': ok, 'error': msg})

@app.route('/api/products/<int:product_id>', methods=['PATCH'])
def api_update_product(product_id):
    d = request.json
    db.update_product(product_id, d['name'], d['price'], d.get('category_id'))
    return jsonify({'success': True})

@app.route('/api/expenses/<int:expense_id>', methods=['PATCH'])
def api_update_expense(expense_id):
    d = request.json
    db.update_expense(expense_id, d['description'], d['amount'],
                      d.get('category','Genel'), d.get('payment_method','cash'), d.get('subcategory',''))
    return jsonify({'success': True})

@app.route('/api/stock/<int:item_id>/movement', methods=['POST'])
def api_stock_movement(item_id):
    d = request.json
    mtype = d['movement_type']
    try:
        movement_date = d.get('date', None)
        movement_unit = d.get('unit', None)
        if mtype == 'in':
            db.add_stock_purchase(item_id, d['quantity'], d.get('cost', 0),
                                  d.get('payment_method', 'cash'), d.get('description', ''),
                                  date=movement_date, unit=movement_unit)
        else:
            db.add_stock_movement(item_id, mtype, d['quantity'],
                                  d.get('cost', 0), d.get('reason', 'manuel'), d.get('description', ''),
                                  date=movement_date, unit=movement_unit)
        return jsonify({'success': True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stock/movements/<int:mid>', methods=['PATCH'])
def api_update_movement(mid):
    d = request.json
    db.update_stock_movement(mid, d['quantity'], d.get('cost', 0), d.get('description', ''))
    return jsonify({'success': True})

@app.route('/api/stock/movements/<int:mid>', methods=['DELETE'])
def api_delete_movement(mid):
    ok, msg = db.delete_stock_movement(mid)
    return jsonify({'success': ok, 'error': msg})

@app.route('/api/stock/movements', methods=['GET'])
def api_stock_movements():
    item_id = request.args.get('item_id', None)
    return jsonify(db.get_stock_movements(item_id))

# REÇETE
@app.route('/api/recipes', methods=['GET'])
def api_recipes():
    product_id = request.args.get('product_id', None)
    return jsonify(db.get_recipes(product_id))

@app.route('/api/recipes', methods=['POST'])
def api_set_recipe():
    d = request.json
    db.set_recipe(d['product_id'], d['stock_item_id'], d['quantity'])
    return jsonify({'success': True})

@app.route('/api/recipes/<int:rid>', methods=['DELETE'])
def api_delete_recipe(rid):
    db.delete_recipe(rid)
    return jsonify({'success': True})

@app.route('/expenses')
def expenses_page():
    return render_template('expenses.html')


# API: Kategoriler
@app.route('/api/categories', methods=['GET', 'POST'])
def api_categories():
    if request.method == 'GET':
        return jsonify(db.get_categories())
    
    elif request.method == 'POST':
        data = request.json
        db.add_category(data['name'], data.get('color', '#3B82F6'))
        return jsonify({'success': True})

@app.route('/api/categories/<int:category_id>', methods=['DELETE'])
def api_delete_category(category_id):
    ok, msg = db.delete_category_safe(category_id)
    return jsonify({'success': ok, 'error': msg})

# API: Ürünler
@app.route('/api/products', methods=['GET', 'POST'])
def api_products():
    if request.method == 'GET':
        category_id = request.args.get('category_id')
        return jsonify(db.get_products(category_id))
    
    elif request.method == 'POST':
        data = request.json
        db.add_product(data['name'], data['category_id'], data['price'])
        return jsonify({'success': True})

@app.route('/api/products/excel-export', methods=['GET'])
def api_products_excel_export():
    """Ürünleri CSV olarak indir"""
    import io, csv
    products = db.get_products()
    categories = db.get_categories()
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(['id', 'name', 'price', 'category_name'])
    for p in products:
        writer.writerow([p['id'], p['name'], p['price'], p.get('category_name', '')])
    output.seek(0)
    bom = '\ufeff'
    from flask import Response
    return Response(
        bom + output.getvalue(),
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=firinna_urunler.csv'}
    )

@app.route('/api/products/excel-import', methods=['POST'])
def api_products_excel_import():
    """CSV'den ürün güncelle/ekle"""
    import io, csv
    data = request.json  # [{id, name, price, category_name}]
    if not data:
        return jsonify({'error': 'Veri yok'}), 400

    categories = {c['name']: c['id'] for c in db.get_categories()}
    results = {'updated': 0, 'added': 0, 'errors': []}

    for row in data:
        try:
            name = str(row.get('name', '')).strip()
            price = float(str(row.get('price', 0)).replace(',', '.'))
            cat_name = str(row.get('category_name', '')).strip()
            pid = row.get('id')

            if not name or price < 0:
                results['errors'].append(f"Geçersiz satır: {row}")
                continue

            cat_id = categories.get(cat_name)
            if not cat_id and cat_name:
                db.add_category(cat_name)
                categories = {c['name']: c['id'] for c in db.get_categories()}
                cat_id = categories.get(cat_name)

            if pid:
                try:
                    db.update_product(int(pid), name, price, cat_id)
                    results['updated'] += 1
                except:
                    results['errors'].append(f"Güncelleme hatası id={pid}")
            else:
                if cat_id:
                    db.add_product(name, cat_id, price)
                    results['added'] += 1
                else:
                    results['errors'].append(f"Kategori bulunamadı: {cat_name}")
        except Exception as e:
            results['errors'].append(str(e))

    return jsonify(results)

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def api_delete_product(product_id):
    db.delete_product(product_id)
    return jsonify({'success': True})

# API: Bölgeler
@app.route('/api/zones', methods=['GET', 'POST'])
def api_zones():
    if request.method == 'GET':
        return jsonify(db.get_zones())
    
    elif request.method == 'POST':
        data = request.json
        db.add_zone(data['name'])
        return jsonify({'success': True})

@app.route('/api/zones/<int:zone_id>', methods=['DELETE'])
def api_delete_zone(zone_id):
    ok, msg = db.delete_zone_safe(zone_id)
    return jsonify({'success': ok, 'error': msg})

# API: Masalar
@app.route('/api/tables', methods=['GET', 'POST'])
def api_tables():
    if request.method == 'GET':
        zone_id = request.args.get('zone_id')
        return jsonify(db.get_tables(zone_id))
    
    elif request.method == 'POST':
        data = request.json
        db.add_table(data['name'], data['zone_id'])
        return jsonify({'success': True})

@app.route('/api/tables/<int:table_id>', methods=['DELETE'])
def api_delete_table(table_id):
    ok, msg = db.delete_table_safe(table_id)
    return jsonify({'success': ok, 'error': msg})

@app.route('/api/tables/<int:table_id>', methods=['GET'])
def api_get_single_table(table_id):
    """Tek masa bilgisi — QR sipariş için"""
    tables = db.get_tables()
    table  = next((t for t in tables if t['id'] == table_id), None)
    if not table:
        return jsonify({'error': 'Masa bulunamadı'}), 404
    order = db.get_table_order(table_id)
    return jsonify({
        'id':               table['id'],
        'name':             table.get('name', 'Masa ' + str(table_id)),
        'current_order_id': order['id'] if order else None,
    })

@app.route('/api/tables/<int:table_id>/split', methods=['POST'])
def api_split_table(table_id):
    data = request.json or {}
    suffix = data.get('suffix')
    if not suffix:
        return jsonify({'success': False, 'error': 'Alt masa eki (örn: A, B veya 2) gerekli'}), 400
    try:
        new_table_id = db.split_table(table_id, suffix)
        return jsonify({'success': True, 'new_table_id': new_table_id})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# ── QR Self-Servis Sipariş ──
@app.route('/siparis/<int:table_id>')
def qr_order_page(table_id):
    """QR kod ile müşteri sipariş sayfası"""
    return render_template('qr_order.html', table_id=table_id)

@app.route('/api/qr-code/<int:table_id>')
def api_qr_code(table_id):
    """Masa için QR kod PNG üret"""
    try:
        import qrcode
        import io
        url = request.host_url.rstrip('/') + f'/siparis/{table_id}'
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        from flask import send_file
        return send_file(buf, mimetype='image/png',
                         download_name=f'masa-{table_id}-qr.png')
    except ImportError:
        return jsonify({'error': 'qrcode kütüphanesi yüklü değil. pip install qrcode[pil]'}), 500

# API: Siparişler
@app.route('/api/orders/table/<int:table_id>', methods=['GET'])
def api_get_table_order(table_id):
    order = db.get_table_order(table_id)
    if order:
        return jsonify(order)
    else:
        # Sipariş yok — boş döndür, ürün eklenince create edilecek
        return jsonify({'id': None, 'table_id': table_id, 'total': 0, 'items': []})

@app.route('/api/orders/create', methods=['POST'])
def api_create_order():
    data = request.json
    table_id = data.get('table_id')
    if not table_id:
        return jsonify({'error': 'table_id gerekli'}), 400
    # Zaten açık sipariş varsa onu döndür
    existing = db.get_table_order(table_id)
    if existing:
        return jsonify({'id': existing['id']})
    order_id = db.create_order(table_id, data.get('created_at'))
    return jsonify({'id': order_id})

@app.route('/api/orders/cleanup-empty', methods=['POST'])
def api_cleanup_empty_orders():
    """items'sız boş siparişleri temizle"""
    deleted = db.cleanup_empty_orders()
    return jsonify({'success': True, 'deleted': deleted})

@app.route('/api/orders/<int:order_id>/items', methods=['POST'])
def api_append_order_item(order_id):
    data = request.json
    db.add_order_item(
        order_id,
        data['product_id'],
        data['quantity'],
        data['price'],
        product_name=data.get('product_name'),
        kitchen_notes=data.get('kitchen_notes'),
        is_complimentary=int(data.get('is_complimentary', 0))
    )
    return jsonify({'success': True})

@app.route('/api/orders/items/<int:item_id>', methods=['DELETE'])
def api_delete_order_item(item_id):
    db.delete_order_item(item_id)
    return jsonify({'success': True})

@app.route('/api/orders/<int:order_id>/close', methods=['POST'])
def api_close_order(order_id):
    db.close_order(order_id)
    db.deduct_stock_for_order(order_id)
    telegram_notify.check_low_stock_after_order(order_id)
    return jsonify({'success': True})

# API: Adisyon yazdır
@app.route('/api/print/receipt/<int:order_id>', methods=['POST'])
def api_print_receipt(order_id):
    order = db.get_table_order_by_id(order_id)
    if not order:
        return jsonify({"success": False, "error": "Sipariş bulunamadı"})
    from printer import ThermalPrinter
    try:
        printer = ThermalPrinter(printer_type="receipt")
        success = printer.print_receipt(order)
        if not success:
            ip = db.get_setting('printer_ip', '192.168.1.99')
            port = db.get_setting('printer_port', '9100')
            return jsonify({"success": False,
                "error": f"Yazıcıya bağlanılamadı ({ip}:{port}). Ayarlar → Yazıcı menüsünden IP'yi kontrol edin."})
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# API: Masraflar
@app.route('/api/expenses', methods=['GET', 'POST'])
def api_expenses():
    if request.method == 'GET':
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        return jsonify(db.get_expenses(start_date, end_date))
    elif request.method == 'POST':
        data = request.json
        db.add_expense(
            data['description'], data['amount'],
            data.get('category', 'Genel'),
            data.get('payment_method', 'cash'),
            data.get('subcategory', ''),
            date=data.get('date', None)
        )
        return jsonify({'success': True})

@app.route('/api/expenses/template', methods=['GET'])
def api_expenses_template():
    """Toplu masraf girişi için CSV şablonu indir"""
    import io
    output = io.StringIO()
    output.write('\ufeff')  # BOM — Excel'de Türkçe için
    output.write('Tarih,Kategori,Alt Kategori,Açıklama,Tutar,Ödeme Yöntemi\n')
    output.write('2026-03-23,Malzeme,Un/Tahıl,Buğday unu 25kg,450.00,cash\n')
    output.write('2026-03-23,Malzeme,Süt Ürünleri,Tereyağı 5kg,320.00,cash\n')
    output.write('2026-03-24,Faturalar,Elektrik,Mart elektrik faturası,1200.00,card\n')
    output.write('# Ödeme Yöntemi: cash = Nakit Kasa  |  card = Banka Kasa\n')
    output.write('# Kategori seçenekleri: Faturalar / Kira / Personel / Malzeme / Temizlik / Tamir-Bakım / Demirbaş / Pazarlama / Diğer\n')
    content = output.getvalue()
    from flask import Response
    return Response(
        content,
        mimetype='text/csv; charset=utf-8',
        headers={'Content-Disposition': 'attachment; filename=masraf_sablonu.csv'}
    )

@app.route('/api/expenses/import', methods=['POST'])
def api_expenses_import():
    """CSV ile toplu masraf yükle"""
    import io, csv
    file = request.files.get('file')
    if not file:
        return jsonify({'success': False, 'error': 'Dosya yok'})
    try:
        content = file.read().decode('utf-8-sig')  # BOM'u atla
        reader = csv.DictReader(io.StringIO(content))
        imported = 0
        errors = []
        for i, row in enumerate(reader, 2):
            # Yorum satırlarını atla
            tarih = (row.get('Tarih') or '').strip()
            if tarih.startswith('#') or not tarih:
                continue
            try:
                aciklama = row.get('Açıklama', '').strip()
                tutar_str = row.get('Tutar', '0').strip().replace(',', '.')
                tutar = float(tutar_str)
                if not aciklama or tutar <= 0:
                    continue
                kategori = row.get('Kategori', 'Genel').strip()
                alt_kat = row.get('Alt Kategori', '').strip()
                odeme = row.get('Ödeme Yöntemi', 'cash').strip()
                if odeme not in ('cash', 'card'):
                    odeme = 'cash'
                db.add_expense(aciklama, tutar, kategori, odeme, alt_kat, date=tarih)
                imported += 1
            except Exception as e:
                errors.append(f'Satır {i}: {e}')
        return jsonify({'success': True, 'imported': imported, 'errors': errors})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/expenses/summary', methods=['GET'])
def api_expense_summary():
    start = request.args.get('start')
    end = request.args.get('end')
    return jsonify(db.get_expense_summary(start, end))

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def api_delete_expense(expense_id):
    ok, msg = db.delete_expense_safe(expense_id)
    return jsonify({'success': ok, 'error': msg})

# API: Raporlar
@app.route('/api/reports/daily', methods=['GET'])
def api_daily_report():
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    report = db.get_daily_report(date)
    return jsonify(report)

@app.route('/api/reports/range', methods=['GET'])
def api_report_range():
    from datetime import timedelta
    period = request.args.get('period', 'daily')
    today = datetime.now().date()
    if period == 'daily':
        date = request.args.get('date', str(today))
        start = end = date
    elif period == 'weekly':
        start = str(today - timedelta(days=today.weekday()))
        end = str(today)
    elif period == 'monthly':
        start = str(today.replace(day=1))
        end = str(today)
    elif period == 'custom':
        start = request.args.get('start', str(today))
        end = request.args.get('end', str(today))
    else:
        start = '2000-01-01'
        end = str(today)
    report = db.get_report(start, end)
    return jsonify(report)

@app.route('/api/reports/hourly', methods=['GET'])
def api_reports_hourly():
    from datetime import date as _date, timedelta
    today = datetime.now().strftime('%Y-%m-%d')
    period = request.args.get('period', 'daily')
    d = _date.today()
    if period == 'weekly':
        start = str(d - timedelta(days=d.weekday()))
        end = str(d)
    elif period == 'monthly':
        start = str(d.replace(day=1))
        end = str(d)
    else:
        start = end = request.args.get('date', today)
    return jsonify(db.get_hourly_sales(start, end))

@app.route('/api/reports/daily-close', methods=['GET'])
def api_daily_close_report():
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    return jsonify(db.get_daily_close_report(date))

def get_tomorrow_schedule_alert():
    """Checks if tomorrow's operating schedule is CLOSED or DIFFERENT from standard hours."""
    try:
        settings = {}
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
        
        daily_hours = settings.get('daily_hours', {})
        if not daily_hours:
            return ""
            
        days_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        now = datetime.now()
        tomorrow_idx = (now.weekday() + 1) % 7
        tomorrow_day = days_tr[tomorrow_idx]
        
        tomorrow_cfg = daily_hours.get(tomorrow_day, {"open": "08:30", "close": "23:00", "active": True})
        
        active_hours = [
            f"{cfg.get('open','08:30')}-{cfg.get('close','23:00')}"
            for d, cfg in daily_hours.items()
            if cfg.get('active', True)
        ]
        
        from collections import Counter
        standard_hours = Counter(active_hours).most_common(1)[0][0] if active_hours else "08:30-23:00"
        
        tomorrow_is_active = tomorrow_cfg.get('active', True)
        tomorrow_hours = f"{tomorrow_cfg.get('open','08:30')}-{tomorrow_cfg.get('close','23:00')}"
        
        if not tomorrow_is_active:
            return (
                f"\n\n⚠️ <b>DİKKAT: YARINKİ ÇALIŞMA SAATİ KONTROLÜ!</b>\n"
                f"Yarın (<b>{tomorrow_day}</b>) mekan yönetim panelinde <b>KAPALI</b> olarak ayarlanmış!\n"
                f"<i>Bu bilgi doğru mu? Eğer kapalı olmayacaksanız lütfen yönetim panelinden kontrol edin.</i>"
            )
        elif tomorrow_hours != standard_hours:
            open_t = tomorrow_cfg.get('open', '08:30')
            close_t = tomorrow_cfg.get('close', '23:00')
            std_t = standard_hours.replace('-', ' - ')
            return (
                f"\n\n⚠️ <b>DİKKAT: YARINKİ ÇALIŞMA SAATİ KONTROLÜ!</b>\n"
                f"Yarın (<b>{tomorrow_day}</b>) çalışma saati diğer günlerden farklı tanımlanmış: <b>{open_t} - {close_t}</b> (Standart: {std_t})\n"
                f"<i>Bu bilgi doğru mu? Eğer özel bir durum yoksa yönetim panelinden kontrol edebilirsiniz.</i>"
            )
    except Exception as e:
        print("Schedule alert calculation error:", e)
    return ""

@app.route('/api/reports/daily-close/send-telegram', methods=['POST'])
def api_send_daily_close_telegram():
    data = request.json or {}
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    report = db.get_daily_close_report(date)
    restaurant = db.get_setting('restaurant_name', 'Fırınna')
    top = report.get('top_products', [])[:5]
    open_warn = ''
    if report.get('open_orders_count', 0) > 0:
        open_warn = f"\n\n⚠️ {report['open_orders_count']} masa hâlâ açık!"
    top_lines = ''
    if top:
        top_lines = '\n\n🏆 En Çok Satan 5 Ürün:\n' + '\n'.join(
            f"  {i+1}. {p['name']} × {p['quantity']} adet — {p['total']:.2f} ₺"
            for i, p in enumerate(top)
        )
    
    tomorrow_alert = get_tomorrow_schedule_alert()

    msg = (
        f"🏪 <b>{restaurant} — Günlük Rapor</b>\n"
        f"📅 {date}\n"
        f"─────────────────\n"
        f"💰 Toplam Satış:  <b>{report['total_sales']:.2f} ₺</b>\n"
        f"💵 Nakit:         {report['total_cash']:.2f} ₺\n"
        f"💳 Kart:          {report['total_card']:.2f} ₺\n"
        f"🎁 Bahşiş:        {report['total_tips']:.2f} ₺\n"
        f"🏷️ İndirim:       {report['total_discount']:.2f} ₺\n"
        f"📦 Masraf:        {report['total_expenses']:.2f} ₺\n"
        f"─────────────────\n"
        f"✅ Net Kasa:      <b>{report['net']:.2f} ₺</b>"
        f"{top_lines}{open_warn}{tomorrow_alert}"
    )
    ok = telegram_notify.send_message(msg)
    
    # Gün sonu yapıldığında web durumunu otomatik (auto) moda al
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
            if settings.get('manual_status') != 'auto':
                settings['manual_status'] = 'auto'
                with open(SETTINGS_FILE, 'w') as f:
                    json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print("Web status reset error on day close:", e)

    return jsonify({'success': ok, 'message': msg if not ok else ''})

@app.route('/kitchen')
def kitchen_page():
    return render_template('kitchen.html')

@app.route('/notes')
def notes_page():
    return render_template('notes.html')

@app.route('/api/pos/store-status', methods=['GET', 'POST'])
def api_pos_store_status():
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
        except: pass
    if request.method == 'GET':
        return jsonify({"manual_status": settings.get("manual_status", "auto")})
    
    data = request.json
    new_status = data.get('manual_status', 'auto')
    settings['manual_status'] = new_status
    if new_status != 'auto':
        settings['manual_status_time'] = datetime.now().timestamp()
    else:
        settings.pop('manual_status_time', None)
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except: pass
    return jsonify({"success": True, "manual_status": new_status})

@app.route('/api/kitchen/orders', methods=['GET'])
def api_kitchen_orders():
    return jsonify(db.get_kitchen_orders())

@app.route('/api/kitchen/orders/<int:order_id>/ready', methods=['POST'])
def api_kitchen_set_ready(order_id):
    db.set_kitchen_ready(order_id, ready=1)
    return jsonify({'success': True})

@app.route('/api/orders/<int:order_id>/transfer', methods=['POST'])
def api_transfer_order(order_id):
    data = request.json or {}
    new_table_id = data.get('new_table_id')
    if not new_table_id:
        return jsonify({'success': False, 'error': 'new_table_id gerekli'}), 400
    try:
        db.transfer_order(order_id, new_table_id)
        return jsonify({'success': True})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/orders/<int:order_id>/merge', methods=['POST'])
def api_merge_orders(order_id):
    data = request.json or {}
    target_order_id = data.get('target_order_id')
    if not target_order_id:
        return jsonify({'success': False, 'error': 'target_order_id gerekli'}), 400
    try:
        db.merge_orders(order_id, target_order_id)
        return jsonify({'success': True})
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/print/daily-report', methods=['POST'])
def api_print_daily_report():
    data = request.json
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    report = db.get_daily_report(date)
    success = printer.print_daily_report(report)
    return jsonify({'success': success})

# API: Yedekleme
@app.route('/api/backup', methods=['POST'])
def api_backup():
    backup_path = db.backup_database()
    return jsonify({'success': True, 'path': backup_path})

@app.route('/api/backup/download', methods=['GET'])
def api_backup_download():
    """Mevcut DB'yi doğrudan indir"""
    from flask import send_file
    import io, shutil
    tmp = io.BytesIO()
    with open(db.DB_PATH, 'rb') as f:
        tmp.write(f.read())
    tmp.seek(0)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(tmp, mimetype='application/octet-stream',
                     as_attachment=True, download_name=f'firinna_backup_{ts}.db')

@app.route('/api/backup/dump', methods=['GET'])
def api_backup_dump():
    """DB'yi SQL dump olarak indir"""
    from flask import send_file
    dump_path = db.dump_database_sql()
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    return send_file(dump_path, mimetype='text/plain',
                     as_attachment=True, download_name=f'firinna_dump_{ts}.sql')

@app.route('/api/backup/list', methods=['GET'])
def api_backup_list():
    return jsonify(db.list_backups())

@app.route('/api/backup/restore', methods=['POST'])
def api_backup_restore():
    """Yüklenen .db veya .sql dosyasından geri yükle"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Dosya yok'})
    f = request.files['file']
    fn = f.filename.lower()
    import tempfile, os
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(fn)[1])
    f.save(tmp.name)
    tmp.close()
    try:
        if fn.endswith('.sql'):
            db.restore_database_sql(tmp.name)
        elif fn.endswith('.db'):
            import shutil
            # Önce yedeğini al
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            import os as _os
            bdir = _os.path.join(_os.path.dirname(db.DB_PATH), 'backups')
            _os.makedirs(bdir, exist_ok=True)
            shutil.copy2(db.DB_PATH, _os.path.join(bdir, f'pre_restore_{ts}.db'))
            shutil.copy2(tmp.name, db.DB_PATH)
        else:
            return jsonify({'success': False, 'error': 'Sadece .db veya .sql dosyası'})
        os.unlink(tmp.name)
        return jsonify({'success': True})
    except Exception as e:
        try: os.unlink(tmp.name)
        except: pass
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/backup/restore-local/<filename>', methods=['POST'])
def api_backup_restore_local(filename):
    """Sunucudaki yerel yedekten geri yükle"""
    import os, shutil
    backup_dir = os.path.join(os.path.dirname(db.DB_PATH), 'backups')
    fp = os.path.join(backup_dir, filename)
    if not os.path.exists(fp):
        return jsonify({'success': False, 'error': 'Dosya bulunamadı'})
    try:
        if filename.endswith('.sql'):
            db.restore_database_sql(fp)
        else:
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            shutil.copy2(db.DB_PATH, os.path.join(backup_dir, f'pre_restore_{ts}.db'))
            shutil.copy2(fp, db.DB_PATH)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/backup/download-local/<filename>', methods=['GET'])
def api_backup_download_local(filename):
    import os
    from flask import send_file
    backup_dir = os.path.join(os.path.dirname(db.DB_PATH), 'backups')
    fp = os.path.join(backup_dir, filename)
    if not os.path.exists(fp):
        return "Dosya bulunamadi", 404
    return send_file(fp, as_attachment=True, download_name=filename)

@app.route('/api/backup/full-zip', methods=['GET'])
def api_backup_full_zip():
    import zipfile, io, os
    buf = io.BytesIO()
    base = os.path.dirname(db.DB_PATH)
    skip = {'__pycache__', '.git', 'backups', 'venv'}
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in skip]
            for fname in files:
                if fname.endswith('.pyc'):
                    continue
                fpath = os.path.join(root, fname)
                zf.write(fpath, os.path.relpath(fpath, base))
    buf.seek(0)
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    from flask import send_file
    return send_file(buf, mimetype='application/zip',
                     as_attachment=True, download_name=f'firinna_full_{ts}.zip')

@app.route('/api/backup/sync-push', methods=['POST'])
def api_backup_sync_push():
    try:
        db.backup_database()
        dump_path = db.dump_database_sql()
        run_git(['add', 'db_export.sql'])
        run_git(['commit', '-m', f'db sync {datetime.now().strftime("%Y-%m-%d %H:%M")}'])
        ok, out = run_git(['push'], timeout=60)
        if ok:
            return jsonify({'success': True, 'message': "Veritabani GitHub'a gonderildi."})
        else:
            return jsonify({'success': False, 'error': f"Push hatası: {out}"})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/backup/sync-pull', methods=['POST'])
def api_backup_sync_pull():
    import os
    try:
        ok, out = run_git(['pull'], timeout=60)
        if not ok:
            return jsonify({'success': False, 'error': f"Pull hatası: {out}"})
            
        base = os.path.dirname(db.DB_PATH)
        dump_path = os.path.join(base, 'db_export.sql')
        if os.path.exists(dump_path):
            db.backup_database()
            db.restore_database_sql(dump_path)
            return jsonify({'success': True, 'message': 'Pull yapildi ve veritabani guncellendi.'})
        else:
            return jsonify({'success': True, 'message': 'Pull yapildi. db_export.sql bulunamadi, veritabani degistirilmedi.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# API: Test verilerini temizle
@app.route('/api/clear-test-data', methods=['POST'])
def api_clear_test_data():
    db.clear_test_data()
    return jsonify({'success': True})

# API: Yazıcı test
@app.route('/api/printer/test', methods=['POST'])
def api_printer_test():
    try:
        from printer import ThermalPrinter
        p = ThermalPrinter(printer_type='receipt')
        success = p.test_print()
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# API: Ayarlar
@app.route('/settings')
def settings_page():
    return render_template('settings.html')

@app.route('/api/settings/printer', methods=['GET', 'POST'])
def api_printer_settings():
    global PRINTER_IP, PRINTER_PORT, printer
    
    if request.method == 'GET':
        return jsonify({'ip': PRINTER_IP, 'port': PRINTER_PORT})
    
    elif request.method == 'POST':
        data = request.json
        PRINTER_IP = data['ip']
        PRINTER_PORT = int(data['port'])
        printer = ThermalPrinter(PRINTER_IP, PRINTER_PORT)
        return jsonify({'success': True})
@app.route('/api/orders/items/<int:item_id>/quantity', methods=['PATCH'])

def api_update_item_quantity(item_id):
    data = request.json
    db.update_order_item_quantity(item_id, data['quantity'])
    return jsonify({'success': True})

@app.route('/api/orders/items/<int:item_id>', methods=['PATCH'])
def api_update_item(item_id):
    data = request.json
    db.update_order_item(
        item_id,
        is_complimentary=data.get('is_complimentary'),
        kitchen_notes=data.get('kitchen_notes')
    )
    return jsonify({'success': True})

@app.route('/api/orders/<int:order_id>/custom-item', methods=['POST'])
def api_add_custom_item(order_id):
    data = request.json
    db.add_custom_order_item(order_id, data['name'], data['price'])
    return jsonify({'success': True})

@app.route('/api/orders/<int:order_id>/discount', methods=['PATCH'])
def api_set_discount(order_id):
    data = request.json
    db.set_order_discount(
        order_id,
        data['type'],
        data['value'],
        data.get('reason', '')
    )
    return jsonify({'success': True})

@app.route('/api/orders/<int:order_id>/close-with-payment', methods=['POST'])
def api_close_with_payment(order_id):
    data = request.json
    pay_entries = data.get('pay_entries')
    if pay_entries:
        payment_cash = sum(e['amount'] for e in pay_entries if e['method'] == 'cash')
        payment_card = sum(e['amount'] for e in pay_entries if e['method'] == 'card')
    else:
        payment_cash = data.get('payment_cash', 0)
        payment_card = data.get('payment_card', 0)

    db.close_order_with_payment(
        order_id,
        payment_cash,
        payment_card,
        data.get('tip_amount', 0),
        data.get('tip_method', 'cash'),
        data.get('closed_at'),
        pay_entries=pay_entries
    )
    db.deduct_stock_for_order(order_id)
    telegram_notify.check_low_stock_after_order(order_id)
    return jsonify({'success': True})

@app.route('/api/orders/<int:order_id>/split', methods=['POST'])
def api_split_order(order_id):
    data = request.json
    per_person = db.split_order_equal(order_id, data['num_people'])
    return jsonify({'per_person': per_person})



@app.route('/api/orders/<int:order_id>/transfer-items', methods=['POST'])
def api_transfer_order_items(order_id):
    data = request.json or {}
    target_table_id = data.get('target_table_id')
    items_to_move = data.get('items', [])
    
    if not target_table_id:
        return jsonify({'success': False, 'error': 'Hedef masa seçilmedi.'}), 400
    if not items_to_move:
        return jsonify({'success': False, 'error': 'Aktarılacak ürün seçilmedi.'}), 400
        
    try:
        target_order_id, source_deleted = db.transfer_order_items(order_id, target_table_id, items_to_move)
        return jsonify({
            'success': True,
            'target_order_id': target_order_id,
            'source_deleted': source_deleted
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/categories/<int:category_id>/order', methods=['PATCH'])
def api_update_category_order(category_id):
    data = request.json
    db.update_category_order(category_id, data['sort_order'])
    return jsonify({'success': True})

@app.route('/api/products/<int:product_id>/order', methods=['PATCH'])
def api_update_product_order(product_id):
    data = request.json
    db.update_product_order(product_id, data['sort_order'])
    return jsonify({'success': True})

@app.route('/api/products/<int:product_id>/favorite', methods=['PATCH'])
def api_toggle_favorite(product_id):
    new_value = db.toggle_product_favorite(product_id)
    return jsonify({'success': True, 'is_favorite': new_value})

@app.route('/api/products/<int:product_id>/availability', methods=['PATCH'])
def api_toggle_availability(product_id):
    new_value = db.toggle_product_availability(product_id)
    return jsonify({'success': True, 'is_available': new_value})

@app.route('/api/products/search', methods=['GET'])
def api_search_products():
    query = request.args.get('q', '')
    products = db.search_products(query)
    return jsonify(products)

@app.route('/api/orders/<int:order_id>', methods=['GET'])
def api_get_order(order_id):
    order = db.get_table_order_by_id(order_id)
    if not order:
        return jsonify({'error': 'bulunamadı'}), 404
    return jsonify(order)

@app.route('/api/orders/history', methods=['GET'])
def api_order_history():
    date  = request.args.get('date')
    start = request.args.get('start')
    end   = request.args.get('end')
    limit = int(request.args.get('limit', 200))
    orders = db.get_closed_orders(date=date, start=start, end=end, limit=limit)
    return jsonify(orders)

@app.route('/api/orders/<int:order_id>/reopen', methods=['POST'])
def api_reopen_order(order_id):
    db.reopen_order(order_id)
    return jsonify({'success': True})

@app.route('/api/tables/<int:table_id>/note', methods=['PATCH'])
def api_update_table_note(table_id):
    data = request.json
    db.update_table_note(table_id, data['note'])
    return jsonify({'success': True})

@app.route('/api/settings/<key>', methods=['GET', 'PUT'])
def api_settings(key):
    if request.method == 'GET':
        value = db.get_setting(key)
        return jsonify({'key': key, 'value': value})
    else:
        data = request.json
        db.set_setting(key, data['value'])
        return jsonify({'success': True})


# ===== QR KOD (FİŞ ALT) =====

@app.route('/api/settings/qr', methods=['GET'])
def api_qr_get():
    url = db.get_setting('receipt_qr_image_url', '')
    label = db.get_setting('receipt_qr_label', '')
    return jsonify({'url': url, 'label': label})

@app.route('/api/settings/qr', methods=['POST'])
def api_qr_upload():
    import base64
    file = request.files.get('file')
    label = request.form.get('label', '')
    if not file:
        return jsonify({'success': False, 'error': 'Dosya yok'})
    try:
        data = file.read()
        b64 = base64.b64encode(data).decode()
        mime = file.content_type or 'image/png'
        data_url = f'data:{mime};base64,{b64}'
        db.set_setting('receipt_qr_image_url', data_url)
        db.set_setting('receipt_qr_label', label)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/settings/qr/label', methods=['POST'])
def api_save_qr_label():
    data = request.get_json()
    label = data.get('label', '')
    db.set_setting('receipt_qr_label', label)
    return jsonify({'success': True})

@app.route('/api/settings/qr', methods=['DELETE'])
def api_qr_delete():
    db.set_setting('receipt_qr_image_url', '')
    db.set_setting('receipt_qr_label', '')
    return jsonify({'success': True})

# ===== GEÇMİŞ SİPARİŞ GİRİŞİ API =====

@app.route('/api/orders/past', methods=['POST'])
def api_create_past_order():
    data = request.json
    
    order_id = db.create_past_order(
        table_id=data['table_id'],
        created_at=data['created_at'],
        closed_at=data['closed_at'],
        items=data['items'],
        payment_cash=data.get('payment_cash', 0),
        payment_card=data.get('payment_card', 0),
        discount_type=data.get('discount_type'),
        discount_value=data.get('discount_value', 0),
        discount_reason=data.get('discount_reason', ''),
        tip_amount=data.get('tip_amount', 0),
        tip_method=data.get('tip_method', 'cash')
    )
    
    return jsonify({'success': True, 'order_id': order_id})


# ===== İSİM DÜZENLEME API'LERİ =====

@app.route('/api/zones/<int:zone_id>/name', methods=['PATCH'])
def api_update_zone_name(zone_id):
    data = request.json
    db.update_zone_name(zone_id, data['name'])
    return jsonify({'success': True})

@app.route('/api/tables/<int:table_id>/name', methods=['PATCH'])
def api_update_table_name(table_id):
    data = request.json
    db.update_table_name(table_id, data['name'])
    return jsonify({'success': True})

@app.route('/api/categories/<int:category_id>/name', methods=['PATCH'])
def api_update_category_name(category_id):
    data = request.json
    db.update_category_name(category_id, data['name'])
    return jsonify({'success': True})

@app.route('/api/products/<int:product_id>/name', methods=['PATCH'])
def api_update_product_name(product_id):
    data = request.json
    db.update_product_name(product_id, data['name'])
    return jsonify({'success': True})


# ===== SİPARİŞ SİLME =====

@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def api_delete_order(order_id):
    db.delete_order(order_id)
    return jsonify({'success': True})


# ===== MUTFAK FİŞİ =====

@app.route('/api/print/kitchen/<int:order_id>', methods=['POST'])
def api_print_kitchen(order_id):
    order = db.get_table_order_by_id(order_id)
    if not order:
        return jsonify({'success': False, 'error': 'Sipariş bulunamadı'})
    
    # Mutfak yazıcısı kontrolü
    kitchen_ip = db.get_setting('kitchen_printer_ip')
    if not kitchen_ip:
        return jsonify({'success': False, 'error': 'Mutfak yazıcısı ayarlanmamış'})
    
    from printer import ThermalPrinter
    printer = ThermalPrinter(printer_type='kitchen')
    
    success = printer.print_kitchen_order(order)
    return jsonify({'success': success})


# ===== LOGO YÜKLEME (#15) =====

@app.route('/api/settings/logo', methods=['POST'])
def api_upload_logo():
    if 'logo' not in request.files:
        return jsonify({'success': False, 'error': 'Dosya seçilmedi'}), 400
    file = request.files['logo']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Boş dosya adı'}), 400
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Desteklenmeyen format. PNG, JPG, GIF veya WEBP kullanın'}), 400
    # Sabit isim kullan — her yüklemede üzerine yaz
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f'logo.{ext}'
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    # Eski logo dosyalarını temizle
    for old_ext in ALLOWED_EXTENSIONS:
        old_path = os.path.join(UPLOAD_FOLDER, f'logo.{old_ext}')
        if os.path.exists(old_path) and old_ext != ext:
            os.remove(old_path)
    file.save(filepath)
    logo_url = f'/static/uploads/{filename}'
    db.set_setting('logo_url', logo_url)
    return jsonify({'success': True, 'url': logo_url})

@app.route('/api/settings/logo', methods=['DELETE'])
def api_delete_logo():
    logo_url = db.get_setting('logo_url', '')
    if logo_url:
        filepath = os.path.join(os.path.dirname(__file__), logo_url.lstrip('/'))
        if os.path.exists(filepath):
            os.remove(filepath)
        db.set_setting('logo_url', '')
    return jsonify({'success': True})

@app.route('/api/settings/logo', methods=['GET'])
def api_get_logo():
    logo_url = db.get_setting('logo_url', '')
    return jsonify({'url': logo_url})


# ===== NOT SAYFASI YAZDIRMA (#17) =====

@app.route('/api/print/note', methods=['POST'])
def api_print_note():
    data = request.json
    note_text = data.get('note', '').strip()
    title = data.get('title', 'NOT')
    if not note_text:
        return jsonify({'success': False, 'error': 'Not içeriği boş'}), 400
    try:
        p = ThermalPrinter(printer_type='receipt')
        success = p.print_note(title, note_text)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/print/photo', methods=['POST'])
def api_print_photo():
    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': 'Fotoğraf seçilmedi'}), 400
    photo = request.files['photo']
    paper_width = request.form.get('paper_width', '80')
    max_width = 576 if paper_width == '80' else 384
    try:
        p = ThermalPrinter(printer_type='receipt')
        success = p.print_photo(photo.read(), max_width=max_width)
        return jsonify({'success': success, 'error': None if success else 'Yazıcıya bağlanılamadı'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/print/note/preview', methods=['POST'])
def api_preview_note():
    data = request.json
    note_text = data.get('note', '').strip()
    title = data.get('title', 'NOT')
    restaurant_name = db.get_setting('restaurant_name', 'Fırınna')
    return render_template('receipts/note_receipt.html',
        note=note_text,
        title=title,
        restaurant_name=restaurant_name,
        restaurant_address=db.get_setting('restaurant_address', ''),
        restaurant_phone=db.get_setting('restaurant_phone', ''),
        restaurant_web=db.get_setting('restaurant_web', ''),
        logo_url=db.get_setting('logo_url', ''),
        qr_image_url=db.get_setting('note_qr_image_url', ''),
        qr_label=db.get_setting('note_qr_label', ''),
        timestamp=datetime.now().strftime('%d.%m.%Y %H:%M')
    )


# ===== TELEGRAM (#41) =====

@app.route('/api/settings/telegram', methods=['GET'])
def api_get_telegram():
    return jsonify({
        'token': db.get_setting('telegram_bot_token', ''),
        'chat_id': db.get_setting('telegram_chat_id', '')
    })

@app.route('/api/settings/telegram', methods=['POST'])
def api_save_telegram():
    data = request.get_json()
    db.set_setting('telegram_bot_token', data.get('token', '').strip())
    db.set_setting('telegram_chat_id', data.get('chat_id', '').strip())
    return jsonify({'success': True})

@app.route('/api/settings/telegram/test', methods=['POST'])
def api_test_telegram():
    result = telegram_notify.test_connection()
    return jsonify(result)

@app.route('/api/settings/telegram/instant_report', methods=['POST'])
def api_instant_report_telegram():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        report = db.get_daily_close_report(today)
        restaurant = db.get_setting('restaurant_name', 'Fırınna')
        top = report.get('top_products', [])[:5]
        open_warn = ''
        if report.get('open_orders_count', 0) > 0:
            open_warn = f"\n⚠️ {report['open_orders_count']} masa hâlâ açık!"
        top_txt = '\n'.join([f"  {i+1}. {p['name']} — {p['quantity']} adet" for i, p in enumerate(top)]) if top else '  —'
        text = (
            f"📊 <b>{restaurant} — Anlık Durum Raporu</b> ({datetime.now().strftime('%H:%M')})\n\n"
            f"💰 Toplam Satış: <b>{report.get('total_sales',0):.2f} ₺</b>\n"
            f"💵 Nakit: {report.get('total_cash',0):.2f} ₺\n"
            f"💳 Kart: {report.get('total_card',0):.2f} ₺\n"
            f"💸 Bahşiş: {report.get('total_tips',0):.2f} ₺\n"
            f"🎁 İkramlar: {report.get('total_ikram',0):.2f} ₺\n"
            f"📉 İndirimler: {report.get('total_discount',0):.2f} ₺\n"
            f"🔻 Giderler: {report.get('total_expenses',0):.2f} ₺\n"
            f"💵 Net Kasa: <b>{report.get('net',0):.2f} ₺</b>\n\n"
            f"🧾 Masa Sayısı: {report.get('order_count',0)} ({report.get('cash_order_count',0)} Nakit, {report.get('card_order_count',0)} Kart, {report.get('mixed_order_count',0)} Parçalı)\n\n"
            f"📦 En Çok Satanlar:\n{top_txt}"
            f"{open_warn}"
        )
        import telegram_notify
        telegram_notify.send_message(text)
        return jsonify({'success': True})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/telegram/contacts', methods=['GET'])
def api_get_telegram_contacts():
    return jsonify(db.get_telegram_contacts())

@app.route('/api/telegram/contacts', methods=['POST'])
def api_add_telegram_contact():
    data = request.get_json()
    name = data.get('name', '').strip()
    chat_id = data.get('chat_id', '').strip()
    if not name or not chat_id:
        return jsonify({'success': False, 'error': 'İsim ve Chat ID zorunlu'}), 400
    db.add_telegram_contact(name, chat_id)
    return jsonify({'success': True})

@app.route('/api/telegram/contacts/<int:contact_id>', methods=['DELETE'])
def api_delete_telegram_contact(contact_id):
    db.delete_telegram_contact(contact_id)
    return jsonify({'success': True})

@app.route('/api/telegram/updates', methods=['GET'])
def api_telegram_get_updates():
    """Bota yazan kişilerin chat ID'lerini getir"""
    try:
        import urllib.request, json as _json
        token = db.get_setting('telegram_bot_token', '')
        if not token:
            return jsonify([])
        url = f'https://api.telegram.org/bot{token}/getUpdates?limit=50'
        with urllib.request.urlopen(url, timeout=8) as resp:
            data = _json.loads(resp.read())
        seen = {}
        for upd in data.get('result', []):
            msg = upd.get('message') or upd.get('callback_query', {}).get('message')
            if not msg:
                continue
            chat = msg.get('chat', {})
            cid = str(chat.get('id', ''))
            if cid and cid not in seen:
                first = chat.get('first_name', '')
                last  = chat.get('last_name', '')
                seen[cid] = {
                    'chat_id': cid,
                    'name': (first + ' ' + last).strip() or chat.get('title', 'Anonim'),
                    'username': chat.get('username', '')
                }
        return jsonify(list(seen.values()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings/telegram/send', methods=['POST'])
def api_send_telegram_note():
    data = request.get_json()
    message = data.get('message', '').strip()
    chat_id = (data.get('chat_id') or '').strip()  # opsiyonel — None veya boşsa default
    if not message:
        return jsonify({'success': False, 'error': 'Mesaj boş'}), 400
    if chat_id:
        ok = telegram_notify.send_message_to(message, chat_id)
    else:
        ok = telegram_notify.send_message(message)
    if ok:
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Mesaj gönderilemedi. Chat ID veya token hatalı olabilir.'})

# ===== ORDER ITEMS CRUD (#düzenleme) =====

@app.route('/api/order-items/<int:item_id>', methods=['PATCH'])
def api_edit_order_item_qty(item_id):
    d = request.json
    conn = db.get_db()
    conn.execute('UPDATE order_items SET quantity=? WHERE id=?', (d['quantity'], item_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/api/order-items/<int:item_id>', methods=['DELETE'])
def api_remove_order_item(item_id):
    conn = db.get_db()
    conn.execute('DELETE FROM order_items WHERE id=?', (item_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# ===== ÜRÜN-STOK BAĞLANTISI =====

@app.route('/api/products/<int:product_id>/stock-link', methods=['GET', 'POST', 'DELETE'])
def api_product_stock_link(product_id):
    if request.method == 'GET':
        sid = db.get_product_stock_link(product_id)
        return jsonify({'stock_item_id': sid})
    elif request.method == 'POST':
        sid = request.json.get('stock_item_id')
        db.set_product_stock_link(product_id, sid)
        return jsonify({'success': True})
    elif request.method == 'DELETE':
        db.set_product_stock_link(product_id, None)
        return jsonify({'success': True})

# ===== STOK UYARI API =====

@app.route('/api/stock/alerts')
def api_stock_alerts():
    items = db.get_low_stock_items()
    return jsonify(items)

# ===== KAPALI SİPARİŞ DÜZENLEME =====

@app.route('/api/orders/<int:order_id>/reclose', methods=['POST'])
def api_reclose_order(order_id):
    """Düzenlenen siparişi yeniden kapat"""
    d = request.json or {}
    conn = db.get_db()
    existing = conn.execute('SELECT created_at, closed_at FROM orders WHERE id = ?', (order_id,)).fetchone()
    if not existing:
        conn.close()
        return jsonify({'error': 'Sipariş bulunamadı'}), 404

    # Toplam yeniden hesapla
    total = conn.execute('''
        SELECT COALESCE(SUM(CASE WHEN is_complimentary=0 THEN quantity*price ELSE 0 END),0) as t
        FROM order_items WHERE order_id=?
    ''', (order_id,)).fetchone()['t']

    custom_dt = d.get('closed_at') or d.get('date') or d.get('created_at')
    if custom_dt:
        dt_str = str(custom_dt).replace('T', ' ').strip()
        if len(dt_str) == 16:
            dt_str += ':00'
        target_closed_at = dt_str
        target_created_at = dt_str
    else:
        target_closed_at = existing['closed_at'] or existing['created_at'] or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        target_created_at = existing['created_at'] or target_closed_at

    conn.execute('''UPDATE orders SET status='closed', total=?, closed_at=?, created_at=?,
        payment_cash=?, payment_card=?, tip_amount=?, tip_method=?
        WHERE id=?''',
        (total, target_closed_at, target_created_at, d.get('payment_cash',0), d.get('payment_card',0), d.get('tip_amount',0), d.get('tip_method', 'cash'), order_id))
    conn.execute('DELETE FROM transactions WHERE related_order_id = ?', (order_id,))
    db.record_order_transaction(
        conn, order_id,
        d.get('payment_cash',0), d.get('payment_card',0),
        d.get('tip_amount',0), d.get('tip_method', 'cash'),
        target_closed_at
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'total': total})

# ===== ÖN MUHASEBE (#50) =====

@app.route('/backup')
def backup_page():
    return render_template('backup.html', app_version=APP_VERSION)

@app.route('/hesap')
def page_hesap():
    return render_template('hesap.html')

@app.route('/api/hesap/overview')
def api_hesap_overview():
    start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
    end   = request.args.get('end',   datetime.now().strftime('%Y-%m-%d'))

    data = db.get_report(start, end)
    data['hourly'] = db.get_hourly_sales(start, end)
    data['kasa_nakit'] = db.get_kasa_data(start, end, 'cash')
    data['kasa_kart']  = db.get_kasa_data(start, end, 'card')
    data['kasa_ana']   = db.get_kasa_data(start, end, None)

    import sqlite3
    conn = sqlite3.connect(db.DB_PATH)
    conn.row_factory = sqlite3.Row
    cats = conn.execute('''
        SELECT COALESCE(category,'Genel') as category,
               SUM(amount) as total,
               COUNT(*) as count
        FROM expenses
        WHERE DATE(created_at) BETWEEN ? AND ?
        GROUP BY category
        ORDER BY total DESC
    ''', (start, end)).fetchall()

    open_orders = conn.execute('''
        SELECT o.id, t.name as table_name, o.total, o.created_at
        FROM orders o
        JOIN tables t ON o.table_id = t.id
        WHERE o.status = 'open'
        ORDER BY o.created_at
    ''').fetchall()
    conn.close()

    data['expense_categories'] = [dict(r) for r in cats]
    data['open_orders'] = [dict(r) for r in open_orders]
    data['open_orders_count'] = len(open_orders)

    vat_rate = float(db.get_setting('vat_rate', '18'))
    data['vat_rate'] = vat_rate
    data['vat_amount'] = round(data['total_sales'] * vat_rate / (100 + vat_rate), 2)
    data['sales_excl_vat'] = round(data['total_sales'] - data['vat_amount'], 2)

    return jsonify(data)

@app.route('/muhasebe')
def page_muhasebe():
    return render_template('muhasebe.html')

@app.route('/reports')
def page_reports_redirect():
    return render_template('reports.html')

@app.route('/api/muhasebe')
def api_muhasebe():
    start = request.args.get('start', datetime.now().strftime('%Y-%m-%d'))
    end   = request.args.get('end',   datetime.now().strftime('%Y-%m-%d'))

    data = db.get_report(start, end)

    # Masraf kategorileri
    import sqlite3
    conn = sqlite3.connect(db.DB_PATH)
    conn.row_factory = sqlite3.Row
    cats = conn.execute('''
        SELECT COALESCE(category,'Genel') as category,
               SUM(amount) as total
        FROM expenses
        WHERE DATE(created_at) BETWEEN ? AND ?
        GROUP BY category
        ORDER BY total DESC
    ''', (start, end)).fetchall()
    conn.close()
    data['expense_categories'] = [dict(r) for r in cats]

    vat_rate = float(db.get_setting('vat_rate', '18'))
    data['vat_rate'] = vat_rate
    data['vat_amount'] = round(data['total_sales'] * vat_rate / (100 + vat_rate), 2)
    data['sales_excl_vat'] = round(data['total_sales'] - data['vat_amount'], 2)

    return jsonify(data)

# ===== NOT QR =====

@app.route('/api/settings/note-qr', methods=['POST'])
def api_upload_note_qr():
    import base64
    file = request.files.get('file')
    label = request.form.get('label', '')
    if not file:
        return jsonify({'success': False, 'error': 'Dosya yok'})
    try:
        data = file.read()
        b64 = base64.b64encode(data).decode()
        mime = file.content_type or 'image/png'
        data_url = f'data:{mime};base64,{b64}'
        db.set_setting('note_qr_image_url', data_url)
        db.set_setting('note_qr_label', label)
        return jsonify({'success': True, 'url': data_url})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/settings/note-qr/label', methods=['POST'])
def api_save_note_qr_label():
    data = request.get_json()
    db.set_setting('note_qr_label', data.get('label', ''))
    return jsonify({'success': True})

@app.route('/api/settings/note-qr', methods=['GET'])
def api_get_note_qr():
    return jsonify({
        'url': db.get_setting('note_qr_image_url', ''),
        'label': db.get_setting('note_qr_label', '')
    })

@app.route('/api/settings/note-qr', methods=['DELETE'])
def api_delete_note_qr():
    db.set_setting('note_qr_image_url', '')
    db.set_setting('note_qr_label', '')
    return jsonify({'success': True})

# ===== KAYITLI NOTLAR =====

@app.route('/api/notes/saved', methods=['GET'])
def api_saved_notes_list():
    return jsonify(db.get_saved_notes())

@app.route('/api/notes/saved', methods=['POST'])
def api_saved_notes_create():
    data = request.get_json()
    title = data.get('title', 'NOT').strip() or 'NOT'
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'success': False, 'error': 'İçerik boş'}), 400
    note_id = db.add_saved_note(title, content)
    return jsonify({'success': True, 'id': note_id})

@app.route('/api/notes/saved/<int:note_id>', methods=['PUT'])
def api_saved_notes_update(note_id):
    data = request.get_json()
    title = data.get('title', 'NOT').strip() or 'NOT'
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'success': False, 'error': 'İçerik boş'}), 400
    db.update_saved_note(note_id, title, content)
    return jsonify({'success': True})

@app.route('/api/notes/saved/<int:note_id>', methods=['DELETE'])
def api_saved_notes_delete(note_id):
    db.delete_saved_note(note_id)
    return jsonify({'success': True})

# ===== FİŞ ÖNİZLEME =====

@app.route('/api/print/receipt/<int:order_id>/preview', methods=['GET'])
def api_preview_receipt(order_id):
    order = db.get_table_order_by_id(order_id)
    if not order:
        return "Sipariş bulunamadı", 404
    
    return render_template('receipts/customer_receipt.html',
        order=order,
        restaurant_name=db.get_setting('restaurant_name', 'Fırınna'),
        restaurant_address=db.get_setting('restaurant_address', ''),
        restaurant_phone=db.get_setting('restaurant_phone', ''),
        restaurant_web=db.get_setting('restaurant_web', ''),
        footer_note=db.get_setting('receipt_footer', 'Afiyet olsun!'),
        logo_url=db.get_setting('logo_url', ''),
        qr_image_url=db.get_setting('receipt_qr_image_url', ''),
        qr_label=db.get_setting('receipt_qr_label', 'Bizi Google Haritalarda bulun')
    )

@app.route('/api/print/kitchen/<int:order_id>/preview', methods=['GET'])
def api_preview_kitchen(order_id):
    order = db.get_table_order_by_id(order_id)
    if not order:
        return "Sipariş bulunamadı", 404
    
    return render_template('receipts/kitchen_receipt.html', order=order)


# ===== FİŞ PDF EXPORT =====

@app.route('/api/print/receipt/<int:order_id>/pdf', methods=['GET'])
def api_pdf_receipt(order_id):
    from weasyprint import HTML
    from io import BytesIO
    
    order = db.get_table_order_by_id(order_id)
    if not order:
        return "Sipariş bulunamadı", 404
    
    # HTML render et
    html_content = render_template('receipts/customer_receipt.html',
        order=order,
        restaurant_name=db.get_setting('restaurant_name', 'Fırınna'),
        restaurant_address=db.get_setting('restaurant_address', ''),
        restaurant_phone=db.get_setting('restaurant_phone', ''),
        restaurant_web=db.get_setting('restaurant_web', ''),
        footer_note=db.get_setting('receipt_footer', 'Afiyet olsun!'),
        logo_url=db.get_setting('logo_url', '')
    )
    
    # PDF'e çevir
    pdf_file = BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    pdf_file.seek(0)
    
    from flask import send_file
    return send_file(pdf_file, mimetype='application/pdf', 
                     as_attachment=True, 
                     download_name=f'fis_{order_id}.pdf')

@app.route('/api/print/kitchen/<int:order_id>/pdf', methods=['GET'])
def api_pdf_kitchen(order_id):
    from weasyprint import HTML
    from io import BytesIO
    
    order = db.get_table_order_by_id(order_id)
    if not order:
        return "Sipariş bulunamadı", 404
    
    # HTML render et
    html_content = render_template('receipts/kitchen_receipt.html', order=order)
    
    # PDF'e çevir
    pdf_file = BytesIO()
    HTML(string=html_content).write_pdf(pdf_file)
    pdf_file.seek(0)
    
    from flask import send_file
    return send_file(pdf_file, mimetype='application/pdf',
                     as_attachment=True,
                     download_name=f'mutfak_{order_id}.pdf')

# Muhasebe tablolarını başlat ve migrasyonu çalıştır

@app.route('/debug/transactions')
def debug_transactions():
    import os
    try:
        conn = db.get_db()
        # Hangi DB dosyası kullanılıyor?
        db_path = db.DB_PATH
        abs_path = os.path.abspath(db_path)
        # transactions tablosu var mı?
        tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        # Son 10 transaction
        txns = []
        if 'transactions' in tables:
            txns = [dict(r) for r in conn.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT 10").fetchall()]
        # Son 5 stock_movement
        moves = []
        if 'stock_movements' in tables:
            moves = [dict(r) for r in conn.execute("SELECT * FROM stock_movements ORDER BY id DESC LIMIT 5").fetchall()]
        conn.close()
        return jsonify({
            'db_path_relative': db_path,
            'db_path_absolute': abs_path,
            'db_exists': os.path.exists(abs_path),
            'db_size_bytes': os.path.getsize(abs_path) if os.path.exists(abs_path) else 0,
            'cwd': os.getcwd(),
            'tables': tables,
            'last_transactions': txns,
            'last_stock_movements': moves,
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()})


# ===== GİTHUB SYNC (#40) =====

GIT_DIR = os.path.dirname(os.path.abspath(__file__))
GIT_CRED_FILE = '/home/turan/.firinna_git_credentials.json'

def get_git_credentials():
    try:
        if os.path.exists(GIT_CRED_FILE):
            with open(GIT_CRED_FILE) as f:
                import json as _json
                return _json.load(f)
    except:
        pass
    return {'username': '', 'token': ''}

def run_git(args, timeout=30):
    """Git komutunu çalıştır, (success, output) döndür"""
    import os
    env = os.environ.copy()
    env['GIT_TERMINAL_PROMPT'] = '0'
    try:
        result = subprocess.run(
            ['/usr/bin/git'] + args,
            cwd=GIT_DIR,
            env=env,
            capture_output=True, text=True, timeout=timeout
        )
        out = (result.stdout + result.stderr).strip()
        return result.returncode == 0, out
    except subprocess.TimeoutExpired:
        return False, f'Zaman aşımı ({timeout}s)'
    except Exception as e:
        return False, str(e)

# ── Local config (makine başına ayarlar — git'e gitmez) ──
_LOCAL_CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'firinna_local.json')

def read_local_config():
    """Bu cihaza özel ayarları oku (git'e gitmez)"""
    try:
        if os.path.exists(_LOCAL_CONFIG_PATH):
            with open(_LOCAL_CONFIG_PATH, 'r') as f:
                import json
                return json.load(f)
    except Exception:
        pass
    return {}

def write_local_config(updates: dict):
    """Local config'i güncelle (mevcut değerleri koru)"""
    cfg = read_local_config()
    cfg.update(updates)
    try:
        import json
        with open(_LOCAL_CONFIG_PATH, 'w') as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f'[local_config] Yazma hatası: {e}')


@app.route("/api/git/credentials", methods=["GET"])
def api_git_credentials_get():
    cred = get_git_credentials()
    return jsonify({'username': cred.get('username',''), 'has_token': bool(cred.get('token',''))})

@app.route('/api/git/credentials', methods=['POST'])
def api_git_credentials_set():
    data = request.json or {}
    username = data.get('username','').strip()
    token    = data.get('token','').strip()
    existing = get_git_credentials()
    if not token:
        token = existing.get('token','')
    try:
        import json as _json
        with open(GIT_CRED_FILE, 'w') as f:
            _json.dump({'username': username, 'token': token}, f)
        os.chmod(GIT_CRED_FILE, 0o600)
        if username and token:
            subprocess.run(
                ['/usr/bin/git', 'remote', 'set-url', 'origin',
                 f'https://{username}:{token}@github.com/{username}/firinna-pos.git'],
                cwd=GIT_DIR
            )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/git/status', methods=['GET'])
def api_git_status():
    """Yerel ile GitHub arasındaki farkı göster"""
    # Önce fetch yap
    run_git(['fetch', 'origin', 'main'])
    
    # Kaç commit geride/ileride?
    ok, ahead = run_git(['rev-list', '--count', 'origin/main..HEAD'])
    ok2, behind = run_git(['rev-list', '--count', 'HEAD..origin/main'])
    ahead = int(ahead) if ok and ahead.isdigit() else 0
    behind = int(behind) if ok2 and behind.isdigit() else 0
    
    # Değişen dosyalar (local vs origin)
    ok3, diff_stat = run_git(['diff', '--stat', 'origin/main'])
    
    # Son yerel commit
    ok4, last_local = run_git(['log', '-1', '--pretty=%h %s (%ar)', 'HEAD'])
    
    # Son uzak commit
    ok5, last_remote = run_git(['log', '-1', '--pretty=%h %s (%ar)', 'origin/main'])
    
    # Kirli dosyalar (commit edilmemiş değişiklikler)
    ok6, dirty = run_git(['status', '--short'])
    
    return jsonify({
        'ahead': ahead,
        'behind': behind,
        'diff_stat': diff_stat if ok3 else '',
        'last_local': last_local if ok4 else '?',
        'last_remote': last_remote if ok5 else '?',
        'dirty': dirty if ok6 else '',
        'dirty_count': len([l for l in dirty.split('\n') if l.strip()]) if dirty else 0
    })

@app.route('/api/git/push', methods=['POST'])
def api_git_push():
    """Tüm değişiklikleri commit + push (önce pull ile senkronize et)"""
    data = request.json or {}
    msg = data.get('message', '').strip()
    if not msg:
        now = datetime.now().strftime('%d.%m.%Y %H:%M')
        msg = f'Güncelleme — {now}'

    # 1. Önce commit edilmemiş değişiklikleri stash'e al
    ok_s, dirty = run_git(['status', '--short'])
    has_changes = bool(dirty.strip())

    if has_changes:
        ok1, out1 = run_git(['add', '-A'])
        if not ok1:
            return jsonify({'success': False, 'error': 'git add hatası: ' + out1})
        ok2, out2 = run_git(['commit', '-m', msg])
        if not ok2:
            return jsonify({'success': False, 'error': 'git commit hatası: ' + out2})

    # 2. Önce GitHub'dan pull (rebase ile — commit geçmişini temiz tutar)
    ok_pull, out_pull = run_git(['pull', '--rebase', 'origin', 'main'], timeout=60)
    if not ok_pull:
        # Rebase çakışması — abort + force push yerine hata ver
        run_git(['rebase', '--abort'])
        return jsonify({'success': False, 'error': 'Pull/rebase hatası: ' + out_pull})

    # 3. DB dump al ve commit'e ekle
    try:
        dump_path = db.dump_database_sql()
        run_git(['add', dump_path])
        ok_dc, out_dc = run_git(['commit', '-m', f'DB dump — {datetime.now().strftime("%d.%m.%Y %H:%M")}'])
    except Exception as e:
        pass  # dump başarısız olsa da push devam eder

    # 4. Push
    ok3, out3 = run_git(['push', 'origin', 'main'], timeout=60)
    if not ok3:
        return jsonify({'success': False, 'error': 'git push hatası: ' + out3})

    return jsonify({
        'success': True,
        'had_changes': has_changes,
        'output': out_pull + '\n' + out3
    })


@app.route('/api/git/pull', methods=['POST'])
def api_git_pull():
    """GitHub'tan en son sürümü çek — DB dahil"""
    # Önce fetch
    ok_fetch, out_fetch = run_git(['fetch', 'origin', 'main'], timeout=30)
    if not ok_fetch:
        return jsonify({'success': False, 'error': 'fetch hatası: ' + out_fetch})

    # Kaç commit geride?
    ok_behind, behind = run_git(['rev-list', '--count', 'HEAD..origin/main'])
    already_up = ok_behind and behind.strip() == '0'

    if already_up:
        return jsonify({'success': True, 'already_up': True, 'output': 'Zaten güncel.'})

    # Yerel commit edilmemiş değişiklik varsa stash'e at
    ok_s, dirty = run_git(['status', '--short'])
    if dirty.strip():
        run_git(['stash', '--include-untracked'])

    # Pull
    ok, out = run_git(['pull', 'origin', 'main', '--strategy-option=theirs'], timeout=60)
    if not ok:
        # Stash'i geri al
        run_git(['stash', 'pop'])
        return jsonify({'success': False, 'error': out})

    # Servis restart et
    try:
        subprocess.Popen(['/usr/bin/sudo', '/usr/bin/systemctl', 'restart', 'firinna-pos'])
    except:
        pass

    return jsonify({
        'success': True,
        'already_up': False,
        'output': out
    })

@app.route('/api/git/auto-pull/status', methods=['GET'])
def api_auto_pull_status():
    cfg = read_local_config()
    return jsonify({
        'mode': cfg.get('auto_pull_mode', 'off'),
        'interval': int(cfg.get('auto_pull_interval', 0)),
        'time': cfg.get('auto_pull_time', '')
    })

@app.route('/api/git/auto-pull/set', methods=['POST'])
def api_auto_pull_set():
    data = request.json or {}
    mode = data.get('mode', 'off')
    interval = int(data.get('interval', 0))
    pull_time = data.get('time', '')
    write_local_config({
        'auto_pull_mode': mode,
        'auto_pull_interval': interval,
        'auto_pull_time': pull_time
    })
    # Thread'i yeniden başlat
    start_auto_pull_smart()
    return jsonify({'success': True, 'mode': mode})

# --- Auto-pull arka plan iş parçacığı ---
_auto_pull_timer = None
_auto_pull_time_thread = None
_auto_pull_time_running = False

def start_auto_pull_smart():
    """Local config'e göre doğru pull modunu başlat"""
    cfg = read_local_config()
    mode = cfg.get('auto_pull_mode', 'off')
    if mode == 'interval':
        interval = int(cfg.get('auto_pull_interval', 0))
        if interval > 0:
            start_auto_pull(interval)
    elif mode == 'time':
        pull_time = cfg.get('auto_pull_time', '')
        if pull_time:
            start_auto_pull_at_time(pull_time)
    else:
        # Kapat
        global _auto_pull_timer, _auto_pull_time_running
        if _auto_pull_timer:
            _auto_pull_timer.cancel()
        _auto_pull_time_running = False

_telegram_auto_send_running = False
_telegram_auto_send_thread = None

def start_telegram_auto_send():
    """Her gün belirli saatte günlük kapanış raporunu Telegram'a gönder"""
    global _telegram_auto_send_running, _telegram_auto_send_thread
    _telegram_auto_send_running = True

    def loop():
        import time as _time
        last_sent = None
        while _telegram_auto_send_running:
            try:
                enabled = db.get_setting('telegram_daily_close_enabled', '0')
                t = db.get_setting('telegram_daily_close_time', '')
                if enabled == '1' and t:
                    now = datetime.now()
                    h, m = map(int, t.split(':'))
                    today = now.strftime('%Y-%m-%d')
                    if now.hour == h and now.minute == m and last_sent != today:
                        report = db.get_daily_close_report(today)
                        restaurant = db.get_setting('restaurant_name', 'Fırınna')
                        top = report.get('top_products', [])[:5]
                        open_warn = ''
                        if report.get('open_orders_count', 0) > 0:
                            open_warn = f"\n⚠️ {report['open_orders_count']} masa hâlâ açık!"
                        top_txt = '\n'.join([f"  {i+1}. {p['name']} — {p['quantity']} adet" for i, p in enumerate(top)]) if top else '  —'
                        text = (
                            f"📋 <b>{restaurant} — Günlük Kapanış</b> ({today})\n\n"
                            f"💰 Toplam Satış: <b>{report.get('total_sales',0):.2f} ₺</b>\n"
                            f"💵 Nakit: {report.get('total_cash',0):.2f} ₺\n"
                            f"💳 Kart: {report.get('total_card',0):.2f} ₺\n"
                            f"💸 Bahşiş: {report.get('total_tips',0):.2f} ₺\n"
                            f"🎁 İkramlar: {report.get('total_ikram',0):.2f} ₺\n"
                            f"📉 İndirimler: {report.get('total_discount',0):.2f} ₺\n"
                            f"🔻 Giderler: {report.get('total_expenses',0):.2f} ₺\n"
                            f"💵 Net Kasa: <b>{report.get('net',0):.2f} ₺</b>\n\n"
                            f"🧾 Masa Sayısı: {report.get('order_count',0)} ({report.get('cash_order_count',0)} Nakit, {report.get('card_order_count',0)} Kart, {report.get('mixed_order_count',0)} Parçalı)\n\n"
                            f"📦 En Çok Satanlar:\n{top_txt}"
                            f"{open_warn}"
                            f"{get_tomorrow_schedule_alert()}"
                        )
                        try:
                            import telegram_notify
                            telegram_notify.send_message(text)
                            
                            # Gün sonu telegram'ı otomatik gönderildiğinde web durumunu da auto'ya al
                            try:
                                if os.path.exists(SETTINGS_FILE):
                                    with open(SETTINGS_FILE, 'r') as f:
                                        s_data = json.load(f)
                                    if s_data.get('manual_status') != 'auto':
                                        s_data['manual_status'] = 'auto'
                                        with open(SETTINGS_FILE, 'w') as f:
                                            json.dump(s_data, f, indent=4, ensure_ascii=False)
                            except Exception as ex:
                                print(f"Auto status reset error: {ex}")

                        except Exception as te:
                            print(f"Telegram auto-send hatasi: {te}")
                        last_sent = today
                        _time.sleep(60) # Sadece 1 dakika uyut (60 saniye), böylece o dakika içinde bir daha göndermez
                        continue
            except Exception as e:
                import traceback
                print(f"Telegram auto-send loop hatasi: {e}")
                traceback.print_exc()
            _time.sleep(30)

    _telegram_auto_send_thread = threading.Thread(target=loop, daemon=True)
    _telegram_auto_send_thread.start()

def start_auto_pull_at_time(pull_time_str):
    """Her gün belirli saatte pull yap"""
    global _auto_pull_time_running, _auto_pull_time_thread
    _auto_pull_time_running = True

    def loop():
        import time as _time
        last_pulled = None
        while _auto_pull_time_running:
            cfg = read_local_config()
            t = cfg.get('auto_pull_time', '')
            if t:
                try:
                    now = datetime.now()
                    h, m = map(int, t.split(':'))
                    today = now.strftime('%Y-%m-%d')
                    if now.hour == h and now.minute == m and last_pulled != today:
                        ok, out = run_git(['pull', 'origin', 'main', '--strategy-option=theirs'])
                        if ok and 'Already up to date' not in out:
                            try:
                                subprocess.Popen(['/usr/bin/sudo', '/usr/bin/systemctl', 'restart', 'firinna-pos'])
                            except:
                                pass
                        last_pulled = today
                        _time.sleep(70)
                        continue
                except Exception as e:
                    print(f"Auto pull time hatasi: {e}")
            _time.sleep(30)

    _auto_pull_time_thread = threading.Thread(target=loop, daemon=True)
    _auto_pull_time_thread.start()

def start_auto_pull(interval_minutes):
    global _auto_pull_timer
    if _auto_pull_timer:
        _auto_pull_timer.cancel()
    if interval_minutes <= 0:
        return
    
    def do_pull():
        global _auto_pull_timer
        ok, out = run_git(['fetch', 'origin', 'main'])
        ok2, behind = run_git(['rev-list', '--count', 'HEAD..origin/main'])
        if ok2 and behind.strip().isdigit() and int(behind.strip()) > 0:
            run_git(['pull', 'origin', 'main'])
            # Sadece gerçekten pull yapılırsa restart
            try:
                subprocess.Popen(['/usr/bin/sudo', '/usr/bin/systemctl', 'restart', 'firinna-pos'])
            except:
                pass
        # Bir sonraki kontrol
        _auto_pull_timer = threading.Timer(interval_minutes * 60, do_pull)
        _auto_pull_timer.daemon = True
        _auto_pull_timer.start()
    
    _auto_pull_timer = threading.Timer(interval_minutes * 60, do_pull)
    _auto_pull_timer.daemon = True
    _auto_pull_timer.start()

# ===== OTOMATİK PUSH (belirli saatte) =====

_auto_push_thread = None
_auto_push_running = False

def start_auto_push():
    """Her gün ayarlanan saatte otomatik push yapar"""
    global _auto_push_running
    _auto_push_running = True

    def loop():
        import time as _time
        last_interval_push = 0
        last_time_push_date = None
        while _auto_push_running:
            try:
                cfg = read_local_config()
                mode = cfg.get('auto_push_mode', 'off')
                now = datetime.now()
                should_push = False

                if mode == 'interval':
                    interval_min = int(cfg.get('auto_push_interval', 0))
                    if interval_min > 0:
                        elapsed = (_time.time() - last_interval_push) / 60
                        if elapsed >= interval_min:
                            should_push = True

                elif mode == 'time':
                    push_time = cfg.get('auto_push_time', '')
                    if push_time:
                        h, m = map(int, push_time.split(':'))
                        today = now.strftime('%Y-%m-%d')
                        if now.hour == h and now.minute == m and last_time_push_date != today:
                            should_push = True
                            last_time_push_date = today

                if should_push:
                    ok_add, _ = run_git(['add', '-A'])
                    if ok_add:
                        msg = f"Otomatik push - {now.strftime('%d.%m.%Y %H:%M')}"
                        run_git(['commit', '-m', msg])
                    run_git(['push', 'origin', 'main'])
                    last_interval_push = _time.time()
                    _time.sleep(70)
                    continue

            except Exception as e:
                print(f"Auto push hatası: {e}")
            _time.sleep(30)

    global _auto_push_thread
    _auto_push_thread = threading.Thread(target=loop, daemon=True)
    _auto_push_thread.start()

@app.route('/api/git/auto-push', methods=['GET'])
def api_auto_push_status():
    cfg = read_local_config()
    return jsonify({
        'mode': cfg.get('auto_push_mode', 'off'),
        'interval': int(cfg.get('auto_push_interval', 0)),
        'time': cfg.get('auto_push_time', '')
    })

@app.route('/api/git/auto-push', methods=['POST'])
def api_auto_push_set():
    data = request.json or {}
    mode = data.get('mode', 'off')
    interval = int(data.get('interval', 0))
    push_time = data.get('time', '')
    write_local_config({
        'auto_push_mode': mode,
        'auto_push_interval': interval,
        'auto_push_time': push_time
    })
    return jsonify({'success': True, 'mode': mode})


# ── Fabrika Ayarları ──

@app.route('/api/factory/github-reset', methods=['POST'])
def api_factory_github_reset():
    import subprocess as _sp, threading
    def _do():
        import time
        _sp.run('git -C /opt/firinna-pos fetch origin', shell=True)
        _sp.run('git -C /opt/firinna-pos reset --hard origin/main', shell=True)
        _sp.run('git -C /opt/firinna-pos clean -fd', shell=True)
        _sp.run('find /opt/firinna-pos -name "*.pyc" -delete', shell=True)
        time.sleep(1)
        _sp.run('systemctl restart firinna-pos', shell=True)
    threading.Thread(target=_do, daemon=True).start()
    return jsonify({'success': True, 'message': 'Reset başlatıldı, sayfa yenileniyor...'})


@app.route('/api/factory/db-reset-restore', methods=['POST'])
def api_factory_db_reset_restore():
    """DB'yi sıfırla ve yüklenen yedeği geri yükle"""
    import shutil
    f = request.files.get('db_file')
    if not f:
        return jsonify({'success': False, 'error': 'db_file gönderilmedi'})
    ext = os.path.splitext(f.filename or '')[1].lower()
    if ext not in ('.db', '.sqlite', '.sqlite3'):
        return jsonify({'success': False, 'error': 'Sadece .db dosyası kabul edilir'})
    db_path = db.DB_PATH
    backup_path = db_path + '.factory_backup'
    try:
        shutil.copy2(db_path, backup_path)
        f.save(db_path)
        return jsonify({'success': True, 'message': 'DB değiştirildi. Sunucuyu yeniden başlatın.'})
    except Exception as e:
        # Geri al
        try:
            shutil.copy2(backup_path, db_path)
        except Exception:
            pass
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/factory/db-wipe', methods=['POST'])
def api_factory_db_wipe():
    """Tüm verileri sil — DB'yi sıfırdan oluştur"""
    import shutil
    db_path = db.DB_PATH
    backup_path = db_path + '.wipe_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
    try:
        shutil.copy2(db_path, backup_path)
        os.remove(db_path)
        db.init_db()
        db.init_muhasebe_tables()
        return jsonify({'success': True,
                        'message': f'DB tamamen silindi ve yeniden oluşturuldu. Yedek: {os.path.basename(backup_path)}'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})




@app.route('/api/reports/profitability', methods=['GET'])
def api_profitability():
    """Ürün bazlı karlılık raporu — tüm zamanlar"""
    import sqlite3 as _sq
    conn = _sq.connect(db.DB_PATH)
    conn.row_factory = _sq.Row
    # Satış verileri
    sales = conn.execute('''
        SELECT
            COALESCE(oi.product_id, 0) as pid,
            COALESCE(oi.product_name, p.name, 'Silinmiş') as name,
            SUM(CASE WHEN oi.is_complimentary=0 THEN oi.quantity ELSE 0 END) as sold_qty,
            SUM(CASE WHEN oi.is_complimentary=0 THEN oi.quantity * oi.price ELSE 0 END) as revenue,
            AVG(CASE WHEN oi.is_complimentary=0 THEN oi.price ELSE NULL END) as avg_price
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.id
        JOIN orders o ON oi.order_id = o.id
        WHERE o.status = 'closed'
        GROUP BY oi.product_id
        ORDER BY revenue DESC
    ''').fetchall()
    # Reçete maliyet hesabı
    recipes = conn.execute('''
        SELECT r.product_id, SUM(r.quantity * s.cost_per_unit) as unit_cost
        FROM recipes r
        JOIN stock_items s ON r.stock_item_id = s.id
        GROUP BY r.product_id
    ''').fetchall()
    conn.close()
    cost_map = {r['product_id']: float(r['unit_cost'] or 0) for r in recipes}
    result = []
    for s in sales:
        pid      = s['pid']
        revenue  = float(s['revenue'] or 0)
        sold_qty = float(s['sold_qty'] or 0)
        avg_price= float(s['avg_price'] or 0)
        unit_cost= cost_map.get(pid, 0)
        total_cost = unit_cost * sold_qty
        profit   = revenue - total_cost
        margin   = (profit / revenue * 100) if revenue > 0 else 0
        result.append({
            'product_id':  pid,
            'name':        s['name'],
            'sold_qty':    round(sold_qty, 2),
            'avg_price':   round(avg_price, 2),
            'unit_cost':   round(unit_cost, 2),
            'revenue':     round(revenue, 2),
            'total_cost':  round(total_cost, 2),
            'profit':      round(profit, 2),
            'margin':      round(margin, 1),
            'has_recipe':  pid in cost_map
        })
    return jsonify(result)


@app.route("/api/orders/<int:order_id>/note", methods=["GET", "POST"])
def order_note(order_id):
    """Sipariş notu: GET döner, POST kaydeder."""
    import sqlite3 as _sq
    conn = _sq.connect('pos_data.db')
    conn.row_factory = _sq.Row
    if request.method == "GET":
        row = conn.execute(
            "SELECT note FROM orders WHERE id = ?", (order_id,)
        ).fetchone()
        conn.close()
        if row is None:
            return jsonify({"error": "Sipariş bulunamadı"}), 404
        return jsonify({"note": row["note"] or ""})
    else:
        data = request.get_json(silent=True) or {}
        note = data.get("note", "").strip()
        conn.execute(
            "UPDATE orders SET note = ? WHERE id = ?", (note, order_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"ok": True, "note": note})

# ===== GELİŞTİRİCİ TALEPLERİ =====
DEV_REQUESTS_FILE = os.path.join(os.path.dirname(__file__), 'static', 'dev_requests.json')

def _load_dev_requests():
    if not os.path.exists(DEV_REQUESTS_FILE):
        return []
    with open(DEV_REQUESTS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def _save_dev_requests(items):
    with open(DEV_REQUESTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

@app.route('/api/dev-requests', methods=['GET'])
def api_dev_requests_get():
    return jsonify(_load_dev_requests())

@app.route('/api/dev-requests', methods=['POST'])
def api_dev_requests_add():
    data = request.json
    items = _load_dev_requests()
    new_id = max((i['id'] for i in items), default=0) + 1
    items.append({
        'id': new_id,
        'text': data.get('text', ''),
        'done': False,
        'date': data.get('date', datetime.now().strftime('%Y-%m-%d')),
        'cat': data.get('cat', 'istek')
    })
    _save_dev_requests(items)
    return jsonify({'success': True, 'id': new_id})

@app.route('/api/dev-requests/<int:req_id>', methods=['PATCH'])
def api_dev_requests_patch(req_id):
    data = request.json
    items = _load_dev_requests()
    for item in items:
        if item['id'] == req_id:
            if 'done' in data:
                item['done'] = data['done']
            if 'text' in data:
                item['text'] = data['text']
            break
    _save_dev_requests(items)
    return jsonify({'success': True})

@app.route('/api/dev-requests/<int:req_id>', methods=['DELETE'])
def api_dev_requests_delete(req_id):
    items = _load_dev_requests()
    items = [i for i in items if i['id'] != req_id]
    _save_dev_requests(items)
    return jsonify({'success': True})
# =========================================================================
# WEB SITE INTEGRATION (API BRIDGES)
# =========================================================================
import telegram_notify

@app.route('/api/web/reservations', methods=['POST'])
def web_reservation():
    data = request.json
    name = data.get('name', 'Bilinmeyen')
    phone = data.get('phone', '')
    date = data.get('date', '')
    time = data.get('time', '')
    guests = data.get('guests', 2)
    note = data.get('note', '')
    
    msg = f"📅 <b>YENİ REZERVASYON TALEBİ (Web'den)</b>\n\n"
    msg += f"👤 <b>İsim:</b> {name}\n"
    msg += f"📞 <b>Telefon:</b> {phone}\n"
    msg += f"🗓 <b>Tarih/Saat:</b> {date} - {time}\n"
    msg += f"👥 <b>Kişi Sayısı:</b> {guests}\n"
    if note:
        msg += f"📝 <b>Not:</b> {note}\n"
    
    telegram_notify.send_async(msg)
    return jsonify({"success": True, "message": "Rezervasyon talebiniz alındı."})

@app.route('/api/web/messages', methods=['POST'])
def web_message():
    data = request.json
    name = data.get('name', 'Bilinmeyen')
    phone = data.get('phone', '')
    message = data.get('message', '')
    
    msg = f"💬 <b>YENİ İLETİŞİM MESAJI (Web'den)</b>\n\n"
    msg += f"👤 <b>İsim:</b> {name}\n"
    msg += f"📞 <b>Telefon:</b> {phone}\n"
    msg += f"📝 <b>Mesaj:</b> {message}\n"
    
    telegram_notify.send_async(msg)
    return jsonify({"success": True, "message": "Mesajınız iletildi."})

import json
import os
SETTINGS_FILE = '/opt/firinna-pos/web_settings.json'

@app.route('/api/web/settings', methods=['GET'])
def get_web_settings():
    if not os.path.exists(SETTINGS_FILE):
        return jsonify({})
    with open(SETTINGS_FILE, 'r') as f:
        return jsonify(json.load(f))

@app.route('/api/web/settings', methods=['POST'])
def save_web_settings():
    data = request.json
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    return jsonify({"success": True})

@app.route('/api/web/status', methods=['GET'])
def get_store_status():
    """Public CORS-enabled real-time Store Status API for external crawlers & directories."""
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
        except Exception:
            pass

    manual_status = settings.get('manual_status', 'auto')
    daily_hours = settings.get('daily_hours', {
        "Pazartesi": {"open": "08:30", "close": "23:00", "active": True},
        "Salı":      {"open": "08:30", "close": "23:00", "active": True},
        "Çarşamba":  {"open": "08:30", "close": "23:00", "active": True},
        "Perşembe":  {"open": "08:30", "close": "23:00", "active": True},
        "Cuma":      {"open": "08:30", "close": "23:00", "active": True},
        "Cumartesi": {"open": "08:30", "close": "23:00", "active": True},
        "Pazar":     {"open": "08:30", "close": "23:00", "active": True}
    })

    now = datetime.now()
    days_tr = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    current_day_tr = days_tr[now.weekday()]
    current_hm = now.strftime("%H:%M")

    today_cfg = daily_hours.get(current_day_tr, {"open": "08:30", "close": "23:00", "active": True})
    open_str = today_cfg.get('open', '08:30')
    close_str = today_cfg.get('close', '23:00')

    # 1. Check for open tables implicitly keeping the store open
    has_open_tables = False
    try:
        tables = db.get_tables()
        for t in tables:
            if db.get_table_order(t['id']):
                has_open_tables = True
                break
    except: pass

    if has_open_tables:
        manual_status = 'open'
    
    # 2. Check 2-hour timeout or auto-open time crossover for manual status
    if manual_status != 'auto' and not has_open_tables:
        set_time = settings.get('manual_status_time', 0)
        if set_time:
            dt_set = datetime.fromtimestamp(set_time)
            # Timeout (2 hours)
            if (now.timestamp() - set_time) > 2 * 3600:
                manual_status = 'auto'
            # Crossover to auto open time (e.g. set closed at 07:00, but 08:30 has arrived)
            elif dt_set.strftime("%H:%M") < open_str <= current_hm:
                manual_status = 'auto'

    if manual_status == 'closed':
        is_open = False
        badge = "🔴 ŞU AN KAPALI (Geçici Olarak Kapalı)"
    elif manual_status == 'open':
        is_open = True
        badge = f"🟢 ŞU AN AÇIK ({close_str}'e Kadar)"
    else:
        # Automatic calculation based on current time & daily schedule
        if not today_cfg.get('active', True):
            is_open = False
            badge = "🔴 ŞU AN KAPALI (Bugün Kapalı)"
        else:
            if open_str <= current_hm <= close_str:
                is_open = True
                badge = f"🟢 ŞU AN AÇIK ({close_str}'e Kadar)"
            else:
                is_open = False
                badge = f"🔴 ŞU AN KAPALI (Açılış: {open_str})"

    is_exceptional_open = False
    if is_open and (current_hm < open_str or current_hm > close_str):
        is_exceptional_open = True
    elif not is_open and (open_str <= current_hm <= close_str):
        is_exceptional_closed = True # just in case we need it later
        
    res = jsonify({
        "status": "success",
        "store_name": "Fırınna Cafe & Restaurant",
        "is_open": is_open,
        "is_exceptional_open": is_exceptional_open,
        "status_text": "Açık" if is_open else "Kapalı",
        "status_badge": badge,
        "current_day": current_day_tr,
        "current_time": current_hm,
        "today_hours": f"{open_str} - {close_str}",
        "hours": daily_hours,
        "address": "Şahkulu Mah. Kumbaracı Yokuşu Sok. No:41A, Beyoğlu, İstanbul",
        "phone": "+905456301214",
        "website": "https://firinna.com"
    })
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    res.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return res

@app.route('/api/web/upload-menu', methods=['POST'])
def upload_menu():
    lang = request.form.get('lang')
    if 'file' not in request.files or not lang:
        return jsonify({"success": False, "error": "Geçersiz istek"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "Dosya seçilmedi"})
    
    from werkzeug.utils import secure_filename
    lang = secure_filename(lang)
    if not lang: lang = "tr"
    filename = f"firinna_menu_{lang}.pdf"
    filepath = os.path.join('/opt/firinna-pos/web', filename)
    file.save(filepath)
    return jsonify({"success": True, "filename": filename})

import secrets
import time as _time
from werkzeug.security import generate_password_hash, check_password_hash

# Token -> expiry timestamp (24 saat)
VALID_ADMIN_TOKENS = {}
TOKEN_EXPIRY_SECONDS = 86400  # 24 saat

def _cleanup_expired_tokens():
    now = _time.time()
    expired = [t for t, exp in VALID_ADMIN_TOKENS.items() if now > exp]
    for t in expired:
        VALID_ADMIN_TOKENS.pop(t, None)

DEFAULT_PASSWORD_HASH = generate_password_hash('FirinnaPos2026!')

def _get_password_hash():
    """Settings dosyasından hashlenmiş şifreyi al veya varsayılanı döndür."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
            stored = settings.get('admin_password_hash', '')
            if stored:
                return stored
            # Eski düz metin şifre varsa, hashle ve güncelle (migration)
            old_plain = settings.get('admin_password', '')
            if old_plain:
                hashed = generate_password_hash(old_plain)
                settings['admin_password_hash'] = hashed
                del settings['admin_password']
                with open(SETTINGS_FILE, 'w') as fw:
                    json.dump(settings, fw, indent=4, ensure_ascii=False)
                return hashed
    return DEFAULT_PASSWORD_HASH

def verify_admin_auth():
    _cleanup_expired_tokens()
    token = request.headers.get('X-Admin-Token') or request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    if token and token in VALID_ADMIN_TOKENS:
        if _time.time() <= VALID_ADMIN_TOKENS[token]:
            return True
        else:
            VALID_ADMIN_TOKENS.pop(token, None)
    auth = request.authorization
    if auth and auth.password:
        pw_hash = _get_password_hash()
        if check_password_hash(pw_hash, auth.password):
            return True
    return False

@app.route('/api/web/admin-login', methods=['POST'])
def admin_login():
    data = request.json or {}
    password = data.get('password', '')
    pw_hash = _get_password_hash()
    if check_password_hash(pw_hash, password):
        _cleanup_expired_tokens()
        token = secrets.token_hex(32)
        VALID_ADMIN_TOKENS[token] = _time.time() + TOKEN_EXPIRY_SECONDS
        return jsonify({"success": True, "token": token})
    return jsonify({"success": False, "error": "Hatalı şifre!"})

@app.route('/api/web/change-password', methods=['POST'])
def change_password():
    if not verify_admin_auth():
        return jsonify({"success": False, "error": "Yetkisiz erişim!"}), 401
    data = request.json or {}
    old_pass = data.get('old_password', '')
    new_pass = data.get('new_password', '')
    if not new_pass or len(new_pass) < 6:
        return jsonify({"success": False, "error": "Yeni şifre en az 6 karakter olmalıdır."})
    
    pw_hash = _get_password_hash()
    if not check_password_hash(pw_hash, old_pass):
        return jsonify({"success": False, "error": "Mevcut şifreniz hatalı!"})
        
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            settings = json.load(f)
    
    settings['admin_password_hash'] = generate_password_hash(new_pass)
    settings.pop('admin_password', None)  # Eski düz metin şifreyi sil
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
    return jsonify({"success": True, "message": "Şifreniz başarıyla değiştirildi."})

@app.route('/api/web/reset-analytics', methods=['POST'])
def reset_analytics():
    if not verify_admin_auth():
        return jsonify({"success": False, "error": "Yetkisiz erişim! Lütfen giriş yapın."}), 401
    data = request.json or {}
    scope = data.get('scope', 'all')
    start_date = data.get('startDate')
    end_date = data.get('endDate')

    analytics_file = '/opt/firinna-pos/web_analytics.json'
    if not os.path.exists(analytics_file):
        return jsonify({"success": True, "message": "Sıfırlanacak veri yok."})

    try:
        with open(analytics_file, 'r', encoding='utf-8') as f:
            stats = json.load(f)

        import datetime
        today_str = datetime.datetime.now().strftime("%Y-%m-%d")

        if scope == 'all':
            stats = {
                "today": 0, "month": 0, "total": 0, "menu": 0, "actions": 0, "map_clicks": 0, "last_date": "",
                "devices": {}, "browsers": {}, "countries": {}, "referrers": {},
                "recent_visitors": [], "repeat_visitors": 0, "new_visitors": 0, "os": {}, "peak_hours": {}, "menu_interests": {}
            }
        elif scope == 'today':
            stats["today"] = 0
            stats["recent_visitors"] = [v for v in stats.get("recent_visitors", []) if v.get("iso_date") != today_str]
        elif scope == 'range' and start_date and end_date:
            stats["recent_visitors"] = [
                v for v in stats.get("recent_visitors", [])
                if not (start_date <= (v.get("iso_date") or "") <= end_date)
            ]

        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)

        return jsonify({"success": True, "message": "İstatistikler başarıyla sıfırlandı/güncellendi."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# WEB ÜRÜN & MENÜ YÖNETİMİ APIS
PRODUCTS_FILE = '/opt/firinna-pos/web_products.json'
CATEGORIES_FILE = '/opt/firinna-pos/web_categories.json'

def load_web_categories():
    if os.path.exists(CATEGORIES_FILE):
        try:
            with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_web_categories(categories):
    with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(categories, f, ensure_ascii=False, indent=4)

@app.route('/api/web/categories', methods=['GET'])
def get_web_categories():
    return jsonify(load_web_categories())

@app.route('/api/web/categories', methods=['POST'])
def save_web_category():
    if not verify_admin_auth():
        return jsonify({"success": False, "error": "Yetkisiz erişim! Lütfen giriş yapın."}), 401
    import time
    categories = load_web_categories()
    cat_id = request.form.get('id')
    name = request.form.get('name', '').strip()
    icon = request.form.get('icon', 'ph-fork-knife').strip()

    if not name:
        return jsonify({"success": False, "error": "Kategori adı boş olamaz."})

    if not cat_id:
        new_cat = {
            "id": f"cat_{int(time.time()*1000)}",
            "name": name,
            "icon": icon
        }
        categories.append(new_cat)
    else:
        found = False
        for c in categories:
            if c.get('id') == cat_id:
                c['name'] = name
                c['icon'] = icon
                found = True
                break
        if not found:
            return jsonify({"success": False, "error": "Kategori bulunamadı."})

    save_web_categories(categories)
    return jsonify({"success": True, "message": "Kategori kaydedildi."})

@app.route('/api/web/categories/<cat_id>', methods=['DELETE'])
def delete_web_category(cat_id):
    if not verify_admin_auth():
        return jsonify({"success": False, "error": "Yetkisiz erişim! Lütfen giriş yapın."}), 401
    categories = load_web_categories()
    categories = [c for c in categories if c.get('id') != cat_id]
    save_web_categories(categories)
    return jsonify({"success": True, "message": "Kategori silindi."})

def load_web_products():
    if os.path.exists(PRODUCTS_FILE):
        try:
            with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_web_products(products):
    with open(PRODUCTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=4)

@app.route('/api/web/products', methods=['GET'])
def get_web_products():
    return jsonify(load_web_products())

@app.route('/api/web/products', methods=['POST'])
def save_web_product():
    if not verify_admin_auth():
        return jsonify({"success": False, "error": "Yetkisiz erişim! Lütfen giriş yapın."}), 401
    import time
    products = load_web_products()
    prod_id = request.form.get('id')
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'İçecekler & Tatlılar').strip()
    description = request.form.get('description', '').strip()
    price = request.form.get('price', '').strip()
    is_signature = request.form.get('is_signature', 'false').lower() in ['true', '1', 'on']
    is_active = request.form.get('is_active', 'true').lower() in ['true', '1', 'on']
    tags_raw = request.form.get('tags', '')
    tags = [t.strip() for t in tags_raw.split(',') if t.strip()]

    image_url = request.form.get('image_url', '').strip()
    if 'image_file' in request.files:
        img = request.files['image_file']
        if img and img.filename:
            ext = img.filename.split('.')[-1].lower() if '.' in img.filename else 'png'
            fname = f"prod_{int(time.time())}.{ext}"
            fpath = os.path.join('/opt/firinna-pos/web', fname)
            img.save(fpath)
            image_url = fname

    if not prod_id:
        new_prod = {
            "id": f"prod_{int(time.time()*1000)}",
            "title": title,
            "category": category,
            "description": description,
            "price": price,
            "image_url": image_url or "drink_cay.png",
            "is_signature": is_signature,
            "is_active": is_active,
            "tags": tags
        }
        products.append(new_prod)
    else:
        found = False
        for p in products:
            if p.get('id') == prod_id:
                p['title'] = title
                p['category'] = category
                p['description'] = description
                p['price'] = price
                if image_url:
                    p['image_url'] = image_url
                p['is_signature'] = is_signature
                p['is_active'] = is_active
                p['tags'] = tags
                found = True
                break
        if not found:
            return jsonify({"success": False, "error": "Ürün bulunamadı."})

    save_web_products(products)
    return jsonify({"success": True, "message": "Ürün başarıyla kaydedildi."})

@app.route('/api/web/products/<prod_id>/toggle-active', methods=['POST'])
def toggle_web_product_active(prod_id):
    if not verify_admin_auth():
        return jsonify({"success": False, "error": "Yetkisiz erişim! Lütfen giriş yapın."}), 401
    products = load_web_products()
    for p in products:
        if p.get('id') == prod_id:
            p['is_active'] = not p.get('is_active', True)
            save_web_products(products)
            return jsonify({"success": True, "is_active": p['is_active']})
    return jsonify({"success": False, "error": "Ürün bulunamadı."})

@app.route('/api/web/products/<prod_id>/toggle-signature', methods=['POST'])
def toggle_product_signature(prod_id):
    if not verify_admin_auth():
        return jsonify({"success": False, "error": "Yetkisiz erişim! Lütfen giriş yapın."}), 401
    products = load_web_products()
    found = False
    new_state = False
    for p in products:
        if p.get('id') == prod_id:
            p['is_signature'] = not p.get('is_signature', False)
            new_state = p['is_signature']
            found = True
            break
    if not found:
        return jsonify({"success": False, "error": "Ürün bulunamadı."})
    save_web_products(products)
    return jsonify({"success": True, "is_signature": new_state})

@app.route('/api/web/products/<prod_id>', methods=['DELETE'])
def delete_web_product(prod_id):
    if not verify_admin_auth():
        return jsonify({"success": False, "error": "Yetkisiz erişim! Lütfen giriş yapın."}), 401
    products = load_web_products()
    products = [p for p in products if p.get('id') != prod_id]
    save_web_products(products)
    return jsonify({"success": True, "message": "Ürün silindi."})

@app.route('/api/web/upload-gallery-photo', methods=['POST'])
def upload_gallery_photo():
    slot = request.form.get('slot')
    if not slot or 'file' not in request.files:
        return jsonify({"success": False, "error": "Geçersiz istek"})
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "Dosya seçilmedi"})
        
    from werkzeug.utils import secure_filename
    slot = secure_filename(slot)
    if not slot: slot = "default"
    filename = f"gallery_{slot}.jpg"
    filepath = os.path.join('/opt/firinna-pos/web', filename)
    file.save(filepath)
    return jsonify({"success": True, "filename": filename})

IP_GEO_CACHE = {}

def get_ip_location(ip):
    if not ip or ip in ['127.0.0.1', 'Gizli IP', 'localhost']:
        return "📍 İstanbul / Türkiye (Yerel)"
    if ip in IP_GEO_CACHE:
        return IP_GEO_CACHE[ip]
    try:
        import urllib.request
        req = urllib.request.urlopen(f'http://ip-api.com/json/{ip}?fields=status,country,city,regionName', timeout=1.5)
        res = json.loads(req.read().decode('utf-8'))
        if res.get('status') == 'success':
            city = res.get('city') or res.get('regionName') or ''
            country = res.get('country') or ''
            loc_str = f"📍 {city} / {country}" if city else f"📍 {country}"
            IP_GEO_CACHE[ip] = loc_str
            return loc_str
    except Exception:
        pass
    IP_GEO_CACHE[ip] = "🌐 Bilinmeyen Konum"
    return IP_GEO_CACHE[ip]

import time
RATE_LIMIT_STORE = {}

def check_rate_limit(ip, endpoint, max_requests, window_seconds):
    now = time.time()
    key = f"{ip}_{endpoint}"
    if key not in RATE_LIMIT_STORE:
        RATE_LIMIT_STORE[key] = []
    RATE_LIMIT_STORE[key] = [t for t in RATE_LIMIT_STORE[key] if now - t < window_seconds]
    if len(RATE_LIMIT_STORE[key]) >= max_requests:
        return False
    RATE_LIMIT_STORE[key].append(now)
    return True

@app.route('/api/web/track-visit', methods=['POST'])
def track_visit():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    if not check_rate_limit(ip, 'track', max_requests=20, window_seconds=60):
        return jsonify({"success": False, "error": "Rate limit exceeded"}), 429
        
    analytics_file = '/opt/firinna-pos/web_analytics.json'
    try:
        if os.path.exists(analytics_file):
            with open(analytics_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
        else:
            stats = {
                "today": 0, "month": 0, "total": 0, "menu": 0, "actions": 0, "last_date": "",
                "devices": {"Mobil": 0, "Masaüstü": 0},
                "browsers": {},
                "countries": {},
                "locations": {},
                "traffic_sources": {},
                "store_modes": {},
                "lang_comparisons": {},
                "referrers": {"Direkt Giriş": 0, "Google": 0, "Instagram": 0, "Diğer": 0}
            }
            
        import datetime
        today_str = datetime.date.today().isoformat()
        
        if stats.get("last_date") != today_str:
            stats["today"] = 0
            if stats.get("last_date", "")[:7] != today_str[:7]:
                stats["month"] = 0
            stats["last_date"] = today_str
            
        data = request.json or {}
        event = data.get('event', 'pageview')
        
        # IP & Zaman tespiti
        visitor_ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
        if not visitor_ip or visitor_ip == '127.0.0.1':
            visitor_ip = request.remote_addr or 'Gizli IP'
            
        now_dt = datetime.datetime.now()
        months_tr = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
        time_str = f"{now_dt.day} {months_tr[now_dt.month - 1]} {now_dt.strftime('%H:%M')}"
        
        # Cihaz & İşletim Sistemi Tespiti
        ua = data.get('userAgent', '').lower()
        if 'ipad' in ua or 'tablet' in ua:
            device_type = "📱 Tablet"
        elif 'mobi' in ua or 'android' in ua or 'iphone' in ua:
            device_type = "📱 Mobil"
        else:
            device_type = "💻 Masaüstü"
            
        os_name = "Diğer Sistem"
        if 'iphone' in ua or 'ipad' in ua: os_name = "Apple iOS"
        elif 'android' in ua: os_name = "Android OS"
        elif 'windows' in ua: os_name = "Windows PC"
        elif 'mac os' in ua or 'macintosh' in ua: os_name = "Apple macOS"
        elif 'linux' in ua: os_name = "Linux"
            
        # Tarayıcı Tespiti
        browser = "Diğer Tarayıcı"
        if 'instagram' in ua: browser = "Instagram App"
        elif 'edg' in ua: browser = "Microsoft Edge"
        elif 'chrome' in ua: browser = "Google Chrome"
        elif 'safari' in ua: browser = "Apple Safari"
        elif 'firefox' in ua: browser = "Mozilla Firefox"
        
        # Dil / Ülke / Konum Tespiti
        geo_location = get_ip_location(visitor_ip)
        
        # Pazarlama Kaynağı (Traffic Channels)
        ref = (data.get('referrer') or '').lower()
        url_query = (data.get('urlQuery') or '').lower()
        
        if 'src=qr' in url_query or 'table=' in url_query or 'qr' in ref:
            traffic_source = "📲 Masa QR Kodu (Dükkan İçi)"
            store_mode = "🏪 Masada Oturan Müşteri"
        elif 'g.page' in ref or 'maps.google' in ref or 'google.com/maps' in ref:
            traffic_source = "🗺️ Google Haritalar"
            store_mode = "🌐 Dışarıdan İnceleyen"
        elif 'google' in ref:
            traffic_source = "🔍 Google Arama (SEO)"
            store_mode = "🌐 Dışarıdan İnceleyen"
        elif 'instagram' in ref:
            traffic_source = "📸 Instagram Bio Link"
            store_mode = "🌐 Dışarıdan İnceleyen"
        elif ref == '' or ref == 'direct':
            traffic_source = "🔗 Doğrudan (Direct)"
            store_mode = "🌐 Dışarıdan İnceleyen"
        else:
            traffic_source = "🌐 Diğer Web Sitesi"
            store_mode = "🌐 Dışarıdan İnceleyen"

        # Kalma Süresi & Kaydırma Derinliği & Dil Karşılaştırması
        scroll_depth = data.get('scrollDepth', 0)
        time_spent_sec = data.get('timeSpentSeconds', 0)
        user_device_lang = (data.get('language') or 'tr').upper()[:2]
        selected_menu_lang = (data.get('selectedLanguage') or 'tr').upper()[:2]
        lang_compare_str = f"{user_device_lang} ➔ {selected_menu_lang}"

        # Ziyaret Tipi
        is_repeat = data.get('isRepeat', False)
        visitor_type = "🔄 Tekrar Gelen Misafir" if is_repeat else "✨ Yeni Ziyaretçi"

        # Peak Hours (Giriş Saati Aralığı)
        hour = now_dt.hour
        if 8 <= hour < 11: hour_slot = "08:00 - 11:00 (Sabah Kahvaltı)"
        elif 11 <= hour < 14: hour_slot = "11:00 - 14:00 (Öğle Brunch)"
        elif 14 <= hour < 17: hour_slot = "14:00 - 17:00 (İkindi Kahve/Tatlı)"
        elif 17 <= hour < 20: hour_slot = "17:00 - 20:00 (Akşam Yemeği)"
        elif 20 <= hour < 23: hour_slot = "20:00 - 23:00 (Gece Keyfi)"
        else: hour_slot = "23:00 - 08:00 (Gece / Erken)"

        item_raw = str(data.get('item', ''))
        if 'Gezi Rehberi' in item_raw:
            hotel_txt = data.get('hotelName') or data.get('startPoint') or 'Merkezi Başlangıç Hub'
            reg_txt = data.get('selectedRegion') or 'Galata'
            time_txt = data.get('selectedTime') or 'Yarım Gün'
            action_name = f"🗺️ Gezi Rotası Oluşturdu (Otel/Konum: {hotel_txt} | Bölge: {reg_txt})"

            # Telegram Canlı Bildirimi Gönder
            try:
                import telegram_notify
                tg_msg = (
                    f"🗺️ <b>YENİ İSTANBUL GEZİ ROTASI OLUŞTURULDU!</b>\n\n"
                    f"🏨 <b>Otel / Konum:</b> {hotel_txt}\n"
                    f"🗺️ <b>Seçilen Bölge:</b> {reg_txt}\n"
                    f"⏱️ <b>Süre:</b> {time_txt}\n"
                    f"📍 <b>Ziyaretçi Konumu:</b> {geo_location} ({visitor_ip})\n"
                    f"📱 <b>Cihaz:</b> {device_type} ({os_name})\n"
                    f"⏰ <b>Zaman:</b> {time_str}"
                )
                telegram_notify.send_async(tg_msg)
            except Exception as e:
                print(f"[Gezi Track TG Error]: {e}")
        elif event == 'menu': action_name = "📄 PDF Menü İndirme"
        elif event == 'action': action_name = "💬 WhatsApp / İletişim"
        elif event == 'map': action_name = "🗺️ Harita / Navigasyon Niyeti"
        elif event == 'duration_update': action_name = f"⏱️ Sitede Kalma ({time_spent_sec}s)"
        elif event == 'pageview': action_name = "👁️ Sayfa Görüntüleme"
        elif event == 'item':
            item_name = data.get('item', 'Özel Lezzet')
            action_name = f"🍽️ Ürün İnceleme ({item_name})"
            stats.setdefault("menu_interests", {})[item_name] = stats.get("menu_interests", {}).get(item_name, 0) + 1

        # Ziyaretçi Günlükleri
        recent = stats.setdefault("recent_visitors", [])
        recent.insert(0, {
            "id": f"log_{int(now_dt.timestamp()*1000)}",
            "time": time_str,
            "iso_date": now_dt.strftime("%Y-%m-%d"),
            "raw_time": now_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "ip": visitor_ip,
            "country": geo_location,
            "location": geo_location,
            "traffic_source": traffic_source,
            "store_mode": store_mode,
            "device": f"{device_type} ({os_name})",
            "browser": browser,
            "action": action_name,
            "type": visitor_type,
            "scroll_depth": f"%{scroll_depth}",
            "time_spent": f"{time_spent_sec} sn",
            "lang_compare": lang_compare_str
        })
        stats["recent_visitors"] = recent[:5000]

        # Sadece yeni bir sayfa görüntülemesinde sayaçları artır
        if event == 'pageview':
            stats["today"] += 1
            stats["month"] += 1
            stats["total"] += 1
            
            if is_repeat:
                stats["repeat_visitors"] = stats.get("repeat_visitors", 0) + 1
            else:
                stats["new_visitors"] = stats.get("new_visitors", 0) + 1
                
            stats.setdefault("devices", {})[device_type] = stats.get("devices", {}).get(device_type, 0) + 1
            stats.setdefault("os", {})[os_name] = stats.get("os", {}).get(os_name, 0) + 1
            stats.setdefault("browsers", {})[browser] = stats.get("browsers", {}).get(browser, 0) + 1
            stats.setdefault("locations", {})[geo_location] = stats.get("locations", {}).get(geo_location, 0) + 1
            stats.setdefault("traffic_sources", {})[traffic_source] = stats.get("traffic_sources", {}).get(traffic_source, 0) + 1
            stats.setdefault("store_modes", {})[store_mode] = stats.get("store_modes", {}).get(store_mode, 0) + 1
            stats.setdefault("lang_comparisons", {})[lang_compare_str] = stats.get("lang_comparisons", {}).get(lang_compare_str, 0) + 1
            stats.setdefault("peak_hours", {})[hour_slot] = stats.get("peak_hours", {}).get(hour_slot, 0) + 1
            stats.setdefault("referrers", {})[traffic_source] = stats.get("referrers", {}).get(traffic_source, 0) + 1
            
        elif event == 'menu':
            stats["menu"] = stats.get("menu", 0) + 1
        elif event == 'action':
            stats["actions"] = stats.get("actions", 0) + 1
        elif event == 'map':
            stats["map_clicks"] = stats.get("map_clicks", 0) + 1
            
        with open(analytics_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=4, ensure_ascii=False)
            
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/web/analytics', methods=['GET'])
def get_analytics():
    analytics_file = '/opt/firinna-pos/web_analytics.json'
    if os.path.exists(analytics_file):
        with open(analytics_file, 'r') as f:
            response = jsonify(json.load(f))
    else:
        response = jsonify({"today": 0, "month": 0, "total": 0, "menu": 0, "actions": 0})
        
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

@app.route('/api/web/tables-status', methods=['GET'])
def api_web_tables_status():
    try:
        tables = [t for t in db.get_tables() if 'takeaway' not in t.get('name', '').lower() and 'paket' not in t.get('name', '').lower()]
        empty_count = 0
        total_count = len(tables)
        for t in tables:
            order = db.get_table_order(t['id'])
            if not order:
                empty_count += 1
        return jsonify({'success': True, 'total': total_count, 'empty': empty_count})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/web/contact', methods=['POST'])
def api_web_contact():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    if not check_rate_limit(ip, 'contact', max_requests=3, window_seconds=60):
        return jsonify({'success': False, 'error': 'Çok fazla istek gönderdiniz, lütfen bekleyin.'}), 429
    try:
        data = request.json
        msg = f"📩 <b>Web'den Yeni Mesaj</b>\n\n👤 İsim: {data.get('name')}\n📞 Telefon: {data.get('phone')}\n💬 Mesaj: {data.get('message')}"
        telegram_notify.send_async(msg)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/web/reservation', methods=['POST'])
def api_web_reservation():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0].strip()
    if not check_rate_limit(ip, 'contact', max_requests=3, window_seconds=60):
        return jsonify({'success': False, 'error': 'Çok fazla istek gönderdiniz, lütfen bekleyin.'}), 429
    try:
        data = request.json
        msg = f"📅 <b>Web'den Masa Rezervasyonu Talebi</b>\n\n👤 İsim: {data.get('name')}\n📞 Telefon: {data.get('phone')}\n🗓 Tarih: {data.get('date')} - {data.get('time')}\n👥 Kişi: {data.get('guests')}\n📝 Not: {data.get('note', '-')}"
        telegram_notify.send_async(msg)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/<path:filename>')
def serve_web_static(filename):
    """Serve static files from web directory (for port 5000 access)"""
    import os
    web_path = os.path.join(os.path.dirname(__file__), 'web', filename)
    if os.path.isfile(web_path):
        return send_from_directory('web', filename)
    # Fall through to other routes / 404
    from flask import abort
    abort(404)


import os
import json
from datetime import datetime
import threading

_tv_settings_lock = threading.Lock()
TV_SETTINGS_FILE = os.path.join(os.path.dirname(__file__), 'tv_settings.json')
TV_MEDIA_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'tv_media')
os.makedirs(os.path.join(TV_MEDIA_FOLDER, 'videos'), exist_ok=True)
os.makedirs(os.path.join(TV_MEDIA_FOLDER, 'audio'), exist_ok=True)

import tempfile
import time

def get_tv_settings():
    with _tv_settings_lock:
        if os.path.exists(TV_SETTINGS_FILE):
            for _ in range(3):
                try:
                    with open(TV_SETTINGS_FILE, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if not data.get('logo_url'):
                            data['logo_url'] = db.get_setting('logo_url', '')
                        if 'playlist_videos' not in data:
                            data['playlist_videos'] = data.get('local_videos', [])
                        
                        # Ensure all physical video files + bayrak.mp4 are in local_videos
                        v_dir = os.path.join(TV_MEDIA_FOLDER, 'videos')
                        server_videos = []
                        if os.path.exists(v_dir):
                            server_videos = [f"/static/tv_media/videos/{v}" for v in sorted(os.listdir(v_dir)) if v.endswith(('.mp4', '.webm', '.ogg'))]
                        all_sync_videos = list(dict.fromkeys(server_videos + [
                            "/static/tv_media/videos/bayrak.mp4"
                        ]))
                        data['local_videos'] = all_sync_videos
                        return data
                except Exception:
                    time.sleep(0.05)
        return {
            "logo_url": db.get_setting('logo_url', ''),
            "layout": "modern_grid",
            "video_playlist": "",
            "playlist_videos": ["/static/tv_media/videos/istanbul.mp4"],
            "local_videos": ["/static/tv_media/videos/bayrak.mp4"],
            "local_audio": [],
            "media_source": "local",
            "audio_priority": "video",
            "ticker_text_enabled": True,
            "ticker_currency_enabled": True,
            "ticker_rss_enabled": True,
            "promo_text": "",
            "qr_code": "",
            "qr_text": "",
            "celebration": {
                "active": False,
                "title": "İyi ki Doğdun!",
                "subtitle": "Fırınna Ailesi Olarak Nice Mutlu Yıllara Dileriz! 🎂🎉",
                "image_url": "",
                "effects": {"balloons": True, "fireworks": True, "confetti": True}
            },
            "widgets": {"weather": True, "clock": True},
            "messages": [],
            "last_ping": None
        }

def save_tv_settings(data):
    with _tv_settings_lock:
        dir_name = os.path.dirname(TV_SETTINGS_FILE) or '.'
        with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False, encoding='utf-8') as tf:
            json.dump(data, tf, ensure_ascii=False, indent=4)
            temp_name = tf.name
        os.replace(temp_name, TV_SETTINGS_FILE)

@app.route('/api/tv/settings', methods=['GET', 'POST'])
def api_tv_settings():
    if request.method == 'POST':
        data = request.json or {}
        current = get_tv_settings()
        
        # When admin sends active playlist in local_videos or playlist_videos
        if 'playlist_videos' in data:
            current['playlist_videos'] = data['playlist_videos']
        elif 'local_videos' in data:
            current['playlist_videos'] = data['local_videos']
            
        current.update(data)
        
        # Keep local_videos filled with all available server videos + bayrak.mp4
        v_dir = os.path.join(TV_MEDIA_FOLDER, 'videos')
        server_videos = []
        if os.path.exists(v_dir):
            server_videos = [f"/static/tv_media/videos/{v}" for v in sorted(os.listdir(v_dir)) if v.endswith(('.mp4', '.webm', '.ogg'))]
        all_sync_videos = list(dict.fromkeys(server_videos + [
            "/static/tv_media/videos/bayrak.mp4"
        ]))
        current['local_videos'] = all_sync_videos
        
        now_ts = int(datetime.now().timestamp() * 1000)
        current['version'] = now_ts
        current['last_push'] = {
            "action": "clear_cache",
            "target": "all",
            "timestamp": now_ts
        }
        save_tv_settings(current)
        return jsonify({"success": True, "version": current['version'], "pushed": current['last_push']})
    return jsonify(get_tv_settings())

# In-memory TV clients registry: { client_id: { ip, device_type, user_agent, last_ping, name } }
_tv_clients = {}

@app.route('/api/tv/ping', methods=['GET', 'POST'])
def api_tv_ping():
    data = {}
    try:
        if request.is_json:
            data = request.get_json(silent=True) or {}
    except Exception:
        pass
    
    user_agent = request.headers.get('User-Agent', '')
    # Get real client IP when behind Nginx reverse proxy
    ip_addr = request.headers.get('X-Forwarded-For', request.headers.get('X-Real-IP', request.remote_addr))
    if ip_addr and ',' in ip_addr:
        ip_addr = ip_addr.split(',')[0].strip()
    if not ip_addr:
        ip_addr = request.remote_addr

    # Auto-detect device type if not provided
    ua_lower = user_agent.lower()
    if 'android' in ua_lower and 'tv' in ua_lower:
        detected_type = '📺 Android TV'
    elif 'android' in ua_lower or 'mobile' in ua_lower or 'iphone' in ua_lower:
        detected_type = '📱 Mobil (Telefon/Tablet)'
    else:
        detected_type = '💻 Web / Masaüstü'

    device_type = data.get('device_type') or detected_type
    screen_name = data.get('name', 'Ekran')
    
    # Deterministic client_id fallback if missing
    client_id = data.get('client_id')
    if not client_id or client_id == 'unknown':
        import hashlib
        raw_key = f"{ip_addr}_{user_agent}"
        client_id = f"tv_{hashlib.md5(raw_key.encode()).hexdigest()[:8]}"

    # Deduplicate: if another entry has the SAME IP and device_type, clean it up so physical devices are never duplicated
    for old_cid, old_info in list(_tv_clients.items()):
        if old_cid != client_id and old_info.get('ip') == ip_addr and old_info.get('device_type') == device_type:
            del _tv_clients[old_cid]

    _tv_clients[client_id] = {
        'client_id': client_id,
        'ip': ip_addr,
        'device_type': device_type,
        'name': screen_name,
        'user_agent': user_agent,
        'last_ping': datetime.now().isoformat(),
        'last_ping_ts': time.time()
    }
    
    return jsonify({"success": True, "client_id": client_id})

@app.route('/api/tv/clients', methods=['GET'])
def api_tv_clients():
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
    return jsonify({"clients": active_list})

@app.route('/api/tv/clients/clean', methods=['POST'])
def api_tv_clients_clean():
    now_ts = time.time()
    for cid, info in list(_tv_clients.items()):
        if (now_ts - info.get('last_ping_ts', 0)) >= 45:
            del _tv_clients[cid]
    return jsonify({"success": True, "remaining": len(_tv_clients)})

@app.route('/api/tv/push', methods=['POST'])
def api_tv_push():
    data = request.json or {}
    action = data.get('action', 'reload') # 'reload', 'sync', 'clear_cache'
    target_client_id = data.get('client_id', 'all') # 'all' or specific client_id
    
    current = get_tv_settings()
    current['last_push'] = {
        'action': action,
        'target': target_client_id,
        'timestamp': int(datetime.now().timestamp() * 1000)
    }
    save_tv_settings(current)
    return jsonify({"success": True, "pushed": current['last_push']})

# ==============================================================
# AUTO SCHEDULED HARDWARE REBOOT BACKGROUND WORKER (Mi TV Stick)
# ==============================================================
_last_auto_reboot_date = ""

def _auto_reboot_worker():
    global _last_auto_reboot_date
    import subprocess
    import shutil
    while True:
        try:
            time.sleep(30)
            settings = get_tv_settings()
            auto_reb = settings.get('auto_reboot') or {}
            if not auto_reb.get('enabled'):
                continue
                
            scheduled_time = auto_reb.get('time', '04:30').strip()
            now = datetime.now()
            current_hm = now.strftime('%H:%M')
            today_str = now.strftime('%Y-%m-%d')
            
            if current_hm == scheduled_time and _last_auto_reboot_date != today_str:
                _last_auto_reboot_date = today_str
                # Find connected Android TV client IP
                adb_bin = shutil.which('adb') or '/usr/bin/adb'
                if not os.path.exists(adb_bin):
                    continue
                    
                target_ips = set()
                for cid, info in list(_tv_clients.items()):
                    ip = info.get('ip', '')
                    dev = info.get('device_type', '')
                    if ip and not ip.startswith('127.') and ('Android' in dev or 'TV' in dev):
                        target_ips.add(ip)
                        
                for tip in target_ips:
                    try:
                        target_addr = f"{tip}:5555" if ':' not in tip else tip
                        subprocess.run([adb_bin, 'connect', target_addr], capture_output=True, text=True, timeout=6)
                        subprocess.run([adb_bin, '-s', target_addr, 'shell', 'reboot'], capture_output=True, text=True, timeout=5)
                    except Exception:
                        pass
        except Exception:
            pass

_reb_thread = threading.Thread(target=_auto_reboot_worker, daemon=True)
_reb_thread.start()

@app.route('/api/tv/device/reboot', methods=['POST'])
def api_tv_device_reboot():
    data = request.json or {}
    target_ip = data.get('ip', '').strip()
    
    if not target_ip or target_ip.startswith('127.') or target_ip.startswith('localhost'):
        return jsonify({"success": False, "error": "Geçerli bir yerel cihaz IP'si bulunamadı."})
        
    import subprocess
    import shutil
    try:
        adb_bin = shutil.which('adb') or '/usr/bin/adb'
        if not os.path.exists(adb_bin):
            return jsonify({
                "success": False, 
                "error": "Sunucuda ADB kurulu değil. Lütfen terminalde: sudo apt update && sudo apt install -y adb çalıştırın."
            })
            
        # Connect to Mi Stick via TCP/IP port 5555
        target_addr = f"{target_ip}:5555" if ':' not in target_ip else target_ip
        subprocess.run([adb_bin, 'connect', target_addr], capture_output=True, text=True, timeout=6)
        
        # Send reboot command using shell reboot (reliable on Android TV)
        try:
            reb = subprocess.run([adb_bin, '-s', target_addr, 'shell', 'reboot'], capture_output=True, text=True, timeout=5)
            return jsonify({"success": True, "message": f"Mi Stick ({target_addr}) donanımsal olarak baştan başlatılıyor..."})
        except subprocess.TimeoutExpired:
            # Device often closes connection immediately on reboot causing timeout - this is success
            return jsonify({"success": True, "message": f"Mi Stick ({target_addr}) donanımsal olarak baştan başlatılıyor..."})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/tv/rates', methods=['GET'])
def api_tv_rates():
    rates_data = {
        'usd_try': None,
        'eur_try': None,
        'eur_usd': None,
        'btc_usdt': None,
        'eth_usdt': None
    }
    # 1. Fetch TCMB rates (Official Central Bank of Turkey)
    try:
        req = urllib.request.Request('https://www.tcmb.gov.tr/kurlar/today.xml', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            xml_data = resp.read()
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_data)
        for cur in root.findall('Currency'):
            code = cur.get('CurrencyCode')
            if code == 'USD':
                buying = cur.find('ForexBuying')
                if buying is not None and buying.text:
                    rates_data['usd_try'] = round(float(buying.text), 2)
            elif code == 'EUR':
                buying = cur.find('ForexBuying')
                if buying is not None and buying.text:
                    rates_data['eur_try'] = round(float(buying.text), 2)
        if rates_data.get('usd_try') and rates_data.get('eur_try'):
            rates_data['eur_usd'] = round(rates_data['eur_try'] / rates_data['usd_try'], 4)
    except Exception as e:
        print(f"[TV RATES] TCMB fetch error: {e}")

    # Fallback for Forex if TCMB fails
    if not rates_data.get('usd_try'):
        try:
            req = urllib.request.Request('https://open.er-api.com/v6/latest/USD', headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            if data and 'rates' in data:
                usd_try = data['rates'].get('TRY', 0)
                usd_eur = data['rates'].get('EUR', 0)
                if usd_try and usd_eur:
                    rates_data['usd_try'] = round(float(usd_try), 2)
                    rates_data['eur_try'] = round(float(usd_try / usd_eur), 2)
                    rates_data['eur_usd'] = round(float(1 / usd_eur), 4)
        except Exception as e:
            print(f"[TV RATES] Er-api fallback error: {e}")

    # 2. Fetch Crypto (BTC/USDT, ETH/USDT) from Binance API
    try:
        req = urllib.request.Request('https://api.binance.com/api/v3/ticker/price?symbols=["BTCUSDT","ETHUSDT"]', headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            crypto_data = json.loads(resp.read().decode('utf-8'))
        for item in crypto_data:
            if item.get('symbol') == 'BTCUSDT':
                rates_data['btc_usdt'] = round(float(item['price']), 2)
            elif item.get('symbol') == 'ETHUSDT':
                rates_data['eth_usdt'] = round(float(item['price']), 2)
    except Exception as e:
        print(f"[TV RATES] Binance crypto fetch error: {e}")

    return jsonify(rates_data)

_rss_cache = {"key": "", "time": 0, "titles": [], "items": [], "last_updated": ""}

PRESET_FEEDS = {
    "turkey_archaeo": ("🏛️ Tarih & Arkeoloji", "https://news.google.com/rss/search?q=when:7d+turkey+archaeology+OR+arkeoloji+OR+excavation+OR+heritage+OR+unesco&hl=en-US&gl=US&ceid=US:en"),
    "ds_arts_en": ("🎨 Daily Sabah Kültür", "https://www.dailysabah.com/rssFeed/arts"),
    "aa_life_en": ("📜 Anadolu Agency Yaşam", "https://www.aa.com.tr/en/rss/default?cat=life"),
    "turkey_exp_en": ("☕ İstanbul & Kültür", "https://news.google.com/rss/search?q=when:48h+Istanbul+OR+Turkey+culture+OR+arts+OR+events+OR+tourism+OR+heritage&hl=en-US&gl=US&ceid=US:en"),
    "goodnews_en": ("🌱 Good News Network", "https://www.goodnewsnetwork.org/feed/")
}

# Unwanted disaster / crime / war words to maintain pleasant bakery ambience
NEGATIVE_KEYWORDS = [
    'war', 'killed', 'killing', 'dead', 'death', 'strike', 'attack', 'bomb', 'blast',
    'hostage', 'military', 'soldier', 'murder', 'gunman', 'shooting', 'missile',
    'sanctions', 'suicide', 'tragedy', 'casualty', 'disaster', 'crash', 'arrest',
    'gaza', 'israel', 'syria', 'iran', 'palestinian', 'court', 'jail', 'prison',
    'savaş', 'ölü', 'ölüm', 'saldırı', 'bomba', 'patlama', 'cinayet', 'çatışma',
    'kaza', 'facia', 'ceset', 'gözaltı', 'tutuklama', 'rehin', 'yaralı', 'operasyon',
    'netanyahu', 'dictator', 'antisemitic'
]

@app.route('/api/tv/rss', methods=['GET'])
def api_tv_rss():
    global _rss_cache
    import time
    import email.utils
    import xml.etree.ElementTree as ET
    from datetime import datetime
    
    settings = get_tv_settings()
    force_refresh = request.args.get('force') == '1'
    
    # Enabled sources
    enabled_sources = []
    if settings.get('rss_turkey_archaeo_enabled', True):
        enabled_sources.append(('turkey_archaeo', PRESET_FEEDS['turkey_archaeo'][0], PRESET_FEEDS['turkey_archaeo'][1]))
    if settings.get('rss_ds_arts_en_enabled', True):
        enabled_sources.append(('ds_arts_en', PRESET_FEEDS['ds_arts_en'][0], PRESET_FEEDS['ds_arts_en'][1]))
    if settings.get('rss_aa_life_en_enabled', True):
        enabled_sources.append(('aa_life_en', PRESET_FEEDS['aa_life_en'][0], PRESET_FEEDS['aa_life_en'][1]))
    if settings.get('rss_turkey_exp_en_enabled', True):
        enabled_sources.append(('turkey_exp_en', PRESET_FEEDS['turkey_exp_en'][0], PRESET_FEEDS['turkey_exp_en'][1]))
    if settings.get('rss_goodnews_en_enabled', True):
        enabled_sources.append(('goodnews_en', PRESET_FEEDS['goodnews_en'][0], PRESET_FEEDS['goodnews_en'][1]))
        
    custom_url = settings.get('rss_url', '').strip()
    if custom_url and settings.get('rss_custom_enabled', False):
        enabled_sources.append(('custom', '🔗 Özel Kaynak', custom_url))
        
    if not enabled_sources:
        return jsonify({"titles": [], "items": [], "count": 0, "enabled": False})
        
    cache_key = "_".join([s[0] for s in enabled_sources]) + "_" + custom_url
    now = time.time()
    
    # Cache duration: 120 seconds unless force refreshed
    if not force_refresh and _rss_cache.get("key") == cache_key and (now - _rss_cache.get("time", 0) < 120) and _rss_cache.get("items"):
        return jsonify({
            "titles": _rss_cache["titles"],
            "items": _rss_cache["items"],
            "count": len(_rss_cache["items"]),
            "last_updated": _rss_cache.get("last_updated", ""),
            "enabled": True
        })
        
    raw_items = []
    for key_id, label, feed_url in enabled_sources:
        try:
            req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=6) as resp:
                content = resp.read()
                
            if b'<html' in content.lower() or b'<!doctype' in content.lower() or feed_url.endswith('.html'):
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(content.decode('utf-8', errors='ignore'), 'html.parser')
                for a in soup.find_all('a'):
                    txt = a.get_text().strip()
                    if txt and len(txt) > 20 and not txt.startswith(('Feed Informer', 'Widgets', 'Privacy', 'Terms')):
                        if not any(bad in txt.lower() for bad in NEGATIVE_KEYWORDS):
                            raw_items.append({
                                'title': txt,
                                'source': label,
                                'source_id': key_id,
                                'pub_date': '',
                                'ts': now - 3600  # Fallback to 1h ago if HTML widget doesn't have timestamps
                            })
            else:
                root = ET.fromstring(content)
                # Standard RSS items
                for item in root.findall('.//item'):
                    t = item.find('title')
                    d = item.find('pubDate')
                    title = t.text.strip() if t is not None and t.text else ''
                    date_str = d.text.strip() if d is not None and d.text else ''
                    ts = 0
                    if date_str:
                        try:
                            dt = email.utils.parsedate_to_datetime(date_str)
                            ts = dt.timestamp()
                        except Exception:
                            pass
                    if title and len(title) > 10:
                        if not any(bad in title.lower() for bad in NEGATIVE_KEYWORDS):
                            raw_items.append({
                                'title': title,
                                'source': label,
                                'source_id': key_id,
                                'pub_date': date_str,
                                'ts': ts or (now - 7200)
                            })
                # Atom entries fallback
                if len(raw_items) < 5:
                    for item in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                        t = item.find('{http://www.w3.org/2005/Atom}title')
                        d = item.find('{http://www.w3.org/2005/Atom}updated') or item.find('{http://www.w3.org/2005/Atom}published')
                        title = t.text.strip() if t is not None and t.text else ''
                        date_str = d.text.strip() if d is not None and d.text else ''
                        ts = 0
                        if date_str:
                            try:
                                dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                                ts = dt.timestamp()
                            except Exception:
                                pass
                        if title and len(title) > 10:
                            if not any(bad in title.lower() for bad in NEGATIVE_KEYWORDS):
                                raw_items.append({
                                    'title': title,
                                    'source': label,
                                    'source_id': key_id,
                                    'pub_date': date_str,
                                    'ts': ts or (now - 7200)
                                })
        except Exception as e:
            print(f"[RSS ERROR] Failed to fetch {label} ({feed_url}): {e}")
            
    # Deduplicate by title
    unique_items = []
    seen_titles = set()
    for it in raw_items:
        clean = it['title'].strip().lower()
        if clean not in seen_titles:
            seen_titles.add(clean)
            unique_items.append(it)
            
    # Sort chronologically by publication timestamp (newest first)
    unique_items.sort(key=lambda x: x['ts'], reverse=True)
    
    # Strictly take top 20 latest news items (discard all older ones)
    top20_items = unique_items[:20]
    
    # Format publication time and relative time
    formatted_items = []
    for it in top20_items:
        ts = it['ts']
        diff = int(now - ts) if ts else 0
        if diff < 60:
            time_ago = 'Az önce'
        elif diff < 3600:
            time_ago = f'{diff // 60} dk önce'
        elif diff < 86400:
            time_ago = f'{diff // 3600} saat önce'
        else:
            time_ago = f'{diff // 86400} gün önce'
            
        date_formatted = datetime.fromtimestamp(ts).strftime('%d.%m.%Y %H:%M') if ts else 'Belirtilmemiş'
        
        formatted_items.append({
            'title': it['title'],
            'source': it['source'],
            'source_id': it['source_id'],
            'pub_date': date_formatted,
            'time_ago': time_ago,
            'ts': ts
        })
        
    titles_20 = [it['title'] for it in formatted_items]
    last_updated_str = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
    
    _rss_cache = {
        "key": cache_key,
        "time": now,
        "titles": titles_20,
        "items": formatted_items,
        "last_updated": last_updated_str
    }
    
    return jsonify({
        "titles": titles_20,
        "items": formatted_items,
        "count": len(formatted_items),
        "last_updated": last_updated_str,
        "enabled": True
    })

@app.route('/api/tv/products', methods=['GET'])
def get_tv_products():
    try:
        with open('/opt/firinna-pos/web_products.json', 'r', encoding='utf-8') as f:
            products = json.load(f)
        return jsonify(products)
    except Exception as e:
        return jsonify([])

@app.route('/api/tv/products/save', methods=['POST'])
def save_tv_products():
    try:
        products = request.json or []
        with open('/opt/firinna-pos/web_products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, indent=4, ensure_ascii=False)
        return jsonify({"success": True, "count": len(products)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/tv/products/upload', methods=['POST'])
def upload_tv_product_image():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    from werkzeug.utils import secure_filename
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        prod_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads', 'products')
        os.makedirs(prod_dir, exist_ok=True)
        filename = f"prod_{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
        filepath = os.path.join(prod_dir, filename)
        file.save(filepath)
        return jsonify({"success": True, "url": f"/static/uploads/products/{filename}"})

@app.route('/api/tv/facts', methods=['GET'])
def api_tv_facts():
    settings = get_tv_settings()
    facts = settings.get('did_you_know', [])
    return jsonify({
        "facts": facts,
        "count": len(facts),
        "cycle_speed": settings.get('facts_cycle_speed', settings.get('ticker_slide_duration', 8)),
        "enabled": settings.get('ticker_facts_enabled', True)
    })

@app.route('/api/tv/facts/save', methods=['POST'])
def api_tv_facts_save():
    try:
        payload = request.json or {}
        facts = payload.get('facts', [])
        settings = get_tv_settings()
        settings['did_you_know'] = facts
        if 'cycle_speed' in payload:
            speed = int(payload['cycle_speed'])
            settings['facts_cycle_speed'] = speed
            settings['ticker_slide_duration'] = speed
        if 'enabled' in payload:
            settings['ticker_facts_enabled'] = bool(payload['enabled'])
        save_tv_settings(settings)
        return jsonify({"success": True, "count": len(facts), "cycle_speed": settings.get('facts_cycle_speed', 8)})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/tv/facts/export', methods=['GET'])
def api_tv_facts_export():
    import csv
    import io
    settings = get_tv_settings()
    facts = settings.get('did_you_know', [])
    fmt = request.args.get('format', 'csv').lower()

    if fmt == 'json':
        response = make_response(json.dumps(facts, ensure_ascii=False, indent=4))
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        response.headers['Content-Disposition'] = 'attachment; filename=firinna_tv_facts.json'
        return response

    # Default: UTF-8 BOM CSV (Excel Compatible)
    si = io.StringIO()
    # Write UTF-8 BOM so Excel opens Turkish/Arabic/Russian correctly
    si.write('\ufeff')
    writer = csv.writer(si, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([
        'ID', 'Ikon', 'Renk', 'Durum', 
        'Baslik_EN', 'Metin_EN', 
        'Baslik_ES', 'Metin_ES', 
        'Baslik_RU', 'Metin_RU', 
        'Baslik_AR', 'Metin_AR'
    ])
    for f in facts:
        writer.writerow([
            f.get('id', ''),
            f.get('icon', '🏛️'),
            f.get('color', '#0F172A'),
            'Aktif' if f.get('enabled', True) else 'Pasif',
            f.get('title_en', f.get('title', '')),
            f.get('text_en', f.get('text', '')),
            f.get('title_es', ''),
            f.get('text_es', ''),
            f.get('title_ru', ''),
            f.get('text_ru', ''),
            f.get('title_ar', ''),
            f.get('text_ar', '')
        ])
    
    output = make_response(si.getvalue().encode('utf-8-sig'))
    output.headers['Content-Type'] = 'text/csv; charset=utf-8'
    output.headers['Content-Disposition'] = 'attachment; filename=firinna_tv_bilgiler.csv'
    return output

@app.route('/api/tv/facts/import', methods=['POST'])
def api_tv_facts_import():
    import csv
    import io
    try:
        if 'file' not in request.files:
            return jsonify({"success": False, "error": "Dosya seçilmedi"}), 400
        file = request.files['file']
        if not file.filename:
            return jsonify({"success": False, "error": "Geçersiz dosya"}), 400

        content = file.read()
        imported_facts = []

        if file.filename.endswith('.json'):
            raw_text = content.decode('utf-8')
            parsed = json.loads(raw_text)
            if isinstance(parsed, list):
                imported_facts = parsed
            elif isinstance(parsed, dict) and 'facts' in parsed:
                imported_facts = parsed['facts']
        else:
            # CSV processing with multiple encoding support
            decoded = None
            for enc in ['utf-8-sig', 'utf-8', 'cp1254', 'iso-8859-9', 'latin-1']:
                try:
                    decoded = content.decode(enc)
                    break
                except UnicodeDecodeError:
                    continue
            if not decoded:
                decoded = content.decode('utf-8', errors='ignore')

            # Detect delimiter (; or , or \t)
            sample_line = decoded.splitlines()[0] if decoded.splitlines() else ''
            delimiter = ';' if ';' in sample_line else (',' if ',' in sample_line else '\t')
            
            reader = csv.reader(io.StringIO(decoded), delimiter=delimiter)
            rows = list(reader)
            if len(rows) > 0:
                header = [h.strip().lower() for h in rows[0]]
                data_rows = rows[1:]
                for idx, row in enumerate(data_rows):
                    if not row or len(row) < 3 or not any(row):
                        continue
                    
                    # Match columns or fallback to position
                    fid = row[0].strip() if len(row) > 0 and row[0].strip() else f"dyk_import_{int(time.time())}_{idx}"
                    ficon = row[1].strip() if len(row) > 1 and row[1].strip() else '🏛️'
                    fcolor = row[2].strip() if len(row) > 2 and row[2].strip() else '#0F172A'
                    fenabled = (row[3].strip().lower() in ['aktif', 'true', '1', 'yes', 'evet', '']) if len(row) > 3 else True
                    
                    ftitle_en = row[4].strip() if len(row) > 4 else ''
                    ftext_en = row[5].strip() if len(row) > 5 else ''
                    ftitle_es = row[6].strip() if len(row) > 6 else ''
                    ftext_es = row[7].strip() if len(row) > 7 else ''
                    ftitle_ru = row[8].strip() if len(row) > 8 else ''
                    ftext_ru = row[9].strip() if len(row) > 9 else ''
                    ftitle_ar = row[10].strip() if len(row) > 10 else ''
                    ftext_ar = row[11].strip() if len(row) > 11 else ''

                    imported_facts.append({
                        "id": fid,
                        "icon": ficon,
                        "color": fcolor,
                        "enabled": fenabled,
                        "title_en": ftitle_en,
                        "text_en": ftext_en,
                        "title_es": ftitle_es,
                        "text_es": ftext_es,
                        "title_ru": ftitle_ru,
                        "text_ru": ftext_ru,
                        "title_ar": ftitle_ar,
                        "text_ar": ftext_ar
                    })

        if not imported_facts:
            return jsonify({"success": False, "error": "İçe aktarılacak geçerli bilgi bulunamadı."}), 400

        mode = request.form.get('mode', 'replace') # 'replace' or 'append'
        settings = get_tv_settings()
        if mode == 'append':
            existing = settings.get('did_you_know', [])
            existing_ids = {f.get('id') for f in existing}
            for nf in imported_facts:
                if nf.get('id') not in existing_ids:
                    existing.append(nf)
            settings['did_you_know'] = existing
        else:
            settings['did_you_know'] = imported_facts

        save_tv_settings(settings)
        return jsonify({
            "success": True, 
            "count": len(settings['did_you_know']), 
            "imported": len(imported_facts),
            "message": f"Başarıyla {len(imported_facts)} adet bilgi içe aktarıldı!"
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"İçe aktarma hatası: {str(e)}"}), 400

@app.route('/api/tv/celebration', methods=['GET'])
def api_tv_celebration():
    settings = get_tv_settings()
    return jsonify(settings.get('celebration', {
        "active": False,
        "title": "İyi ki Doğdun!",
        "subtitle": "Fırınna Ailesi Olarak Nice Mutlu Yıllara Dileriz! 🎂🎉",
        "image_url": "",
        "effects": {"balloons": True, "fireworks": True, "confetti": True}
    }))

@app.route('/api/tv/celebration/save', methods=['POST'])
def api_tv_celebration_save():
    try:
        payload = request.json or {}
        settings = get_tv_settings()
        settings['celebration'] = payload
        save_tv_settings(settings)
        return jsonify({"success": True, "celebration": settings['celebration']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/tv/night_media/upload', methods=['POST'])
def api_upload_tv_night_media():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    from werkzeug.utils import secure_filename
    file = request.files['file']
    media_type = request.form.get('type', 'image') # 'video' or 'image'
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        folder = 'videos' if media_type == 'video' else 'images'
        night_dir = os.path.join(os.path.dirname(__file__), 'static', 'tv_media', 'night', folder)
        os.makedirs(night_dir, exist_ok=True)
        filename = f"night_{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
        filepath = os.path.join(night_dir, filename)
        file.save(filepath)
        return jsonify({"success": True, "url": f"/static/tv_media/night/{folder}/{filename}"})

@app.route('/api/tv/after_hours/save', methods=['POST'])
@app.route('/api/tv/night_mode/save', methods=['POST'])
def api_tv_after_hours_save():
    try:
        payload = request.json or {}
        settings = get_tv_settings()
        settings['after_hours'] = payload
        settings['night_mode'] = payload
        save_tv_settings(settings)
        return jsonify({"success": True, "after_hours": settings['after_hours']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/api/tv/media', methods=['GET'])
def api_get_tv_media():
    videos = os.listdir(os.path.join(TV_MEDIA_FOLDER, 'videos'))
    audio = os.listdir(os.path.join(TV_MEDIA_FOLDER, 'audio'))
    return jsonify({
        "videos": ["/static/tv_media/videos/" + v for v in videos if v.endswith(('.mp4', '.webm', '.ogg'))],
        "audio": ["/static/tv_media/audio/" + a for a in audio if a.endswith(('.mp3', '.wav', '.ogg'))]
    })

@app.route('/api/tv/watermark/upload', methods=['POST'])
def api_upload_tv_watermark():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    from werkzeug.utils import secure_filename
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        wm_dir = os.path.join(os.path.dirname(__file__), 'static', 'img', 'watermarks')
        os.makedirs(wm_dir, exist_ok=True)
        filename = f"wm_{int(datetime.now().timestamp())}_{secure_filename(file.filename)}"
        filepath = os.path.join(wm_dir, filename)
        file.save(filepath)
        return jsonify({"success": True, "url": f"/static/img/watermarks/{filename}"})

@app.route('/api/tv/media/upload', methods=['POST'])
def api_upload_tv_media():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    from werkzeug.utils import secure_filename
    file = request.files['file']
    type_ = request.form.get('type', 'video')
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        folder = 'videos' if type_ == 'video' else 'audio'
        file.save(os.path.join(TV_MEDIA_FOLDER, folder, filename))
        return jsonify({"success": True})

@app.route('/api/tv/media/delete', methods=['POST'])
def api_delete_tv_media():
    data = request.json
    raw_filename = data.get('filename', '')
    type_ = data.get('type', 'video')
    if raw_filename:
        from werkzeug.utils import secure_filename
        filename = secure_filename(raw_filename)
        if not filename:
            return jsonify({"success": False, "error": "Geçersiz dosya adı."}), 400
        # Protect core fallback video (bayrak.mp4) from deletion
        if filename.lower() == 'bayrak.mp4':
            return jsonify({"success": False, "error": f"{filename} sistemin kalıcı ana fallback videosudur ve silinemez."}), 400
            
        folder = 'videos' if type_ == 'video' else 'audio'
        filepath = os.path.join(TV_MEDIA_FOLDER, folder, filename)
        # Verify resolved path is within TV_MEDIA_FOLDER
        real_path = os.path.realpath(filepath)
        if not real_path.startswith(os.path.realpath(TV_MEDIA_FOLDER)):
            return jsonify({"success": False, "error": "Geçersiz dosya yolu."}), 400
        if os.path.exists(filepath):
            os.remove(filepath)
            return jsonify({"success": True})
    return jsonify({"success": False, "error": "File not found"}), 404

@app.route('/tv-admin')
def tv_admin():
    return render_template('tv_admin.html', settings=get_tv_settings())

@app.route('/tv-player')
def tv_player():
    return render_template('tv_player.html', settings=get_tv_settings())

@app.route('/tv')
def tv_redirect():
    return render_template('tv_player.html', settings=get_tv_settings())

# ==============================================================================
# 📻 RADYO & MERKEZİ MÜZİK ÇALAR SİSTEMİ (WEB & TV SENKRON)
# ==============================================================================
MUSIC_LIBRARY_DIR = '/home/turan/firinna_music_library'
RADIO_DATA_FILE = os.path.join(os.path.dirname(__file__), 'radio_settings.json')
os.makedirs(MUSIC_LIBRARY_DIR, exist_ok=True)

_radio_lock = threading.Lock()

DEFAULT_RADIO_STATIONS = [
    {"id": "tr_powerfm", "name": "Power FM", "country": "TR", "country_name": "Türkiye", "genre": "Pop / Hit", "url": "https://listen.powerapp.com.tr/powerfm/mpeg/icecast.audio", "logo": "🇹🇷"},
    {"id": "tr_slowturk", "name": "Slow Türk", "country": "TR", "country_name": "Türkiye", "genre": "Türkçe Slow", "url": "https://radyo.duhnet.tv/slowturk", "logo": "🇹🇷"},
    {"id": "tr_powerturk", "name": "Power Türk", "country": "TR", "country_name": "Türkiye", "genre": "Türkçe Pop", "url": "https://listen.powerapp.com.tr/powerturk/mpeg/icecast.audio", "logo": "🇹🇷"},
    {"id": "ua_hitfm", "name": "Hit FM Ukraine", "country": "UA", "country_name": "Ukrayna", "genre": "Pop / Dance", "url": "https://online.hitfm.ua/HitFM_HD", "logo": "🇺🇦"},
    {"id": "ua_roks", "name": "Radio ROKS", "country": "UA", "country_name": "Ukrayna", "genre": "Classic Rock", "url": "https://online.radioroks.ua/RadioROKS_HD", "logo": "🇺🇦"},
    {"id": "ua_relax", "name": "Radio Relax Ukraine", "country": "UA", "country_name": "Ukrayna", "genre": "Lounge / Relax", "url": "https://online.radiorelax.ua/RadioRelax_HD", "logo": "🇺🇦"},
    {"id": "ua_kissfm", "name": "Kiss FM Ukraine", "country": "UA", "country_name": "Ukrayna", "genre": "EDM / Dance", "url": "https://online.kissfm.ua/KissFM_HD", "logo": "🇺🇦"},
    {"id": "eu_swissjazz", "name": "Radio Swiss Jazz", "country": "EU", "country_name": "İsviçre / Avrupa", "genre": "Jazz / Soul / Blues", "url": "https://stream.srg-ssr.ch/m/rsj/mp3_128", "logo": "🇨🇭"},
    {"id": "eu_swissclassic", "name": "Radio Swiss Classic", "country": "EU", "country_name": "İsviçre / Avrupa", "genre": "Classical Music", "url": "https://stream.srg-ssr.ch/m/rsc_de/mp3_128", "logo": "🇨🇭"},
    {"id": "eu_ibiza", "name": "Ibiza Global Radio", "country": "EU", "country_name": "İspanya / Ibiza", "genre": "Deep House / Electronic", "url": "https://listenssl.ibizaglobalradio.com:8024/ibizaglobalradio.mp3", "logo": "🇪🇸"},
    {"id": "eu_fip", "name": "FIP Radio Paris", "country": "EU", "country_name": "Fransa", "genre": "Eclectic / World / Jazz", "url": "https://icecast.radiofrance.fr/fip-midfi.mp3", "logo": "🇫🇷"},
    {"id": "eu_paradise", "name": "Radio Paradise (Main Mix)", "country": "EU", "country_name": "Global / US", "genre": "Acoustic / Rock / World", "url": "https://stream.radioparadise.com/mp3-128", "logo": "🌴"},
    {"id": "eu_paradise_mellow", "name": "Radio Paradise (Mellow Mix)", "country": "EU", "country_name": "Global / US", "genre": "Mellow / Chillout", "url": "https://stream.radioparadise.com/mellow-128", "logo": "🌿"},
    {"id": "us_somafm_groove", "name": "SomaFM: Groove Salad", "country": "US", "country_name": "ABD", "genre": "Downtempo / Ambient", "url": "https://ice1.somafm.com/groovesalad-128-mp3", "logo": "🇺🇸"},
    {"id": "us_somafm_secret", "name": "SomaFM: Secret Agent", "country": "US", "country_name": "ABD", "genre": "Spy / Lounge / Surf", "url": "https://ice1.somafm.com/secretagent-128-mp3", "logo": "🇺🇸"},
    {"id": "us_181_chill", "name": "181.fm Chilled Out", "country": "US", "country_name": "ABD", "genre": "Lounge / Smooth Chill", "url": "https://listen.181fm.com/181-chilled_128k.mp3", "logo": "🇺🇸"},
    {"id": "us_181_acoustic", "name": "181.fm The Breeze (Acoustic)", "country": "US", "country_name": "ABD", "genre": "Acoustic Soft Rock", "url": "https://listen.181fm.com/181-breeze_128k.mp3", "logo": "🇺🇸"},
    {"id": "us_kexp", "name": "KEXP 90.3 FM Seattle", "country": "US", "country_name": "ABD", "genre": "Indie / Alternative", "url": "https://kexp.streamguys1.com/kexp128.mp3", "logo": "🇺🇸"},
]

def load_radio_data():
    with _radio_lock:
        if os.path.exists(RADIO_DATA_FILE):
            try:
                with open(RADIO_DATA_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'stations' not in data or not data['stations']:
                        data['stations'] = DEFAULT_RADIO_STATIONS
                    if 'custom_stations' not in data:
                        data['custom_stations'] = []
                    if 'playlists' not in data:
                        data['playlists'] = []
                    if 'state' not in data:
                        data['state'] = {
                            "is_playing": False,
                            "mode": "sequential", # "sequential" or "shuffle"
                            "source_type": "station", # "station", "playlist", "folder"
                            "current_title": "Hazır",
                            "current_url": "",
                            "current_item_id": "",
                            "queue": [],
                            "queue_index": 0,
                            "tv_audio_enabled": False,
                            "updated_at": int(time.time())
                        }
                    return data
            except Exception:
                pass
        # Default fresh state
        return {
            "stations": DEFAULT_RADIO_STATIONS,
            "custom_stations": [],
            "playlists": [],
            "state": {
                "is_playing": False,
                "mode": "sequential",
                "source_type": "station",
                "current_title": "Power FM",
                "current_url": "https://listen.powerapp.com.tr/powerfm/mpeg/icecast.audio",
                "current_item_id": "tr_powerfm",
                "queue": [],
                "queue_index": 0,
                "tv_audio_enabled": False,
                "updated_at": int(time.time())
            }
        }

def save_radio_data(data):
    with _radio_lock:
        dir_name = os.path.dirname(RADIO_DATA_FILE) or '.'
        with tempfile.NamedTemporaryFile('w', dir=dir_name, delete=False, encoding='utf-8') as tf:
            json.dump(data, tf, ensure_ascii=False, indent=2)
            temp_name = tf.name
        os.replace(temp_name, RADIO_DATA_FILE)

AUDIO_EXTENSIONS = ('.mp3', '.m4a', '.aac', '.flac', '.wav', '.ogg')

def scan_music_library():
    """Recursively scans /home/turan/firinna_music_library and groups files by directories"""
    root_path = os.path.realpath(MUSIC_LIBRARY_DIR)
    folders_dict = {}
    all_tracks = []
    
    if not os.path.exists(root_path):
        os.makedirs(root_path, exist_ok=True)
        return {"folders": [], "all_tracks": [], "total_tracks": 0}

    for root, dirs, files in os.walk(root_path):
        dirs.sort()
        rel_dir = os.path.relpath(root, root_path)
        folder_display_name = "Ana Müzik Klasörü" if rel_dir == "." else rel_dir.replace(os.path.sep, " / ")
        
        folder_tracks = []
        for file in sorted(files):
            if file.lower().endswith(AUDIO_EXTENSIONS):
                rel_file_path = os.path.relpath(os.path.join(root, file), root_path)
                track_title = os.path.splitext(file)[0].replace('_', ' ')
                track_info = {
                    "filename": file,
                    "rel_path": rel_file_path.replace('\\', '/'),
                    "title": track_title,
                    "folder": folder_display_name,
                    "stream_url": f"/api/radio/stream/{urllib.parse.quote(rel_file_path.replace(os.path.sep, '/'))}"
                }
                folder_tracks.append(track_info)
                all_tracks.append(track_info)

        if folder_tracks:
            folders_dict[rel_dir] = {
                "folder_key": rel_dir.replace('\\', '/'),
                "name": folder_display_name,
                "count": len(folder_tracks),
                "tracks": folder_tracks
            }

    folders_list = list(folders_dict.values())
    return {
        "folders": folders_list,
        "all_tracks": all_tracks,
        "total_tracks": len(all_tracks)
    }

_stream_meta_cache = {}
_stream_meta_fetching = set()

def _async_fetch_live_title(url):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 'Icy-MetaData': '1'})
        with urllib.request.urlopen(req, timeout=3.0) as response:
            headers = dict(response.info())
            metaint_val = headers.get('icy-metaint')
            if metaint_val:
                metaint = int(metaint_val)
                response.read(metaint)
                raw_len = response.read(1)
                if raw_len:
                    metadata_len = raw_len[0] * 16 if isinstance(raw_len, bytes) else ord(raw_len) * 16
                    if metadata_len > 0:
                        metadata = response.read(metadata_len).decode('utf-8', errors='ignore')
                        match = re.search(r"StreamTitle='([^']*)';", metadata)
                        if match and match.group(1).strip():
                            _stream_meta_cache[url] = (match.group(1).strip(), time.time())
    except Exception:
        pass
    finally:
        _stream_meta_fetching.discard(url)

def get_live_stream_title_fast(url):
    """Returns cached title instantly; triggers background fetch if cache expired or missing"""
    if not url or not url.startswith('http'):
        return None
    now = time.time()
    cached_title = None
    if url in _stream_meta_cache:
        title, ts = _stream_meta_cache[url]
        if now - ts < 30: # 30 saniye geçerli önbellek
            return title
        cached_title = title

    # Arka planda asenkron yenile (asla API'yi veya sarmayı bloklamaz)
    if url not in _stream_meta_fetching:
        _stream_meta_fetching.add(url)
        threading.Thread(target=_async_fetch_live_title, args=(url,), daemon=True).start()

    return cached_title

def _get_audio_env():
    env = dict(os.environ)
    uid = 1000
    try:
        u = os.getuid()
        if u != 0:
            uid = u
    except Exception:
        pass
    env['XDG_RUNTIME_DIR'] = f'/run/user/{uid}'
    env['PULSE_SERVER'] = f'unix:/run/user/{uid}/pulse/native'
    env['PATH'] = f"{env.get('PATH', '')}:/usr/bin:/usr/local/bin:/bin:/usr/sbin:/sbin"
    return env

def get_system_volume():
    env = _get_audio_env()
    for cmd in [
        ['/usr/bin/amixer', '-c', '0', 'sget', 'PCM'],
        ['amixer', '-c', '0', 'sget', 'PCM'],
        ['/usr/bin/pactl', 'get-sink-volume', '@DEFAULT_SINK@'],
        ['pactl', 'get-sink-volume', '@DEFAULT_SINK@'],
        ['/usr/bin/amixer', 'get', 'Master'],
        ['amixer', 'get', 'Master'],
        ['/usr/bin/amixer', 'get', 'Headphone'],
        ['amixer', 'get', 'Headphone']
    ]:
        try:
            out = subprocess.check_output(cmd, env=env, stderr=subprocess.DEVNULL, universal_newlines=True)
            m = re.search(r'(?:\[|\s)(\d+)%', out)
            if m:
                return int(m.group(1))
        except Exception:
            continue
    return 80

def set_system_volume(volume):
    try:
        vol = max(0, min(100, int(volume)))
    except (ValueError, TypeError):
        vol = 80
    env = _get_audio_env()
    
    # Raspberry Pi ALSA card 0 PCM control
    for amixer_bin in ['/usr/bin/amixer', 'amixer']:
        try:
            subprocess.run([amixer_bin, '-c', '0', 'sset', 'PCM', f'{vol}%', 'unmute'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
        for ctrl in ['Master', 'Headphone', 'PCM', 'Speaker']:
            try:
                subprocess.run([amixer_bin, 'set', ctrl, f'{vol}%', 'unmute'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    for pactl_bin in ['/usr/bin/pactl', 'pactl']:
        try:
            subprocess.run([pactl_bin, 'set-sink-volume', '@DEFAULT_SINK@', f'{vol}%'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run([pactl_bin, 'set-sink-mute', '@DEFAULT_SINK@', '0' if vol > 0 else '1'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            try:
                out = subprocess.check_output([pactl_bin, 'list', 'sink-inputs', 'short'], env=env, text=True, stderr=subprocess.DEVNULL)
                for line in out.strip().splitlines():
                    if line:
                        input_id = line.split()[0]
                        subprocess.run([pactl_bin, 'set-sink-input-volume', input_id, '100%'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        subprocess.run([pactl_bin, 'set-sink-input-mute', input_id, '0' if vol > 0 else '1'], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass
            break
        except Exception:
            pass

    return vol

# ==================== LOCAL AUDIO PLAYBACK ENGINE (RPI HARDWARE AUX JACK) ====================
PLAYER_PID_FILE = '/tmp/firinna_audio_player.pid'
PLAYER_LOCK_FILE = '/tmp/firinna_audio_player.lock'
MONITOR_LOCK_FILE = '/tmp/firinna_audio_monitor.lock'

def _stop_all_audio_processes():
    try:
        if os.path.exists(PLAYER_PID_FILE):
            with open(PLAYER_PID_FILE, 'r') as f:
                pid_str = f.read().strip()
                if pid_str.isdigit():
                    pid = int(pid_str)
                    try:
                        os.kill(pid, signal.SIGTERM)
                        time.sleep(0.05)
                        if os.path.exists(f"/proc/{pid}"):
                            os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    except Exception:
                        pass
            try:
                os.remove(PLAYER_PID_FILE)
            except Exception:
                pass
    except Exception:
        pass
    # Safety sweep: kill any leftover mpv with our signature
    try:
        subprocess.run(['pkill', '-9', '-f', 'mpv.*--ao=alsa'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['pkill', '-9', '-f', 'cvlc.*--network-caching'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

def sync_local_audio_player():
    try:
        with open(PLAYER_LOCK_FILE, 'w') as lock_f:
            fcntl.flock(lock_f, fcntl.LOCK_EX)
            try:
                data = load_radio_data()
                state = data.get('state', {})
                is_playing = state.get('is_playing', False)
                current_url = state.get('current_url', '')

                target_url = current_url
                if target_url.startswith('/api/radio/stream/'):
                    rel_file = urllib.parse.unquote(target_url.replace('/api/radio/stream/', ''))
                    disk_path = os.path.realpath(os.path.join(MUSIC_LIBRARY_DIR, rel_file))
                    if os.path.exists(disk_path):
                        target_url = disk_path
                    else:
                        target_url = f"http://127.0.0.1:5000{target_url}"

                # Always stop existing player first so NO duplicate sound is ever possible
                _stop_all_audio_processes()

                if is_playing and target_url:
                    env = _get_audio_env()
                    proc = None
                    if os.path.exists('/usr/bin/mpv'):
                        proc = subprocess.Popen(
                            [
                                '/usr/bin/mpv',
                                '--no-video',
                                '--ao=alsa',
                                '--audio-device=alsa/default',
                                '--cache=yes',
                                '--demuxer-max-bytes=16M',
                                '--demuxer-readahead-secs=20',
                                '--audio-buffer=0.4',
                                target_url
                            ],
                            env=env,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL
                        )
                    elif os.path.exists('/usr/bin/cvlc'):
                        proc = subprocess.Popen(
                            ['/usr/bin/cvlc', '--no-video', '--network-caching=2000', target_url],
                            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                    elif os.path.exists('/usr/bin/ffplay'):
                        proc = subprocess.Popen(
                            ['/usr/bin/ffplay', '-nodisp', '-nostats', '-loglevel', 'quiet', target_url],
                            env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                    
                    if proc and proc.pid:
                        with open(PLAYER_PID_FILE, 'w') as pf:
                            pf.write(str(proc.pid))
                        print(f"[Radio Engine] (PID {proc.pid}) Playing: {target_url}", flush=True)
                else:
                    print("[Radio Engine] Playback stopped.", flush=True)
            finally:
                fcntl.flock(lock_f, fcntl.LOCK_UN)
    except Exception as e:
        print(f"[Radio Engine] sync_local_audio_player error: {e}", flush=True)

def _local_player_monitor_loop():
    # Only ONE Gunicorn worker acquires this non-blocking lock to act as supervisor
    lock_file = None
    try:
        lock_file = open(MONITOR_LOCK_FILE, 'w')
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except (IOError, BlockingIOError):
        return

    print("[Radio Engine] Single supervisor monitor active.", flush=True)
    while True:
        try:
            time.sleep(2)
            data = load_radio_data()
            state = data.get('state', {})
            if state.get('is_playing') and state.get('source_type') in ('folder', 'playlist'):
                pid = None
                if os.path.exists(PLAYER_PID_FILE):
                    try:
                        with open(PLAYER_PID_FILE, 'r') as f:
                            pid_str = f.read().strip()
                            if pid_str.isdigit():
                                pid = int(pid_str)
                    except Exception:
                        pass
                
                # If song process ended naturally, advance to next
                if pid is not None and not os.path.exists(f"/proc/{pid}"):
                    print(f"[Radio Engine] Track PID {pid} finished naturally, advancing...", flush=True)
                    _advance_next_track()
        except Exception:
            pass

def _advance_next_track():
    try:
        data = load_radio_data()
        state = data.get('state', {})
        queue = state.get('queue', [])
        if queue:
            idx = state.get('queue_index', 0)
            mode = state.get('mode', 'sequential')
            if mode == 'shuffle' and len(queue) > 1:
                import random
                next_idx = random.randint(0, len(queue) - 1)
            else:
                next_idx = (idx + 1) % len(queue)
            state['queue_index'] = next_idx
            cur = queue[next_idx]
            state['current_title'] = cur.get('title') or cur.get('name') or "Müzik"
            state['current_url'] = cur.get('stream_url') or cur.get('url') or ""
            state['current_item_id'] = cur.get('rel_path') or cur.get('id') or ""
            state['is_playing'] = True
            state['updated_at'] = int(time.time())
            data['state'] = state
            save_radio_data(data)
            sync_local_audio_player()
    except Exception as e:
        print(f"[Radio Engine] Advance track error: {e}", flush=True)

threading.Thread(target=_local_player_monitor_loop, daemon=True).start()

@app.route('/radio')
def radio_page():
    return render_template('radio_admin.html')

@app.route('/api/radio/status', methods=['GET'])
def api_radio_status():
    data = load_radio_data()
    state = dict(data.get('state', {}))
    state['volume'] = get_system_volume()
    
    if state.get('source_type') == 'spotify':
        try:
            from spotify_integration import get_valid_access_token
            token = get_valid_access_token()
            if token:
                s_res = requests.get('https://api.spotify.com/v1/me/player', headers={'Authorization': f'Bearer {token}'}, timeout=1.5)
                if s_res.status_code == 200 and s_res.text:
                    s_data = s_res.json()
                    if s_data.get('is_playing'):
                        state['is_playing'] = True
                        it = s_data.get('item') or {}
                        artists = ", ".join([a.get('name') for a in it.get('artists', [])])
                        track_name = it.get('name', 'Spotify Müzik')
                        state['display_title'] = f"🟢 {track_name} - {artists}"
                        state['current_title'] = f"{track_name} - {artists}"
        except Exception:
            pass
    elif state.get('is_playing') and state.get('source_type') == 'station':
        live_title = get_live_stream_title_fast(state.get('current_url'))
        if live_title:
            state['live_track_title'] = live_title
            base_name = state.get('current_title', '').split(' - ')[0].split(' (')[0]
            state['display_title'] = f"{base_name}: {live_title}"
    return jsonify(state)

@app.route('/api/radio/volume', methods=['GET', 'POST'])
def api_radio_volume():
    if request.method == 'POST':
        req = request.json or {}
        vol = req.get('volume', 80)
        actual_vol = set_system_volume(vol)
        data = load_radio_data()
        state = data.get('state', {})
        state['volume'] = actual_vol
        state['updated_at'] = int(time.time())
        data['state'] = state
        save_radio_data(data)
        return jsonify({"success": True, "volume": actual_vol})
    else:
        return jsonify({"volume": get_system_volume()})

@app.route('/api/radio/control', methods=['POST'])
def api_radio_control():
    req = request.json or {}
    data = load_radio_data()
    state = data.get('state', {})
    
    action = req.get('action') # 'play', 'pause', 'play_station', 'play_track', 'play_queue', 'next', 'prev', 'toggle_mode', 'toggle_tv_audio'
    
    if action == 'play':
        state['is_playing'] = True
    elif action == 'pause':
        state['is_playing'] = False
    elif action == 'set_volume':
        vol = req.get('volume', 80)
        actual_vol = set_system_volume(vol)
        state['volume'] = actual_vol
    elif action == 'toggle_mode':
        current_mode = state.get('mode', 'sequential')
        state['mode'] = 'shuffle' if current_mode == 'sequential' else 'sequential'
    elif action == 'toggle_tv_audio':
        state['tv_audio_enabled'] = not state.get('tv_audio_enabled', True)
    elif action == 'play_station':
        st_id = req.get('station_id')
        all_st = data.get('stations', []) + data.get('custom_stations', [])
        st = next((s for s in all_st if s.get('id') == st_id), None)
        if st:
            state['is_playing'] = True
            state['source_type'] = 'station'
            state['current_title'] = st.get('name')
            state['current_url'] = st.get('url')
            state['current_item_id'] = st.get('id')
            state['queue'] = [st]
            state['queue_index'] = 0
    elif action == 'play_queue':
        items = req.get('items', [])
        start_idx = req.get('start_index', 0)
        source_type = req.get('source_type', 'folder')
        title_prefix = req.get('title_prefix', '')
        
        if items:
            state['is_playing'] = True
            state['source_type'] = source_type
            state['queue'] = items
            
            mode = state.get('mode', 'sequential')
            if mode == 'shuffle' and len(items) > 1:
                import random
                chosen = items[start_idx] if 0 <= start_idx < len(items) else items[0]
                rest = [it for it in items if it != chosen]
                random.shuffle(rest)
                state['queue'] = [chosen] + rest
                state['queue_index'] = 0
            else:
                state['queue_index'] = max(0, min(start_idx, len(items) - 1))
                
            cur = state['queue'][state['queue_index']]
            state['current_title'] = cur.get('title') or cur.get('name') or "Müzik"
            if title_prefix:
                state['current_title'] = f"{title_prefix} - {state['current_title']}"
            state['current_url'] = cur.get('stream_url') or cur.get('url') or ""
            state['current_item_id'] = cur.get('rel_path') or cur.get('id') or ""
    elif action == 'next':
        queue = state.get('queue', [])
        if queue:
            idx = state.get('queue_index', 0)
            mode = state.get('mode', 'sequential')
            if mode == 'shuffle' and len(queue) > 1:
                import random
                next_idx = random.randint(0, len(queue) - 1)
            else:
                next_idx = (idx + 1) % len(queue)
            state['queue_index'] = next_idx
            cur = queue[next_idx]
            state['current_title'] = cur.get('title') or cur.get('name') or "Müzik"
            state['current_url'] = cur.get('stream_url') or cur.get('url') or ""
            state['current_item_id'] = cur.get('rel_path') or cur.get('id') or ""
            state['is_playing'] = True
    elif action == 'prev':
        queue = state.get('queue', [])
        if queue:
            idx = state.get('queue_index', 0)
            prev_idx = (idx - 1 + len(queue)) % len(queue)
            state['queue_index'] = prev_idx
            cur = queue[prev_idx]
            state['current_title'] = cur.get('title') or cur.get('name') or "Müzik"
            state['current_url'] = cur.get('stream_url') or cur.get('url') or ""
            state['current_item_id'] = cur.get('rel_path') or cur.get('id') or ""
            state['is_playing'] = True

    state['updated_at'] = int(time.time())
    data['state'] = state
    save_radio_data(data)
    threading.Thread(target=sync_local_audio_player, daemon=True).start()
    return jsonify({"success": True, "state": state})

@app.route('/api/radio/stations', methods=['GET', 'POST'])
def api_radio_stations():
    data = load_radio_data()
    if request.method == 'POST':
        req = request.json or {}
        action = req.get('action', 'add')
        custom = data.get('custom_stations', [])
        if action == 'add':
            name = req.get('name', '').strip()
            url = req.get('url', '').strip()
            genre = req.get('genre', 'Genel').strip()
            country = req.get('country', 'Özel').strip()
            if not name or not url:
                return jsonify({"success": False, "error": "İstasyon adı ve URL zorunludur"}), 400
            new_st = {
                "id": f"custom_{int(time.time()*1000)}",
                "name": name,
                "country": "CUSTOM",
                "country_name": country,
                "genre": genre,
                "url": url,
                "logo": "📻",
                "is_custom": True
            }
            custom.append(new_st)
            data['custom_stations'] = custom
            save_radio_data(data)
            return jsonify({"success": True, "station": new_st})
        elif action == 'delete':
            st_id = req.get('station_id')
            data['custom_stations'] = [s for s in custom if s.get('id') != st_id]
            save_radio_data(data)
            return jsonify({"success": True})

    return jsonify({
        "stations": data.get('stations', DEFAULT_RADIO_STATIONS),
        "custom_stations": data.get('custom_stations', [])
    })

@app.route('/api/radio/library', methods=['GET'])
def api_radio_library():
    return jsonify(scan_music_library())

@app.route('/api/radio/upload', methods=['POST'])
def api_radio_upload():
    """Accepts individual audio files or entire folder trees via relative paths"""
    print(f"[DEBUG] Request content_type: {request.content_type}")
    print(f"[DEBUG] Request form keys: {list(request.form.keys())}")
    print(f"[DEBUG] Request files keys: {list(request.files.keys())}")
    
    files = request.files.getlist('files') or request.files.getlist('file')
    if not files or len(files) == 0:
        print("[DEBUG] No files found in request.files")
        return jsonify({"success": False, "error": "Yüklenecek dosya seçilmedi"}), 400

    target_folder_param = request.form.get('target_folder', '').strip()
    paths_param_raw = request.form.get('paths', '[]')
    try:
        paths_list = json.loads(paths_param_raw)
    except Exception:
        paths_list = []

    saved_count = 0
    errors = []

    for idx, file_storage in enumerate(files):
        if not file_storage or file_storage.filename == '':
            continue
            
        # Get relative path either from paths list or filename
        raw_rel_path = paths_list[idx] if idx < len(paths_list) else file_storage.filename
        
        # If user specified target_folder and path is single file
        if target_folder_param and ('/' not in raw_rel_path.replace('\\', '/')):
            raw_rel_path = f"{target_folder_param}/{raw_rel_path}"

        path_parts = [p.strip() for p in raw_rel_path.replace('\\', '/').split('/') if p.strip() and p not in ('.', '..')]
        if not path_parts:
            continue
            
        # Keep clean directory names and filename
        clean_parts = []
        for part in path_parts:
            # Replace risky characters while preserving Turkish chars and spaces
            cleaned = "".join(c for c in part if c not in '/\\:*?"<>|').strip()
            if not cleaned:
                cleaned = "unnamed"
            clean_parts.append(cleaned)

        target_filename = clean_parts[-1]
        if not target_filename.lower().endswith(AUDIO_EXTENSIONS):
            continue
            
        target_dir = os.path.join(MUSIC_LIBRARY_DIR, *clean_parts[:-1]) if len(clean_parts) > 1 else MUSIC_LIBRARY_DIR
        os.makedirs(target_dir, exist_ok=True)
        
        full_dest = os.path.join(target_dir, target_filename)
        try:
            file_storage.save(full_dest)
            saved_count += 1
        except Exception as e:
            errors.append(f"{raw_rel_path}: {str(e)}")

    return jsonify({
        "success": True,
        "saved_count": saved_count,
        "errors": errors,
        "library": scan_music_library()
    })

@app.route('/api/radio/delete_file', methods=['POST'])
def api_radio_delete_file():
    req = request.json or {}
    rel_path = req.get('rel_path', '')
    if not rel_path:
        return jsonify({"success": False, "error": "Dosya yolu belirtilmedi"}), 400
    
    full_path = os.path.realpath(os.path.join(MUSIC_LIBRARY_DIR, rel_path))
    if not full_path.startswith(os.path.realpath(MUSIC_LIBRARY_DIR)):
        return jsonify({"success": False, "error": "Geçersiz dosya konumu"}), 400
        
    if os.path.exists(full_path):
        try:
            if os.path.isfile(full_path):
                os.remove(full_path)
            elif os.path.isdir(full_path):
                import shutil
                shutil.rmtree(full_path)
            return jsonify({"success": True})
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
            
    return jsonify({"success": False, "error": "Dosya bulunamadı"}), 404

@app.route('/api/radio/playlists', methods=['GET', 'POST'])
def api_radio_playlists():
    data = load_radio_data()
    playlists = data.get('playlists', [])
    
    if request.method == 'POST':
        req = request.json or {}
        action = req.get('action', 'save')
        
        if action == 'save':
            pl_id = req.get('id') or f"pl_{int(time.time()*1000)}"
            name = req.get('name', 'Yeni Liste').strip()
            items = req.get('items', []) # list of track objects or stations
            
            existing = next((p for p in playlists if p.get('id') == pl_id), None)
            if existing:
                existing['name'] = name
                existing['items'] = items
                existing['count'] = len(items)
                existing['updated_at'] = int(time.time())
            else:
                playlists.append({
                    "id": pl_id,
                    "name": name,
                    "items": items,
                    "count": len(items),
                    "created_at": int(time.time()),
                    "updated_at": int(time.time())
                })
            data['playlists'] = playlists
            save_radio_data(data)
            return jsonify({"success": True, "playlists": playlists})
            
        elif action == 'delete':
            pl_id = req.get('id')
            data['playlists'] = [p for p in playlists if p.get('id') != pl_id]
            save_radio_data(data)
            return jsonify({"success": True, "playlists": data['playlists']})

    return jsonify({"playlists": playlists})

@app.route('/api/radio/stream/<path:filename>')
def api_radio_stream(filename):
    """Secure range-supporting audio streaming from outside project directory"""
    safe_path = os.path.realpath(os.path.join(MUSIC_LIBRARY_DIR, filename))
    if not safe_path.startswith(os.path.realpath(MUSIC_LIBRARY_DIR)):
        from flask import abort
        abort(403)
    if not os.path.isfile(safe_path):
        from flask import abort
        abort(404)
        
    directory = os.path.dirname(safe_path)
    file_name = os.path.basename(safe_path)
    resp = make_response(send_from_directory(directory, file_name))
    resp.headers['Accept-Ranges'] = 'bytes'
    resp.headers['Cache-Control'] = 'public, max-age=86400'
    return resp



if __name__ == '__main__':
    db.init_db()
    try: db.init_muhasebe_tables()
    except: pass
    try: db.migrate_product_stock_link()
    except: pass
    try: db.migrate_orders_to_transactions()
    except: pass
    try: db.init_telegram_contacts()
    except: pass
    # Auto-pull başlat (local config'e göre)
    try:
        start_auto_pull_smart()
    except:
        pass
    # Auto-push başlat
    start_auto_push()
    # Telegram günlük otomatik gönderim
    try:
        db.migrate_is_available()
    except:
        pass
    try:
        start_telegram_auto_send()
    except:
        pass
        
    try:
        import auto_webp
        auto_webp.convert_to_webp('/opt/firinna-pos/web')
    except Exception as e:
        print("Auto WebP Error:", e)
        
    

    app.run(host='0.0.0.0', port=5000, debug=False)
