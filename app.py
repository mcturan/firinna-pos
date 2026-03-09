from flask import Flask, render_template, request, jsonify, send_from_directory
import database as db
from printer import ThermalPrinter
import os
import subprocess
import threading
import time
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Ana sayfa (masalar görünümü)
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
def api_add_order_item(order_id):
    data = request.json
    db.add_order_item(order_id, data['product_id'], data['quantity'], data['price'])
    return jsonify({'success': True})

@app.route('/api/orders/items/<int:item_id>', methods=['DELETE'])
def api_delete_order_item(item_id):
    db.delete_order_item(item_id)
    return jsonify({'success': True})

@app.route('/api/orders/<int:order_id>/close', methods=['POST'])
def api_close_order(order_id):
    db.close_order(order_id)
    return jsonify({'success': True})

# API: Adisyon yazdır
@app.route('/api/print/receipt/<int:order_id>', methods=['POST'])
def api_print_receipt(order_id):
    order = db.get_table_order_by_id(order_id)
    if not order:
        return jsonify({"success": False, "error": "Sipariş bulunamadı"})
    
    from printer import ThermalPrinter
    printer = ThermalPrinter(printer_type="receipt")
    success = printer.print_receipt(order)
    return jsonify({"success": success})

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

# API: Test verilerini temizle
@app.route('/api/clear-test-data', methods=['POST'])
def api_clear_test_data():
    db.clear_test_data()
    return jsonify({'success': True})

# API: Yazıcı test
@app.route('/api/printer/test', methods=['POST'])
def api_printer_test():
    success = printer.test_print()
    return jsonify({'success': success})

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
        timestamp=datetime.now().strftime('%d.%m.%Y %H:%M')
    )


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
        footer_note=db.get_setting('receipt_footer', 'Afiyet olsun!'),
        logo_url=db.get_setting('logo_url', '')
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
db.init_muhasebe_tables()
db.migrate_orders_to_transactions()

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
    """Tüm değişiklikleri commit + push"""
    data = request.json or {}
    msg = data.get('message', '').strip()
    if not msg:
        now = datetime.now().strftime('%d.%m.%Y %H:%M')
        msg = f'Güncelleme — {now}'
    
    # Commit edilmemiş değişiklik var mı?
    ok, status = run_git(['status', '--short'])
    has_changes = bool(status.strip())
    
    if has_changes:
        ok1, out1 = run_git(['add', '-A'])
        if not ok1:
            return jsonify({'success': False, 'error': 'git add hatası: ' + out1})
        
        ok2, out2 = run_git(['commit', '-m', msg])
        if not ok2:
            return jsonify({'success': False, 'error': 'git commit hatası: ' + out2})
    
    ok3, out3 = run_git(['push', 'origin', 'main'], timeout=60)
    if not ok3:
        return jsonify({'success': False, 'error': 'git push hatası: ' + out3})
    
    return jsonify({
        'success': True,
        'had_changes': has_changes,
        'output': out3
    })

@app.route('/api/git/pull', methods=['POST'])
def api_git_pull():
    """GitHub'tan en son sürümü çek"""
    ok, out = run_git(['pull', 'origin', 'main'], timeout=60)
    if not ok:
        return jsonify({'success': False, 'error': out})
    
    already_up = 'Already up to date' in out or 'Zaten güncel' in out
    
    if not already_up:
        # Servis restart et (değişiklikler aktif olsun)
        try:
            subprocess.Popen(['sudo', 'systemctl', 'restart', 'firinna-pos'])
        except:
            pass
    
    return jsonify({
        'success': True,
        'already_up': already_up,
        'output': out
    })

@app.route('/api/git/auto-pull/status', methods=['GET'])
def api_auto_pull_status():
    interval = db.get_setting('git_auto_pull_interval', '0')
    return jsonify({'interval': int(interval)})

@app.route('/api/git/auto-pull/set', methods=['POST'])
def api_auto_pull_set():
    data = request.json or {}
    interval = int(data.get('interval', 0))  # dakika, 0 = kapalı
    db.set_setting('git_auto_pull_interval', str(interval))
    if interval > 0:
        start_auto_pull(interval)
    return jsonify({'success': True, 'interval': interval})

# --- Auto-pull arka plan iş parçacığı ---
_auto_pull_timer = None

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
                subprocess.Popen(['sudo', 'systemctl', 'restart', 'firinna-pos'])
            except:
                pass
        # Bir sonraki kontrol
        _auto_pull_timer = threading.Timer(interval_minutes * 60, do_pull)
        _auto_pull_timer.daemon = True
        _auto_pull_timer.start()
    
    _auto_pull_timer = threading.Timer(interval_minutes * 60, do_pull)
    _auto_pull_timer.daemon = True
    _auto_pull_timer.start()

if __name__ == '__main__':
    db.init_db()
    # Auto-pull başlat (eğer ayarlıysa)
    try:
        interval = int(db.get_setting('git_auto_pull_interval', '0'))
        if interval > 0:
            start_auto_pull(interval)
    except:
        pass
    app.run(host='0.0.0.0', port=5000, debug=True)
