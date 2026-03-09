"""
Telegram Bildirim Modülü — Fırınna POS (#41)
Stok minimum altına düştüğünde mesaj gönderir.
"""
import urllib.request
import urllib.parse
import json
import threading
import database as db


def get_bot_config():
    token = db.get_setting('telegram_bot_token', '')
    chat_id = db.get_setting('telegram_chat_id', '')
    return token, chat_id


def send_message(text: str) -> bool:
    """Telegram'a mesaj gönder. Hata olursa False döner, sistemi durdurmaz."""
    try:
        token, chat_id = get_bot_config()
        if not token or not chat_id:
            return False
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = json.dumps({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }).encode('utf-8')
        req = urllib.request.Request(url, data=payload,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            result = json.loads(resp.read())
            return result.get('ok', False)
    except Exception as e:
        print(f"[Telegram] Gönderim hatası: {e}")
        return False


def send_async(text: str):
    """Arka planda gönder — siparişi yavaşlatmaz."""
    t = threading.Thread(target=send_message, args=(text,), daemon=True)
    t.start()


def check_low_stock_after_order(order_id: int):
    """
    Sipariş sonrası minimum altına düşen stokları kontrol et.
    Sadece bu siparişte düşen kalemleri bildir — tekrar tekrar mesaj atmaz.
    """
    try:
        import sqlite3
        conn = sqlite3.connect(db.DB_PATH)
        conn.row_factory = sqlite3.Row

        # Bu siparişte etkilenen stok kalemleri
        affected = conn.execute('''
            SELECT DISTINCT r.stock_item_id
            FROM order_items oi
            JOIN recipes r ON r.product_id = oi.product_id
            WHERE oi.order_id = ? AND oi.is_complimentary = 0
        ''', (order_id,)).fetchall()

        if not affected:
            conn.close()
            return

        affected_ids = [row['stock_item_id'] for row in affected]
        placeholders = ','.join('?' * len(affected_ids))

        # Minimum altına düşenler
        low_items = conn.execute(f'''
            SELECT s.name, s.unit, s.min_quantity,
                   COALESCE(SUM(CASE WHEN sm.movement_type='in'  THEN sm.quantity
                                     WHEN sm.movement_type='out' THEN -sm.quantity
                                     WHEN sm.movement_type='adjust' THEN sm.quantity
                                     ELSE 0 END), 0) AS current_qty
            FROM stock_items s
            LEFT JOIN stock_movements sm ON sm.stock_item_id = s.id
            WHERE s.id IN ({placeholders}) AND s.active = 1 AND s.min_quantity > 0
            GROUP BY s.id
            HAVING current_qty <= s.min_quantity
        ''', affected_ids).fetchall()

        conn.close()

        if not low_items:
            return

        restaurant = db.get_setting('restaurant_name', 'Fırınna')
        lines = [f"⚠️ <b>{restaurant} — Düşük Stok Uyarısı</b>\n"]
        for item in low_items:
            qty = round(item['current_qty'], 2)
            mn  = round(item['min_quantity'], 2)
            lines.append(
                f"🔴 <b>{item['name']}</b>\n"
                f"   Mevcut: {qty} {item['unit']}  |  Minimum: {mn} {item['unit']}"
            )
        lines.append(f"\n📦 Sipariş #{order_id} sonrası tespit edildi.")
        send_async('\n'.join(lines))

    except Exception as e:
        print(f"[Telegram] Stok kontrol hatası: {e}")


def test_connection() -> dict:
    """Bağlantı testi — ayarlar sayfasından çağrılır."""
    token, chat_id = get_bot_config()
    if not token:
        return {'success': False, 'error': 'Bot token girilmemiş'}
    if not chat_id:
        return {'success': False, 'error': 'Chat ID girilmemiş'}
    ok = send_message("✅ <b>Fırınna POS</b> — Telegram bildirimleri aktif!")
    if ok:
        return {'success': True}
    return {'success': False, 'error': 'Mesaj gönderilemedi. Token veya Chat ID hatalı olabilir.'}
