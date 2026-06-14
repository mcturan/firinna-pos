#!/usr/bin/env python3
import sqlite3

DB_PATH = 'pos_data.db'

print("FAZ 2 Migration başlıyor...")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

try:
    c.execute("ALTER TABLE categories ADD COLUMN sort_order INTEGER DEFAULT 0")
    print("✓ categories.sort_order eklendi")
except: print("⚠ categories.sort_order zaten var")

try:
    c.execute("ALTER TABLE products ADD COLUMN sort_order INTEGER DEFAULT 0")
    print("✓ products.sort_order eklendi")
except: print("⚠ products.sort_order zaten var")

try:
    c.execute("ALTER TABLE products ADD COLUMN is_favorite INTEGER DEFAULT 0")
    print("✓ products.is_favorite eklendi")
except: print("⚠ products.is_favorite zaten var")

try:
    c.execute("ALTER TABLE tables ADD COLUMN table_note TEXT")
    print("✓ tables.table_note eklendi")
except: print("⚠ tables.table_note zaten var")

try:
    c.execute('''CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key TEXT UNIQUE NOT NULL,
        value TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    print("✓ settings tablosu oluşturuldu")
except: print("⚠ settings tablosu zaten var")

conn.commit()
conn.close()
print("✅ Migration tamamlandı!")
