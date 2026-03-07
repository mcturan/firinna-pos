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
        SELECT oi.*, p.name as product_name
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
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
