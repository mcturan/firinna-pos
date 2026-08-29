import re

with open("/opt/firinna-pos/templates/tv_player.html", "r") as f:
    content = f.read()

day_names_block = """        const trDayNames = ["Pazar", "Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi"];
        const enDayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
        const ruDayNames = ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"];
        const arDayNames = ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"];
        const esDayNames = ["Domingo", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];"""

day_names_block_new = day_names_block + """
        const elDayNames = ["Κυριακή", "Δευτέρα", "Τρίτη", "Τετάρτη", "Πέμπτη", "Παρασκευή", "Σάββατο"];
        const jaDayNames = ["日曜日", "月曜日", "火曜日", "水曜日", "木曜日", "金曜日", "土曜日"];"""

content = content.replace(day_names_block, day_names_block_new)


badge_logic = """                if (lang === 'en') return `☀️ Opening: ${fallbackTime} AM`;
                if (lang === 'ru') return `☀️ Открытие: в ${fallbackTime}`;
                if (lang === 'ar') return `☀️ الافتتاح: الساعة ${fallbackTime} صباحاً`;
                if (lang === 'es') return `☀️ Apertura: a las ${fallbackTime}`;
                return `☀️ Açılış: ${fallbackTime}`;"""

badge_logic_new = """                if (lang === 'en') return `☀️ Opening: ${fallbackTime} AM`;
                if (lang === 'ru') return `☀️ Открытие: в ${fallbackTime}`;
                if (lang === 'ar') return `☀️ الافتتاح: الساعة ${fallbackTime} صباحاً`;
                if (lang === 'es') return `☀️ Apertura: a las ${fallbackTime}`;
                if (lang === 'el') return `☀️ Άνοιγμα: στις ${fallbackTime}`;
                if (lang === 'ja') return `☀️ 開店: ${fallbackTime}`;
                return `☀️ Açılış: ${fallbackTime}`;"""

content = content.replace(badge_logic, badge_logic_new)

lang_logic = """            } else if (lang === 'es') {
                if (daysAhead === 0) return `☀️ Apertura: Hoy a las ${openTime}`;
                if (daysAhead === 1) return `☀️ Apertura: Mañana a las ${openTime}`;
                return `☀️ Apertura: ${esDayNames[dayIdx]} a las ${openTime}`;
            } else {"""

lang_logic_new = """            } else if (lang === 'es') {
                if (daysAhead === 0) return `☀️ Apertura: Hoy a las ${openTime}`;
                if (daysAhead === 1) return `☀️ Apertura: Mañana a las ${openTime}`;
                return `☀️ Apertura: ${esDayNames[dayIdx]} a las ${openTime}`;
            } else if (lang === 'el') {
                if (daysAhead === 0) return `☀️ Άνοιγμα: Σήμερα στις ${openTime}`;
                if (daysAhead === 1) return `☀️ Άνοιγμα: Αύριο στις ${openTime}`;
                return `☀️ Άνοιγμα: ${elDayNames[dayIdx]} στις ${openTime}`;
            } else if (lang === 'ja') {
                if (daysAhead === 0) return `☀️ 開店: 本日 ${openTime}`;
                if (daysAhead === 1) return `☀️ 開店: 明日 ${openTime}`;
                return `☀️ 開店: ${jaDayNames[dayIdx]} ${openTime}`;
            } else {"""

content = content.replace(lang_logic, lang_logic_new)

with open("/opt/firinna-pos/templates/tv_player.html", "w") as f:
    f.write(content)
