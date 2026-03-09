# 🗺️ Fırınna POS — Roadmap

Son güncelleme: 2026-03-09

---

## ✅ FAZ 1 — Temel POS (Tamamlandı)

- [x] #1 Kategori yönetimi (renk kodlu)
- [x] #2 Ürün yönetimi (fiyat, kategori)
- [x] #3 Masa & bölge yönetimi
- [x] #4 Sipariş alma (ürün ekleme, miktar)
- [x] #5 Müşteri fişi yazdırma (ESC/POS, XPrinter)
- [x] #6 Masraf takibi (basit giriş)
- [x] #7 Temel raporlama (günlük özet)

---

## ✅ FAZ 2 — UI & Sipariş Geliştirmeleri (Tamamlandı)

- [x] #8  İkram (complimentary) özelliği
- [x] #9  Miktar düzenleme (+/-)
- [x] #10 Mutfak notu (ürün bazlı)
- [x] #11 Ödeme yöntemi (nakit/kart/havale) + çoklu ödeme modalı
- [x] #12 Adisyon bölme (split)
- [x] #13 Geçmiş sipariş girişi ve düzenleme
- [x] #14 Sipariş silme

---

## ✅ FAZ 3 — Muhasebe & Stok (Tamamlandı)

- [x] #20 Stok takibi (giriş/çıkış/düzeltme)
- [x] #21 Reçete yönetimi (ürün → hammadde)
- [x] #22 Kasa modülü (nakit/banka ayrımı)
- [x] #23 Gelişmiş masraf yönetimi (kategori, ödeme kaynağı)
- [x] #24 Raporlar (5 sekme, grafik, CSV export)
- [x] #25 Kasa × Stok çapraz silme
- [x] #26 Fiş önizleme (tarayıcı print → PDF)
- [x] #27 Logo & fiş ayarları
- [x] #28 Not fişi yazdırma
- [x] #29 Ayarlar sayfası (işletme, yazıcı, logo)

---

## ✅ FAZ 4 — Stabilizasyon & Responsive (Tamamlandı)

- [x] #30 Saat dilimi düzeltmesi (UTC→TR+3)
- [x] #31 Responsive CSS — telefon uyumlu
- [x] #32 Buton & yazı boyutu tutarlılığı
- [x] #33 Fiş iptal düzeltmesi
- [x] #34 Kalıntı sipariş temizleme
- [x] #35 Masa durumu senkronizasyonu
- [x] #36 Müşteri fişinden mutfak notlarını kaldırma
- [x] #37 Excel import/export (ürün listesi)
- [x] #38 Stok uyarı rozeti (navbar 🔔)
- [x] #39 İşletme web alanı (/web müşteri menü sayfası)

---

## ✅ FAZ 5 — Senkronizasyon & Yedekleme (Tamamlandı)

- [x] #40 GitHub Sync — Push (kod + DB dump) / Pull (kod + DB uygulama)
- [x] #41 Otomatik push/pull — aralıklı veya belirli saatte
- [x] #42 Yedekleme sayfası — .db / SQL indir, dosyadan geri yükle
- [x] #43 Sunucu yedek listesi ve yerel geri yükleme
- [x] #44 Ürün–Stok direkt bağlantısı (sipariş kapanınca otomatik stok düşümü)
- [x] #45 Türkçe ESC/POS yazdırma (transliterasyon, 42 char hizalama)
- [x] #46 Favicon & marka tutarlılığı
- [x] #47 Footer versiyon bilgisi (uygulama + DB şema + boyutu)
- [x] #48 Telegram bildirimleri (sipariş + stok uyarısı)

---

## 🟡 FAZ 6 — Mobil & PWA (Sıradaki)

- [ ] **#55 PWA manifest** — "Ana ekrana ekle" (tarayıcıdan uygulama gibi)
  - `manifest.json`, `service-worker.js`
  - Offline sipariş görüntüleme
  - Tahmini süre: ~1 saat

- [ ] **#56 Flutter Android App** — Proje dokümanı hazır
  - Garson uygulaması: sipariş al, masa seç
  - Mutfak ekranı: gelen siparişler (sadece görüntüleme)
  - Push bildirim (Firebase)

---

## 📋 FAZ 7 — Müşteri Kanalları (Sonraya)

- [ ] **#60 Self-Servis QR Sipariş**
  - Masaya QR, müşteri kendi siparişini verir
  - Garson onay ekranı

- [ ] **#61 Fiş QR & Google Review**
  - Fişin altına QR (Google Review linki)

- [ ] **#62 WhatsApp Fiş Gönderme**

---

## 🐛 Bilinen Sorunlar

| # | Konu | Durum |
|---|------|-------|
| — | Türkçe karakter yazıcıda transliterasyon (ğ→g vb.) | Kalıcı çözüm: CP857 yazıcı firmware |
| — | PDF export tarayıcı print dialog kullanıyor | Native PDF (weasyprint) kurulmadı |
| — | İki PC pull sırasında DB çakışma riski | SQL dump text formatı ile minimize edildi |

---

*Fırınna POS — Muhammed Cevad Turan (TA1XTA) © 2026*
