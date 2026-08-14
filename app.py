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
    if request.path.startswith('/api/web/analytics') or 'admin' in request.path or 'yonetim' in request.path:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response

# Ana sayfa (masalar görünümü)
@app.route('/api/mobile_version')
def api_mobile_version():
    return jsonify({
        'version': APP_VERSION,
        'apk_url': '/download_apk'
    })

@app.route('/download_apk')
def download_apk():
    return send_from_directory('mobile_app', 'Firinna-Garson.apk', as_attachment=True)

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
    return jsonify({'success': ok, 'message': msg if not ok else ''})

@app.route('/kitchen')
def kitchen_page():
    return render_template('kitchen.html')

@app.route('/notes')
def notes_page():
    return render_template('notes.html')

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
    db.close_order_with_payment(
        order_id,
        data.get('payment_cash', 0),
        data.get('payment_card', 0),
        data.get('tip_amount', 0),
        data.get('tip_method', 'cash'),
        data.get('closed_at')
    )
    db.deduct_stock_for_order(order_id)
    telegram_notify.check_low_stock_after_order(order_id)
    return jsonify({'success': True})

@app.route('/api/orders/<int:order_id>/split', methods=['POST'])
def api_split_order(order_id):
    data = request.json
    per_person = db.split_order_equal(order_id, data['num_people'])
    return jsonify({'per_person': per_person})

@app.route('/api/orders/<int:order_id>/pay-items', methods=['POST'])
def api_pay_order_items(order_id):
    data = request.json or {}
    items_to_pay = data.get('items', [])
    payment_cash = data.get('payment_cash', 0)
    payment_card = data.get('payment_card', 0)
    tip_amount = data.get('tip_amount', 0)
    tip_method = data.get('tip_method', 'cash')
    
    if not items_to_pay:
        return jsonify({'success': False, 'error': 'Ödenecek ürün seçilmedi.'}), 400
        
    try:
        new_order_id, original_closed = db.pay_order_items(
            order_id, items_to_pay, payment_cash, payment_card, tip_amount, tip_method
        )
        db.deduct_stock_for_order(new_order_id)
        telegram_notify.check_low_stock_after_order(new_order_id)
        
        return jsonify({
            'success': True,
            'new_order_id': new_order_id,
            'original_closed': original_closed
        })
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400

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
    return render_template('backup.html', app_version=APP_VERSION)

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
                        except Exception as te:
                            print(f"Telegram auto-send hatasi: {te}")
                        last_sent = today
                        _time.sleep(70)
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

    if manual_status == 'closed':
        is_open = False
        badge = "🔴 ŞU AN KAPALI (Geçici Olarak Kapalı)"
    elif manual_status == 'open':
        is_open = True
        badge = f"🟢 ŞU AN AÇIK ({today_cfg.get('close', '23:00')}'e Kadar)"
    else:
        # Automatic calculation based on current time & daily schedule
        if not today_cfg.get('active', True):
            is_open = False
            badge = "🔴 ŞU AN KAPALI (Bugün Kapalı)"
        else:
            open_str = today_cfg.get('open', '08:30')
            close_str = today_cfg.get('close', '23:00')
            if open_str <= current_hm <= close_str:
                is_open = True
                badge = f"🟢 ŞU AN AÇIK ({close_str}'e Kadar)"
            else:
                is_open = False
                badge = f"🔴 ŞU AN KAPALI (Açılış: {open_str})"

    res = jsonify({
        "status": "success",
        "store_name": "Fırınna Cafe & Restaurant",
        "is_open": is_open,
        "status_text": "Açık" if is_open else "Kapalı",
        "status_badge": badge,
        "current_day": current_day_tr,
        "current_time": current_hm,
        "today_hours": f"{today_cfg.get('open', '08:30')} - {today_cfg.get('close', '23:00')}",
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
