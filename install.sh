#!/bin/bash

# Fırınna POS - Otomatik Kurulum Scripti
# Pardus Linux için

echo "============================================"
echo "🍽️  Fırınna POS Kurulumu Başlatılıyor..."
echo "============================================"
echo ""

# Renk kodları
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Root kontrolü
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Bu scripti root olarak çalıştırın: sudo bash install.sh${NC}"
    exit 1
fi

# Python 3 kontrolü
echo -e "${YELLOW}[1/6] Python kontrolü...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}Python3 kuruluyor...${NC}"
    apt update
    apt install -y python3 python3-pip python3-venv
else
    echo -e "${GREEN}✓ Python3 mevcut${NC}"
fi

# Uygulama dizinine git
cd "$(dirname "$0")"

# Virtual environment oluştur
echo -e "${YELLOW}[2/6] Python sanal ortamı oluşturuluyor...${NC}"
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları kur
echo -e "${YELLOW}[3/6] Python paketleri kuruluyor...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Dizinleri oluştur
echo -e "${YELLOW}[4/6] Gerekli dizinler oluşturuluyor...${NC}"
mkdir -p backups
mkdir -p static/css
mkdir -p static/js
mkdir -p templates

# Yazıcı IP'sini sor
echo ""
echo -e "${YELLOW}[5/6] Yazıcı ayarları...${NC}"
read -p "XPrinter POS80 IP adresi (örn: 192.168.1.100): " PRINTER_IP
read -p "Port (varsayılan 9100): " PRINTER_PORT
PRINTER_PORT=${PRINTER_PORT:-9100}

# .env dosyası oluştur
echo "PRINTER_IP=$PRINTER_IP" > .env
echo "PRINTER_PORT=$PRINTER_PORT" >> .env

# Systemd servis dosyası oluştur
echo -e "${YELLOW}[6/6] Sistem servisi oluşturuluyor...${NC}"

CURRENT_DIR=$(pwd)
SERVICE_FILE="/etc/systemd/system/firinna-pos.service"

cat > $SERVICE_FILE <<EOF
[Unit]
Description=Firinna POS Service
After=network.target

[Service]
Type=simple
User=$SUDO_USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Servisi etkinleştir ve başlat
systemctl daemon-reload
systemctl enable firinna-pos
systemctl start firinna-pos

echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}✓ Kurulum tamamlandı!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo -e "${YELLOW}Uygulama adresleri:${NC}"
echo -e "  Lokal:  http://localhost:5000"
echo -e "  Ağ:     http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo -e "${YELLOW}Servis komutları:${NC}"
echo -e "  Başlat:   sudo systemctl start firinna-pos"
echo -e "  Durdur:   sudo systemctl stop firinna-pos"
echo -e "  Yeniden başlat: sudo systemctl restart firinna-pos"
echo -e "  Durum:    sudo systemctl status firinna-pos"
echo -e "  Log:      sudo journalctl -u firinna-pos -f"
echo ""
echo -e "${YELLOW}Yedekler:${NC}"
echo -e "  Otomatik yedekler: $CURRENT_DIR/backups/"
echo ""
echo -e "${GREEN}Şimdi tarayıcıdan http://localhost:5000 adresine gidin!${NC}"
echo ""
