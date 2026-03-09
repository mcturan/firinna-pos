# 🗺️ Fırınna POS — Roadmap

Son güncelleme: Mart 2026

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
- [x] #11 Ödeme yöntemi (nakit/kart/havale)
- [x] #12 Adisyon bölme (split)
- [x] #13 Geçmiş sipariş girişi (gün içi)
- [x] #14 Sipariş silme

---

## ✅ FAZ 3 — Muhasebe & Stok (Tamamlandı)

- [x] #20 Stok takibi (giriş/çıkış/düzeltme)
- [x] #21 Reçete yönetimi (ürün → hammadde)
- [x] #22 Kasa modülü (nakit/banka ayrımı)
- [x] #23 Gelişmiş masraf yönetimi (kategori, ödeme kaynağı)
- [x] #24 Raporlar (5 sekme, grafik, CSV export)
- [x] #25 Kasa × Stok çapraz silme
- [x] #26 Fiş önizleme & PDF export
- [x] #27 Logo & fiş ayarları
- [x] #28 Not fişi yazdırma
- [x] #29 Ayarlar sayfası (işletme, yazıcı, logo)

---

## ✅ FAZ 4 — Stabilizasyon & Responsive (Tamamlandı)

- [x] #30 Saat dilimi düzeltmesi (UTC→TR)
- [x] #31 Responsive CSS — telefon uyumlu (tam yeniden yazım)
- [x] #32 Buton & yazı boyutu tutarlılığı (design system)
- [x] #33 Fiş İptal düzeltmesi (JS syntax + lazy order create)
- [x] #34 Kalıntı sipariş temizleme (cleanup-empty endpoint)
- [x] #35 Masa durumu senkronizasyonu (iptal → boş)
- [x] #36 Müşteri fişinden mutfak notlarını kaldırma

---

## 🔄 FAZ 5 — Senkronizasyon & Bildirimler (Sıradaki)

- [ ] **#40 GitHub Sync** — tek butonla push/pull + DB yedek dahil (iki PC senkron)
  - `git push` ile kod + DB yedek
  - `git pull` ile diğer makinede güncelleme
  - Tarayıcıdan erişilebilir UI

- [ ] **#41 Telegram Stok Bildirimi** — minimum stok aşılınca otomatik mesaj
  - Bot token + chat ID ayarları sayfasına eklenecek
  - Stok girişinde kontrol
  - Günlük özet mesajı (isteğe bağlı)

---

## 📋 FAZ 6 — Ön Muhasebe (Orta Vadeli)

- [ ] **#50 Gelir/Gider Dengesi** — transactions altyapısı hazır
  - Günlük/haftalık/aylık bilanço
  - Nakit akış tablosu

- [ ] **#51 Kar/Zarar Raporu**
  - Brüt / net kar hesaplama
  - Kategori bazlı maliyet analizi

- [ ] **#52 KDV Hesaplama** — isteğe bağlı KDV oranı/ürün

---

## 🔮 FAZ 7 — Müşteri Kanalları (Sonraya)

- [ ] **#60 Self-Servis QR Sipariş**
  - Masaya QR kod yapıştır, müşteri kendi siparişini verir
  - Garson onay ekranı (kasada bildirim + onayla/reddet)
  - Mutfağa otomatik iletim

- [ ] **#61 Fiş QR & Google Review**
  - Fişin altına QR kod (Google Review linki)
  - Ayarlar sayfasından URL girişi

- [ ] **#62 WhatsApp Fiş Gönderme**
  - Telefon numarası → WhatsApp web linki

---

## 🐛 Bilinen Sorunlar / Notlar

| # | Konu | Durum |
|---|------|-------|
| — | Veritabanı tek dosya (pos_data.db), RAID yok | Günlük yedek önerilir |
| — | PDF export tarayıcı print dialog kullanıyor | Native PDF henüz yok |
| — | İki bilgisayar arası senkronizasyon manuel | #40 ile çözülecek |

---

*Fırınna POS — TA1XTA © 2026*
