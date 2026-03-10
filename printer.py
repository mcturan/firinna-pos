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
        CODEPAGE = b''   # Codepage komutu gönderilmiyor — yazıcı desteklemiyor

        def tr(text):
            """Türkçe karakterleri CP437-uyumlu ASCII'ye çevir"""
            table = str.maketrans('ğüşıöçĞÜŞİÖÇ', 'gusiocGUSIOC')
            return str(text).translate(table)
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
        data += tr(f"{restaurant_name}\n").encode('ascii', errors='replace')
        data += BOLD_OFF
        
        if restaurant_address:
            data += tr(f"{restaurant_address}\n").encode('ascii', errors='replace')
        if restaurant_phone:
            data += tr(f"Tel: {restaurant_phone}\n").encode('ascii', errors='replace')
        if restaurant_web:
            data += tr(f"{restaurant_web}\n").encode('ascii', errors='replace')
        
        data += "==========================================\n".encode('ascii', errors='replace')
        data += LEFT
        
        # Tarih/Saat
        now = datetime.now().strftime('%d.%m.%Y %H:%M')
        data += tr(f"Tarih: {now}\n").encode('ascii', errors='replace')
        data += tr(f"Masa: {order_data.get('table_name', '-')}\n").encode('ascii', errors='replace')
        data += tr(f"Siparis No: {order_data.get('order_id', '-')}\n").encode('ascii', errors='replace')
        data += "==========================================\n".encode('ascii', errors='replace')
        
        # Ürünler
        for item in order_data.get('items', []):
            name = item.get('product_name', 'Urun')
            qty = item.get('quantity', 1)
            price = item.get('price', 0)
            total = qty * price
            
            if item.get('is_complimentary'):
                data += tr(f"{qty}x {name}").encode('ascii', errors='replace')
                data += " (IKRAM)\n".encode('ascii', errors='replace')
            else:
                line = f"{qty}x {name}"
                price_str = f"{total:.2f} TL"
                LINE_WIDTH = 42
                spaces = LINE_WIDTH - len(line) - len(price_str)
                if spaces < 1: spaces = 1
                data += tr(f"{line}{' ' * spaces}{price_str}\n").encode('ascii', errors='replace')
            
        data += "==========================================\n".encode('ascii', errors='replace')
        
        # Toplam
        subtotal = order_data.get('subtotal', 0)
        discount = order_data.get('discount_value', 0)
        total = order_data.get('total', 0)
        
        LW = 42
        def rjust_row(label, value):
            spaces = LW - len(label) - len(value)
            if spaces < 1: spaces = 1
            return tr(label + ' ' * spaces + value + '\n').encode('ascii', errors='replace')

        data += rjust_row('Ara Toplam:', f'{subtotal:.2f} TL')
        
        if discount > 0:
            discount_text = order_data.get('discount_reason', 'Indirim')
            data += rjust_row(f'{discount_text}:', f'-{discount:.2f} TL')
        
        data += BOLD_ON
        data += rjust_row('TOPLAM:', f'{total:.2f} TL')
        data += BOLD_OFF
        data += "==========================================\n".encode('ascii', errors='replace')
        
        # Ödeme bilgisi
        if order_data.get('payment_cash', 0) > 0:
            data += rjust_row('Nakit:', f"{order_data['payment_cash']:.2f} TL")
        if order_data.get('payment_card', 0) > 0:
            data += rjust_row('Kart:', f"{order_data['payment_card']:.2f} TL")
        if order_data.get('tip_amount', 0) > 0:
            data += rjust_row('Bahsis:', f"{order_data['tip_amount']:.2f} TL")
        
        # Footer
        data += "\n".encode('ascii', errors='replace')
        data += CENTER
        for line in footer_note.split('\n'):
            data += tr(f"{line}\n").encode('ascii', errors='replace')
        
        # QR Kod
        qr_url = db.get_setting('receipt_qr_image_url', '')
        qr_label = db.get_setting('receipt_qr_label', '')
        if qr_url:
            qr_bytes = self._image_to_escpos(qr_url)
            if qr_bytes:
                data += qr_bytes
            if qr_label:
                data += CENTER
                data += tr(qr_label).encode('ascii', errors='replace') + b'\n'

        data += "\n\n".encode('ascii', errors='replace')
        data += CUT
        
        return self.send_command(data)
    
    def print_kitchen_order(self, order_data):
        """Mutfak fişi yazdır (sadece ürünler + notlar)"""
        ESC = b'\x1B'
        INIT = ESC + b'@'
        CODEPAGE = b''   # Codepage komutu gönderilmiyor — yazıcı desteklemiyor

        def tr(text):
            """Türkçe karakterleri CP437-uyumlu ASCII'ye çevir"""
            table = str.maketrans('ğüşıöçĞÜŞİÖÇ', 'gusiocGUSIOC')
            return str(text).translate(table)
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
        data += "MUTFAK SIPARIS\n".encode('ascii', errors='replace')
        data += NORMAL + BOLD_OFF
        data += "==========================================\n".encode('ascii', errors='replace')
        data += LEFT
        
        # Tarih/Saat
        now = datetime.now().strftime('%d.%m.%Y %H:%M')
        data += BOLD_ON
        data += tr(f"MASA: {order_data.get('table_name', '-')}\n").encode('ascii', errors='replace')
        data += tr(f"Saat: {now}\n").encode('ascii', errors='replace')
        data += BOLD_OFF
        data += "==========================================\n".encode('ascii', errors='replace')
        
        # Ürünler (ikramlar hariç)
        for item in order_data.get('items', []):
            if item.get('is_complimentary'):
                continue
            
            name = item.get('product_name', 'Urun')
            qty = item.get('quantity', 1)
            
            data += BOLD_ON + DOUBLE_HEIGHT
            data += tr(f"{qty}x {name}\n").encode('ascii', errors='replace')
            data += NORMAL + BOLD_OFF
            
            if item.get('kitchen_notes'):
                data += tr(f">>> {item.get('kitchen_notes')}\n").encode('ascii', errors='replace')
            
            data += "--------------------------------\n".encode('ascii', errors='replace')
        
        data += "\n\n".encode('ascii', errors='replace')
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
        data += tr(f'Test: {now}\n').encode('ascii', errors='replace')
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

        def tr(text):
            table = str.maketrans('ğüşıöçĞÜŞİÖÇ', 'gusiocGUSIOC')
            return str(text).translate(table)

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
        data += tr(f"{restaurant_name}\n").encode('ascii', errors='replace')
        data += BOLD_OFF
        if restaurant_address:
            data += tr(restaurant_address).encode('ascii', errors='replace') + b'\n'
        if restaurant_phone:
            data += tr(f"Tel: {restaurant_phone}\n").encode('ascii', errors='replace')
        data += "==========================================\n".encode('ascii', errors='replace')
        data += BOLD_ON
        data += tr(f"--- {title} ---\n").encode('ascii', errors='replace')
        data += BOLD_OFF
        data += tr(f"{now}\n").encode('ascii', errors='replace')
        data += "==========================================\n".encode('ascii', errors='replace')
        data += LEFT
        data += "\n".encode('ascii', errors='replace')
        for line in note_text.split('\n'):
            data += tr(f"{line}\n").encode('ascii', errors='replace')
        data += "\n================================\n".encode('ascii', errors='replace')

        # QR Kod
        if qr_url:
            qr_bytes = self._image_to_escpos(qr_url)
            if qr_bytes:
                data += CENTER
                data += qr_bytes
            if qr_label:
                data += CENTER
                data += tr(qr_label).encode('ascii', errors='replace') + b'\n'

        data += "\n\n".encode('ascii', errors='replace')
        data += CUT

        return self.send_command(data)

