from flask import Flask, render_template, request, jsonify
import database as db
from printer import ThermalPrinter
import os
from datetime import datetime

app = Flask(__name__)

# Yazıcı ayarları (config'den okunacak)
PRINTER_IP = os.getenv('PRINTER_IP', '192.168.1.100')
PRINTER_PORT = int(os.getenv('PRINTER_PORT', 9100))

printer = ThermalPrinter(PRINTER_IP, PRINTER_PORT)

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
    db.delete_category(category_id)
    return jsonify({'success': True})

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
    db.delete_zone(zone_id)
    return jsonify({'success': True})

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
    db.delete_table(table_id)
    return jsonify({'success': True})

# API: Siparişler
@app.route('/api/orders/table/<int:table_id>', methods=['GET'])
def api_get_table_order(table_id):
    order = db.get_table_order(table_id)
    if order:
        return jsonify(order)
    else:
        # Yeni sipariş oluştur
        order_id = db.create_order(table_id)
        return jsonify({'id': order_id, 'table_id': table_id, 'total': 0, 'items': []})

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
    # Sipariş bilgilerini al
    conn = db.get_db()
    order = conn.execute('SELECT * FROM orders WHERE id = ?', (order_id,)).fetchone()
    table = conn.execute('SELECT * FROM tables WHERE id = ?', (order['table_id'],)).fetchone()
    items = conn.execute('''
        SELECT oi.*, p.name as product_name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    conn.close()
    
    order_data = {
        'order_id': order['id'],
        'table_name': table['name'],
        'total': order['total'],
        'items': [dict(item) for item in items]
    }
    
    success = printer.print_receipt(order_data)
    return jsonify({'success': success})

# API: Masraflar
@app.route('/api/expenses', methods=['GET', 'POST'])
def api_expenses():
    if request.method == 'GET':
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        return jsonify(db.get_expenses(start_date, end_date))
    
    elif request.method == 'POST':
        data = request.json
        db.add_expense(data['description'], data['amount'], data.get('category', 'Genel'))
        return jsonify({'success': True})

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def api_delete_expense(expense_id):
    db.delete_expense(expense_id)
    return jsonify({'success': True})

# API: Raporlar
@app.route('/api/reports/daily', methods=['GET'])
def api_daily_report():
    date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    report = db.get_daily_report(date)
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

if __name__ == '__main__':
    db.init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
