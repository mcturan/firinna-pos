import sqlite3
import re
import random
from datetime import datetime, timedelta

def get_product(conn, name):
    c = conn.cursor()
    c.execute("SELECT id, price FROM products WHERE name=?", (name,))
    row = c.fetchone()
    if row: return row
    c.execute("SELECT id, name, price FROM products")
    for r in c.fetchall():
        if r[1].lower().replace(" ", "") == name.lower().replace(" ", ""):
            return (r[0], r[2])
    print(f"Adding unknown product: {name}")
    c.execute("INSERT INTO products (name, price, category_id) VALUES (?, ?, 1)", (name, 1.0))
    return (c.lastrowid, 1.0)

def main():
    conn = sqlite3.connect('/opt/firinna-pos/pos_data.db')
    c = conn.cursor()
    
    # Create Muhtelif Ürün
    c.execute("SELECT id FROM products WHERE name='Muhtelif Ürün'")
    row = c.fetchone()
    if row:
        muhtelif_id = row[0]
    else:
        c.execute("INSERT INTO products (name, price, category_id) VALUES (?, ?, 1)", ('Muhtelif Ürün', 1.0))
        muhtelif_id = c.lastrowid
        
    lines = open('/home/turan/Belgeler/fn.txt').read().splitlines()
    
    current_date = None
    data = {}
    
    # Parse the file
    for line in lines:
        m = re.search(r'Günlük Kapanış \((\d{4}-\d{2}-\d{2})\)', line)
        if m:
            current_date = m.group(1)
            data[current_date] = {'sales': 0, 'cash': 0, 'card': 0, 'count': 0, 'items': []}
            continue
        if not current_date: continue
        
        if 'Toplam Satış:' in line:
            data[current_date]['sales'] = float(re.search(r'([\d\.]+)', line).group(1))
        elif 'Nakit:' in line:
            data[current_date]['cash'] = float(re.search(r'([\d\.]+)', line).group(1))
        elif 'Kart:' in line:
            data[current_date]['card'] = float(re.search(r'([\d\.]+)', line).group(1))
        elif 'Sipariş Sayısı:' in line:
            data[current_date]['count'] = int(re.search(r'(\d+)', line).group(1))
        elif re.search(r'\d+\.\s+(.*?)\s+—\s+(\d+)\s+adet', line):
            m2 = re.search(r'\d+\.\s+(.*?)\s+—\s+(\d+)\s+adet', line)
            name = m2.group(1).strip()
            qty = int(m2.group(2))
            data[current_date]['items'].append((name, qty))

    # Clear existing orders from these dates to prevent duplicates if run twice
    for date in data.keys():
        c.execute("DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE DATE(created_at) = ?)", (date,))
        c.execute("DELETE FROM orders WHERE DATE(created_at) = ?", (date,))

    for date, info in data.items():
        if info['sales'] == 0: continue
        
        # Calculate base time
        dt = datetime.strptime(date, '%Y-%m-%d')
        start_time = dt + timedelta(hours=12) # 12:00
        
        # 1. Distribute cash and card into orders
        count = info['count']
        if count == 0: count = 1
        
        all_items = []
        for name, qty in info['items']:
            pid, price = get_product(conn, name)
            for _ in range(qty):
                all_items.append((pid, price, name))
                
        random.shuffle(all_items)
        
        total_items_price = sum(item[1] for item in all_items)
        diff = info['sales'] - total_items_price
        
        if diff > 0:
            all_items.append((muhtelif_id, diff, 'Muhtelif Ürün'))
            
        random.shuffle(all_items)
        
        orders = [{'items': [], 'total': 0, 'cash': 0, 'card': 0} for _ in range(count)]
        for i, item in enumerate(all_items):
            orders[i % count]['items'].append(item)
            orders[i % count]['total'] += item[1]
            
        rem_cash = info['cash']
        rem_card = info['card']
        
        for i, o in enumerate(orders):
            if rem_cash >= o['total']:
                o['cash'] = o['total']
                rem_cash -= o['total']
            else:
                o['cash'] = rem_cash
                rem_cash = 0
                
            o['card'] = o['total'] - o['cash']
            rem_card -= o['card']
            
        orders[-1]['cash'] += rem_cash
        orders[-1]['card'] += rem_card
        
        for i, o in enumerate(orders):
            order_time = start_time + timedelta(minutes=int(600 / count) * i)
            order_time_str = order_time.strftime('%Y-%m-%d %H:%M:%S')
            closed_time_str = (order_time + timedelta(minutes=30)).strftime('%Y-%m-%d %H:%M:%S')
            
            c.execute('''INSERT INTO orders (table_id, total, status, created_at, closed_at, payment_cash, payment_card)
                         VALUES (?, ?, 'closed', ?, ?, ?, ?)''',
                      (1, o['total'], order_time_str, closed_time_str, o['cash'], o['card']))
            oid = c.lastrowid
            
            item_counts = {}
            for item in o['items']:
                if item not in item_counts: item_counts[item] = 0
                item_counts[item] += 1
                
            for item, qty in item_counts.items():
                c.execute('''INSERT INTO order_items (order_id, product_id, product_name, quantity, price, created_at)
                             VALUES (?, ?, ?, ?, ?, ?)''',
                          (oid, item[0], item[2], qty, item[1], order_time_str))
                          
        print(f"Restored {date}: {count} orders, {info['sales']} TL")
        
    conn.commit()
    conn.close()

if __name__ == '__main__':
    main()
