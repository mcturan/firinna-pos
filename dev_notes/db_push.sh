#!/bin/bash
# =============================================
#  Fırınna POS — DB + Kod Push
#  Kullanım: bash db_push.sh "commit mesajı"
#  İşyerinden eve gitmeden önce çalıştır.
# =============================================

cd /opt/firinna-pos

MSG="${1:-DB ve kod güncellemesi}"

echo "🔄 Değişiklikler hazırlanıyor..."
git add pos_data.db
git add -A

if git diff --cached --quiet; then
    echo "ℹ️  Değişiklik yok, push atlandı."
    exit 0
fi

git commit -m "$MSG"
git push origin main

echo ""
echo "✅ Push tamamlandı: $MSG"
echo "   Şimdi evde: git pull"
