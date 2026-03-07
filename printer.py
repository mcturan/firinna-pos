import socket
from datetime import datetime

class ThermalPrinter:
    """XPrinter POS80 için ESC/POS komutları"""
    
    def __init__(self, ip='192.168.1.100', port=9100):
        self.ip = ip
        self.port = port
    
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
        """Adisyon yazdır"""
        # ESC/POS komutları
        ESC = b'\x1B'
        INIT = ESC + b'@'  # Yazıcıyı başlat
        CENTER = ESC + b'a\x01'  # Ortala
        LEFT = ESC + b'a\x00'  # Sola hizala
        BOLD_ON = ESC + b'E\x01'  # Kalın
        BOLD_OFF = ESC + b'E\x00'  # Kalın kapat
        DOUBLE_HEIGHT = ESC + b'!\x10'  # Çift yükseklik
        NORMAL_SIZE = ESC + b'!\x00'  # Normal boyut
        CUT = b'\x1D\x56\x00'  # Kağıdı kes
        
        data = INIT
        
        # Başlık
        data += CENTER + BOLD_ON + DOUBLE_HEIGHT
        data += "FIRINNA\n".encode('cp857')
        data += NORMAL_SIZE + BOLD_OFF
        data += "Cafe & Restaurant\n".encode('cp857')
        data += "-" * 32 + "\n"
        
        # Masa bilgisi
        data += LEFT + BOLD_ON
        data += f"MASA: {order_data['table_name']}\n".encode('cp857')
        data += BOLD_OFF
        data += f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n".encode('cp857')
        data += f"Adisyon No: {order_data['order_id']}\n".encode('cp857')
        data += "-" * 32 + "\n\n"
        
        # Ürünler
        data += LEFT
        for item in order_data['items']:
            name = item['product_name'][:20]  # Uzun isimleri kısalt
            quantity = item['quantity']
            price = item['price']
            total = quantity * price
            
            line = f"{quantity}x {name}"
            spaces = 32 - len(line) - len(f"{total:.2f}")
            data += f"{line}{' ' * spaces}{total:.2f}\n".encode('cp857')
        
        data += "\n" + "=" * 32 + "\n"
        
        # Toplam
        data += BOLD_ON + DOUBLE_HEIGHT
        total_str = f"TOPLAM: {order_data['total']:.2f} TL"
        data += total_str.encode('cp857') + "\n"
        data += NORMAL_SIZE + BOLD_OFF
        
        data += "\n" + "-" * 32 + "\n"
        data += CENTER
        data += "Bizi tercih ettiginiz icin\ntesekkur ederiz!\n\n".encode('cp857')
        
        # Kağıdı kes
        data += b'\n\n\n'
        data += CUT
        
        return self.send_command(data)
    
    def print_daily_report(self, report_data):
        """Günlük rapor yazdır"""
        ESC = b'\x1B'
        INIT = ESC + b'@'
        CENTER = ESC + b'a\x01'
        LEFT = ESC + b'a\x00'
        BOLD_ON = ESC + b'E\x01'
        BOLD_OFF = ESC + b'E\x00'
        DOUBLE_HEIGHT = ESC + b'!\x10'
        NORMAL_SIZE = ESC + b'!\x00'
        CUT = b'\x1D\x56\x00'
        
        data = INIT
        
        # Başlık
        data += CENTER + BOLD_ON + DOUBLE_HEIGHT
        data += "GUNLUK RAPOR\n".encode('cp857')
        data += NORMAL_SIZE + BOLD_OFF
        data += f"{report_data['date']}\n".encode('cp857')
        data += "-" * 32 + "\n\n"
        
        # Özet
        data += LEFT + BOLD_ON
        data += f"TOPLAM SATIS: {report_data['total_sales']:.2f} TL\n".encode('cp857')
        data += f"TOPLAM MASRAF: {report_data['total_expenses']:.2f} TL\n".encode('cp857')
        data += "-" * 32 + "\n"
        data += f"NET: {report_data['net']:.2f} TL\n".encode('cp857')
        data += BOLD_OFF
        data += "\n"
        
        # Ürün detayları
        if report_data['products']:
            data += "URUN BAZLI SATIS:\n".encode('cp857')
            data += "-" * 32 + "\n"
            
            for product in report_data['products']:
                name = product['name'][:15]
                qty = product['quantity']
                total = product['total']
                
                line = f"{name} x{qty}"
                spaces = 32 - len(line) - len(f"{total:.2f}")
                data += f"{line}{' ' * spaces}{total:.2f}\n".encode('cp857')
        
        data += b'\n\n\n'
        data += CUT
        
        return self.send_command(data)
    
    def test_print(self):
        """Test yazdırma"""
        ESC = b'\x1B'
        INIT = ESC + b'@'
        CENTER = ESC + b'a\x01'
        BOLD_ON = ESC + b'E\x01'
        BOLD_OFF = ESC + b'E\x00'
        CUT = b'\x1D\x56\x00'
        
        data = INIT
        data += CENTER + BOLD_ON
        data += "YAZICI TEST\n".encode('cp857')
        data += BOLD_OFF
        data += f"{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n".encode('cp857')
        data += "Baglanti basarili!\n\n\n".encode('cp857')
        data += CUT
        
        return self.send_command(data)
