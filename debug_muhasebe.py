import sys
sys.path.insert(0, '/opt/firinna-pos')
import database as db

conn = db.get_db()

print("=== Kapalı siparişler (closed_at değerleri) ===")
rows = conn.execute("SELECT id, closed_at, payment_cash, payment_card, total FROM orders WHERE status='closed' ORDER BY id").fetchall()
for r in rows:
    print(f"  #{r['id']}: '{r['closed_at']}' | nakit:{r['payment_cash']} kart:{r['payment_card']}")

print("\n=== DATE(closed_at) sonuçları ===")
rows2 = conn.execute("SELECT id, DATE(closed_at) as d FROM orders WHERE status='closed'").fetchall()
for r in rows2:
    print(f"  #{r['id']}: DATE={r['d']}")

print("\n=== Ocak 2026 arası sorgu testi ===")
rows3 = conn.execute("""
    SELECT COUNT(*) as cnt, COALESCE(SUM(total),0) as toplam
    FROM orders
    WHERE DATE(closed_at) BETWEEN '2026-01-01' AND '2026-12-31'
    AND status='closed'
""").fetchone()
print(f"  Bulunan: {rows3['cnt']} sipariş, toplam {rows3['toplam']} TL")

print("\n=== Transactions ===")
txs = conn.execute("SELECT id, date, amount, category FROM transactions ORDER BY id").fetchall()
for t in txs:
    print(f"  #{t['id']}: {t['date']} | {t['amount']} | {t['category']}")

conn.close()
