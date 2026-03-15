from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
import database as db
import telegram_notify
from printer import ThermalPrinter
import os
import json
import subprocess
import threading
import time
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

APP_VERSION = "1.2.0"
APP_BUILD   = "2026-03-09"

# DB migration — __name__ kontrolü olmadan her başlangıçta çalışır
try:
    db.init_db()
    db.migrate_product_stock_link()
except Exception as _e:
    print(f"Startup migration warning: {_e}")

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ana sayfa (masalar görünümü)
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
    return render_template('index.html')

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
    )
    return jsonify({'success': True})

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
        if mtype == 'in':
            db.add_stock_purchase(item_id, d['quantity'], d.get('cost', 0),
                                  d.get('payment_method', 'cash'), d.get('description', ''))
        else:
            db.add_stock_movement(item_id, mtype, d['quantity'],
                                  d.get('cost', 0), d.get('reason', 'manuel'), d.get('description', ''))
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

@app.route('/reports')
def reports_page():
    return render_template('reports.html')

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
    order_id = db.create_order(table_id)
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
            data.get('subcategory', '')
        )
        return jsonify({'success': True})

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
    import subprocess, os
    try:
        db.backup_database()
        dump_path = db.dump_database_sql()
        base = os.path.dirname(db.DB_PATH)
        subprocess.run(['git', '-C', base, 'add', 'db_export.sql'], capture_output=True, timeout=30)
        r = subprocess.run(['git', '-C', base, 'commit', '-m',
            f'db sync {datetime.now().strftime("%Y-%m-%d %H:%M")}'],
            capture_output=True, text=True, timeout=30)
        subprocess.run(['git', '-C', base, 'push'], capture_output=True, timeout=60)
        return jsonify({'success': True, 'message': "Veritabani GitHub'a gonderildi."})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/backup/sync-pull', methods=['POST'])
def api_backup_sync_pull():
    import subprocess, os
    try:
        base = os.path.dirname(db.DB_PATH)
        subprocess.run(['git', '-C', base, 'pull'], capture_output=True, text=True, timeout=60)
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
    db.close_order_with_payment(
        order_id,
        data.get('payment_cash', 0),
        data.get('payment_card', 0),
        data.get('tip_amount', 0),
        data.get('tip_method', 'cash')
    )
    db.deduct_stock_for_order(order_id)
    telegram_notify.check_low_stock_after_order(order_id)
    return jsonify({'success': True})

@app.route('/api/orders/<int:order_id>/split', methods=['POST'])
def api_split_order(order_id):
    data = request.json
    per_person = db.split_order_equal(order_id, data['num_people'])
    return jsonify({'per_person': per_person})

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

@app.route('/api/products/search', methods=['GET'])
def api_search_products():
    query = request.args.get('q', '')
    products = db.search_products(query)
    return jsonify(products)

@app.route('/api/orders/history', methods=['GET'])
def api_order_history():
    date = request.args.get('date')
    limit = int(request.args.get('limit', 50))
    orders = db.get_closed_orders(date, limit)
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
    # Toplam yeniden hesapla
    total = conn.execute('''
        SELECT COALESCE(SUM(CASE WHEN is_complimentary=0 THEN quantity*price ELSE 0 END),0) as t
        FROM order_items WHERE order_id=?
    ''', (order_id,)).fetchone()['t']
    conn.execute('''UPDATE orders SET status='closed', total=?, closed_at=CURRENT_TIMESTAMP,
        payment_cash=?, payment_card=?, tip_amount=?
        WHERE id=?''',
        (total, d.get('payment_cash',0), d.get('payment_card',0), d.get('tip_amount',0), order_id))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'total': total})

# ===== ÖN MUHASEBE (#50) =====

@app.route('/backup')
def backup_page():
    return render_template('backup.html')

@app.route('/muhasebe')
def page_muhasebe():
    return render_template('muhasebe.html')

@app.route('/reports')
def page_reports_redirect():
    return redirect('/muhasebe')

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

    return jsonify(data)

# ===== NOT QR =====

@app.route('/api/settings/note-qr', methods=['POST'])
def api_upload_note_qr():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'Dosya yok'}), 400
    file = request.files['file']
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Desteklenmeyen format'}), 400
    ext = file.filename.rsplit('.', 1)[1].lower()
    filename = f'note_qr.{ext}'
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    for old_ext in ALLOWED_EXTENSIONS:
        old_path = os.path.join(UPLOAD_FOLDER, f'note_qr.{old_ext}')
        if os.path.exists(old_path) and old_ext != ext:
            os.remove(old_path)
    file.save(filepath)
    qr_url = f'/static/uploads/{filename}'
    db.set_setting('note_qr_image_url', qr_url)
    label = request.form.get('label', '')
    if label:
        db.set_setting('note_qr_label', label)
    return jsonify({'success': True, 'url': qr_url})

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
    qr_url = db.get_setting('note_qr_image_url', '')
    if qr_url:
        filepath = os.path.join(os.path.dirname(__file__), qr_url.lstrip('/'))
        if os.path.exists(filepath):
            os.remove(filepath)
        db.set_setting('note_qr_image_url', '')
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
    try:
        result = subprocess.run(
            ['/usr/bin/git'] + args,
            cwd=GIT_DIR,
            capture_output=True, text=True, timeout=timeout
        )
        out = (result.stdout + result.stderr).strip()
        return result.returncode == 0, out
    except subprocess.TimeoutExpired:
        return False, 'Zaman aşımı (30s)'
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
    """GitHub'tan tam yeniden kurulum — git yoksa clone, varsa hard reset"""
    cred = get_git_credentials()
    username = cred.get('username', '')
    token    = cred.get('token', '')
    if not username or not token:
        return jsonify({'success': False, 'error': 'GitHub kimlik bilgileri eksik. Ayarlar → Yedek & Senkron sayfasından token girin.'})

    repo_url = f'https://{username}:{token}@github.com/{username}/firinna-pos.git'
    app_dir  = GIT_DIR

    # .git klasörü var mı?
    has_git = os.path.isdir(os.path.join(app_dir, '.git'))

    if not has_git:
        # Mevcut dosyaları geçici yere taşı, clone yap
        import tempfile, shutil
        tmp = tempfile.mkdtemp()
        # Kritik dosyaları koru
        preserve = ['pos_data.db', 'firinna_local.json', 'static']
        for f in preserve:
            src = os.path.join(app_dir, f)
            if os.path.exists(src):
                dst = os.path.join(tmp, f)
                try:
                    if os.path.isdir(src):
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
                except Exception:
                    pass
        # Clone
        result = subprocess.run(
            ['git', 'clone', repo_url, app_dir + '_clone'],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode != 0:
            return jsonify({'success': False, 'error': 'git clone hatası: ' + result.stderr[:300]})
        # Klonlanan dosyaları ana dizine kopyala (db ve local hariç)
        clone_dir = app_dir + '_clone'
        for item in os.listdir(clone_dir):
            if item in preserve:
                continue
            src = os.path.join(clone_dir, item)
            dst = os.path.join(app_dir, item)
            try:
                if os.path.isdir(src):
                    if os.path.exists(dst):
                        shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            except Exception as e:
                pass
        # .git klasörünü taşı
        shutil.copytree(os.path.join(clone_dir, '.git'), os.path.join(app_dir, '.git'))
        shutil.rmtree(clone_dir)
        # Remote URL'i güncelle (plain url)
        subprocess.run(['git', '-C', app_dir, 'remote', 'set-url', 'origin', repo_url],
                       capture_output=True)
        return jsonify({'success': True, 'message': 'git clone tamamlandı. Sunucuyu yeniden başlatın.'})
    else:
        # Remote URL'i güncelle (token dahil)
        subprocess.run(['git', '-C', app_dir, 'remote', 'set-url', 'origin', repo_url],
                       capture_output=True, timeout=10)
        ok_fetch, out_fetch = run_git(['fetch', 'origin', 'main'], timeout=60)
        if not ok_fetch:
            return jsonify({'success': False, 'error': 'fetch hatası: ' + out_fetch})
        ok_reset, out_reset = run_git(['reset', '--hard', 'origin/main'], timeout=30)
        if not ok_reset:
            return jsonify({'success': False, 'error': 'reset hatası: ' + out_reset})
        return jsonify({'success': True, 'message': 'Hard reset tamamlandı. Sunucuyu yeniden başlatın.'})


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
    app.run(host='0.0.0.0', port=5000, debug=True)
