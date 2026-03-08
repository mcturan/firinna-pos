# FIRINНА POS - PROJE DURUM RAPORU

**Son Güncelleme:** 8 Mart 2026  
**Proje Sahibi:** Muhammed Cevad Turan (TA1XTA)  
**Lokasyon:** Fırınna Cafe, Beyoğlu, İstanbul

---

## 🖥️ SİSTEM BİLGİLERİ

### Donanım ve Ağ
- **İşletim Sistemi:** Pardus Linux 25 (yirmibes)
- **Python Versiyonu:** 3.13.5
- **Yerel IP:** 192.168.1.209
- **Port:** 5000
- **Erişim URL:** http://192.168.1.209:5000

### Yazıcı Bilgileri
- **Model:** XPrinter POS80
- **Yazıcı IP:** 192.168.1.99
- **Port:** 9100
- **Durum:** İş yerinde kurulu (şu an erişilemez - ev bilgisayarından çalışıyoruz)

### Proje Dizini
- **Ana Dizin:** `/opt/firinna-pos`
- **Virtual Env:** `/opt/firinna-pos/venv/`
- **Database:** `pos_data.db` (SQLite)
- **Servis:** systemd (`firinna-pos.service`)

---

## 📁 PROJE YAPISI
```
/opt/firinna-pos/
├── app.py                    # Flask ana uygulama (~460 satır)
├── database.py               # Database işlemleri (~700 satır)
├── printer.py                # Fiş yazdırma (ESC/POS, 182 satır)
├── pos_data.db              # SQLite veritabanı
├── requirements.txt         # Python bağımlılıkları
├── roadmap.html            # Proje yol haritası
├── CHANGELOG.html          # Sürüm notları
├── static/
│   └── css/style.css       # Ana CSS
├── templates/
│   ├── index.html          # Ana sayfa (masalar) (~1250 satır)
│   ├── products.html       # Ürün yönetimi
│   ├── tables.html         # Masa yönetimi
│   ├── expenses.html       # Masraflar
│   ├── reports.html        # Raporlar
│   └── receipts/
│       ├── customer_receipt.html  # Müşteri fişi template
│       └── kitchen_receipt.html   # Mutfak fişi template
└── venv/                   # Python virtual environment
```

---

## 🗄️ VERİTABANI YAPISI

### Tablolar
1. **zones** - Bölgeler (İç Mekan, Dış Mekan, vb.)
2. **tables** - Masalar (table_note, sort_order)
3. **categories** - Ürün kategorileri (sort_order)
4. **products** - Ürünler (is_favorite, sort_order)
5. **orders** - Siparişler (status: open/closed)
6. **order_items** - Sipariş kalemleri (product_name, kitchen_notes, is_complimentary)
7. **expenses** - Masraflar
8. **settings** - Sistem ayarları (key-value)

### Önemli Settings Keys
- `restaurant_name`: "Fırınna"
- `restaurant_address`: "Beyoğlu, İstanbul"
- `restaurant_phone`: ""
- `restaurant_web`: ""
- `receipt_footer`: "Bizi Google Haritalar'da yorumlayın!\nAfiyet olsun!"
- `printer_ip`: "192.168.1.99"
- `printer_port`: "9100"
- `kitchen_printer_ip`: ""
- `kitchen_printer_port`: "9100"

---

## ✅ TAMAMLANAN ÖZELLİKLER (23/42)

### FAZ 1 - Sipariş & Ödeme (8/8) ✅
1. **#4** - Ürün miktarı +/- butonları
2. **#5** - Karma ödeme (nakit + kart)
3. **#6** - Ürün düzenleme + İkram checkbox
4. **#10** - Bahşiş takibi (nakit/kart)
5. **#11** - Basit hesap bölme (eşit paylaşım)
6. **#12** - Özel sipariş girişi (custom items)
7. **#13** - İndirim sistemi (% veya TL)
8. **#20** - Şefe özel notlar (kitchen_notes)

**Backend:** `close_order_with_payment()`, `split_order_equal()`, `update_order_item()`, `add_custom_order_item()`

### FAZ 2 - UI İyileştirmeleri (6/6) ✅
1. **#2** - Ürün arama/filtreleme (🔍 search box)
2. **#3** - Favori ürün işaretleme (⭐ yıldız)
3. **#7** - Sipariş geçmişi modal (tarih filtresi, tekrar açma)
4. **#8** - Masa notları (📝 modal)
5. **#9** - Tema altyapısı (settings tablosu)
6. **#1** - Sıralama altyapısı (sort_order kolonları)

**Backend:** `search_products()`, `toggle_product_favorite()`, `get_closed_orders()`, `reopen_order()`, `update_table_note()`

### Ekstra Kritik Özellikler (5/5) ✅
1. **#3** - Geçmiş sipariş girişi (tarih/masa/ürün/ödeme seçimi)
   - `create_past_order()` fonksiyonu
   - Navbar'da "➕ Eski Sipariş Ekle" butonu
   - Modal: tarih, masa, ürünler, ödeme
   
2. **#33** - İsim düzenleme API'leri (Backend hazır, UI FAZ 4'te)
   - `update_zone_name()`, `update_table_name()`
   - `update_category_name()`, `update_product_name()`
   - Endpoint'ler: `PATCH /api/zones/<id>/name`, vb.

3. **#34** - Sipariş tarih koruması
   - 1 günden eski siparişler `reopen_order()` ile açılamaz
   - `ValueError` hatası döner
   - Tam çözüm (read-only modal) FAZ 4'te

4. **#35** - Fazla ödeme → bahşiş önerisi
   - `completePayment()` fonksiyonunda otomatik algılama
   - Confirm dialog: "X TL fazla ödeme var. Bahşiş olarak eklensin mi?"
   - Otomatik nakit/kart düzeltme

5. **#36** - Sipariş silme
   - `delete_order()` fonksiyonu (order + items)
   - Sipariş geçmişinde 🔄 (Tekrar Aç) ve 🗑️ (Sil) butonları
   - Onay mesajı: "Bu işlem geri alınamaz!"

### FAZ 3 - Yazıcı & Fiş (4/7 kısmi) 🔄

**✅ TAMAMLANANLAR:**

1. **Fiş Ayarları Sistemi**
   - Settings tablosuna restaurant bilgileri eklendi
   - `init_receipt_settings.py` ile default değerler

2. **printer.py Güncellemesi**
   - Settings entegrasyonu (`db.get_setting()`)
   - `ThermalPrinter(printer_type='receipt'|'kitchen')`
   - `print_receipt()` - Müşteri fişi (header, ürünler, toplam, footer)
   - `print_kitchen_order()` - Mutfak fişi (sadece ürünler + notlar)

3. **Fiş Template'leri**
   - `templates/receipts/customer_receipt.html`
   - `templates/receipts/kitchen_receipt.html`
   - Jinja2 template'leri (Courier New font, 300px genişlik)

4. **Ön İzleme & PDF Export**
   - `/api/print/receipt/<id>/preview` - HTML önizleme
   - `/api/print/kitchen/<id>/preview` - HTML önizleme
   - `/api/print/receipt/<id>/pdf` - PDF download (WeasyPrint)
   - `/api/print/kitchen/<id>/pdf` - PDF download
   - `get_table_order_by_id()` fonksiyonu

5. **Frontend Entegrasyonu**
   - Sipariş modal'ında buton düzeni:
     - İndirim | Hesap Öde
     - "📄 Sipariş Fişi" başlık + Önizle/Yazdır
     - "👨‍🍳 Mutfak Fişi" başlık + Önizle/Yazdır
     - 📥 PDF | 📱 Gönder (simgeler)
     - 🗑️ Sipariş İptal
   - JavaScript fonksiyonları:
     - `previewReceipt()`, `previewKitchen()`
     - `downloadPDF()` - PDF menüsü
     - `printKitchen()` - Mutfak yazıcısı
     - `sendToPhone()` - Placeholder (WhatsApp)
     - `cancelOrder()` - Sipariş iptal

**❌ KALANLAR:**

1. **#15 - Logo Yükleme**
   - Logo upload endpoint
   - Static dosyada sakla
   - Fiş template'lerinde göster
   - Ayarlar sayfasında upload UI

2. **#17 - Not Sayfası Yazdırma**
   - Müşterilere tarif/bilgi yazdırma
   - Template: `note_page.html`
   - Önizleme + PDF

3. **Ayarlar Sayfası UI**
   - Restaurant bilgileri düzenleme
   - Yazıcı ayarları
   - Fiş footer düzenleme
   - Logo yükleme

---

## 🔄 DEVAM EDEN ÇALIŞMA

**FAZ 3 - Yazıcı & Fiş** devam ediyor.

**Sonraki Adımlar:**
1. Logo yükleme sistemi
2. Not sayfası template
3. Ayarlar sayfası UI

---

## 📋 YAKIN GELECEK (FAZ 4)

### Yeni Eklenen Talepler (Henüz başlanmadı)
- **#36b** - Masa notu masaya tıklayınca açılsın
- **#37** - Masa notu siparişe özel olsun (order_notes tablosu)
- **#38** - Sipariş iptal butonu (modal'da) - ✅ YAPILDI
- **#39** - Ürün silme uyarısı (geçmiş siparişlerde kullanılmışsa)

### FAZ 4 - Raporlama
- **#7** - Raporlar sayfası
- **#31** - Bahşiş raporları
- **#33 UI** - İsim düzenleme frontend
- **#34 UI** - Read-only sipariş modal

---

## 🛠️ ÖNEMLİ KOMUTLAR

### Servis Yönetimi
```bash
sudo systemctl restart firinna-pos
sudo systemctl status firinna-pos
journalctl -u firinna-pos -n 50 --no-pager
```

### Geliştirme
```bash
cd /opt/firinna-pos
source venv/bin/activate  # Virtual env aktifleştir
pip install <paket> --break-system-packages  # Sistem paketleri için
/opt/firinna-pos/venv/bin/pip install <paket>  # Venv için
```

### Git İşlemleri
```bash
git add .
git status
git commit -m "Mesaj"
git push
# Kullanıcı: mcturan
# Token gerekli (https://github.com/settings/tokens)
```

### Database
```bash
sqlite3 pos_data.db
.tables
.schema orders
SELECT * FROM settings;
.quit
```

---

## ⚠️ BİLİNEN SORUNLAR & ÇÖZÜMLER

### if __name__ Bloğu Sorunu
**Sorun:** Yeni endpoint'ler eklendikten sonra 404 hatası  
**Sebep:** `if __name__ == '__main__':` bloğu endpoint'lerden önce  
**Çözüm:** Her zaman en sona taşı:
```bash
grep -n "if __name__" app.py  # Satır numarasını bul
sed -i 'X,Yd' app.py  # Eski bloğu sil
cat >> app.py << 'EOF'

if __name__ == '__main__':
    db.init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
