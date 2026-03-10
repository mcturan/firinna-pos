-- Fırınna POS DB Dump
-- 2026-03-10 10:43:33

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
INSERT INTO "order_items" VALUES(17,9,6,1,250.0,'2026-03-09 23:29:56',0,'','Menemen');
INSERT INTO "order_items" VALUES(18,9,15,2,40.0,'2026-03-09 23:29:56',0,'','Çay');
INSERT INTO "order_items" VALUES(19,10,6,1,250.0,'2026-03-09 23:31:19',0,'','Menemen');
INSERT INTO "order_items" VALUES(20,10,9,1,170.0,'2026-03-09 23:31:19',0,'','Omlet Peynirli');
INSERT INTO "order_items" VALUES(21,10,26,1,150.0,'2026-03-09 23:31:19',0,'','Çikolatalı Kek');
INSERT INTO "order_items" VALUES(22,10,28,1,100.0,'2026-03-09 23:31:19',0,'','Maraş Dondurma');
INSERT INTO "order_items" VALUES(23,10,19,2,120.0,'2026-03-09 23:31:19',0,'','Türk Kahvesi');
INSERT INTO "order_items" VALUES(24,10,15,2,40.0,'2026-03-09 23:31:19',0,'','Çay');
INSERT INTO "order_items" VALUES(25,11,6,2,250.0,'2026-03-09 23:32:13',0,'','Menemen');
INSERT INTO "order_items" VALUES(26,12,6,1,250.0,'2026-03-09 23:33:37',0,'','Menemen');
INSERT INTO "order_items" VALUES(27,12,9,1,170.0,'2026-03-09 23:33:37',0,'','Omlet Peynirli');
INSERT INTO "order_items" VALUES(28,13,4,1,400.0,'2026-03-09 23:34:25',0,'','Pizza Karışık');
INSERT INTO "order_items" VALUES(29,13,6,1,250.0,'2026-03-09 23:34:25',0,'','Menemen');
INSERT INTO "order_items" VALUES(30,14,15,4,40.0,'2026-03-09 23:34:53',0,'','Çay');
INSERT INTO "order_items" VALUES(31,15,15,1,40.0,'2026-03-09 23:35:54',0,'','Çay');
INSERT INTO "order_items" VALUES(32,15,19,1,120.0,'2026-03-09 23:35:54',0,'','Türk Kahvesi');
INSERT INTO "order_items" VALUES(33,16,20,1,150.0,'2026-03-09 23:36:54',0,'','Glitwein');
INSERT INTO "order_items" VALUES(34,16,15,1,40.0,'2026-03-09 23:36:54',0,'','Çay');
INSERT INTO "order_items" VALUES(35,16,19,2,120.0,'2026-03-09 23:36:54',0,'','Türk Kahvesi');
INSERT INTO "order_items" VALUES(36,17,13,1,250.0,'2026-03-09 23:37:36',0,'','Bazlama Sucuklu');
INSERT INTO "order_items" VALUES(37,18,6,2,250.0,'2026-03-09 23:38:48',0,'','Menemen');
INSERT INTO "order_items" VALUES(38,18,15,4,40.0,'2026-03-09 23:38:48',0,'','Çay');
INSERT INTO "order_items" VALUES(39,18,26,2,150.0,'2026-03-09 23:38:48',0,'','Çikolatalı Kek');
INSERT INTO "order_items" VALUES(40,19,15,2,40.0,'2026-03-09 23:40:16',0,'','Çay');
INSERT INTO "order_items" VALUES(41,19,6,1,250.0,'2026-03-09 23:40:16',0,'','Menemen');
INSERT INTO "order_items" VALUES(42,19,13,1,250.0,'2026-03-09 23:40:16',0,'','Bazlama Sucuklu');
INSERT INTO "order_items" VALUES(43,20,4,1,400.0,'2026-03-09 23:41:37',0,'','Pizza Karışık');
INSERT INTO "order_items" VALUES(44,20,6,2,250.0,'2026-03-09 23:41:37',0,'','Menemen');
INSERT INTO "order_items" VALUES(45,20,15,4,40.0,'2026-03-09 23:41:37',0,'','Çay');
INSERT INTO "order_items" VALUES(46,20,18,1,120.0,'2026-03-09 23:41:37',0,'','Kahve Americano');
INSERT INTO "order_items" VALUES(47,20,21,1,20.0,'2026-03-09 23:41:37',0,'','Su');
INSERT INTO "order_items" VALUES(48,21,23,1,70.0,'2026-03-09 23:42:28',0,'','Sarıyer Kola');
INSERT INTO "order_items" VALUES(49,21,21,1,20.0,'2026-03-09 23:42:28',0,'','Su');
INSERT INTO "order_items" VALUES(50,21,3,1,380.0,'2026-03-09 23:42:28',0,'','Pizza Margarita');
INSERT INTO "order_items" VALUES(51,21,26,1,150.0,'2026-03-09 23:42:28',0,'','Çikolatalı Kek');
INSERT INTO "order_items" VALUES(52,22,26,1,150.0,'2026-03-09 23:43:08',0,'','Çikolatalı Kek');
INSERT INTO "order_items" VALUES(53,22,15,3,40.0,'2026-03-09 23:43:08',0,'','Çay');
INSERT INTO "order_items" VALUES(54,23,13,2,250.0,'2026-03-09 23:47:49',0,'','Bazlama Sucuklu');
INSERT INTO "order_items" VALUES(55,23,8,1,150.0,'2026-03-09 23:47:49',0,'','Omlet');
INSERT INTO "order_items" VALUES(56,23,15,6,40.0,'2026-03-09 23:47:49',0,'','Çay');
INSERT INTO "order_items" VALUES(57,23,25,1,70.0,'2026-03-09 23:47:49',0,'','FuseTea Soğukçay');
INSERT INTO "order_items" VALUES(58,23,4,2,400.0,'2026-03-09 23:47:49',0,'','Pizza Karışık');
INSERT INTO "order_items" VALUES(59,23,19,2,120.0,'2026-03-09 23:47:49',0,'','Türk Kahvesi');
INSERT INTO "order_items" VALUES(60,23,21,1,20.0,'2026-03-09 23:47:49',0,'','Su');
INSERT INTO "order_items" VALUES(61,23,7,1,350.0,'2026-03-09 23:47:49',0,'','Menemen Kavurmalı');
INSERT INTO "order_items" VALUES(62,23,12,1,200.0,'2026-03-09 23:47:49',0,'','Bazlama Yumurtalı');
INSERT INTO "order_items" VALUES(63,23,20,1,150.0,'2026-03-09 23:47:49',0,'','Glitwein');
INSERT INTO "order_items" VALUES(64,24,4,9,400.0,'2026-03-10 00:03:17',0,'','Pizza Karışık');
INSERT INTO "order_items" VALUES(65,24,7,4,350.0,'2026-03-10 00:03:17',0,'','Menemen Kavurmalı');
INSERT INTO "order_items" VALUES(66,24,6,11,250.0,'2026-03-10 00:03:17',0,'','Menemen');
INSERT INTO "order_items" VALUES(67,24,15,41,40.0,'2026-03-10 00:03:17',0,'','Çay');
INSERT INTO "order_items" VALUES(68,24,20,4,150.0,'2026-03-10 00:03:17',0,'','Glitwein');
INSERT INTO "order_items" VALUES(69,24,26,13,150.0,'2026-03-10 00:03:17',0,'','Çikolatalı Kek');
INSERT INTO "order_items" VALUES(70,24,12,2,200.0,'2026-03-10 00:03:17',0,'','Bazlama Yumurtalı');
INSERT INTO "order_items" VALUES(71,24,14,9,300.0,'2026-03-10 00:03:17',0,'','Bazlama Kavurmalı');
INSERT INTO "order_items" VALUES(72,24,19,8,120.0,'2026-03-10 00:03:17',0,'','Türk Kahvesi');
INSERT INTO "order_items" VALUES(73,24,18,5,120.0,'2026-03-10 00:03:17',0,'','Kahve Americano');
INSERT INTO "order_items" VALUES(74,24,10,3,250.0,'2026-03-10 00:03:17',0,'','Omlet Sucuklu');
INSERT INTO "order_items" VALUES(75,24,21,8,20.0,'2026-03-10 00:03:17',0,'','Su');
INSERT INTO "order_items" VALUES(76,24,9,2,170.0,'2026-03-10 00:03:17',0,'','Omlet Peynirli');
INSERT INTO "order_items" VALUES(77,24,13,4,250.0,'2026-03-10 00:03:17',0,'','Bazlama Sucuklu');
INSERT INTO "order_items" VALUES(78,24,5,1,500.0,'2026-03-10 00:03:17',0,'','Pizza Kavurmalı');
INSERT INTO "order_items" VALUES(79,24,17,2,150.0,'2026-03-10 00:03:17',0,'','Kahve Cappucino');
INSERT INTO "order_items" VALUES(80,24,28,6,100.0,'2026-03-10 00:03:17',0,'','Maraş Dondurma');
INSERT INTO "order_items" VALUES(81,24,22,2,40.0,'2026-03-10 00:03:17',0,'','Madensuyu');
INSERT INTO "order_items" VALUES(82,24,11,1,250.0,'2026-03-10 00:03:17',0,'','Omlet Kavurmalı');
INSERT INTO "order_items" VALUES(83,24,23,1,70.0,'2026-03-10 00:03:17',0,'','Sarıyer Kola');
INSERT INTO "order_items" VALUES(84,25,6,2,250.0,'2026-03-10 00:30:46',0,'','Menemen');
INSERT INTO "order_items" VALUES(85,25,14,3,300.0,'2026-03-10 00:30:46',0,'','Bazlama Kavurmalı');
INSERT INTO "order_items" VALUES(86,25,15,6,40.0,'2026-03-10 00:30:46',0,'','Çay');
INSERT INTO "order_items" VALUES(87,25,18,1,120.0,'2026-03-10 00:30:46',0,'','Kahve Americano');
INSERT INTO "order_items" VALUES(88,25,23,1,70.0,'2026-03-10 00:30:46',0,'','Sarıyer Kola');
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
INSERT INTO "orders" VALUES(9,1,330.0,'closed','2026-02-23T23:28','2026-02-23T23:28',NULL,0.0,'',330.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(10,1,990.0,'closed','2026-02-23T23:30','2026-02-23T23:30',NULL,0.0,'',990.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(11,1,500.0,'closed','2026-01-17T23:31','2026-01-17T23:31',NULL,0.0,'',500.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(12,1,420.0,'closed','2026-03-09T23:32','2026-03-09T23:32',NULL,0.0,'',420.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(13,1,650.0,'closed','2026-01-17T23:33','2026-01-17T23:33',NULL,0.0,'',650.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(14,1,160.0,'closed','2026-01-17T23:34','2026-01-17T23:34',NULL,0.0,'',160.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(15,1,160.0,'closed','2026-01-18T23:34','2026-01-18T23:34',NULL,0.0,'',160.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(16,1,430.0,'closed','2026-01-20T23:36','2026-01-20T23:36',NULL,0.0,'',430.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(17,1,250.0,'closed','2026-01-20T23:36','2026-01-20T23:36',NULL,0.0,'',250.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(18,1,960.0,'closed','2026-01-23T23:37','2026-01-23T23:37',NULL,0.0,'',960.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(19,1,580.0,'closed','2026-03-09T23:39','2026-03-09T23:39',NULL,0.0,'',580.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(20,1,1200.0,'closed','2026-01-25T23:40','2026-01-25T23:40',NULL,0.0,'',1200.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(21,1,620.0,'closed','2026-01-28T23:41','2026-01-28T23:41',NULL,0.0,'',620.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(22,1,270.0,'closed','2026-01-28T23:42','2026-01-28T23:42',NULL,0.0,'',270.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(23,1,2720.0,'closed','2026-01-30T23:44','2026-01-30T23:44',NULL,0.0,'',2720.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(24,1,20650.0,'closed','2026-02-01T23:48','2026-02-01T23:48',NULL,0.0,'',20650.0,0.0,0.0,'cash');
INSERT INTO "orders" VALUES(25,1,1830.0,'closed','2026-02-24T00:28','2026-02-24T00:28',NULL,0.0,'',1830.0,0.0,0.0,'cash');
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
INSERT INTO "recipes" VALUES(1,27,16,2.0);
INSERT INTO "recipes" VALUES(2,14,7,1.0);
INSERT INTO "recipes" VALUES(3,14,4,100.0);
INSERT INTO "recipes" VALUES(4,13,7,1.0);
INSERT INTO "recipes" VALUES(5,13,15,100.0);
INSERT INTO "recipes" VALUES(6,12,7,1.0);
INSERT INTO "recipes" VALUES(7,12,5,2.0);
INSERT INTO "recipes" VALUES(8,25,12,1.0);
INSERT INTO "recipes" VALUES(9,22,9,1.0);
INSERT INTO "recipes" VALUES(10,6,13,170.0);
INSERT INTO "recipes" VALUES(11,6,5,2.0);
INSERT INTO "recipes" VALUES(12,7,13,170.0);
INSERT INTO "recipes" VALUES(13,6,3,50.0);
INSERT INTO "recipes" VALUES(14,7,4,50.0);
INSERT INTO "recipes" VALUES(15,7,3,50.0);
INSERT INTO "recipes" VALUES(16,8,5,2.0);
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
INSERT INTO "settings" VALUES('restaurant_name','____ F I R I N N A ____','2026-03-09 21:33:04');
INSERT INTO "settings" VALUES('restaurant_address','Beyoğlu İstanbul','2026-03-09 21:33:04');
INSERT INTO "settings" VALUES('restaurant_phone','+905456301214','2026-03-09 21:33:04');
INSERT INTO "settings" VALUES('tax_number','','2026-03-09 21:33:04');
INSERT INTO "settings" VALUES('receipt_footer','','2026-03-09 21:33:04');
INSERT INTO "settings" VALUES('receipt_qr_image_url','','2026-03-09 15:48:55');
INSERT INTO "settings" VALUES('receipt_qr_label','','2026-03-09 15:48:55');
INSERT INTO "settings" VALUES('note_qr_image_url','/static/uploads/note_qr.jpeg','2026-03-09 12:15:21');
INSERT INTO "settings" VALUES('note_qr_label','','2026-03-09 12:27:29');
INSERT INTO "settings" VALUES('telegram_bot_token','8626007432:AAGTtM-zuM0-3hvjcl0Qa3vULZqY4r3QVmY','2026-03-09 13:02:10');
INSERT INTO "settings" VALUES('telegram_chat_id','8490520505','2026-03-09 13:02:10');
INSERT INTO "settings" VALUES('restaurant_web','www.firinna.com.tr','2026-03-09 21:33:04');
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
INSERT INTO "transactions" VALUES(4,'2026-01-17','in',500.0,'satis','cash','Sipariş #11',11,'2026-01-17T23:31');
INSERT INTO "transactions" VALUES(5,'2026-01-17','in',650.0,'satis','cash','Sipariş #13',13,'2026-01-17T23:33');
INSERT INTO "transactions" VALUES(6,'2026-01-17','in',160.0,'satis','cash','Sipariş #14',14,'2026-01-17T23:34');
INSERT INTO "transactions" VALUES(7,'2026-01-18','in',160.0,'satis','cash','Sipariş #15',15,'2026-01-18T23:34');
INSERT INTO "transactions" VALUES(8,'2026-01-20','in',430.0,'satis','cash','Sipariş #16',16,'2026-01-20T23:36');
INSERT INTO "transactions" VALUES(9,'2026-01-20','in',250.0,'satis','cash','Sipariş #17',17,'2026-01-20T23:36');
INSERT INTO "transactions" VALUES(10,'2026-01-23','in',960.0,'satis','cash','Sipariş #18',18,'2026-01-23T23:37');
INSERT INTO "transactions" VALUES(11,'2026-01-25','in',1200.0,'satis','cash','Sipariş #20',20,'2026-01-25T23:40');
INSERT INTO "transactions" VALUES(12,'2026-01-28','in',620.0,'satis','cash','Sipariş #21',21,'2026-01-28T23:41');
INSERT INTO "transactions" VALUES(13,'2026-01-28','in',270.0,'satis','cash','Sipariş #22',22,'2026-01-28T23:42');
INSERT INTO "transactions" VALUES(14,'2026-01-30','in',2720.0,'satis','cash','Sipariş #23',23,'2026-01-30T23:44');
INSERT INTO "transactions" VALUES(15,'2026-02-01','in',20650.0,'satis','cash','Sipariş #24',24,'2026-02-01T23:48');
INSERT INTO "transactions" VALUES(16,'2026-02-23','in',330.0,'satis','cash','Sipariş #9',9,'2026-02-23T23:28');
INSERT INTO "transactions" VALUES(17,'2026-02-23','in',990.0,'satis','cash','Sipariş #10',10,'2026-02-23T23:30');
INSERT INTO "transactions" VALUES(18,'2026-02-24','in',1830.0,'satis','cash','Sipariş #25',25,'2026-02-24T00:28');
INSERT INTO "transactions" VALUES(19,'2026-03-09','in',420.0,'satis','cash','Sipariş #12',12,'2026-03-09T23:32');
INSERT INTO "transactions" VALUES(20,'2026-03-09','in',580.0,'satis','cash','Sipariş #19',19,'2026-03-09T23:39');
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
INSERT INTO "sqlite_sequence" VALUES('orders',25);
INSERT INTO "sqlite_sequence" VALUES('order_items',88);
INSERT INTO "sqlite_sequence" VALUES('telegram_contacts',4);
INSERT INTO "sqlite_sequence" VALUES('transactions',20);
INSERT INTO "sqlite_sequence" VALUES('stock_items',16);
INSERT INTO "sqlite_sequence" VALUES('recipes',16);
COMMIT;