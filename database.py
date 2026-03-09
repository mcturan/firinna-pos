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
        product_name TEXT,
        quantity INTEGER DEFAULT 1,
        price REAL NOT NULL,
        kitchen_notes TEXT,
        is_complimentary INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    )''')
    # Migrasyon: mevcut tabloya eksik kolonları ekle
    for _col, _def in [('product_name','TEXT'), ('kitchen_notes','TEXT'), ('is_complimentary','INTEGER DEFAULT 0')]:
        try:
            c.execute(f'ALTER TABLE order_items ADD COLUMN {_col} {_def}')
        except:
            pass
    
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
        value TEXT,
        updated_at TEXT
    )''')
    # Mevcut tabloda updated_at eksikse ekle (migrasyon)
    try:
        c.execute('ALTER TABLE settings ADD COLUMN updated_at TEXT')
    except:
        pass
    
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

def add_expense(description, amount, category='Genel', payment_method='cash', subcategory=''):
    conn = get_db()
    # Migration: kolonlar yoksa ekle
    cols = [r[1] for r in conn.execute("PRAGMA table_info(expenses)").fetchall()]
    if 'payment_method' not in cols:
        conn.execute("ALTER TABLE expenses ADD COLUMN payment_method TEXT DEFAULT 'cash'")
    if 'subcategory' not in cols:
        conn.execute("ALTER TABLE expenses ADD COLUMN subcategory TEXT DEFAULT ''")
    conn.execute('INSERT INTO expenses (description, amount, category, payment_method, subcategory) VALUES (?, ?, ?, ?, ?)',
                 (description, amount, category, payment_method, subcategory))
    # Transaction kaydı
    date = datetime.now().strftime('%Y-%m-%d')
    conn.execute('''INSERT INTO transactions
        (date, type, amount, category, payment_method, description)
        VALUES (?, 'out', ?, 'masraf', ?, ?)''',
        (date, amount, payment_method, f'[{category}] {description}'))
    conn.commit()
    conn.close()

def get_expense_summary(start_date=None, end_date=None):
    """Kategori bazlı masraf özeti"""
    conn = get_db()
    if not start_date:
        start_date = '2000-01-01'
    if not end_date:
        from datetime import datetime as dt
        end_date = dt.now().strftime('%Y-%m-%d')
    rows = conn.execute('''
        SELECT category, subcategory,
               COUNT(*) as count,
               COALESCE(SUM(amount),0) as total,
               payment_method
        FROM expenses
        WHERE DATE(created_at) BETWEEN ? AND ?
        GROUP BY category, subcategory, payment_method
        ORDER BY category, total DESC
    ''', (start_date, end_date)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

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
    closed_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn.execute('''
        UPDATE orders 
        SET status = 'closed', 
            closed_at = ?,
            payment_cash = ?,
            payment_card = ?,
            tip_amount = ?,
            tip_method = ?
        WHERE id = ?
    ''', (closed_at, payment_cash, payment_card, tip_amount, tip_method, order_id))
    record_order_transaction(conn, order_id, payment_cash, payment_card, tip_amount, tip_method, closed_at)
    conn.commit()
    conn.close()
    deduct_stock_for_order(order_id)

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
        WHERE p.active = 1 AND (p.name LIKE ? OR c.name LIKE ?)
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

def delete_order(order_id):
    """Siparişi tamamen sil (items ile birlikte)"""
    conn = get_db()
    
    # Önce order_items'ları sil
    conn.execute('DELETE FROM order_items WHERE order_id = ?', (order_id,))
    
    # Sonra order'ı sil
    conn.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    
    conn.commit()
    conn.close()

def cleanup_empty_orders():
    """Hiç ürünü olmayan açık siparişleri sil (kalıntıları temizle)"""
    conn = get_db()
    rows = conn.execute('''
        DELETE FROM orders
        WHERE status = 'open'
          AND id NOT IN (SELECT DISTINCT order_id FROM order_items)
    ''')
    deleted = rows.rowcount
    conn.commit()
    conn.close()
    return deleted

def get_table_order_by_id(order_id):
    """Order ID ile sipariş detaylarını getir (yazdırma için)"""
    conn = get_db()
    
    order = conn.execute('''
        SELECT o.*, t.name as table_name, z.name as zone_name
        FROM orders o
        JOIN tables t ON o.table_id = t.id
        JOIN zones z ON t.zone_id = z.id
        WHERE o.id = ?
    ''', (order_id,)).fetchone()
    
    if not order:
        conn.close()
        return None
    
    order_dict = dict(order)
    order_dict['order_id'] = order_id
    
    # Items'ları getir
    items = conn.execute('''
        SELECT oi.*, COALESCE(oi.product_name, p.name, 'Ürün') as product_name
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    ''', (order_id,)).fetchall()
    
    order_dict['items'] = []
    for item in items:
        d = dict(item)
        if not d.get('product_name'):
            d['product_name'] = 'Ürün'
        order_dict['items'].append(d)
    
    # Ara toplam hesapla
    subtotal = sum(item['quantity'] * item['price'] for item in order_dict['items'] if not item['is_complimentary'])
    order_dict['subtotal'] = subtotal
    
    conn.close()
    return order_dict

# ===== GENİŞLETİLMİŞ RAPORLAR (#7, #31) =====

def get_report(start_date, end_date):
    """Tarih aralığı raporu — günlük/haftalık/aylık/toplam için ortak fonksiyon"""
    conn = get_db()

    # Toplam satış, nakit, kart, bahşiş, indirim, sipariş sayısı
    summary = conn.execute('''
        SELECT
            COUNT(*) as order_count,
            COALESCE(SUM(total), 0) as total_sales,
            COALESCE(SUM(payment_cash), 0) as total_cash,
            COALESCE(SUM(payment_card), 0) as total_card,
            COALESCE(SUM(tip_amount), 0) as total_tips,
            COALESCE(SUM(discount_value), 0) as total_discount
        FROM orders
        WHERE DATE(closed_at) BETWEEN ? AND ?
          AND status = 'closed'
    ''', (start_date, end_date)).fetchone()

    # Top ürünler
    top_products = conn.execute('''
        SELECT
            COALESCE(oi.product_name, p.name, 'Silinmiş Ürün') as name,
            SUM(oi.quantity) as quantity,
            SUM(CASE WHEN oi.is_complimentary = 0 THEN oi.quantity * oi.price ELSE 0 END) as total
        FROM order_items oi
        LEFT JOIN products p ON oi.product_id = p.id
        JOIN orders o ON oi.order_id = o.id
        WHERE DATE(o.closed_at) BETWEEN ? AND ?
          AND o.status = 'closed'
          AND oi.is_complimentary = 0
        GROUP BY COALESCE(oi.product_name, p.name)
        ORDER BY quantity DESC
        LIMIT 20
    ''', (start_date, end_date)).fetchall()

    # Günlük dağılım (grafik için)
    daily = conn.execute('''
        SELECT
            DATE(closed_at) as day,
            COUNT(*) as order_count,
            COALESCE(SUM(total), 0) as total_sales,
            COALESCE(SUM(tip_amount), 0) as tips
        FROM orders
        WHERE DATE(closed_at) BETWEEN ? AND ?
          AND status = 'closed'
        GROUP BY DATE(closed_at)
        ORDER BY day
    ''', (start_date, end_date)).fetchall()

    # Masraf
    expenses = conn.execute('''
        SELECT COALESCE(SUM(amount), 0) as total
        FROM expenses
        WHERE DATE(created_at) BETWEEN ? AND ?
    ''', (start_date, end_date)).fetchone()

    conn.close()

    s = dict(summary)
    net = s['total_sales'] + s['total_tips'] - expenses['total']

    return {
        'start_date': start_date,
        'end_date': end_date,
        'order_count': s['order_count'],
        'total_sales': round(s['total_sales'], 2),
        'total_cash': round(s['total_cash'], 2),
        'total_card': round(s['total_card'], 2),
        'total_tips': round(s['total_tips'], 2),
        'total_discount': round(s['total_discount'], 2),
        'total_expenses': round(expenses['total'], 2),
        'net': round(net, 2),
        'top_products': [dict(p) for p in top_products],
        'daily': [dict(d) for d in daily],
    }

# ===== KASA (#8) =====

def get_kasa_summary(date=None):
    """Günlük kasa özeti"""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    conn = get_db()

    # Nakit, kart, bahşiş
    payments = conn.execute('''
        SELECT
            COALESCE(SUM(payment_cash), 0) as cash,
            COALESCE(SUM(payment_card), 0) as card,
            COALESCE(SUM(tip_amount), 0) as tips,
            COUNT(*) as order_count,
            COALESCE(SUM(total), 0) as total_sales
        FROM orders
        WHERE DATE(closed_at) = ? AND status = 'closed'
    ''', (date,)).fetchone()

    # Masraflar
    expenses = conn.execute('''
        SELECT COALESCE(SUM(amount), 0) as total, COUNT(*) as count
        FROM expenses
        WHERE DATE(created_at) = ?
    ''', (date,)).fetchone()

    # Masraf listesi
    expense_list = conn.execute('''
        SELECT id, description, category, amount, created_at
        FROM expenses
        WHERE DATE(created_at) = ?
        ORDER BY created_at DESC
    ''', (date,)).fetchall()

    # Açık siparişler (kasada bekleyen)
    open_orders = conn.execute('''
        SELECT o.id, t.name as table_name, o.total
        FROM orders o
        JOIN tables t ON o.table_id = t.id
        WHERE o.status = 'open'
        ORDER BY o.created_at
    ''').fetchall()

    conn.close()

    cash = payments['cash']
    card = payments['card']
    tips = payments['tips']
    exp = expenses['total']
    net_cash = cash - exp  # kasadaki net nakit

    return {
        'date': date,
        'order_count': payments['order_count'],
        'total_sales': round(payments['total_sales'], 2),
        'cash': round(cash, 2),
        'card': round(card, 2),
        'tips': round(tips, 2),
        'total_expenses': round(exp, 2),
        'expense_count': expenses['count'],
        'net_cash': round(net_cash, 2),
        'net_total': round(cash + card + tips - exp, 2),
        'expense_list': [dict(e) for e in expense_list],
        'open_orders': [dict(o) for o in open_orders],
    }

# ===== ÖN MUHASEBE ALTYAPISI =====

def init_muhasebe_tables():
    """Muhasebe, stok ve reçete tablolarını oluştur"""
    conn = get_db()
    c = conn.cursor()

    # Tüm para hareketleri — kasanın temeli
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        type TEXT NOT NULL,           -- 'in' / 'out'
        amount REAL NOT NULL,
        category TEXT DEFAULT 'Genel', -- 'satis','bahsis','masraf','stok_alim','sarf','duzeltme'
        payment_method TEXT DEFAULT 'cash',  -- 'cash' / 'card'
        description TEXT,
        related_order_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Stok kalemleri
    c.execute('''CREATE TABLE IF NOT EXISTS stock_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        unit TEXT DEFAULT 'adet',     -- kg, lt, gr, adet, paket, ml
        quantity REAL DEFAULT 0,
        min_quantity REAL DEFAULT 0,
        cost_per_unit REAL DEFAULT 0,
        category TEXT DEFAULT 'Genel',
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Stok hareketleri
    c.execute('''CREATE TABLE IF NOT EXISTS stock_movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        stock_item_id INTEGER NOT NULL,
        movement_type TEXT NOT NULL,  -- 'in' / 'out' / 'adjust'
        quantity REAL NOT NULL,
        cost REAL DEFAULT 0,
        reason TEXT DEFAULT 'manuel', -- 'satis','alim','duzeltme','fire'
        description TEXT,
        related_transaction_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (stock_item_id) REFERENCES stock_items(id)
    )''')

    # Reçeteler — ürün = hangi stok kalemlerinden oluşur
    c.execute('''CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        stock_item_id INTEGER NOT NULL,
        quantity REAL NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (stock_item_id) REFERENCES stock_items(id)
    )''')

    conn.commit()
    conn.close()

def migrate_orders_to_transactions():
    """Mevcut kapalı siparişleri transactions tablosuna aktar (bir kez çalışır)"""
    conn = get_db()
    existing = conn.execute('SELECT COUNT(*) as c FROM transactions WHERE related_order_id IS NOT NULL').fetchone()
    if existing['c'] > 0:
        conn.close()
        return 0  # Zaten migrasyon yapılmış

    orders = conn.execute('''
        SELECT id, closed_at, payment_cash, payment_card, tip_amount, tip_method, total
        FROM orders WHERE status = 'closed' AND closed_at IS NOT NULL
    ''').fetchall()

    count = 0
    for o in orders:
        date = o['closed_at'][:10] if o['closed_at'] else datetime.now().strftime('%Y-%m-%d')
        if o['payment_cash'] and o['payment_cash'] > 0:
            conn.execute('''INSERT INTO transactions
                (date, type, amount, category, payment_method, description, related_order_id, created_at)
                VALUES (?, 'in', ?, 'satis', 'cash', 'Sipariş #' || ?, ?, ?)''',
                (date, o['payment_cash'], o['id'], o['id'], o['closed_at']))
        if o['payment_card'] and o['payment_card'] > 0:
            conn.execute('''INSERT INTO transactions
                (date, type, amount, category, payment_method, description, related_order_id, created_at)
                VALUES (?, 'in', ?, 'satis', 'card', 'Sipariş #' || ?, ?, ?)''',
                (date, o['payment_card'], o['id'], o['id'], o['closed_at']))
        if o['tip_amount'] and o['tip_amount'] > 0:
            method = o['tip_method'] or 'cash'
            conn.execute('''INSERT INTO transactions
                (date, type, amount, category, payment_method, description, related_order_id, created_at)
                VALUES (?, 'in', ?, 'bahsis', ?, 'Bahşiş - Sipariş #' || ?, ?, ?)''',
                (date, o['tip_amount'], method, o['id'], o['id'], o['closed_at']))
        count += 1

    # Mevcut masrafları da transactions'a aktar
    expenses = conn.execute('SELECT * FROM expenses').fetchall()
    for e in expenses:
        date = e['created_at'][:10] if e['created_at'] else datetime.now().strftime('%Y-%m-%d')
        conn.execute('''INSERT INTO transactions
            (date, type, amount, category, payment_method, description, created_at)
            VALUES (?, 'out', ?, 'masraf', 'cash', ?, ?)''',
            (date, e['amount'], e['description'] + ' (' + (e['category'] or 'Genel') + ')', e['created_at']))

    conn.commit()
    conn.close()
    return count

def record_order_transaction(conn, order_id, payment_cash, payment_card, tip_amount, tip_method, closed_at):
    """Sipariş kapanışında otomatik transaction kaydı"""
    date = closed_at[:10] if closed_at else datetime.now().strftime('%Y-%m-%d')
    if payment_cash and payment_cash > 0:
        conn.execute('''INSERT INTO transactions
            (date, type, amount, category, payment_method, description, related_order_id, created_at)
            VALUES (?, 'in', ?, 'satis', 'cash', 'Sipariş #' || ?, ?, ?)''',
            (date, payment_cash, order_id, order_id, closed_at))
    if payment_card and payment_card > 0:
        conn.execute('''INSERT INTO transactions
            (date, type, amount, category, payment_method, description, related_order_id, created_at)
            VALUES (?, 'in', ?, 'satis', 'card', 'Sipariş #' || ?, ?, ?)''',
            (date, payment_card, order_id, order_id, closed_at))
    if tip_amount and tip_amount > 0:
        conn.execute('''INSERT INTO transactions
            (date, type, amount, category, payment_method, description, related_order_id, created_at)
            VALUES (?, 'in', ?, 'bahsis', ?, 'Bahşiş - Sipariş #' || ?, ?, ?)''',
            (date, tip_amount, tip_method or 'cash', order_id, order_id, closed_at))

def add_transaction(type_, amount, category, payment_method, description, related_order_id=None):
    """Manuel transaction ekle"""
    conn = get_db()
    date = datetime.now().strftime('%Y-%m-%d')
    conn.execute('''INSERT INTO transactions
        (date, type, amount, category, payment_method, description, related_order_id)
        VALUES (?, ?, ?, ?, ?, ?, ?)''',
        (date, type_, amount, category, payment_method, description, related_order_id))
    conn.commit()
    conn.close()

def delete_transaction(transaction_id):
    conn = get_db()
    # Sipariş kaynağından gelenler silinemez
    tx = conn.execute('SELECT * FROM transactions WHERE id=?', (transaction_id,)).fetchone()
    if tx and tx['related_order_id']:
        conn.close()
        return
    # Stok alımıysa ilgili stock_movement'ı da sil
    if tx and tx['category'] == 'stok_alim':
        conn.execute('''DELETE FROM stock_movements
            WHERE related_transaction_id=? OR
                  (reason='alim' AND cost=? AND
                   ABS(JULIANDAY(created_at) - JULIANDAY(?)) < 0.02)''',
            (transaction_id, tx['amount'], tx['created_at']))
    conn.execute('DELETE FROM transactions WHERE id=?', (transaction_id,))
    conn.commit()
    conn.close()

def get_kasa_data(start_date, end_date, payment_method=None):
    """Kasa verisi — nakit, kart veya tümü"""
    conn = get_db()
    params_in = [start_date, end_date]
    params_out = [start_date, end_date]
    method_filter = ''
    if payment_method:
        method_filter = " AND payment_method = ?"
        params_in.append(payment_method)
        params_out.append(payment_method)

    income = conn.execute(f'''
        SELECT COALESCE(SUM(amount),0) as total,
               COALESCE(SUM(CASE WHEN category='satis' THEN amount ELSE 0 END),0) as satis,
               COALESCE(SUM(CASE WHEN category='bahsis' THEN amount ELSE 0 END),0) as bahsis,
               COUNT(CASE WHEN category='satis' THEN 1 END) as siparis_count
        FROM transactions
        WHERE date BETWEEN ? AND ? AND type='in' {method_filter}
    ''', params_in).fetchone()

    outcome = conn.execute(f'''
        SELECT COALESCE(SUM(amount),0) as total,
               COALESCE(SUM(CASE WHEN category='masraf' THEN amount ELSE 0 END),0) as masraf,
               COALESCE(SUM(CASE WHEN category='stok_alim' THEN amount ELSE 0 END),0) as stok_alim,
               COALESCE(SUM(CASE WHEN category='sarf' THEN amount ELSE 0 END),0) as sarf
        FROM transactions
        WHERE date BETWEEN ? AND ? AND type='out' {method_filter}
    ''', params_out).fetchone()

    # Son 50 işlem
    list_params = [start_date, end_date]
    list_filter = ''
    if payment_method:
        list_filter = " AND payment_method = ?"
        list_params.append(payment_method)
    movements = conn.execute(f'''
        SELECT id, date, type, amount, category, payment_method, description, related_order_id, created_at
        FROM transactions
        WHERE date BETWEEN ? AND ? {list_filter}
        ORDER BY created_at DESC LIMIT 100
    ''', list_params).fetchall()

    conn.close()
    net = income['total'] - outcome['total']
    return {
        'income': round(income['total'],2),
        'satis': round(income['satis'],2),
        'bahsis': round(income['bahsis'],2),
        'siparis_count': income['siparis_count'],
        'outcome': round(outcome['total'],2),
        'masraf': round(outcome['masraf'],2),
        'stok_alim': round(outcome['stok_alim'],2),
        'sarf': round(outcome['sarf'],2),
        'net': round(net,2),
        'movements': [dict(m) for m in movements],
    }

# ===== STOK =====

def get_stock_items():
    conn = get_db()
    items = conn.execute('''
        SELECT s.*,
               (SELECT COALESCE(SUM(CASE WHEN movement_type='in' THEN quantity
                                        WHEN movement_type='out' THEN -quantity
                                        ELSE quantity END), 0)
                FROM stock_movements WHERE stock_item_id = s.id) as current_qty
        FROM stock_items s WHERE s.active = 1 ORDER BY s.category, s.name
    ''').fetchall()
    conn.close()
    return [dict(i) for i in items]

def add_stock_item(name, unit, min_quantity, cost_per_unit, category):
    conn = get_db()
    conn.execute('INSERT INTO stock_items (name, unit, min_quantity, cost_per_unit, category) VALUES (?,?,?,?,?)',
                 (name, unit, min_quantity, cost_per_unit, category))
    conn.commit()
    conn.close()

def add_stock_movement(stock_item_id, movement_type, quantity, cost, reason, description, transaction_id=None):
    """Stok hareketi ekle"""
    conn = get_db()
    conn.execute('''INSERT INTO stock_movements
        (stock_item_id, movement_type, quantity, cost, reason, description, related_transaction_id)
        VALUES (?,?,?,?,?,?,?)''',
        (stock_item_id, movement_type, quantity, cost, reason, description, transaction_id))
    conn.commit()
    conn.close()

def get_stock_movements(stock_item_id=None, limit=50):
    conn = get_db()
    if stock_item_id:
        rows = conn.execute('''
            SELECT sm.*, si.name as item_name, si.unit
            FROM stock_movements sm JOIN stock_items si ON sm.stock_item_id = si.id
            WHERE sm.stock_item_id = ? ORDER BY sm.created_at DESC LIMIT ?
        ''', (stock_item_id, limit)).fetchall()
    else:
        rows = conn.execute('''
            SELECT sm.*, si.name as item_name, si.unit
            FROM stock_movements sm JOIN stock_items si ON sm.stock_item_id = si.id
            ORDER BY sm.created_at DESC LIMIT ?
        ''', (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ===== REÇETE =====

def get_recipes(product_id=None):
    conn = get_db()
    if product_id:
        rows = conn.execute('''
            SELECT r.*, s.name as stock_name, s.unit
            FROM recipes r JOIN stock_items s ON r.stock_item_id = s.id
            WHERE r.product_id = ?
        ''', (product_id,)).fetchall()
    else:
        rows = conn.execute('''
            SELECT r.*, p.name as product_name, s.name as stock_name, s.unit
            FROM recipes r
            JOIN products p ON r.product_id = p.id
            JOIN stock_items s ON r.stock_item_id = s.id
            ORDER BY p.name, s.name
        ''').fetchall()
    conn.close()
    return [dict(r) for r in rows]

def set_recipe(product_id, stock_item_id, quantity):
    conn = get_db()
    existing = conn.execute('SELECT id FROM recipes WHERE product_id=? AND stock_item_id=?',
                            (product_id, stock_item_id)).fetchone()
    if existing:
        conn.execute('UPDATE recipes SET quantity=? WHERE id=?', (quantity, existing['id']))
    else:
        conn.execute('INSERT INTO recipes (product_id, stock_item_id, quantity) VALUES (?,?,?)',
                     (product_id, stock_item_id, quantity))
    conn.commit()
    conn.close()

def delete_recipe(recipe_id):
    conn = get_db()
    conn.execute('DELETE FROM recipes WHERE id=?', (recipe_id,))
    conn.commit()
    conn.close()

def deduct_stock_for_order(order_id):
    """Sipariş kapanışında reçetedeki malzemeleri stoktan düş"""
    conn = get_db()
    items = conn.execute('''
        SELECT oi.product_id, oi.quantity as sold_qty
        FROM order_items oi WHERE oi.order_id = ? AND oi.is_complimentary = 0
    ''', (order_id,)).fetchall()
    for item in items:
        recipes = conn.execute('''
            SELECT r.stock_item_id, r.quantity as recipe_qty
            FROM recipes r WHERE r.product_id = ?
        ''', (item['product_id'],)).fetchall()
        for r in recipes:
            total_deduct = r['recipe_qty'] * item['sold_qty']
            conn.execute('''INSERT INTO stock_movements
                (stock_item_id, movement_type, quantity, reason, description)
                VALUES (?, 'out', ?, 'satis', 'Sipariş #' || ?)''',
                (r['stock_item_id'], total_deduct, order_id))
    conn.commit()
    conn.close()


def update_stock_item(item_id, name, unit, min_quantity, cost_per_unit, category):
    conn = get_db()
    conn.execute('''UPDATE stock_items SET name=?, unit=?, min_quantity=?, cost_per_unit=?, category=?
                    WHERE id=?''', (name, unit, min_quantity, cost_per_unit, category, item_id))
    conn.commit()
    conn.close()

def delete_stock_item(item_id):
    """Başka yerde kullanılmıyorsa sil"""
    conn = get_db()
    used_recipe = conn.execute('SELECT COUNT(*) as c FROM recipes WHERE stock_item_id=?', (item_id,)).fetchone()
    used_move = conn.execute('SELECT COUNT(*) as c FROM stock_movements WHERE stock_item_id=?', (item_id,)).fetchone()
    if used_recipe['c'] > 0 or used_move['c'] > 0:
        conn.close()
        return False, 'Bu kalem reçete veya harekette kullanılıyor, silinemez.'
    conn.execute('UPDATE stock_items SET active=0 WHERE id=?', (item_id,))
    conn.commit()
    conn.close()
    return True, ''

def update_product(product_id, name, price, category_id):
    conn = get_db()
    conn.execute('UPDATE products SET name=?, price=?, category_id=? WHERE id=?',
                 (name, price, category_id, product_id))
    conn.commit()
    conn.close()

def update_expense(expense_id, description, amount, category, payment_method='cash', subcategory=''):
    conn = get_db()
    conn.execute('''UPDATE expenses SET description=?, amount=?, category=?,
                    payment_method=?, subcategory=? WHERE id=?''',
                 (description, amount, category, payment_method, subcategory, expense_id))
    conn.commit()
    conn.close()

# ===== KULLANIM KONTROLLÜ SİLME/DÜZENLEME =====

def delete_category_safe(category_id):
    conn = get_db()
    used = conn.execute('SELECT COUNT(*) as c FROM products WHERE category_id=? AND active=1', (category_id,)).fetchone()
    if used['c'] > 0:
        conn.close()
        return False, f'Bu kategoride {used["c"]} aktif ürün var. Önce ürünleri başka kategoriye taşıyın.'
    conn.execute('DELETE FROM categories WHERE id=?', (category_id,))
    conn.commit()
    conn.close()
    return True, ''

def delete_zone_safe(zone_id):
    conn = get_db()
    used = conn.execute('SELECT COUNT(*) as c FROM tables WHERE zone_id=?', (zone_id,)).fetchone()
    if used['c'] > 0:
        conn.close()
        return False, f'Bu bölgede {used["c"]} masa var. Önce masaları silin.'
    conn.execute('DELETE FROM zones WHERE id=?', (zone_id,))
    conn.commit()
    conn.close()
    return True, ''

def delete_table_safe(table_id):
    conn = get_db()
    used = conn.execute("SELECT COUNT(*) as c FROM orders WHERE table_id=? AND status='open'", (table_id,)).fetchone()
    if used['c'] > 0:
        conn.close()
        return False, 'Bu masada açık sipariş var. Önce siparişi kapatın.'
    conn.execute('DELETE FROM tables WHERE id=?', (table_id,))
    conn.commit()
    conn.close()
    return True, ''

def delete_expense_safe(expense_id):
    """Masraf sil — transaction'da kaydı varsa onu da sil"""
    conn = get_db()
    expense = conn.execute('SELECT * FROM expenses WHERE id=?', (expense_id,)).fetchone()
    if not expense:
        conn.close()
        return False, 'Kayıt bulunamadı.'
    conn.execute('DELETE FROM expenses WHERE id=?', (expense_id,))
    conn.commit()
    conn.close()
    return True, ''

# Stok hareketi düzenle/sil
def update_stock_movement(movement_id, quantity, cost, description):
    conn = get_db()
    conn.execute('UPDATE stock_movements SET quantity=?, cost=?, description=? WHERE id=?',
                 (quantity, cost, description, movement_id))
    conn.commit()
    conn.close()

def delete_stock_movement(movement_id):
    conn = get_db()
    m = conn.execute('SELECT * FROM stock_movements WHERE id=?', (movement_id,)).fetchone()
    if not m:
        conn.close()
        return False, 'Kayıt bulunamadı.'
    if m['reason'] == 'satis':
        conn.close()
        return False, 'Satıştan oluşan stok hareketleri silinemez.'
    # İlgili transaction'ı da sil (alım ise)
    if m['reason'] == 'alim' and m['cost'] and m['cost'] > 0:
        if m['related_transaction_id']:
            conn.execute('DELETE FROM transactions WHERE id=?', (m['related_transaction_id'],))
        else:
            # related_transaction_id yoksa tarih+tutar+açıklama ile eşleştir
            conn.execute('''DELETE FROM transactions
                WHERE category='stok_alim' AND amount=? AND
                      ABS(JULIANDAY(created_at) - JULIANDAY(?)) < 0.01''',
                (m['cost'], m['created_at']))
    conn.execute('DELETE FROM stock_movements WHERE id=?', (movement_id,))
    conn.commit()
    conn.close()
    return True, ''

def add_stock_purchase(stock_item_id, quantity, cost, payment_method, description):
    """Stok alımı: hem stok hareketi hem transaction kaydı"""
    conn = get_db()
    # transactions tablosu yoksa oluştur
    conn.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT DEFAULT 'Genel',
        payment_method TEXT DEFAULT 'cash',
        description TEXT,
        related_order_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    date = datetime.now().strftime('%Y-%m-%d')
    # Stok hareketi
    conn.execute('''INSERT INTO stock_movements
        (stock_item_id, movement_type, quantity, cost, reason, description)
        VALUES (?, 'in', ?, ?, 'alim', ?)''',
        (stock_item_id, quantity, cost, description))
    # Kasadan çıkış
    if cost and cost > 0:
        item = conn.execute('SELECT name FROM stock_items WHERE id=?', (stock_item_id,)).fetchone()
        item_name = item['name'] if item else 'Stok'
        desc = description or item_name + ' alımı'
        conn.execute('''INSERT INTO transactions
            (date, type, amount, category, payment_method, description)
            VALUES (?, 'out', ?, 'stok_alim', ?, ?)''',
            (date, cost, payment_method, desc))
    conn.commit()
    conn.close()
