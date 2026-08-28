# Firinna POS — Sunucu Yapılandırma Dosyaları

Bu klasör, Raspberry Pi sunucusuna (192.168.1.2) kurulu olan servis
ve nginx konfigürasyon dosyalarının referans kopyalarını içerir.

## Mimari (28 Ağustos 2026 itibarıyla)

```
İnternet / LAN
     │
     ├─► :80 / :443  ── Nginx ──► firinna.com       (web sitesi)
     │                       └──► pos.firinna.com   (POS, Basic Auth)
     │                               └──► proxy → Gunicorn :5001
     │
     └─► :5000 ───────── Nginx ──► /static/tv_media/  (video → doğrudan dosya)
                               ├──► /static/           (APK → doğrudan dosya)
                               └──► /                  (POS app → Gunicorn :5001)
```

## Neden Gunicorn :5001, Nginx :5000?

**Sorun (28.08.2026 öncesi):**
- Gunicorn sync worker, port 5000'de tüm trafiği karşılıyordu.
- Mi TV Stick 1.mp4 (356 MB) dosyasını XHR blob olarak indirmeye çalışıyordu.
- Gunicorn worker, büyük dosyayı aktarırken 30 sn default timeout'a düşüp
  SIGKILL yiyordu. TV bozuluyordu, diğer POS istekleri engelleniyordu.

**Çözüm:**
- Gunicorn 127.0.0.1:5001'e alındı (dışarıya doğrudan kapalı).
- Nginx port 5000'de öne geçirildi.
- /static/tv_media/ ve /static/ → Nginx'ten doğrudan dosya sistemi.
- Geri kalan istekler → proxy_pass http://127.0.0.1:5001

**Sonuç:** 1.mp4 ~88 MB/s hızda, gunicorn timeout olmadan akıyor.

## Dosyalar

### firinna-pos.service
```bash
sudo cp firinna-pos.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now firinna-pos
```

### nginx-firinna-lan.conf
```bash
sudo cp nginx-firinna-lan.conf /etc/nginx/sites-available/firinna-lan.conf
sudo ln -sf /etc/nginx/sites-available/firinna-lan.conf /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

> Not: firinna.conf (pos.firinna.com, firinna.com) Certbot tarafından yönetilir.
> O dosyadaki proxy_pass adresleri de 127.0.0.1:5001 olmalıdır.
