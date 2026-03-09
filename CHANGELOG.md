# 📋 Fırınna POS — Sürüm Notları

---

## v1.2.0 — 2026-03-09

### ✨ Yeni Özellikler
- **Yedekleme & Senkronizasyon sayfası** — `.db` ve SQL dump indirme, dosyadan geri yükleme, sunucu yedek listesi
- **GitHub Sync** — tek sayfada Push (kod + DB dump) / Pull (kod + DB uygulama)
- **Otomatik Push/Pull** — aralıklı veya belirli saatte otomatik senkronizasyon
- **Ürün–Stok direkt bağlantısı** — sipariş kapanınca otomatik stok düşümü
- **Footer versiyon bilgisi** — ana sayfada uygulama sürümü, build tarihi, DB şema ve boyutu

### 🐛 Düzeltmeler
- Geçmiş sipariş kartı iç içe geçme (`</div>` eksikliği) giderildi
- Masa rengi modal kapatılınca anlık güncelleniyor (sekme değiştirme gerekmez)
- PDF butonu → tarayıcı önizleme (weasyprint bağımlılığı kaldırıldı)
- Favicon tüm sayfalara eklendi
- Navbar "💾 Yedek" linki tüm sayfalarda tutarlı hale getirildi

### 🖨️ Yazıcı
- Türkçe karakter desteği: transliterasyon (ğ→g, ş→s vb.), ASCII encode
- Satır genişliği 32 → 42 karakter (80mm gerçek kapasitesi)
- `rjust_row()` ile label-sol / fiyat-sağ hizalama

---

## v1.1.0 — 2026-02 (Oturum 3-5)

### ✨ Yeni Özellikler
- **Çoklu ödeme modalı** — nakit + kart + havale aynı anda, para üstü hesaplama
- **Ön muhasebe** — gelir/gider dengesi, nakit akış tablosu (Muhasebe sekmesi)
- **Excel import/export** — ürün listesi `.xlsx` olarak indir/yükle
- **Stok uyarı rozeti** — navbar'da 🔔, minimum stok altı kalemleri listeler
- **Kapalı sipariş düzenleme** — geçmiş siparişe ürün ekle/çıkar, yeniden yazdır
- **İşletme web alanı** (`/web`) — müşteriye açık menü sayfası

### 🐛 Düzeltmeler
- Kasa × Stok çapraz silme tutarsızlıkları giderildi
- Raporlar sayfası grafik render düzeltmesi
- Saat dilimi UTC → TR+3 düzeltmesi

---

## v1.0.0 — 2026-01 (Oturum 1-2)

### 🎉 İlk Sürüm
- Masa & bölge yönetimi (renk, durum)
- Sipariş alma, ikram, mutfak notu
- ESC/POS fiş yazdırma (XPrinter POS80, 192.168.1.99:9100)
- Stok takibi + reçete yönetimi
- Kasa modülü (nakit/banka), masraf takibi
- Raporlar (5 sekme, grafik, CSV export)
- Ayarlar (işletme, yazıcı, logo, fiş notu)
- Telegram bildirimleri (sipariş + stok uyarısı)
- Responsive CSS — telefon/tablet uyumlu

---

*Fırınna POS — Muhammed Cevad Turan (TA1XTA) © 2026*
