from datetime import date
import sqlite3
import json
from datetime import datetime
import shutil
import os

DB_PATH = 'pos_data.db'

def init_db():
    """Veritabanını başlat ve tabloları oluştur"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Kategoriler
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        color TEXT DEFAULT '#3B82F6',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Ürünler
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER,
        price REAL NOT NULL,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    )''')
    
    # Bölgeler
    c.execute('''CREATE TABLE IF NOT EXISTS zones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Masalar
    c.execute('''CREATE TABLE IF NOT EXISTS tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        zone_id INTEGER,
        status TEXT DEFAULT 'empty',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (zone_id) REFERENCES zones(id)
    )''')
    
    # Siparişler
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_id INTEGER,
        total REAL DEFAULT 0,
        status TEXT DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        closed_at TIMESTAMP,
        FOREIGN KEY (table_id) REFERENCES tables(id)
    )''')
    
    # Sipariş kalemleri
    c.execute('''CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER DEFAULT 1,
        price REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')
    
    # Masraflar
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Ayarlar
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )''')
    
    conn.commit()
    conn.close()

def get_db():
    """Veritabanı bağlantısı al"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# KATEGORI İŞLEMLERİ
def get_categories():
    conn = get_db()
    categories = conn.execute('SELECT * FROM categories ORDER BY name').fetchall()
    conn.close()
    return [dict(cat) for cat in categories]

def add_category(name, color='#3B82F6'):
    conn = get_db()
    conn.execute('INSERT INTO categories (name, color) VALUES (?, ?)', (name, color))
    conn.commit()
    conn.close()

def delete_category(category_id):
    conn = get_db()
    conn.execute('DELETE FROM categories WHERE id = ?', (category_id,))
    conn.commit()
    conn.close()

# ÜRÜN İŞLEMLERİ
def get_products(category_id=None):
    conn = get_db()
    if category_id:
        products = conn.execute('''
            SELECT p.*, c.name as category_name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            WHERE p.category_id = ? AND p.active = 1
            ORDER BY p.name
        ''', (category_id,)).fetchall()
    else:
        products = conn.execute('''
            SELECT p.*, c.name as category_name 
            FROM products p 
            LEFT JOIN categories c ON p.category_id = c.id 
            WHERE p.active = 1
            ORDER BY p.name
        ''').fetchall()
    conn.close()
    return [dict(prod) for prod in products]

def add_product(name, category_id, price):
    conn = get_db()
    conn.execute('INSERT INTO products (name, category_id, price) VALUES (?, ?, ?)', 
                 (name, category_id, price))
    conn.commit()
    conn.close()

def delete_product(product_id):
    conn = get_db()
    conn.execute('UPDATE products SET active = 0 WHERE id = ?', (product_id,))
    conn.commit()
    conn.close()

# BÖLGE İŞLEMLERİ
def get_zones():
    conn = get_db()
    zones = conn.execute('SELECT * FROM zones ORDER BY name').fetchall()
    conn.close()
    return [dict(zone) for zone in zones]

def add_zone(name):
    conn = get_db()
    conn.execute('INSERT INTO zones (name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

def delete_zone(zone_id):
    conn = get_db()
    conn.execute('DELETE FROM zones WHERE id = ?', (zone_id,))
    conn.commit()
    conn.close()

# MASA İŞLEMLERİ
def get_tables(zone_id=None):
    conn = get_db()
    if zone_id:
        tables = conn.execute('''
            SELECT t.*, z.name as zone_name,
                   (SELECT COUNT(*) FROM orders WHERE table_id = t.id AND status = 'open') as has_order
            FROM tables t 
            LEFT JOIN zones z ON t.zone_id = z.id 
            WHERE t.zone_id = ?
            ORDER BY t.name
        ''', (zone_id,)).fetchall()
    else:
        tables = conn.execute('''
            SELECT t.*, z.name as zone_name,
                   (SELECT COUNT(*) FROM orders WHERE table_id = t.id AND status = 'open') as has_order
            FROM tables t 
            LEFT JOIN zones z ON t.zone_id = z.id 
            ORDER BY t.name
        ''').fetchall()
    conn.close()
    return [dict(table) for table in tables]

def add_table(name, zone_id):
    conn = get_db()
    conn.execute('INSERT INTO tables (name, zone_id) VALUES (?, ?)', (name, zone_id))
    conn.commit()
    conn.close()

def delete_table(table_id):
    conn = get_db()
    conn.execute('DELETE FROM tables WHERE id = ?', (table_id,))
    conn.commit()
    conn.close()

# SİPARİŞ İŞLEMLERİ
def get_table_order(table_id):
    """Masanın açık siparişini getir"""
    conn = get_db()
    order = conn.execute('''
        SELECT * FROM orders 
        WHERE table_id = ? AND status = 'open'
        ORDER BY created_at DESC LIMIT 1
    ''', (table_id,)).fetchone()
    
    if not order:
        return None
    
    order_dict = dict(order)
    items = conn.execute('''
        SELECT oi.id, oi.order_id, oi.product_id, oi.quantity, oi.price, 
               oi.is_complimentary, oi.kitchen_notes, oi.created_at,
               COALESCE(oi.product_name, p.name) as product_name
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_dict['id'],)).fetchall()
    
    order_dict['items'] = [dict(item) for item in items]
    conn.close()
    return order_dict

def create_order(table_id):
    """Yeni sipariş oluştur"""
    conn = get_db()
    c = conn.cursor()
    c.execute('INSERT INTO orders (table_id) VALUES (?)', (table_id,))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id

def add_order_item(order_id, product_id, quantity, price):
    """Siparişe ürün ekle"""
    conn = get_db()
    conn.execute('''
        INSERT INTO order_items (order_id, product_id, quantity, price) 
        VALUES (?, ?, ?, ?)
    ''', (order_id, product_id, quantity, price))
    
    # Toplam tutarı güncelle
    conn.execute('''
        UPDATE orders SET total = (
            SELECT SUM(quantity * price) FROM order_items WHERE order_id = ?
        ) WHERE id = ?
    ''', (order_id, order_id))
    
    conn.commit()
    conn.close()

def close_order(order_id):
    """Siparişi kapat (ödeme al)"""
    conn = get_db()
    conn.execute('''
        UPDATE orders 
        SET status = 'closed', closed_at = CURRENT_TIMESTAMP 
        WHERE id = ?
    ''', (order_id,))
    conn.commit()
    conn.close()

def delete_order_item(item_id):
    """Sipariş kalemini sil"""
    conn = get_db()
    
    # Önce order_id'yi al
    item = conn.execute('SELECT order_id FROM order_items WHERE id = ?', (item_id,)).fetchone()
    if item:
        order_id = item['order_id']
        
        # Kalemi sil
        conn.execute('DELETE FROM order_items WHERE id = ?', (item_id,))
        
        # Toplam tutarı güncelle
        conn.execute('''
            UPDATE orders SET total = (
                SELECT COALESCE(SUM(quantity * price), 0) FROM order_items WHERE order_id = ?
            ) WHERE id = ?
        ''', (order_id, order_id))
    
    conn.commit()
    conn.close()

# MASRAF İŞLEMLERİ
def get_expenses(start_date=None, end_date=None):
    conn = get_db()
    if start_date and end_date:
        expenses = conn.execute('''
            SELECT * FROM expenses 
            WHERE DATE(created_at) BETWEEN ? AND ?
            ORDER BY created_at DESC
        ''', (start_date, end_date)).fetchall()
    else:
        expenses = conn.execute('SELECT * FROM expenses ORDER BY created_at DESC').fetchall()
    conn.close()
    return [dict(exp) for exp in expenses]

def add_expense(description, amount, category='Genel'):
    conn = get_db()
    conn.execute('INSERT INTO expenses (description, amount, category) VALUES (?, ?, ?)', 
                 (description, amount, category))
    conn.commit()
    conn.close()

def delete_expense(expense_id):
    conn = get_db()
    conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()

# RAPOR İŞLEMLERİ
def get_daily_report(date=None):
    """Günlük satış raporu"""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db()
    
    # Toplam satış
    total = conn.execute('''
        SELECT COALESCE(SUM(total), 0) as total
        FROM orders
        WHERE DATE(created_at) = ? AND status = 'closed'
    ''', (date,)).fetchone()
    
    # Ürün bazlı satışlar
    products = conn.execute('''
        SELECT p.name, SUM(oi.quantity) as quantity, SUM(oi.quantity * oi.price) as total
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        JOIN orders o ON oi.order_id = o.id
        WHERE DATE(o.created_at) = ? AND o.status = 'closed'
        GROUP BY p.name
        ORDER BY total DESC
    ''', (date,)).fetchall()
    
    # Toplam masraf
    expenses = conn.execute('''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM expenses
        WHERE DATE(created_at) = ?
    ''', (date,)).fetchone()
    
    conn.close()
    
    return {
        'date': date,
        'total_sales': total['total'],
        'total_expenses': expenses['total'],
        'net': total['total'] - expenses['total'],
        'products': [dict(p) for p in products]
    }

# YEDEKLEME
def backup_database():
    """Veritabanını yedekle"""
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'pos_backup_{timestamp}.db')
    shutil.copy2(DB_PATH, backup_path)
    return backup_path

def clear_test_data():
    """Test verilerini temizle (bugünün siparişleri hariç)"""
    conn = get_db()
    today = datetime.now().strftime('%Y-%m-%d')
    
    conn.execute("DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE DATE(created_at) < ?)", (today,))
    conn.execute("DELETE FROM orders WHERE DATE(created_at) < ?", (today,))
    conn.execute("DELETE FROM expenses WHERE DATE(created_at) < ?", (today,))
    
    conn.commit()
    conn.close()

# İlk çalıştırmada DB'yi oluştur
if not os.path.exists(DB_PATH):
    init_db()

# ===== FAZ 1 YENİ FONKSİYONLAR =====

def update_order_item_quantity(item_id, quantity):
    """Ürün miktarını güncelle (#4)"""
    conn = get_db()
    item = conn.execute('SELECT order_id FROM order_items WHERE id = ?', (item_id,)).fetchone()
    if not item:
        conn.close()
        return
    
    order_id = item['order_id']
    
    if quantity <= 0:
        conn.execute('DELETE FROM order_items WHERE id = ?', (item_id,))
    else:
        conn.execute('UPDATE order_items SET quantity = ? WHERE id = ?', (quantity, item_id))
    
    update_order_total(conn, order_id)
    conn.commit()
    conn.close()

def update_order_item(item_id, is_complimentary=None, kitchen_notes=None):
    """Sipariş kalemini güncelle (#6, #20)"""
    conn = get_db()
    item = conn.execute('SELECT order_id FROM order_items WHERE id = ?', (item_id,)).fetchone()
    if not item:
        conn.close()
        return
    
    order_id = item['order_id']
    updates = []
    params = []
    
    if is_complimentary is not None:
        updates.append('is_complimentary = ?')
        params.append(1 if is_complimentary else 0)
    
    if kitchen_notes is not None:
        updates.append('kitchen_notes = ?')
        params.append(kitchen_notes)
    
    if updates:
        params.append(item_id)
        conn.execute(f'UPDATE order_items SET {", ".join(updates)} WHERE id = ?', params)
        update_order_total(conn, order_id)
    
    conn.commit()
    conn.close()

def add_custom_order_item(order_id, product_name, price):
    """Özel sipariş ekle (#12)"""
    conn = get_db()
    conn.execute('''
        INSERT INTO order_items (order_id, product_id, product_name, quantity, price, kitchen_notes) 
        VALUES (?, NULL, ?, 1, ?, ?)
    ''', (order_id, product_name, price, f'ÖZEL: {product_name}'))
    
    update_order_total(conn, order_id)
    conn.commit()
    conn.close()

def update_order_total(conn, order_id):
    """Sipariş toplamını güncelle (indirim ve ikramlar dahil)"""
    result = conn.execute('''
        SELECT COALESCE(SUM(CASE WHEN is_complimentary = 0 THEN quantity * price ELSE 0 END), 0) as subtotal
        FROM order_items WHERE order_id = ?
    ''', (order_id,)).fetchone()
    
    subtotal = result['subtotal']
    
    order = conn.execute('SELECT discount_type, discount_value FROM orders WHERE id = ?', (order_id,)).fetchone()
    discount = 0
    
    if order and order['discount_value']:
        if order['discount_type'] == 'percent':
            discount = subtotal * (order['discount_value'] / 100)
        else:
            discount = order['discount_value']
    
    total = max(0, subtotal - discount)
    conn.execute('UPDATE orders SET total = ? WHERE id = ?', (total, order_id))

def set_order_discount(order_id, discount_type, discount_value, discount_reason=''):
    """Sipariş indirimi ekle (#13)"""
    conn = get_db()
    conn.execute('''
        UPDATE orders 
        SET discount_type = ?, discount_value = ?, discount_reason = ?
        WHERE id = ?
    ''', (discount_type, discount_value, discount_reason, order_id))
    
    update_order_total(conn, order_id)
    conn.commit()
    conn.close()

def close_order_with_payment(order_id, payment_cash=0, payment_card=0, tip_amount=0, tip_method='cash'):
    """Sipariş kapat ve ödeme kaydet (#5, #10)"""
    conn = get_db()
    conn.execute('''
        UPDATE orders 
        SET status = 'closed', 
            closed_at = CURRENT_TIMESTAMP,
            payment_cash = ?,
            payment_card = ?,
            tip_amount = ?,
            tip_method = ?
        WHERE id = ?
    ''', (payment_cash, payment_card, tip_amount, tip_method, order_id))
    conn.commit()
    conn.close()

def split_order_equal(order_id, num_people):
    """Hesabı eşit böl (#11)"""
    conn = get_db()
    order = conn.execute('SELECT total FROM orders WHERE id = ?', (order_id,)).fetchone()
    if order:
        per_person = order['total'] / num_people
        conn.close()
        return per_person
    conn.close()
    return 0

# ===== FAZ 2 YENİ FONKSİYONLAR =====

def update_category_order(category_id, sort_order):
    """Kategori sıralamasını güncelle"""
    conn = get_db()
    conn.execute('UPDATE categories SET sort_order = ? WHERE id = ?', (sort_order, category_id))
    conn.commit()
    conn.close()

def update_product_order(product_id, sort_order):
    """Ürün sıralamasını güncelle"""
    conn = get_db()
    conn.execute('UPDATE products SET sort_order = ? WHERE id = ?', (sort_order, product_id))
    conn.commit()
    conn.close()

def toggle_product_favorite(product_id):
    """Ürünü favori olarak işaretle/kaldır"""
    conn = get_db()
    product = conn.execute('SELECT is_favorite FROM products WHERE id = ?', (product_id,)).fetchone()
    if product:
        new_value = 0 if product['is_favorite'] else 1
        conn.execute('UPDATE products SET is_favorite = ? WHERE id = ?', (new_value, product_id))
    conn.commit()
    conn.close()
    return new_value if product else 0

def search_products(query):
    """Ürün adına göre arama"""
    conn = get_db()
    products = conn.execute('''
        SELECT p.*, c.name as category_name, c.color as category_color
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.name LIKE ? OR c.name LIKE ?
        ORDER BY p.is_favorite DESC, p.sort_order, p.name
    ''', (f'%{query}%', f'%{query}%')).fetchall()
    conn.close()
    return [dict(p) for p in products]

def get_closed_orders(date=None, limit=50):
    """Kapalı siparişleri getir"""
    conn = get_db()
    if date:
        orders = conn.execute('''
            SELECT o.*, t.name as table_name, z.name as zone_name
            FROM orders o
            JOIN tables t ON o.table_id = t.id
            JOIN zones z ON t.zone_id = z.id
            WHERE o.status = 'closed' AND DATE(o.closed_at) = ?
            ORDER BY o.closed_at DESC
            LIMIT ?
        ''', (date, limit)).fetchall()
    else:
        orders = conn.execute('''
            SELECT o.*, t.name as table_name, z.name as zone_name
            FROM orders o
            JOIN tables t ON o.table_id = t.id
            JOIN zones z ON t.zone_id = z.id
            WHERE o.status = 'closed'
            ORDER BY o.closed_at DESC
            LIMIT ?
        ''', (limit,)).fetchall()
    
    result = []
    for order in orders:
        order_dict = dict(order)
        items = conn.execute('''
            SELECT oi.*, COALESCE(oi.product_name, p.name) as product_name
            FROM order_items oi
            LEFT JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = ?
        ''', (order_dict['id'],)).fetchall()
        order_dict['items'] = [dict(item) for item in items]
        result.append(order_dict)
    
    conn.close()
    return result
    conn.close()

def update_table_note(table_id, note):
    """Masa notunu güncelle"""
    conn = get_db()
    conn.execute('UPDATE tables SET table_note = ? WHERE id = ?', (note, table_id))
    conn.commit()
    conn.close()

def get_setting(key, default=None):
    """Ayar değerini getir"""
    conn = get_db()
    setting = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
    conn.close()
    return setting['value'] if setting else default

def set_setting(key, value):
    """Ayar değerini kaydet"""
    conn = get_db()
    conn.execute('''
        INSERT INTO settings (key, value, updated_at) 
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(key) DO UPDATE SET value = ?, updated_at = CURRENT_TIMESTAMP
    ''', (key, value, value))
    conn.commit()
    conn.close()

# ===== GEÇMİŞ SİPARİŞ GİRİŞİ =====

def create_past_order(table_id, created_at, closed_at, items, payment_cash=0, payment_card=0, 
                      discount_type=None, discount_value=0, discount_reason='', tip_amount=0, tip_method='cash'):
    """Geçmiş tarihli kapalı sipariş oluştur"""
    conn = get_db()
    
    cursor = conn.execute('''
        INSERT INTO orders (table_id, status, total, created_at, closed_at, 
                           payment_cash, payment_card, discount_type, discount_value, 
                           discount_reason, tip_amount, tip_method)
        VALUES (?, 'closed', 0, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (table_id, created_at, closed_at, payment_cash, payment_card, 
          discount_type, discount_value, discount_reason, tip_amount, tip_method))
    
    order_id = cursor.lastrowid
    
    for item in items:
        conn.execute('''
            INSERT INTO order_items (order_id, product_id, product_name, quantity, price, is_complimentary, kitchen_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (order_id, item.get('product_id'), item.get('product_name'), 
              item['quantity'], item['price'], item.get('is_complimentary', 0), 
              item.get('kitchen_notes', '')))
    
    update_order_total(conn, order_id)
    
    conn.commit()
    conn.close()
    
    return order_id

# ===== İSİM DÜZENLEME FONKSİYONLARI =====

def update_zone_name(zone_id, new_name):
    """Bölge adını güncelle"""
    conn = get_db()
    conn.execute('UPDATE zones SET name = ? WHERE id = ?', (new_name, zone_id))
    conn.commit()
    conn.close()

def update_table_name(table_id, new_name):
    """Masa adını güncelle"""
    conn = get_db()
    conn.execute('UPDATE tables SET name = ? WHERE id = ?', (new_name, table_id))
    conn.commit()
    conn.close()

def update_category_name(category_id, new_name):
    """Kategori adını güncelle"""
    conn = get_db()
    conn.execute('UPDATE categories SET name = ? WHERE id = ?', (new_name, category_id))
    conn.commit()
    conn.close()

def update_product_name(product_id, new_name):
    """Ürün adını güncelle"""
    conn = get_db()
    conn.execute('UPDATE products SET name = ? WHERE id = ?', (new_name, product_id))
    conn.commit()
    conn.close()

def reopen_order(order_id):
    """Kapalı siparişi tekrar aç (sadece bugünkü siparişler)"""
    conn = get_db()
    
    # Siparişin tarihini kontrol et
    order = conn.execute('SELECT DATE(closed_at) as order_date FROM orders WHERE id = ?', (order_id,)).fetchone()
    
    if order and order['order_date'] != date.today().isoformat():
        conn.close()
        raise ValueError('1 günden eski siparişler düzenlenemez!')
    
    conn.execute('''
        UPDATE orders 
        SET status = 'open', closed_at = NULL, 
            payment_cash = 0, payment_card = 0, tip_amount = 0
        WHERE id = ?
    ''', (order_id,))
    conn.commit()
    conn.close()
