import socket
from datetime import datetime
import database as db

class ThermalPrinter:
    """XPrinter POS80 için ESC/POS komutları"""
    
    def __init__(self, printer_type='receipt'):
        """
        printer_type: 'receipt' (müşteri) veya 'kitchen' (mutfak)
        """
        if printer_type == 'kitchen':
            self.ip = db.get_setting('kitchen_printer_ip', '192.168.1.99')
            self.port = int(db.get_setting('kitchen_printer_port', 9100))
        else:
            self.ip = db.get_setting('printer_ip', '192.168.1.99')
            self.port = int(db.get_setting('printer_port', 9100))
        
        self.printer_type = printer_type
    
    def send_command(self, data):
        """Yazıcıya komut gönder"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((self.ip, self.port))
            sock.sendall(data)
            sock.close()
            return True
        except Exception as e:
            print(f"Yazıcı hatası: {e}")
            return False
    
    def print_receipt(self, order_data):
        """Müşteri adisyonu yazdır"""
        ESC = b'\x1B'
        INIT = ESC + b'@'
        CODEPAGE = ESC + b't\x06'   # Code Page 857 (Turkish)
        CENTER = ESC + b'a\x01'
        LEFT = ESC + b'a\x00'
        BOLD_ON = ESC + b'E\x01'
        BOLD_OFF = ESC + b'E\x00'
        CUT = ESC + b'd\x05' + ESC + b'm'
        
        # Settings'ten bilgileri al
        restaurant_name = db.get_setting('restaurant_name', 'Fırınna')
        restaurant_address = db.get_setting('restaurant_address', '')
        restaurant_phone = db.get_setting('restaurant_phone', '')
        restaurant_web = db.get_setting('restaurant_web', '')
        footer_note = db.get_setting('receipt_footer', 'Afiyet olsun!')
        
        data = INIT
        data += CODEPAGE
        
        # Header
        data += CENTER
        data += BOLD_ON
        data += f"{restaurant_name}\n".encode('cp857', errors='replace')
        data += BOLD_OFF
        
        if restaurant_address:
            data += f"{restaurant_address}\n".encode('cp857', errors='replace')
        if restaurant_phone:
            data += f"Tel: {restaurant_phone}\n".encode('cp857', errors='replace')
        if restaurant_web:
            data += f"{restaurant_web}\n".encode('cp857', errors='replace')
        
        data += "================================\n".encode('cp857', errors='replace')
        data += LEFT
        
        # Tarih/Saat
        now = datetime.now().strftime('%d.%m.%Y %H:%M')
        data += f"Tarih: {now}\n".encode('cp857', errors='replace')
        data += f"Masa: {order_data.get('table_name', '-')}\n".encode('cp857', errors='replace')
        data += f"Siparis No: {order_data.get('order_id', '-')}\n".encode('cp857', errors='replace')
        data += "================================\n".encode('cp857', errors='replace')
        
        # Ürünler
        for item in order_data.get('items', []):
            name = item.get('product_name', 'Urun')
            qty = item.get('quantity', 1)
            price = item.get('price', 0)
            total = qty * price
            
            if item.get('is_complimentary'):
                data += f"{qty}x {name}".encode('cp857', errors='replace')
                data += " (IKRAM)\n".encode('cp857', errors='replace')
            else:
                line = f"{qty}x {name}"
                price_str = f"{total:.2f} TL"
                spaces = 32 - len(line) - len(price_str)
                data += f"{line}{' ' * spaces}{price_str}\n".encode('cp857', errors='replace')
            
        data += "================================\n".encode('cp857', errors='replace')
        
        # Toplam
        subtotal = order_data.get('subtotal', 0)
        discount = order_data.get('discount_value', 0)
        total = order_data.get('total', 0)
        
        data += f"Ara Toplam:            {subtotal:.2f} TL\n".encode('cp857', errors='replace')
        
        if discount > 0:
            discount_text = order_data.get('discount_reason', 'Indirim')
            data += f"{discount_text}:           -{discount:.2f} TL\n".encode('cp857', errors='replace')
        
        data += BOLD_ON
        data += f"TOPLAM:                {total:.2f} TL\n".encode('cp857', errors='replace')
        data += BOLD_OFF
        data += "================================\n".encode('cp857', errors='replace')
        
        # Ödeme bilgisi
        if order_data.get('payment_cash', 0) > 0:
            data += f"Nakit:                 {order_data['payment_cash']:.2f} TL\n".encode('cp857', errors='replace')
        if order_data.get('payment_card', 0) > 0:
            data += f"Kart:                  {order_data['payment_card']:.2f} TL\n".encode('cp857', errors='replace')
        if order_data.get('tip_amount', 0) > 0:
            data += f"Bahsis:                {order_data['tip_amount']:.2f} TL\n".encode('cp857', errors='replace')
        
        # Footer
        data += "\n".encode('cp857', errors='replace')
        data += CENTER
        for line in footer_note.split('\n'):
            data += f"{line}\n".encode('cp857', errors='replace')
        
        data += "\n\n".encode('cp857', errors='replace')
        data += CUT
        
        return self.send_command(data)
    
    def print_kitchen_order(self, order_data):
        """Mutfak fişi yazdır (sadece ürünler + notlar)"""
        ESC = b'\x1B'
        INIT = ESC + b'@'
        CODEPAGE = ESC + b't\x06'   # Code Page 857 (Turkish)
        CENTER = ESC + b'a\x01'
        LEFT = ESC + b'a\x00'
        BOLD_ON = ESC + b'E\x01'
        BOLD_OFF = ESC + b'E\x00'
        DOUBLE_HEIGHT = ESC + b'!\x10'
        NORMAL = ESC + b'!\x00'
        CUT = ESC + b'd\x05' + ESC + b'm'
        
        data = INIT
        data += CODEPAGE
        data += CENTER
        data += BOLD_ON + DOUBLE_HEIGHT
        data += "MUTFAK SIPARIS\n".encode('cp857', errors='replace')
        data += NORMAL + BOLD_OFF
        data += "================================\n".encode('cp857', errors='replace')
        data += LEFT
        
        # Tarih/Saat
        now = datetime.now().strftime('%d.%m.%Y %H:%M')
        data += BOLD_ON
        data += f"MASA: {order_data.get('table_name', '-')}\n".encode('cp857', errors='replace')
        data += f"Saat: {now}\n".encode('cp857', errors='replace')
        data += BOLD_OFF
        data += "================================\n".encode('cp857', errors='replace')
        
        # Ürünler (ikramlar hariç)
        for item in order_data.get('items', []):
            if item.get('is_complimentary'):
                continue
            
            name = item.get('product_name', 'Urun')
            qty = item.get('quantity', 1)
            
            data += BOLD_ON + DOUBLE_HEIGHT
            data += f"{qty}x ".encode('cp857', errors='replace')
            data += NORMAL
            data += f"{name}\n".encode('cp857', errors='replace')
            data += BOLD_OFF
            
            if item.get('kitchen_notes'):
                data += f">>> {item.get('kitchen_notes')}\n".encode('cp857', errors='replace')
            
            data += "--------------------------------\n".encode('cp857', errors='replace')
        
        data += "\n\n".encode('cp857', errors='replace')
        data += CUT
        
        return self.send_command(data)

    def test_print(self):
        """Bağlantı ve yazdırma testi"""
        ESC = b'\x1B'
        INIT = ESC + b'@'
        CENTER = ESC + b'a\x01'
        BOLD_ON = ESC + b'E\x01'
        BOLD_OFF = ESC + b'E\x00'
        CUT = ESC + b'd\x05' + ESC + b'm'

        now = datetime.now().strftime('%d.%m.%Y %H:%M')
        data = INIT
        data += CENTER
        data += BOLD_ON
        data += b'FIRINNA POS\n'
        data += BOLD_OFF
        data += b'================================\n'
        data += f'Test: {now}\n'.encode('cp857', errors='replace')
        data += b'================================\n'
        data += b'Yazici baglantisi basarili!\n'
        data += b'\n\n'
        data += CUT
        return self.send_command(data)

    def print_note(self, title, note_text):
        """Serbest metin not fişi yazdır (#17)"""
        ESC = b'\x1B'
        INIT = ESC + b'@'
        CENTER = ESC + b'a\x01'
        LEFT = ESC + b'a\x00'
        BOLD_ON = ESC + b'E\x01'
        BOLD_OFF = ESC + b'E\x00'
        CUT = ESC + b'd\x05' + ESC + b'm'

        restaurant_name = db.get_setting('restaurant_name', 'Fırınna')
        now = datetime.now().strftime('%d.%m.%Y %H:%M')

        data = INIT
        data += CENTER
        data += BOLD_ON
        data += f"{restaurant_name}\n".encode('cp857', errors='replace')
        data += BOLD_OFF
        data += "================================\n".encode('cp857', errors='replace')
        data += BOLD_ON
        data += f"--- {title} ---\n".encode('cp857', errors='replace')
        data += BOLD_OFF
        data += f"{now}\n".encode('cp857', errors='replace')
        data += "================================\n".encode('cp857', errors='replace')
        data += LEFT
        data += "\n".encode('cp857', errors='replace')
        for line in note_text.split('\n'):
            data += f"{line}\n".encode('cp857', errors='replace')
        data += "\n================================\n".encode('cp857', errors='replace')
        data += "\n\n".encode('cp857', errors='replace')
        data += CUT

        return self.send_command(data)

