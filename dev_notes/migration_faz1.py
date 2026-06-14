#!/usr/bin/env python3
import sqlite3

DB_PATH = 'pos_data.db'

print("FAZ 1 Migration başlıyor...")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

try:
    c.execute("ALTER TABLE order_items ADD COLUMN is_complimentary INTEGER DEFAULT 0")
    print("✓ is_complimentary eklendi")
except: print("⚠ is_complimentary zaten var")

try:
    c.execute("ALTER TABLE order_items ADD COLUMN kitchen_notes TEXT")
    print("✓ kitchen_notes eklendi")
except: print("⚠ kitchen_notes zaten var")

try:
    c.execute("ALTER TABLE orders ADD COLUMN discount_type TEXT")
    print("✓ discount_type eklendi")
except: print("⚠ discount_type zaten var")

try:
    c.execute("ALTER TABLE orders ADD COLUMN discount_value REAL DEFAULT 0")
    print("✓ discount_value eklendi")
except: print("⚠ discount_value zaten var")

try:
    c.execute("ALTER TABLE orders ADD COLUMN discount_reason TEXT")
    print("✓ discount_reason eklendi")
except: print("⚠ discount_reason zaten var")

try:
    c.execute("ALTER TABLE orders ADD COLUMN payment_cash REAL DEFAULT 0")
    print("✓ payment_cash eklendi")
except: print("⚠ payment_cash zaten var")

try:
    c.execute("ALTER TABLE orders ADD COLUMN payment_card REAL DEFAULT 0")
    print("✓ payment_card eklendi")
except: print("⚠ payment_card zaten var")

try:
    c.execute("ALTER TABLE orders ADD COLUMN tip_amount REAL DEFAULT 0")
    print("✓ tip_amount eklendi")
except: print("⚠ tip_amount zaten var")

try:
    c.execute("ALTER TABLE orders ADD COLUMN tip_method TEXT")
    print("✓ tip_method eklendi")
except: print("⚠ tip_method zaten var")

conn.commit()
conn.close()
print("✅ Migration tamamlandı!")
