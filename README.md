# 🍽️ Fırınna POS

**Fırınna Cafe** için özel geliştirilmiş, hafif ve tam özellikli satış noktası (POS) uygulaması.  
Flask + SQLite tabanlı, internet bağlantısı gerektirmez, ağdaki her cihazdan tarayıcıyla erişilir.

---

## ✨ Özellikler

| Modül | Açıklama |
|---|---|
| 🪑 Masa & Bölge | Bölgelere göre masa yönetimi, dolu/boş gösterge |
| 🛒 Sipariş | Hızlı ürün ekleme, miktar düzenleme, ikram, mutfak notu |
| 🖨️ Fiş Yazdırma | ESC/POS ile müşteri fişi + mutfak fişi (XPrinter POS80) |
| 📋 Geçmiş Sipariş | Gün içi kapanmış siparişler, yeniden açma |
| 📦 Stok | Stok girişi, hareket takibi, min stok uyarısı |
| 💰 Kasa | Nakit/banka ayrımı, masraf girişi, dönem özeti |
| 📊 Raporlar | Günlük/haftalık/aylık satış, ürün bazlı analiz, CSV export |
| ⚙️ Ayarlar | Yazıcı IP, işletme adı, logo, fiş notu |

---

## 🖥️ Gereksinimler

### Donanım
- Bilgisayar: Pardus / Ubuntu / Debian Linux (Raspberry Pi de çalışır)
- Yazıcı: **XPrinter POS80** veya ESC/POS uyumlu termal yazıcı (ağ bağlantılı)
- Ağ: Yazıcı ve POS bilgisayarı aynı yerel ağda olmalı

### Yazılım
| Bağımlılık | Minimum Sürüm | Kurulum |
|---|---|---|
| Python | 3.10 | `sudo apt install python3 python3-pip python3-venv` |
| Flask | 3.0 | `pip install flask` |
| Pillow | 10.0 | `pip install pillow` |
| SQLite | 3.x | Python ile birlikte gelir |

> Yazıcı saf TCP/IP socket ile haberleşir, ek sürücü gerekmez.

---

## 🚀 Kurulum

### 1. Otomatik (Önerilen)

```bash
git clone https://github.com/mcturan/firinna-pos.git
cd firinna-pos
sudo bash install.sh
```

Script şunları yapar:
- Python virtual environment oluşturur
- Bağımlılıkları kurar
- Systemd servisi oluşturur ve başlatır
- Yazıcı IP'sini sorar

### 2. Manuel

```bash
# Repoyu indir
git clone https://github.com/mcturan/firinna-pos.git
cd firinna-pos

# Sanal ortam oluştur
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları kur
pip install -r requirements.txt

# Uygulamayı başlat
python app.py
```

Tarayıcıdan `http://localhost:5000` adresine git.

### 3. Systemd Servisi (Otomatik Başlatma)

```bash
sudo nano /etc/systemd/system/firinna-pos.service
```

```ini
[Unit]
Description=Firinna POS Service
After=network.target

[Service]
Type=simple
User=KULLANICI_ADI
WorkingDirectory=/opt/firinna-pos
Environment="PATH=/opt/firinna-pos/venv/bin"
ExecStart=/opt/firinna-pos/venv/bin/python /opt/firinna-pos/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable firinna-pos
sudo systemctl start firinna-pos
```

---

## ⚙️ Yapılandırma

Uygulama ayarları tarayıcıdan **⚙️ Ayarlar** menüsünden yapılır:

| Ayar | Açıklama |
|---|---|
| İşletme Adı | Fişlerde görünen başlık |
| Yazıcı IP | Müşteri fişi yazıcısı (örn: `192.168.1.100`) |
| Mutfak Yazıcısı IP | Mutfak fişi yazıcısı (örn: `192.168.1.101`) |
| Yazıcı Portu | Varsayılan `9100` |
| Fiş Notu | Fişin altında çıkan teşekkür notu |

> Yazıcı ayarları veritabanında saklanır, `.env` dosyası gerekmez.

---

## 🗃️ Veritabanı

Uygulama `pos_data.db` (SQLite) kullanır. İlk çalıştırmada otomatik oluşturulur.

**Yedekleme:**
```bash
cp /opt/firinna-pos/pos_data.db ~/yedekler/pos_$(date +%Y%m%d).db
```

**Güncelleme sonrası migrasyon:**
```bash
python migration_faz1.py   # FAZ 1 → FAZ 2
python migration_faz2.py   # FAZ 2 → FAZ 3
```

---

## 🔧 Servis Yönetimi

```bash
sudo systemctl start firinna-pos      # Başlat
sudo systemctl stop firinna-pos       # Durdur
sudo systemctl restart firinna-pos    # Yeniden başlat
sudo systemctl status firinna-pos     # Durum
sudo journalctl -u firinna-pos -f     # Canlı log
```

---

## 📁 Proje Yapısı

```
firinna-pos/
├── app.py                  # Flask uygulama ve tüm API endpoint'leri
├── database.py             # SQLite veritabanı işlemleri
├── printer.py              # ESC/POS yazıcı sınıfı
├── requirements.txt        # Python bağımlılıkları
├── install.sh              # Otomatik kurulum scripti
├── migration_faz1.py       # v1→v2 veritabanı migrasyonu
├── migration_faz2.py       # v2→v3 veritabanı migrasyonu
├── static/
│   └── css/style.css       # Tüm CSS (responsive, design system)
└── templates/
    ├── index.html          # Ana sayfa (masa görünümü + sipariş modali)
    ├── products.html       # Ürün & kategori yönetimi
    ├── tables.html         # Masa & bölge yönetimi
    ├── kasa.html           # Kasa & muhasebe
    ├── expenses.html       # Masraf girişi
    ├── stok.html           # Stok takibi
    ├── recete.html         # Reçete yönetimi
    ├── reports.html        # Raporlar
    ├── settings.html       # Ayarlar
    └── receipts/
        ├── customer_receipt.html
        └── kitchen_receipt.html
```

---

## 🗺️ Roadmap

Bkz: [ROADMAP.md](ROADMAP.md)

---

## 👤 Geliştirici

**Muhammed Cevad Turan** — TA1XTA  
Fırınna Cafe, Beyoğlu İstanbul

---

*Fırınna POS — TA1XTA © 2026*
