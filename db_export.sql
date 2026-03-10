-- Fırınna POS DB Dump
-- 2026-03-10 12:09:17

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        color TEXT DEFAULT '#3B82F6',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    , sort_order INTEGER DEFAULT 0);
INSERT INTO "categories" VALUES(3,'Pizza','#3B82F6','2026-03-09 15:13:50',0);
INSERT INTO "categories" VALUES(4,'Menemen','#3B82F6','2026-03-09 15:13:50',0);
INSERT INTO "categories" VALUES(5,'Omlet','#3B82F6','2026-03-09 15:13:50',0);
INSERT INTO "categories" VALUES(6,'Bazlama','#3B82F6','2026-03-09 15:13:50',0);
INSERT INTO "categories" VALUES(8,'Sıcak içecekler','#3b82f6','2026-03-09 15:30:47',0);
INSERT INTO "categories" VALUES(9,'Soğuk içecekler','#3b82f6','2026-03-09 15:31:02',0);
INSERT INTO "categories" VALUES(10,'Tatlı','#3b82f6','2026-03-09 16:23:10',0);
CREATE TABLE expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
CREATE TABLE order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        product_id INTEGER,
        quantity INTEGER DEFAULT 1,
        price REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, is_complimentary INTEGER DEFAULT 0, kitchen_notes TEXT, product_name TEXT,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );
INSERT INTO "order_items" VALUES(6,4,4,1,400.0,'2026-03-09 15:14:30',0,NULL,'Pizza Karışık');
INSERT INTO "order_items" VALUES(7,4,15,2,40.0,'2026-03-09 15:33:02',0,NULL,'Çay');
INSERT INTO "order_items" VALUES(8,4,16,1,150.0,'2026-03-09 15:33:06',0,NULL,'Kahve Latte');
INSERT INTO "order_items" VALUES(9,4,19,1,120.0,'2026-03-09 15:33:14',0,NULL,'Türk Kahvesi');
INSERT INTO "order_items" VALUES(10,5,19,2,120.0,'2026-03-09 16:17:39',0,NULL,'Türk Kahvesi');
INSERT INTO "order_items" VALUES(11,5,21,1,20.0,'2026-03-09 16:24:09',0,NULL,'Su');
INSERT INTO "order_items" VALUES(12,6,3,1,380.0,'2026-03-09 16:50:41',0,NULL,'Pizza Margarita');
INSERT INTO "order_items" VALUES(13,6,14,1,300.0,'2026-03-09 16:50:52',0,NULL,'Bazlama Kavurmalı');
INSERT INTO "order_items" VALUES(14,6,15,2,40.0,'2026-03-09 16:50:57',0,NULL,'Çay');
CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        table_id INTEGER,
        total REAL DEFAULT 0,
        status TEXT DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        closed_at TIMESTAMP, discount_type TEXT, discount_value REAL DEFAULT 0, discount_reason TEXT, payment_cash REAL DEFAULT 0, payment_card REAL DEFAULT 0, tip_amount REAL DEFAULT 0, tip_method TEXT,
        FOREIGN KEY (table_id) REFERENCES tables(id)
    );
INSERT INTO "orders" VALUES(4,1,750.0,'closed','2026-03-09 15:14:30','2026-03-09 19:17:52',NULL,0.0,NULL,0.0,750.0,0.0,'cash');
INSERT INTO "orders" VALUES(5,3,260.0,'closed','2026-03-09 16:17:39','2026-03-09 19:50:27',NULL,0.0,NULL,0.0,260.0,0.0,'cash');
INSERT INTO "orders" VALUES(6,1,760.0,'closed','2026-03-09 16:50:40','2026-03-09 20:07:07',NULL,0.0,NULL,760.0,0.0,0.0,'cash');
CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category_id INTEGER,
        price REAL NOT NULL,
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, sort_order INTEGER DEFAULT 0, is_favorite INTEGER DEFAULT 0, stock_item_id INTEGER DEFAULT NULL,
        FOREIGN KEY (category_id) REFERENCES categories(id)
    );
INSERT INTO "products" VALUES(1,'1',1,1.0,0,'2026-03-09 10:34:36',0,0,NULL);
INSERT INTO "products" VALUES(2,'test',2,333.0,0,'2026-03-09 11:29:31',0,0,NULL);
INSERT INTO "products" VALUES(3,'Pizza Margarita',3,380.0,1,'2026-03-09 15:13:50',0,0,NULL);
INSERT INTO "products" VALUES(4,'Pizza Karışık',3,400.0,1,'2026-03-09 15:13:50',0,0,NULL);
INSERT INTO "products" VALUES(5,'Pizza Kavurmalı',3,500.0,1,'2026-03-09 15:13:50',0,0,NULL);
INSERT INTO "products" VALUES(6,'Menemen',4,250.0,1,'2026-03-09 15:13:50',0,0,NULL);
INSERT INTO "products" VALUES(7,'Menemen Kavurmalı',4,350.0,1,'2026-03-09 15:13:50',0,0,NULL);
INSERT INTO "products" VALUES(8,'Omlet',5,150.0,1,'2026-03-09 15:13:50',0,0,NULL);
INSERT INTO "products" VALUES(9,'Omlet Peynirli',5,170.0,1,'2026-03-09 15:13:50',0,0,NULL);
INSERT INTO "products" VALUES(10,'Omlet Sucuklu',5,250.0,1,'2026-03-09 15:13:50',0,0,NULL);
INSERT INTO "products" VALUES(11,'Omlet Kavurmalı',5,250.0,1,'2026-03-09 15:13:50',0,0,NULL);
INSERT INTO "products" VALUES(12,'Bazlama Yumurtalı',6,200.0,1,'2026-03-09 15:13:50',0,0,NULL);
INSERT INTO "products" VALUES(13,'Bazlama Sucuklu',6,250.0,1,'2026-03-09 15:13:50',0,0,NULL);
INSERT INTO "products" VALUES(14,'Bazlama Kavurmalı',6,300.0,1,'2026-03-09 15:13:50',0,0,NULL);
INSERT INTO "products" VALUES(15,'Çay',8,40.0,1,'2026-03-09 15:31:14',0,0,NULL);
INSERT INTO "products" VALUES(16,'Kahve Latte',8,150.0,1,'2026-03-09 15:31:37',0,0,NULL);
INSERT INTO "products" VALUES(17,'Kahve Cappucino',8,150.0,1,'2026-03-09 15:31:55',0,0,NULL);
INSERT INTO "products" VALUES(18,'Kahve Americano',8,120.0,1,'2026-03-09 15:32:14',0,0,NULL);
INSERT INTO "products" VALUES(19,'Türk Kahvesi',8,120.0,1,'2026-03-09 15:32:34',0,0,NULL);
INSERT INTO "products" VALUES(20,'Glitwein',8,150.0,1,'2026-03-09 15:32:51',0,0,NULL);
INSERT INTO "products" VALUES(21,'Su',9,20.0,1,'2026-03-09 16:21:28',0,0,NULL);
INSERT INTO "products" VALUES(22,'Madensuyu',9,40.0,1,'2026-03-09 16:21:40',0,0,9);
INSERT INTO "products" VALUES(23,'Sarıyer Kola',9,70.0,1,'2026-03-09 16:22:20',0,0,10);
INSERT INTO "products" VALUES(24,'Sarıyer Portakal',9,70.0,1,'2026-03-09 16:22:36',0,0,11);
INSERT INTO "products" VALUES(25,'FuseTea Soğukçay',9,70.0,1,'2026-03-09 16:23:00',0,0,12);
INSERT INTO "products" VALUES(26,'Çikolatalı Kek',10,150.0,1,'2026-03-09 16:23:28',0,0,14);
INSERT INTO "products" VALUES(27,'Baklava',10,170.0,1,'2026-03-09 16:23:41',0,0,16);
INSERT INTO "products" VALUES(28,'Maraş Dondurma',10,100.0,1,'2026-03-09 16:24:02',0,0,NULL);
CREATE TABLE recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER NOT NULL,
        stock_item_id INTEGER NOT NULL,
        quantity REAL NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products(id),
        FOREIGN KEY (stock_item_id) REFERENCES stock_items(id)
    );
CREATE TABLE settings (
        key TEXT PRIMARY KEY,
        value TEXT
    , updated_at TEXT);
INSERT INTO "settings" VALUES('printer_ip','192.168.1.99','2026-03-09 10:25:05');
INSERT INTO "settings" VALUES('printer_port','9100','2026-03-09 10:25:05');
INSERT INTO "settings" VALUES('kitchen_printer_ip','192.168.1.99','2026-03-09 10:25:05');
INSERT INTO "settings" VALUES('kitchen_printer_port','9100','2026-03-09 10:25:05');
INSERT INTO "settings" VALUES('git_auto_push_time','23:59','2026-03-09 10:37:04');
INSERT INTO "settings" VALUES('logo_url','','2026-03-09 15:48:58');
INSERT INTO "settings" VALUES('restaurant_name','____ F I R I N N A ____','2026-03-09 17:43:40');
INSERT INTO "settings" VALUES('restaurant_address','Beyoğlu İstanbul','2026-03-09 17:43:40');
INSERT INTO "settings" VALUES('restaurant_phone','+905456301214','2026-03-09 17:43:40');
INSERT INTO "settings" VALUES('tax_number','','2026-03-09 17:43:40');
INSERT INTO "settings" VALUES('receipt_footer','','2026-03-09 17:43:40');
INSERT INTO "settings" VALUES('receipt_qr_image_url','','2026-03-09 15:48:55');
INSERT INTO "settings" VALUES('receipt_qr_label','','2026-03-09 15:48:55');
INSERT INTO "settings" VALUES('note_qr_image_url','/static/uploads/note_qr.jpeg','2026-03-09 12:15:21');
INSERT INTO "settings" VALUES('note_qr_label','','2026-03-09 12:27:29');
INSERT INTO "settings" VALUES('telegram_bot_token','8626007432:AAGTtM-zuM0-3hvjcl0Qa3vULZqY4r3QVmY','2026-03-09 13:02:10');
INSERT INTO "settings" VALUES('telegram_chat_id','8490520505','2026-03-09 13:02:10');
INSERT INTO "settings" VALUES('restaurant_web','www.firinna.com.tr','2026-03-09 17:43:40');
CREATE TABLE stock_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        unit TEXT DEFAULT 'adet',     -- kg, lt, gr, adet, paket, ml
        quantity REAL DEFAULT 0,
        min_quantity REAL DEFAULT 0,
        cost_per_unit REAL DEFAULT 0,
        category TEXT DEFAULT 'Genel',
        active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
INSERT INTO "stock_items" VALUES(1,'Pizza Margarita','adet',0.0,3.0,0.0,'Tahıl/Un',1,'2026-03-09 18:09:40');
INSERT INTO "stock_items" VALUES(2,'Pizza Karışık','adet',0.0,3.0,0.0,'Tahıl/Un',1,'2026-03-09 18:10:35');
INSERT INTO "stock_items" VALUES(3,'Peynir','gr',0.0,500.0,0.0,'Süt Ürünleri',1,'2026-03-09 18:11:07');
INSERT INTO "stock_items" VALUES(4,'Kavurma','gr',0.0,100.0,0.0,'Et/Tavuk',1,'2026-03-09 18:11:29');
INSERT INTO "stock_items" VALUES(5,'Yumurta','adet',0.0,6.0,0.0,'Et/Tavuk',1,'2026-03-09 18:12:48');
INSERT INTO "stock_items" VALUES(6,'Süt','lt',0.0,0.5,0.0,'Süt Ürünleri',1,'2026-03-09 18:13:28');
INSERT INTO "stock_items" VALUES(7,'Bazlama','adet',0.0,2.0,0.0,'Tahıl/Un',1,'2026-03-09 18:15:32');
INSERT INTO "stock_items" VALUES(8,'Ekmek','adet',0.0,1.0,0.0,'Tahıl/Un',1,'2026-03-09 18:15:40');
INSERT INTO "stock_items" VALUES(9,'Madensuyu','adet',0.0,4.0,0.0,'İçecek',1,'2026-03-09 18:16:21');
INSERT INTO "stock_items" VALUES(10,'Sarıyer Kola','adet',0.0,5.0,0.0,'İçecek',1,'2026-03-09 18:16:37');
INSERT INTO "stock_items" VALUES(11,'Sarıyer Portakal','adet',0.0,5.0,0.0,'İçecek',1,'2026-03-09 18:17:06');
INSERT INTO "stock_items" VALUES(12,'Fusetea Soğukçay','adet',0.0,5.0,0.0,'İçecek',1,'2026-03-09 18:17:20');
INSERT INTO "stock_items" VALUES(13,'Menemen domates sosu','gr',0.0,1000.0,0.0,'Sebze/Meyve',1,'2026-03-09 18:18:02');
INSERT INTO "stock_items" VALUES(14,'Çikolatalı kek','adet',0.0,4.0,0.0,'Tahıl/Un',1,'2026-03-09 18:18:44');
INSERT INTO "stock_items" VALUES(15,'Sucuk','gr',0.0,100.0,0.0,'Et/Tavuk',1,'2026-03-09 18:19:00');
INSERT INTO "stock_items" VALUES(16,'Baklava','adet',0.0,10.0,0.0,'Sebze/Meyve',1,'2026-03-09 18:20:20');
CREATE TABLE stock_movements (
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
    );
CREATE TABLE tables (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        zone_id INTEGER,
        status TEXT DEFAULT 'empty',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, table_note TEXT,
        FOREIGN KEY (zone_id) REFERENCES zones(id)
    );
INSERT INTO "tables" VALUES(1,'1',1,'empty','2026-03-09 10:34:27',NULL);
INSERT INTO "tables" VALUES(2,'2',1,'empty','2026-03-09 15:47:55',NULL);
INSERT INTO "tables" VALUES(3,'3',1,'empty','2026-03-09 15:47:58',NULL);
INSERT INTO "tables" VALUES(4,'4',1,'empty','2026-03-09 15:48:01',NULL);
INSERT INTO "tables" VALUES(5,'1',2,'empty','2026-03-09 15:48:06',NULL);
INSERT INTO "tables" VALUES(6,'2',2,'empty','2026-03-09 15:48:09',NULL);
INSERT INTO "tables" VALUES(7,'3',2,'empty','2026-03-09 15:48:12',NULL);
INSERT INTO "tables" VALUES(8,'4',2,'empty','2026-03-09 15:48:16',NULL);
INSERT INTO "tables" VALUES(9,'Takeaway',3,'empty','2026-03-09 15:48:35',NULL);
CREATE TABLE telegram_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        chat_id TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
INSERT INTO "telegram_contacts" VALUES(3,'FIRINNA','8490520505','2026-03-09 13:32:55');
INSERT INTO "telegram_contacts" VALUES(4,'MC TURAN','1326104090','2026-03-09 13:32:58');
CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        type TEXT NOT NULL,           -- 'in' / 'out'
        amount REAL NOT NULL,
        category TEXT DEFAULT 'Genel', -- 'satis','bahsis','masraf','stok_alim','sarf','duzeltme'
        payment_method TEXT DEFAULT 'cash',  -- 'cash' / 'card'
        description TEXT,
        related_order_id INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
INSERT INTO "transactions" VALUES(1,'2026-03-09','in',750.0,'satis','card','Sipariş #4',4,'2026-03-09 19:17:52');
INSERT INTO "transactions" VALUES(2,'2026-03-09','in',260.0,'satis','card','Sipariş #5',5,'2026-03-09 19:50:27');
INSERT INTO "transactions" VALUES(3,'2026-03-09','in',760.0,'satis','cash','Sipariş #6',6,'2026-03-09 20:07:07');
CREATE TABLE zones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
INSERT INTO "zones" VALUES(1,'Cafe','2026-03-09 10:34:24');
INSERT INTO "zones" VALUES(2,'Street','2026-03-09 15:47:50');
INSERT INTO "zones" VALUES(3,'Takeaway','2026-03-09 15:48:30');
DELETE FROM "sqlite_sequence";
INSERT INTO "sqlite_sequence" VALUES('zones',3);
INSERT INTO "sqlite_sequence" VALUES('tables',9);
INSERT INTO "sqlite_sequence" VALUES('categories',10);
INSERT INTO "sqlite_sequence" VALUES('products',28);
INSERT INTO "sqlite_sequence" VALUES('orders',9);
INSERT INTO "sqlite_sequence" VALUES('order_items',17);
INSERT INTO "sqlite_sequence" VALUES('telegram_contacts',4);
INSERT INTO "sqlite_sequence" VALUES('transactions',3);
INSERT INTO "sqlite_sequence" VALUES('stock_items',16);
COMMIT;