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
        CODEPAGE = ESC + b't\x21'   # Code Page 857/Turkish (0x21=33)
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

        # Logo
        logo_url = db.get_setting('logo_url', '')
        if logo_url:
            logo_bytes = self._image_to_escpos(logo_url)
            if logo_bytes:
                data += logo_bytes
                data += b'\n'

        # Header
        data += CENTER
        data += BOLD_ON
        data += f"{restaurant_name}\n".encode('cp1254', errors='replace')
        data += BOLD_OFF
        
        if restaurant_address:
            data += f"{restaurant_address}\n".encode('cp1254', errors='replace')
        if restaurant_phone:
            data += f"Tel: {restaurant_phone}\n".encode('cp1254', errors='replace')
        if restaurant_web:
            data += f"{restaurant_web}\n".encode('cp1254', errors='replace')
        
        data += "================================\n".encode('cp1254', errors='replace')
        data += LEFT
        
        # Tarih/Saat
        now = datetime.now().strftime('%d.%m.%Y %H:%M')
        data += f"Tarih: {now}\n".encode('cp1254', errors='replace')
        data += f"Masa: {order_data.get('table_name', '-')}\n".encode('cp1254', errors='replace')
        data += f"Siparis No: {order_data.get('order_id', '-')}\n".encode('cp1254', errors='replace')
        data += "================================\n".encode('cp1254', errors='replace')
        
        # Ürünler
        for item in order_data.get('items', []):
            name = item.get('product_name', 'Urun')
            qty = item.get('quantity', 1)
            price = item.get('price', 0)
            total = qty * price
            
            if item.get('is_complimentary'):
                data += f"{qty}x {name}".encode('cp1254', errors='replace')
                data += " (IKRAM)\n".encode('cp1254', errors='replace')
            else:
                line = f"{qty}x {name}"
                price_str = f"{total:.2f} TL"
                spaces = 32 - len(line) - len(price_str)
                data += f"{line}{' ' * spaces}{price_str}\n".encode('cp1254', errors='replace')
            
        data += "================================\n".encode('cp1254', errors='replace')
        
        # Toplam
        subtotal = order_data.get('subtotal', 0)
        discount = order_data.get('discount_value', 0)
        total = order_data.get('total', 0)
        
        data += f"Ara Toplam:            {subtotal:.2f} TL\n".encode('cp1254', errors='replace')
        
        if discount > 0:
            discount_text = order_data.get('discount_reason', 'Indirim')
            data += f"{discount_text}:           -{discount:.2f} TL\n".encode('cp1254', errors='replace')
        
        data += BOLD_ON
        data += f"TOPLAM:                {total:.2f} TL\n".encode('cp1254', errors='replace')
        data += BOLD_OFF
        data += "================================\n".encode('cp1254', errors='replace')
        
        # Ödeme bilgisi
        if order_data.get('payment_cash', 0) > 0:
            data += f"Nakit:                 {order_data['payment_cash']:.2f} TL\n".encode('cp1254', errors='replace')
        if order_data.get('payment_card', 0) > 0:
            data += f"Kart:                  {order_data['payment_card']:.2f} TL\n".encode('cp1254', errors='replace')
        if order_data.get('tip_amount', 0) > 0:
            data += f"Bahsis:                {order_data['tip_amount']:.2f} TL\n".encode('cp1254', errors='replace')
        
        # Footer
        data += "\n".encode('cp1254', errors='replace')
        data += CENTER
        for line in footer_note.split('\n'):
            data += f"{line}\n".encode('cp1254', errors='replace')
        
        # QR Kod
        qr_url = db.get_setting('receipt_qr_image_url', '')
        qr_label = db.get_setting('receipt_qr_label', '')
        if qr_url:
            qr_bytes = self._image_to_escpos(qr_url)
            if qr_bytes:
                data += qr_bytes
            if qr_label:
                data += CENTER
                data += qr_label.encode('cp1254', errors='replace') + b'\n'

        data += "\n\n".encode('cp1254', errors='replace')
        data += CUT
        
        return self.send_command(data)
    
    def print_kitchen_order(self, order_data):
        """Mutfak fişi yazdır (sadece ürünler + notlar)"""
        ESC = b'\x1B'
        INIT = ESC + b'@'
        CODEPAGE = ESC + b't\x21'   # Code Page 857/Turkish (0x21=33)
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
        data += "MUTFAK SIPARIS\n".encode('cp1254', errors='replace')
        data += NORMAL + BOLD_OFF
        data += "================================\n".encode('cp1254', errors='replace')
        data += LEFT
        
        # Tarih/Saat
        now = datetime.now().strftime('%d.%m.%Y %H:%M')
        data += BOLD_ON
        data += f"MASA: {order_data.get('table_name', '-')}\n".encode('cp1254', errors='replace')
        data += f"Saat: {now}\n".encode('cp1254', errors='replace')
        data += BOLD_OFF
        data += "================================\n".encode('cp1254', errors='replace')
        
        # Ürünler (ikramlar hariç)
        for item in order_data.get('items', []):
            if item.get('is_complimentary'):
                continue
            
            name = item.get('product_name', 'Urun')
            qty = item.get('quantity', 1)
            
            data += BOLD_ON + DOUBLE_HEIGHT
            data += f"{qty}x {name}\n".encode('cp1254', errors='replace')
            data += NORMAL + BOLD_OFF
            
            if item.get('kitchen_notes'):
                data += f">>> {item.get('kitchen_notes')}\n".encode('cp1254', errors='replace')
            
            data += "--------------------------------\n".encode('cp1254', errors='replace')
        
        data += "\n\n".encode('cp1254', errors='replace')
        data += CUT
        
        return self.send_command(data)

    def _image_to_escpos(self, image_path):
        """Görseli ESC/POS raster bitmap komutuna çevir"""
        try:
            from PIL import Image
            import os

            # URL veya path'i çöz
            if image_path.startswith('/static/'):
                base = os.path.dirname(os.path.abspath(__file__))
                image_path = os.path.join(base, image_path.lstrip('/'))
            elif image_path.startswith('data:'):
                import base64, io
                header, data = image_path.split(',', 1)
                img = Image.open(io.BytesIO(base64.b64decode(data)))
            
            if not image_path.startswith('data:'):
                if not os.path.exists(image_path):
                    return b''
                img = Image.open(image_path)

            # Gri tona çevir, yeniden boyutlandır (max 384px genişlik - 80mm yazıcı)
            img = img.convert('L')  # Gri ton
            max_width = 384
            if img.width > max_width:
                ratio = max_width / img.width
                img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)

            # Siyah-beyaza çevir (eşik: 128)
            img = img.point(lambda x: 0 if x < 128 else 255, '1')
            img = img.convert('1')

            width, height = img.size
            # Genişliği 8'in katına tamamla
            width_bytes = (width + 7) // 8
            width_padded = width_bytes * 8

            # ESC/POS raster bitmap: GS v 0
            ESC = b'\x1B'
            GS = b'\x1D'
            CENTER = ESC + b'a\x01'
            LEFT = ESC + b'a\x00'

            data = CENTER
            # GS v 0: m=0 (normal), xL xH = width_bytes, yL yH = height
            xL = width_bytes & 0xFF
            xH = (width_bytes >> 8) & 0xFF
            yL = height & 0xFF
            yH = (height >> 8) & 0xFF
            data += GS + b'v0' + bytes([0, xL, xH, yL, yH])

            # Piksel verisi
            pixels = img.load()
            for y in range(height):
                row = 0
                byte_val = 0
                for x in range(width_padded):
                    bit = 0
                    if x < width:
                        pixel = pixels[x, y]
                        bit = 0 if pixel else 1  # 1=siyah
                    byte_val = (byte_val << 1) | bit
                    if (x + 1) % 8 == 0:
                        data += bytes([byte_val])
                        byte_val = 0

            data += LEFT
            return data
        except Exception as e:
            print(f"Logo bitmap hatası: {e}")
            return b''

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
        data += f'Test: {now}\n'.encode('cp1254', errors='replace')
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

        restaurant_address = db.get_setting('restaurant_address', '')
        restaurant_phone   = db.get_setting('restaurant_phone', '')
        logo_url           = db.get_setting('logo_url', '')
        qr_url             = db.get_setting('note_qr_image_url', '')
        qr_label           = db.get_setting('note_qr_label', '')

        data = INIT

        # Logo
        if logo_url:
            logo_bytes = self._image_to_escpos(logo_url)
            if logo_bytes:
                data += logo_bytes
                data += b'\n'

        # Restoran başlık
        data += CENTER
        data += BOLD_ON
        data += f"{restaurant_name}\n".encode('cp1254', errors='replace')
        data += BOLD_OFF
        if restaurant_address:
            data += restaurant_address.encode('cp1254', errors='replace') + b'\n'
        if restaurant_phone:
            data += f"Tel: {restaurant_phone}\n".encode('cp1254', errors='replace')
        data += "================================\n".encode('cp1254', errors='replace')
        data += BOLD_ON
        data += f"--- {title} ---\n".encode('cp1254', errors='replace')
        data += BOLD_OFF
        data += f"{now}\n".encode('cp1254', errors='replace')
        data += "================================\n".encode('cp1254', errors='replace')
        data += LEFT
        data += "\n".encode('cp1254', errors='replace')
        for line in note_text.split('\n'):
            data += f"{line}\n".encode('cp1254', errors='replace')
        data += "\n================================\n".encode('cp1254', errors='replace')

        # QR Kod
        if qr_url:
            qr_bytes = self._image_to_escpos(qr_url)
            if qr_bytes:
                data += CENTER
                data += qr_bytes
            if qr_label:
                data += CENTER
                data += qr_label.encode('cp1254', errors='replace') + b'\n'

        data += "\n\n".encode('cp1254', errors='replace')
        data += CUT

        return self.send_command(data)

