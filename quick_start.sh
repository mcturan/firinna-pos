#!/bin/bash

# Fırınna POS - Hızlı Başlangıç (Manuel Kurulum)
# Tam kurulum yapmadan test etmek için

echo "🍽️  Fırınna POS - Hızlı Başlatma"
echo ""

# Mevcut dizinde kal
cd "$(dirname "$0")"

# Virtual environment var mı kontrol et
if [ ! -d "venv" ]; then
    echo "📦 Python sanal ortamı oluşturuluyor..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Gerekli klasörleri oluştur
mkdir -p backups static/css static/js templates

# .env dosyası yoksa oluştur
if [ ! -f ".env" ]; then
    echo ""
    echo "⚙️  Yazıcı ayarları:"
    read -p "XPrinter POS80 IP adresi (varsayılan 192.168.1.100): " PRINTER_IP
    PRINTER_IP=${PRINTER_IP:-192.168.1.100}
    
    read -p "Port (varsayılan 9100): " PRINTER_PORT
    PRINTER_PORT=${PRINTER_PORT:-9100}
    
    echo "PRINTER_IP=$PRINTER_IP" > .env
    echo "PRINTER_PORT=$PRINTER_PORT" >> .env
fi

# Uygulamayı başlat
echo ""
echo "🚀 Uygulama başlatılıyor..."
echo ""
echo "Erişim adresleri:"
echo "  Lokal:  http://localhost:5000"
echo "  Ağ:     http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "Durdurmak için: CTRL+C"
echo ""

python3 app.py
