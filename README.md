# 🍽️ Fırınna POS Sistemi

Fırınna Cafe & Restaurant için özel geliştirilmiş hafif ve kullanışlı POS uygulaması.

## ✨ Özellikler

✅ **Kategori & Ürün Yönetimi**
- Renk kodlu kategoriler
- Sınırsız ürün ekleme
- Hızlı ürün seçimi

✅ **Masa & Bölge Yönetimi**
- Bölgelere göre masa organizasyonu
- Dolu/boş masa göstergesi
- Sınırsız masa ve bölge

✅ **Sipariş Yönetimi**
- Hızlı sipariş alma
- Gerçek zamanlı sipariş özeti
- Adisyon yazdırma (XPrinter POS80)

✅ **Masraf Takibi**
- Kategorize masraf girişi
- Tarih bazlı filtreleme
- Toplam masraf özeti

✅ **Raporlama**
- Günlük satış raporları
- Ürün bazlı analiz
- Net kar/zarar hesaplama
- Rapor yazdırma

✅ **Yedekleme & Güvenlik**
- Otomatik veritabanı yedekleme
- Manuel yedek alma
- Test verilerini temizleme

✅ **Çoklu Cihaz Desteği**
- Web tabanlı (kurulum yok)
- PC, tablet, telefon uyumlu
- Responsive tasarım

## 📋 Gereksinimler

- **İşletim Sistemi:** Pardus Linux (herhangi bir sürüm)
- **Python:** 3.8 veya üstü
- **Yazıcı:** XPrinter POS80 (Ethernet bağlantılı)
- **Ağ:** Lokal ağ erişimi (opsiyonel)

## 🚀 Kurulum

### Adım 1: Dosyaları indirin
```bash
# Tüm dosyaları bir klasöre kopyalayın (örn: /opt/firinna-pos)
cd /opt
sudo mkdir firinna-pos
cd firinna-pos
# Dosyaları buraya kopyalayın
```

### Adım 2: Kurulum scriptini çalıştırın
```bash
sudo chmod +x install.sh
sudo bash install.sh
```

Script otomatik olarak:
- Python ve bağımlılıkları kurar
- Veritabanını oluşturur
- Sistem servisi kurar
- Uygulamayı başlatır

### Adım 3: Yazıcı ayarları
Kurulum sırasında XPrinter POS80'in IP adresini girin.

**Yazıcı IP'sini bulmak için:**
1. Yazıcıyı açın
2. Test sayfası çıktısı alın (genelde FEED tuşuna 3 saniye basılı tutarak)
3. Test sayfasında IP adresi yazıyor olacak

## 📱 Kullanım

### İlk Kurulum Sonrası

1. **Tarayıcıdan açın:** `http://localhost:5000`

2. **Bölge ekleyin:**
   - "Masa Yönetimi" → Bölge ekle
   - Örnek: "İç Mekan", "Dış Mekan", "Teras"

3. **Masalar ekleyin:**
   - "Masa Yönetimi" → Masa ekle
   - Örnek: "Masa 1", "Masa 2", vb.

4. **Kategori oluşturun:**
   - "Ürünler" → Kategori ekle
   - Örnek: "Sıcak İçecekler", "Soğuk İçecekler", "Tatlılar"

5. **Ürün ekleyin:**
   - "Ürünler" → Ürün ekle
   - İsim, kategori, fiyat girin

### Sipariş Alma

1. Ana sayfada masa seçin (dolu masalar kırmızı, boş masalar yeşil)
2. Kategori seçin
3. Ürünlere tıklayarak sipariş ekleyin
4. "Adisyon Yazdır" ile fişi yazdırın
5. "Hesap Kapat" ile ödeme alın

### Masraf Girişi

1. "Masraflar" sayfasına gidin
2. Açıklama, kategori ve tutarı girin
3. "Ekle" butonuna basın

### Raporlar

1. "Raporlar" sayfasına gidin
2. Tarih seçin
3. "Rapor Getir" ile günlük özeti görün
4. "Yazdır" ile raporu yazıcıdan çıktı alın

## 🔧 Ayarlar

### Yazıcı IP Değiştirme
1. "Raporlar" → Yazıcı Ayarları
2. Yeni IP ve Port girin
3. "Kaydet" butonuna basın
4. "Test" ile bağlantıyı kontrol edin

### Yedekleme

**Manuel yedek:**
1. "Raporlar" → Yedekleme
2. "Yedek Al" butonuna basın
3. Yedek dosyası `backups/` klasörüne kaydedilir

**Otomatik yedek:**
- Sistem her gece 03:00'te otomatik yedek alır
- Yedekler: `backups/pos_backup_YYYYMMDD_HHMMSS.db`

### Test Verilerini Temizleme

**DİKKAT:** Bu işlem geri alınamaz!

1. "Raporlar" → Test Verilerini Temizle
2. Bugün hariç tüm sipariş ve masrafları siler
3. Kategoriler, ürünler, masalar korunur

## 🌐 Ağ Erişimi

Uygulamaya başka cihazlardan erişmek için:

1. Bilgisayarın IP adresini öğrenin:
```bash
hostname -I
```

2. Diğer cihazlardan tarayıcıda:
```
http://[IP-ADRESİ]:5000
```

Örnek: `http://192.168.1.50:5000`

## 🛠️ Sorun Giderme

### Uygulama açılmıyor
```bash
# Servis durumunu kontrol edin
sudo systemctl status firinna-pos

# Logları görün
sudo journalctl -u firinna-pos -f

# Yeniden başlatın
sudo systemctl restart firinna-pos
```

### Yazıcı çalışmıyor
1. Yazıcının açık olduğundan emin olun
2. IP adresinin doğru olduğunu kontrol edin
3. Aynı ağda olduğunuzu doğrulayın
4. Test yazdırma yapın

### Veritabanı hatası
```bash
# Veritabanını yeniden oluştur
cd /opt/firinna-pos
source venv/bin/activate
rm pos_data.db
python3 -c "import database; database.init_db()"
```

## 📂 Dosya Yapısı

```
firinna-pos/
├── app.py              # Ana Flask uygulaması
├── database.py         # Veritabanı işlemleri
├── printer.py          # Yazıcı kontrolü
├── requirements.txt    # Python bağımlılıkları
├── install.sh          # Kurulum scripti
├── pos_data.db         # SQLite veritabanı
├── backups/            # Yedekler
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
└── templates/
    ├── index.html      # Ana sayfa (masalar)
    ├── products.html   # Ürün yönetimi
    ├── tables.html     # Masa yönetimi
    ├── expenses.html   # Masraflar
    └── reports.html    # Raporlar
```

## 🔐 Güvenlik

- Uygulama sadece lokal ağdan erişilebilir
- Kullanıcı adı/şifre yok (iç kullanım için)
- Hassas veri internet üzerinden paylaşılmaz

## 💾 Yedekleme Stratejisi

1. **Günlük otomatik yedek** (03:00)
2. **Manuel yedek** (istediğiniz zaman)
3. **Yedekleri harici diske kopyalayın** (haftalık önerilen)

```bash
# Yedekleri USB'ye kopyalama
cp backups/* /media/usb/firinna-backups/
```

## 🆘 Destek

Sorun yaşarsanız:
1. Log dosyalarını kontrol edin
2. Yazıcı bağlantısını test edin
3. Servisi yeniden başlatın

## 📄 Lisans

Bu yazılım Fırınna Cafe & Restaurant için özel geliştirilmiştir.
Kişisel kullanım içindir.

---

**Geliştirici:** Claude (Anthropic)  
**Versiyon:** 1.0  
**Tarih:** Şubat 2025  
**İletişim:** Muhammed Cevad Turan (TA1XTA)

## 📋 Dokümantasyon

- **[🗺️ Roadmap](https://htmlpreview.github.io/?https://github.com/mcturan/firinna-pos/blob/main/roadmap.html)** - Geliştirme yol haritası ve özellik durumları
- **[📝 Changelog](https://htmlpreview.github.io/?https://github.com/mcturan/firinna-pos/blob/main/CHANGELOG.html)** - Sürüm notları ve değişiklik geçmişi

