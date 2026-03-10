#!/bin/bash
# =============================================
#  Fırınna POS — DB + Kod Pull
#  Kullanım: bash db_pull.sh
#  Başka makinede çalışmadan önce çalıştır.
# =============================================

cd /opt/firinna-pos

echo "🔄 Güncel kod ve DB çekiliyor..."
git pull origin main

echo ""
echo "✅ Pull tamamlandı."
echo "   Servisi yeniden başlatmak ister misin? (e/h)"
read -r ans
if [[ "$ans" == "e" || "$ans" == "E" ]]; then
    sudo systemctl restart firinna-pos
    echo "✅ Servis yeniden başlatıldı."
fi
