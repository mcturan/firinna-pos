"""
Geçmiş siparişlerin eksik transaction kayıtlarını tamamlar.
Çalıştır: python3 /opt/firinna-pos/backfill_transactions.py
"""
import sys, sqlite3
sys.path.insert(0, '/opt/firinna-pos')
import database as db

conn = db.get_db()

# Transaction'ı olmayan kapalı siparişleri bul
orders = conn.execute('''
    SELECT o.id, o.total, o.payment_cash, o.payment_card,
           o.tip_amount, o.tip_method, o.closed_at
    FROM orders o
    WHERE o.status = 'closed'
      AND o.id NOT IN (
          SELECT related_order_id FROM transactions 
          WHERE related_order_id IS NOT NULL
      )
    ORDER BY o.closed_at
''').fetchall()

if not orders:
    print("✅ Tüm siparişlerin transaction kaydı mevcut, işlem gerekmedi.")
    conn.close()
    sys.exit(0)

print(f"📋 {len(orders)} siparişin transaction kaydı eksik, ekleniyor...\n")

count = 0
for o in orders:
    oid      = o['id']
    cash     = o['payment_cash']  or 0
    card     = o['payment_card']  or 0
    tip      = o['tip_amount']    or 0
    method   = o['tip_method']    or 'cash'
    closed   = o['closed_at']     or ''
    date_str = closed[:10] if closed else ''

    if cash > 0:
        conn.execute('''
            INSERT INTO transactions
              (date, type, amount, category, payment_method,
               description, related_order_id, created_at)
            VALUES (?, 'in', ?, 'satis', 'cash',
                    'Sipariş #' || ?, ?, ?)
        ''', (date_str, cash, oid, oid, closed))
        count += 1
        print(f"  ✓ Sipariş #{oid} → nakit {cash} TL  ({date_str})")

    if card > 0:
        conn.execute('''
            INSERT INTO transactions
              (date, type, amount, category, payment_method,
               description, related_order_id, created_at)
            VALUES (?, 'in', ?, 'satis', 'card',
                    'Sipariş #' || ?, ?, ?)
        ''', (date_str, card, oid, oid, closed))
        count += 1
        print(f"  ✓ Sipariş #{oid} → kart  {card} TL  ({date_str})")

    if tip > 0:
        conn.execute('''
            INSERT INTO transactions
              (date, type, amount, category, payment_method,
               description, related_order_id, created_at)
            VALUES (?, 'in', ?, 'bahsis', ?,
                    'Bahşiş - Sipariş #' || ?, ?, ?)
        ''', (date_str, tip, method, oid, oid, closed))
        count += 1
        print(f"  ✓ Sipariş #{oid} → bahşiş {tip} TL ({date_str})")

conn.commit()
conn.close()
print(f"\n✅ Tamamlandı. {count} transaction kaydı eklendi.")
print("Kasa ve muhasebe sayfalarını kontrol edebilirsiniz.")
