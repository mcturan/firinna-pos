document.addEventListener('DOMContentLoaded', () => {
    // Yıl Güncelleme
    const yearSpan = document.getElementById('year');
    if (yearSpan) {
        yearSpan.textContent = new Date().getFullYear();
    }

    // Kartlar için giriş animasyonu
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, 100 + (index * 100));
    });

    // Menü Butonu Davranışı
    const menuLink = document.getElementById('menu-link');
    if (menuLink && menuLink.getAttribute('href') === '#') {
        menuLink.addEventListener('click', (e) => {
            e.preventDefault();
            
            const span = menuLink.querySelector('span');
            const icon = menuLink.querySelector('i');
            const originalText = span.textContent;
            
            span.textContent = 'Menü hazırlanıyor...';
            icon.className = 'ph-bold ph-spinner';
            icon.style.animation = 'spin 1s linear infinite';
            
            setTimeout(() => {
                span.textContent = originalText;
                icon.className = 'ph-bold ph-book-open';
                icon.style.animation = 'none';
            }, 2500);
        });
    }
});

// CSS for the spinner
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        100% { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);

// MODAL LOGIC & API BRIDGES
function openModal(id) {
    document.getElementById(id).style.display = 'flex';
}
function closeModal(id) {
    document.getElementById(id).style.display = 'none';
}

// Close modal if clicked outside content
window.onclick = function(event) {
    if (event.target.classList.contains('modal-overlay')) {
        event.target.style.display = "none";
    }
}

async function submitReservation(e) {
    e.preventDefault();
    const btn = document.getElementById('btnResSubmit');
    const resText = document.getElementById('resResult');
    
    btn.disabled = true;
    btn.innerText = "Gönderiliyor...";
    
    const data = {
        name: document.getElementById('resName').value,
        phone: document.getElementById('resPhone').value,
        date: document.getElementById('resDate').value,
        time: document.getElementById('resTime').value,
        guests: document.getElementById('resGuests').value,
        note: document.getElementById('resNote').value
    };

    try {
        const response = await fetch('/api/web/reservation', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (result.success) {
            resText.style.color = "green";
            resText.innerText = "Rezervasyon talebiniz başarıyla iletildi!";
            document.getElementById('reservationForm').reset();
            setTimeout(() => closeModal('reservationModal'), 3000);
        } else {
            resText.style.color = "red";
            resText.innerText = "Bir hata oluştu.";
        }
    } catch (err) {
        resText.style.color = "red";
        resText.innerText = "Bağlantı hatası.";
    }
    btn.disabled = false;
    btn.innerText = "Talebi Gönder";
}

async function submitMessage(e) {
    e.preventDefault();
    const btn = document.getElementById('btnMsgSubmit');
    const resText = document.getElementById('msgResult');
    
    btn.disabled = true;
    btn.innerText = "Gönderiliyor...";
    
    const data = {
        name: document.getElementById('msgName').value,
        phone: document.getElementById('msgPhone').value,
        message: document.getElementById('msgText').value
    };

    try {
        const response = await fetch('/api/web/contact', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        });
        const result = await response.json();
        if (result.success) {
            resText.style.color = "green";
            resText.innerText = "Mesajınız başarıyla iletildi!";
            document.getElementById('messageForm').reset();
            setTimeout(() => closeModal('messageModal'), 3000);
        } else {
            resText.style.color = "red";
            resText.innerText = "Bir hata oluştu.";
        }
    } catch (err) {
        resText.style.color = "red";
        resText.innerText = "Bağlantı hatası.";
    }
    btn.disabled = false;
    btn.innerText = "Mesajı Gönder";
}

// MULTI-LANGUAGE DICTIONARY & LOGIC
const i18n = {
    tr: {
        category: "Cafe & Restaurant",
        status_open: "Şu An Açık (08:00 - 23:00)",
        btn_menu: "Dijital Menüyü İncele",
        btn_reserve: "Hemen Masa Ayırt",
        btn_message: "Bize Mesaj Gönder",
        title_about: "Hakkımızda",
        text_about: "DEĞERLI MISAFIRIMIZ, FIRINNA'YA HOŞ GELDINIZ.\n\nTÜM ÜRÜNLERIMIZ; EN SEÇKIN MALZEMELERLE, GELENEKSEL TARIFLERE FIRINNA DOKUNUŞLARIYLA EV YAPIMI HAZIRLANMAKTADIR.\n\nBURADA ACELE YOK - 150 YILLIK YAPININ SICAKLIĞINDA LEZZETIN, HUZURUN, SOHBETIN VE GÜZEL ANLARIN TADINI ÇIKARIN.\n\nTARIHI İSTANBUL GEZINIZDE LEZZETLI VE HUZURLU BIR ANI OLABILIRSEK NE MUTLU BIZE.",
        title_top_reviews: "Müşterilerimizin Gözünden",
        review_1: "İstiklal'in gürültüsünden kaçıp nefes alabileceğiniz harika, tarihi bir mekan. Pizzaları efsane!",
        review_2: "Çakallı menemenini denemelisiniz. Personel çok güleryüzlü ve evcil hayvan dostu olmaları harika.",
        review_3: "Galata'da kahve içip tatlı yemek için en iyi nokta. Çalışanlar çok ilgili.",
        title_virtual_tour: "Sanal Tur (360°)",
        text_virtual_tour: "150 yıllık tarihi binamızı oturduğunuz yerden keşfedin.",
        title_location: "Lokasyon",
        title_contact: "İletişim & Ulaşım",
        title_gallery: "Ortam & Lezzetler",
        badge_halal: "%100 Helal",
        badge_quality: "En İyi Kalite",
        badge_price: "Uygun Fiyat",
        title_reviews: "Konum & Son Yorumlar",
        btn_google: "Google'daki Son Yorumları Oku",
        btn_yandex: "Yandex Haritalar'da İncele",
        btn_baidu: "Baidu'da İncele (百度地图)",
        modal_res_title: "Masa Rezervasyonu",
        label_name: "Ad Soyad",
        label_phone: "Telefon",
        label_date: "Tarih",
        label_time: "Saat (08:00-23:00)",
        label_guests: "Kişi Sayısı",
        label_note: "Özel İstek / Not (İsteğe Bağlı)",
        btn_submit: "Talebi Gönder",
        modal_msg_title: "Bize Mesaj Gönderin",
        label_message: "Mesajınız",
        btn_submit_msg: "Mesajı Gönder",
        footer_rights: "Tüm hakları saklıdır.",
        menu_header_title: "İmza Lezzetlerimiz",
        menu_header_sub: "Fırınna Dokunuşlarıyla...",
        menu_back: "Ana Sayfa",
        menu_intro: "Tüm menü seçeneklerimiz için mağazamızı ziyaret edebilir veya personelimizden detaylı bilgi alabilirsiniz. Aşağıda en sevilen imza lezzetlerimizi inceleyebilirsiniz.",
        menu_download: "Fiyatlı Menüyü İndir (PDF)",
        cat_food: "Fırından Sıcak Sıcak",
        cat_drinks: "İçecekler & Tatlılar",
        item_pizza: "Taş Fırın Pizza",
        desc_pizza: "Özel mayalanmış hamurumuz, İtalyan domates sosu ve enfes mozzarella peyniriyle odun ateşinde pişer.",
        item_menemen: "Meşhur Çakallı Menemeni",
        desc_menemen: "Sadece sarısıyla hazırlanan, bol kaşarlı ve tereyağlı, yöresel lezzetiyle kahvaltıların efsanesi.",
        item_toast: "Fırında Bazlama Tost",
        desc_toast: "Köy ekmeği arasında kaşar peyniri ve özel sucuk/kavurma ile taş fırında çıtır çıtır servis edilir.",
        item_coffee: "Közde Türk Kahvesi",
        desc_coffee: "150 yıllık atmosferde, bakır cezvede ağır ağır pişen, lokum eşliğinde servis edilen klasik lezzet.",
        item_tea: "İmza: Gül Yapraklı Çay",
        desc_tea: "Özel harman çayımızın içine katılan taze kurutulmuş gül yapraklarıyla inanılmaz bir aroma şöleni.",
        item_cake: "Çikolata Soslu Sıcak Kek",
        desc_cake: "İçi yumuşacık, bol kakaolu ve üzeri sıcak çikolata sosu ile kaplanmış vazgeçilmez lezzet.",
        badge_veg: "Vejetaryen",
        badge_vegan: "Vegan",
        badge_gluten: "Gluten İçerir",
        badge_dairy: "Süt Ürünü"
    },
    en: {
        category: "Cafe & Restaurant",
        status_open: "Open Now (08:00 - 23:00)",
        btn_menu: "View Digital Menu",
        btn_reserve: "Book a Table",
        btn_message: "Send us a Message",
        title_about: "About Us",
        text_about: "DEAR GUEST, WELCOME TO FIRINNA.\n\nALL OUR PRODUCTS ARE HOMEMADE WITH THE MOST EXCLUSIVE INGREDIENTS, BLENDING TRADITIONAL RECIPES WITH FIRINNA'S SPECIAL TOUCH.\n\nTHERE IS NO RUSH HERE - ENJOY TASTE, PEACE, CONVERSATION, AND BEAUTIFUL MOMENTS IN THE WARMTH OF OUR 150-YEAR-OLD BUILDING.\n\nWE WOULD BE DELIGHTED TO BE A DELICIOUS AND PEACEFUL MEMORY IN YOUR HISTORIC ISTANBUL TRIP.",
        title_top_reviews: "From Our Customers",
        review_1: "A wonderful, historic place to escape the noise of Istiklal and take a breath. Their pizzas are legendary!",
        review_2: "You must try the Çakallı menemen. The staff is very smiling and it's great that they are pet-friendly.",
        review_3: "The best spot in Galata for coffee and desserts. The staff is very attentive.",
        title_virtual_tour: "Virtual Tour (360°)",
        text_virtual_tour: "Explore our 150-year-old historic building right from where you sit.",
        title_location: "Location",
        title_contact: "Contact & Location",
        title_gallery: "Ambiance & Tastes",
        badge_halal: "100% Halal",
        badge_quality: "Best Quality",
        badge_price: "Fair Price",
        title_reviews: "Location & Recent Reviews",
        btn_google: "Read Recent Google Reviews",
        btn_yandex: "View on Yandex Maps",
        btn_baidu: "View on Baidu Maps",
        modal_res_title: "Table Reservation",
        label_name: "Full Name",
        label_phone: "Phone Number",
        label_date: "Date",
        label_time: "Time (08:00-23:00)",
        label_guests: "Number of Guests",
        label_note: "Special Request / Note (Optional)",
        btn_submit: "Send Request",
        modal_msg_title: "Send us a Message",
        label_message: "Your Message",
        btn_submit_msg: "Send Message",
        footer_rights: "All rights reserved.",
        menu_header_title: "Signature Tastes",
        menu_header_sub: "With Firinna's Touch...",
        menu_back: "Home",
        menu_intro: "You can visit our store or get detailed information from our staff for all menu options. Below you can review our most loved signature tastes.",
        menu_download: "Download Priced Menu (PDF)",
        cat_food: "Hot from the Oven",
        cat_drinks: "Beverages & Desserts",
        item_pizza: "Stone-baked Pizza",
        desc_pizza: "Specially fermented dough, Italian tomato sauce, and exquisite mozzarella cheese baked in a wood-fired oven.",
        item_menemen: "Famous Çakallı Menemen",
        desc_menemen: "Prepared only with egg yolks, plenty of cheddar and butter, a legendary regional breakfast taste.",
        item_toast: "Baked Bazlama Toast",
        desc_toast: "Served crispy from the stone oven with cheddar cheese and special sausage/beef between village bread.",
        item_coffee: "Turkish Coffee on Embers",
        desc_coffee: "A classic taste slowly brewed in a copper pot in a 150-year-old atmosphere, served with Turkish delight.",
        item_tea: "Signature: Rose Petal Tea",
        desc_tea: "An incredible feast of aromas with freshly dried rose petals added to our special blend tea.",
        item_cake: "Hot Cake with Chocolate Sauce",
        desc_cake: "Soft on the inside, lots of cocoa, and covered with hot chocolate sauce, an indispensable taste.",
        badge_veg: "Vegetarian",
        badge_vegan: "Vegan",
        badge_gluten: "Contains Gluten",
        badge_dairy: "Contains Dairy"
    },
    ru: {
        category: "Кафе и Ресторан",
        status_open: "Сейчас открыто (08:00 - 23:00)",
        btn_menu: "Посмотреть меню",
        btn_reserve: "Забронировать столик",
        btn_message: "Напишите нам",
        title_about: "О нас",
        text_about: "ДОРОГОЙ ГОСТЬ, ДОБРО ПОЖАЛОВАТЬ В FIRINNA.\n\nВСЕ НАШИ ПРОДУКТЫ ГОТОВЯТСЯ ПО-ДОМАШНЕМУ ИЗ САМЫХ ИЗЫСКАННЫХ ИНГРЕДИЕНТОВ, СОЧЕТАЯ ТРАДИЦИОННЫЕ РЕЦЕПТЫ С ОСОБЫМ ПОДХОДОМ FIRINNA.\n\nЗДЕСЬ НЕТ СПЕШКИ - НАСЛАЖДАЙТЕСЬ ВКУСОМ, ПОКОЕМ, БЕСЕДОЙ И ПРЕКРАСНЫМИ МГНОВЕНИЯМИ В ТЕПЛЕ НАШЕГО 150-ЛЕТНЕГО ЗДАНИЯ.\n\nМЫ БУДЕМ СЧАСТЛИВЫ СТАТЬ ВКУСНЫМ И СПОКОЙНЫМ ВОСПОМИНАНИЕМ О ВАШЕМ ПУТЕШЕСТВИИ ПО ИСТОРИЧЕСКОМУ СТАМБУЛУ.",
        title_top_reviews: "Отзывы клиентов",
        review_1: "Замечательное, историческое место, где можно спрятаться от шума Истикляля и перевести дух. Их пицца легендарна!",
        review_2: "Вы должны попробовать менемен Чакаллы. Персонал очень улыбчивый, и здорово, что к ним можно с питомцами.",
        review_3: "Лучшее место в Галате для кофе и десертов. Персонал очень внимателен.",
        title_location: "Расположение",
        title_contact: "Контакты и расположение",
        title_gallery: "Атмосфера и вкусы",
        badge_halal: "100% Халяль",
        badge_quality: "Лучшее качество",
        badge_price: "Хорошая цена",
        title_reviews: "Расположение и отзывы",
        btn_google: "Читать отзывы в Google",
        btn_yandex: "Смотреть на Яндекс.Картах",
        btn_baidu: "Смотреть на Baidu Maps",
        modal_res_title: "Бронирование столика",
        label_name: "Полное имя",
        label_phone: "Телефон",
        label_date: "Дата",
        label_time: "Время (08:00-23:00)",
        label_guests: "Количество гостей",
        label_note: "Особые пожелания (необязательно)",
        btn_submit: "Отправить запрос",
        modal_msg_title: "Напишите нам",
        label_message: "Ваше сообщение",
        btn_submit_msg: "Отправить сообщение",
        footer_rights: "Все права защищены.",
        menu_header_title: "Фирменные блюда",
        menu_header_sub: "С особым подходом Firinna...",
        menu_back: "Главная",
        menu_intro: "Вы можете посетить наше кафе или получить подробную информацию у нашего персонала обо всех вариантах меню. Ниже вы можете ознакомиться с нашими самыми любимыми фирменными блюдами.",
        menu_download: "Скачать меню с ценами (PDF)",
        cat_food: "Горячее из печи",
        cat_drinks: "Напитки и десерты",
        item_pizza: "Пицца на камне",
        desc_pizza: "Особо ферментированное тесто, итальянский томатный соус и изысканный сыр моцарелла, запеченные в дровяной печи.",
        item_menemen: "Знаменитый Менемен Чакаллы",
        desc_menemen: "Легендарный региональный вкус для завтрака, приготовленный только из яичных желтков, с большим количеством чеддера и сливочного масла.",
        item_toast: "Запеченный тост Базлама",
        desc_toast: "Подается хрустящим из каменной печи с сыром чеддер и особой колбасой/говядиной между ломтиками деревенского хлеба.",
        item_coffee: "Турецкий кофе на углях",
        desc_coffee: "Классический вкус, медленно завариваемый в медной турке в атмосфере со 150-летней историей, подается с рахат-лукумом.",
        item_tea: "Фирменный: Чай с лепестками роз",
        desc_tea: "Невероятный праздник ароматов со свежевысушенными лепестками роз, добавленными в наш особый купажированный чай.",
        item_cake: "Горячий кекс с шоколадным соусом",
        desc_cake: "Мягкий внутри, с большим количеством какао и покрытый горячим шоколадным соусом, незаменимый вкус.",
        badge_veg: "Вегетарианский",
        badge_vegan: "Веганский",
        badge_gluten: "Содержит глютен",
        badge_dairy: "Содержит молочные продукты"
    },
    ar: {
        category: "مقهى ومطعم",
        status_open: "مفتوح الآن (08:00 - 23:00)",
        btn_menu: "عرض القائمة الرقمية",
        btn_reserve: "احجز طاولة",
        btn_message: "ارسل لنا رسالة",
        title_about: "معلومات عنا",
        text_about: "ضيفنا العزيز، مرحباً بك في FIRINNA.\n\nجميع منتجاتنا محلية الصنع باستخدام أفخر المكونات، وتجمع بين الوصفات التقليدية ولمسة FIRINNA الخاصة.\n\nلا عجلة هنا - استمتع بالطعم والسلام والمحادثة واللحظات الجميلة في دفء مبنانا الذي يبلغ عمره 150 عامًا.\n\nيسعدنا أن نكون ذكرى لذيذة وهادئة في رحلتك التاريخية إلى اسطنبول.",
        title_top_reviews: "من عملائنا",
        review_1: "مكان تاريخي رائع للهروب من ضجيج الاستقلال وأخذ قسط من الراحة. البيتزا الخاصة بهم أسطورية!",
        review_2: "يجب أن تجرب مينيمين تشاكالي. الموظفون مبتسمون للغاية ومن الرائع أنهم يسمحون بالحيوانات الأليفة.",
        review_3: "أفضل مكان في غلطة لتناول القهوة والحلويات. فريق العمل مهتم جدا.",
        title_location: "الموقع",
        title_contact: "الاتصال والموقع",
        title_gallery: "الأجواء والمذاق",
        badge_halal: "حلال 100%",
        badge_quality: "أفضل جودة",
        badge_price: "سعر مناسب",
        title_reviews: "الموقع والتعليقات الحديثة",
        btn_google: "اقرأ تعليقات جوجل",
        btn_yandex: "عرض على خرائط ياندكس",
        btn_baidu: "عرض على خرائط بايدو",
        modal_res_title: "حجز طاولة",
        label_name: "الاسم الكامل",
        label_phone: "رقم الهاتف",
        label_date: "التاريخ",
        label_time: "الوقت (08:00-23:00)",
        label_guests: "عدد الضيوف",
        label_note: "طلب خاص / ملاحظة (اختياري)",
        btn_submit: "إرسال الطلب",
        modal_msg_title: "ارسل لنا رسالة",
        label_message: "رسالتك",
        btn_submit_msg: "إرسال الرسالة",
        footer_rights: "كل الحقوق محفوظة.",
        menu_header_title: "نكهاتنا المميزة",
        menu_header_sub: "بلمسة فيرينا...",
        menu_back: "الصفحة الرئيسية",
        menu_intro: "يمكنك زيارة متجرنا أو الحصول على معلومات مفصلة من موظفينا لجميع خيارات القائمة. يمكنك أدناه مراجعة نكهاتنا المميزة المحبوبة.",
        menu_download: "تنزيل القائمة بالأسعار (PDF)",
        cat_food: "ساخن من الفرن",
        cat_drinks: "المشروبات والحلويات",
        item_pizza: "بيتزا مخبوزة على الحجر",
        desc_pizza: "عجينة مخمرة بشكل خاص، صلصة طماطم إيطالية، وجبن موزاريلا رائع يخبز في فرن الحطب.",
        item_menemen: "مينيمين تشاكالي الشهير",
        desc_menemen: "محضر فقط بصفار البيض والكثير من الشيدر والزبدة، طعم إفطار إقليمي أسطوري.",
        item_toast: "توست بازلاما مخبوز",
        desc_toast: "يقدم مقرمشاً من فرن الحجر مع جبن الشيدر والسجق/اللحم البقري الخاص بين خبز القرية.",
        item_coffee: "قهوة تركية على الجمر",
        desc_coffee: "طعم كلاسيكي يخمر ببطء في وعاء نحاسي في جو يمتد لـ 150 عاماً، يقدم مع راحة الحلقوم التركية.",
        item_tea: "مميز: شاي بتلات الورد",
        desc_tea: "مهرجان مذهل من الروائح مع بتلات الورد المجففة حديثاً المضافة إلى مزيج الشاي الخاص بنا.",
        item_cake: "كيك ساخن مع صلصة الشوكولاتة",
        desc_cake: "طري من الداخل، الكثير من الكاكاو، ومغطى بصلصة الشوكولاتة الساخنة، طعم لا غنى عنه.",
        badge_veg: "نباتي",
        badge_vegan: "فيغان",
        badge_gluten: "يحتوي على الجلوتين",
        badge_dairy: "يحتوي على منتجات الألبان"
    },
    zh: {
        category: "咖啡厅与餐厅",
        status_open: "营业中 (08:00 - 23:00)",
        btn_menu: "查看电子菜单",
        btn_reserve: "预订餐桌",
        btn_message: "给我们留言",
        title_about: "关于我们",
        text_about: "尊贵的客人们，欢迎来到 FIRINNA。\n\n我们所有的产品都是自制的，采用最独特的原料，将传统配方与 FIRINNA 的特殊触感相结合。\n\n在这里无需匆忙 - 在我们 150 年历史的建筑的温暖中享受美味、宁静、对话和美好时光。\n\n如果您在伊斯坦布尔的历史之旅中，我们能成为一个美味和平和的回忆，我们将非常高兴。",
        title_top_reviews: "顾客评价",
        review_1: "一个美妙的、充满历史感的地方，在这里可以逃离Istiklal的喧嚣，稍作喘息。他们的比萨堪称传奇！",
        review_2: "你一定要尝尝Çakallı menemen。员工都面带微笑，而且这里对宠物很友好，真是太棒了。",
        review_3: "Galata喝咖啡和吃甜点的最佳去处。员工非常周到。",
        title_location: "地点",
        title_contact: "联系与位置",
        title_gallery: "氛围与口味",
        badge_halal: "100% 清真",
        badge_quality: "最高品质",
        badge_price: "价格合理",
        title_reviews: "地点和最新评论",
        btn_google: "阅读最新的谷歌评论",
        btn_yandex: "在Yandex地图上查看",
        btn_baidu: "在百度地图上查看",
        modal_res_title: "餐桌预订",
        label_name: "全名",
        label_phone: "电话号码",
        label_date: "日期",
        label_time: "时间 (08:00-23:00)",
        label_guests: "客人数量",
        label_note: "特别要求 / 备注（选填）",
        btn_submit: "发送请求",
        modal_msg_title: "给我们留言",
        label_message: "您的留言",
        btn_submit_msg: "发送留言",
        footer_rights: "版权所有。",
        menu_header_title: "招牌美味",
        menu_header_sub: "带有 Firinna 的特色...",
        menu_back: "主页",
        menu_intro: "您可以光临我们的商店或从我们的员工那里获取有关所有菜单选项的详细信息。在下面，您可以查看我们最受欢迎的招牌美味。",
        menu_download: "下载带价格的菜单 (PDF)",
        cat_food: "新鲜出炉",
        cat_drinks: "饮料与甜点",
        item_pizza: "石烤披萨",
        desc_pizza: "特制发酵面团，意大利番茄酱，搭配精美马苏里拉奶酪，在柴火烤炉中烘烤而成。",
        item_menemen: "著名的 Çakallı Menemen",
        desc_menemen: "仅用蛋黄，大量的切达干酪和黄油制成，一种传奇的地域性早餐口味。",
        item_toast: "烤 Bazlama 吐司",
        desc_toast: "石炉烤制，酥脆可口，乡村面包中夹有切达干酪和特制香肠/牛肉。",
        item_coffee: "炭火土耳其咖啡",
        desc_coffee: "在 150 年历史的氛围中，在铜壶中慢慢煮出的经典口味，搭配土耳其软糖。",
        item_tea: "招牌：玫瑰花瓣茶",
        desc_tea: "在我们的特制混合茶中加入新鲜干燥的玫瑰花瓣，带来令人难以置信的香气盛宴。",
        item_cake: "热巧克力酱蛋糕",
        desc_cake: "内里柔软，富含可可，表面覆盖着热巧克力酱，不可或缺的美味。",
        badge_veg: "素食",
        badge_vegan: "纯素",
        badge_gluten: "含麸质",
        badge_dairy: "含乳制品"
    }
};

function trackEvent(eventName) {
    try {
        fetch('/api/web/track-visit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({event: eventName})
        });
    } catch(e) {}
}

document.addEventListener('DOMContentLoaded', () => {
    trackEvent('pageview');
    
    // Yalnızca dışarı giden veya menüye tıklayan eylemleri izle
    document.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', (e) => {
            const href = a.getAttribute('href');
            if (href && href.includes('.pdf')) {
                trackEvent('menu');
            } else if (href && (href.includes('whatsapp') || href.includes('tel:'))) {
                trackEvent('action');
            }
        });
    });
});

function changeLanguage(event, lang) {
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (i18n[lang] && i18n[lang][key]) {
            // Use innerHTML instead of innerText to support line breaks (\n) if present
            el.innerHTML = i18n[lang][key].replace(/\n/g, "<br>");
        }
    });

    // Handle RTL for Arabic
    if (lang === 'ar') {
        document.body.style.direction = 'rtl';
    } else {
        document.body.style.direction = 'ltr';
    }
    
    // Update active button state
    document.querySelectorAll('.lang-selector button').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
}

// FETCH SETTINGS
async function fetchWebSettings() {
    try {
        const res = await fetch('/api/web/settings');
        const data = await res.json();
        
        function updateWorkHours(settingsData) {
            const element = document.getElementById('dynamic_work_hours');
            if (!element) return;
            
            const hours = settingsData.work_hours;
            const manualStatus = settingsData.manual_status || 'auto';
            
            if (manualStatus === 'open') {
                element.innerHTML = `<span class="pulse-dot"></span> Şu An Açık (${hours})`;
                element.parentElement.style.background = '#ecfdf5';
                element.parentElement.style.color = '#059669';
                return;
            } else if (manualStatus === 'closed') {
                const closedUntil = settingsData.closed_until || 'Belirsiz';
                element.innerHTML = `<span class="pulse-dot" style="background:#ef4444; box-shadow:none; animation:none;"></span> Kapalı (Açılış: ${closedUntil})`;
                element.parentElement.style.background = '#fef2f2';
                element.parentElement.style.color = '#dc2626';
                return;
            }
            
            // Auto Mode
            if (hours) {
                const now = new Date();
                const currentHour = now.getHours();
                const currentMinute = now.getMinutes();
                
                const parts = hours.split('-');
                if(parts.length === 2) {
                    const openTime = parts[0].trim();
                    const closeTime = parts[1].trim();
                    const [openH, openM] = openTime.split(':').map(Number);
                    const [closeH, closeM] = closeTime.split(':').map(Number);
                    
                    const nowTotal = currentHour * 60 + currentMinute;
                    const openTotal = openH * 60 + openM;
                    let closeTotal = closeH * 60 + closeM;
                    
                    if(closeTotal < openTotal) {
                        closeTotal += 24 * 60;
                    }
                    
                    let isOpen = false;
                    if(closeH < openH) {
                        if(nowTotal >= openTotal || nowTotal < (closeH * 60 + closeM)) {
                            isOpen = true;
                        }
                    } else {
                        if(nowTotal >= openTotal && nowTotal < closeTotal) {
                            isOpen = true;
                        }
                    }
                    
                    if(isOpen) {
                        element.innerHTML = `<span class="pulse-dot"></span> Şu An Açık (${hours})`;
                        element.parentElement.style.background = '#ecfdf5';
                        element.parentElement.style.color = '#059669';
                    } else {
                        let nextOpenDay = "Bugün";
                        if(nowTotal >= closeTotal || (closeH < openH && nowTotal >= (closeH * 60 + closeM) && nowTotal < openTotal)) {
                            nextOpenDay = "Yarın";
                        }
                        element.innerHTML = `<span class="pulse-dot" style="background:#ef4444; box-shadow:none; animation:none;"></span> Kapalı (Açılış: ${nextOpenDay} ${openTime})`;
                        element.parentElement.style.background = '#fef2f2';
                        element.parentElement.style.color = '#dc2626';
                    }
                } else {
                    element.innerText = hours;
                }
            }
        }
        
        updateWorkHours(data);
        if (data.address) {
            document.getElementById('dynamic_address').innerText = data.address;
        }
        if (data.instagram) {
            document.getElementById('dynamic_instagram').href = data.instagram;
        }
        if (data.baidu) {
            document.getElementById('dynamic_baidu_map').href = data.baidu;
            document.getElementById('dynamic_baidu_review').href = data.baidu;
        }
        if (data.phone) {
            document.getElementById('dynamic_whatsapp').href = `https://api.whatsapp.com/send?phone=${data.phone}`;
            document.getElementById('dynamic_phone').href = `tel:+${data.phone}`;
        }
    } catch (err) {
        console.error("Failed to fetch settings:", err);
    }
}
// Live Table Status Logic
function fetchTableStatus() {
    fetch('/api/web/tables-status')
        .then(response => response.json())
        .then(data => {
            const statusEl = document.getElementById('live-table-status');
            const iconEl = statusEl.previousElementSibling;
            if (data.success) {
                if (data.empty > 0) {
                    statusEl.innerText = `Şu an ${data.empty} masamız müsait, bekleriz!`;
                    statusEl.style.color = '#27ae60';
                    iconEl.style.color = '#2ecc71';
                } else {
                    statusEl.innerText = `Şu an tüm masalarımız dolu.`;
                    statusEl.style.color = '#e74c3c';
                    iconEl.style.color = '#e74c3c';
                }
            } else {
                statusEl.innerText = "Masa durumu alınamadı.";
            }
        })
        .catch(err => {
            console.error('Masa durumu hatası:', err);
            document.getElementById('live-table-status').innerText = "Sistem çevrimdışı.";
        });
}

// Virtual Tour Logic
function changeTour(type) {
    const iframe = document.getElementById('tour-iframe');
    if (type === 'interior') {
        iframe.src = "https://cdn.pannellum.org/2.5/pannellum.htm#panorama=https://pannellum.org/images/alma.jpg&autoLoad=true";
    } else {
        iframe.src = "https://cdn.pannellum.org/2.5/pannellum.htm#panorama=https://pannellum.org/images/cerro-toco-0.jpg&autoLoad=true";
    }
}

document.addEventListener("DOMContentLoaded", () => {
    fetchWebSettings();
    fetchTableStatus();
    // Refresh table status every 30 seconds
    setInterval(fetchTableStatus, 30000);
});

// Review Carousel Auto-Scroll Logic
let currentReviewIndex = 0;
const totalReviews = 3;

function showNextReview() {
    const currentSlide = document.getElementById(`review-slide-${currentReviewIndex}`);
    if (currentSlide) {
        currentSlide.style.opacity = '0';
        currentSlide.style.zIndex = '0';
    }
    
    currentReviewIndex = (currentReviewIndex + 1) % totalReviews;
    
    const nextSlide = document.getElementById(`review-slide-${currentReviewIndex}`);
    if (nextSlide) {
        nextSlide.style.opacity = '1';
        nextSlide.style.zIndex = '1';
    }
}

document.addEventListener("DOMContentLoaded", () => {
    setInterval(showNextReview, 4000);
});

