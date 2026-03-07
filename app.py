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
    if request.method == 'GET':
        return jsonify({'ip': PRINTER_IP, 'port': PRINTER_PORT})
    
    elif request.method == 'POST':
        data = request.json
        global PRINTER_IP, PRINTER_PORT, printer
        PRINTER_IP = data['ip']
        PRINTER_PORT = int(data['port'])
        printer = ThermalPrinter(PRINTER_IP, PRINTER_PORT)
        return jsonify({'success': True})

if __name__ == '__main__':
    # Veritabanını başlat
    db.init_db()
    
    # Uygulamayı başlat (0.0.0.0 = tüm ağdan erişilebilir)
    app.run(host='0.0.0.0', port=5000, debug=True)
