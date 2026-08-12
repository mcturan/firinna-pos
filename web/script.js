document.addEventListener('DOMContentLoaded', () => {
    // Yıl Güncelleme
    const yearSpan = document.getElementById('year');
    if (yearSpan) {
        yearSpan.textContent = '2025';
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
        btn_message: "Yöneticiye Mesaj İlet (Telegram)",
        title_about: "Hakkımızda",
        slogan_about: "GELENEKSEL TATLARA BENZERSİZ DOKUNUŞLAR",
        text_about: "DEĞERLİ MİSAFİRİMİZ, FIRINNA'YA HOŞ GELDİNİZ.\n\nGalata’nın 150 yıllık büyüleyici ve tarihi dokusunda, Kumbaracı Yokuşu'nun huzur veren atmosferinde yer alan Fırınna Cafe & Restaurant; İstiklal’in gürültüsünden kaçıp nefes alabileceğiniz özel bir lezzet durağıdır.\n\nÖzenle seçilmiş malzemelerimiz, fırınımızdan çıkan taze lezzetlerimiz, leziz kahve çeşitlerimiz ve ev yapımı tatlılarımızla geleneksel tarifleri modern dokunuşlarla sunuyoruz.\n\nBurada acele yok! Samimi, misafirperver ve evcil hayvan dostu ekibimizle, 150 yıllık bu tarihi yapının sıcaklığında güzel sohbetlerin ve huzurlu anların tadını çıkarın. Tarihi İstanbul gezinizde tatlı bir anı olabilmek bizim en büyük mutluluğumuz.",
        title_top_reviews: "Müşterilerimizin Gözünden",
        title_gating: "Deneyiminizi Puanlayın",
        sub_gating: "Fırınna deneyiminiz nasıldı? Görüşleriniz bizim için çok kıymetli.",
        gating_high_msg: "🎉 Harika! Beğenmenize çok sevindik. Bize aşağıdaki platformlardan 5 yıldızlı yorum vererek destek olmak ister misiniz?",
        gating_low_title: "Görüşleriniz Bizim İçin Çok Değerli!",
        gating_low_msg: "Yaşadığınız aksaklığı veya önerinizi doğrudan işletme yöneticimize iletebilirsiniz:",
        btn_google_review: "Google'da 5 Yıldız Ver",
        btn_yandex_review: "Yandex'te Puanla",
        btn_tripadvisor_review: "TripAdvisor'da Değerlendir",
        google_perfect: "Google'da Mükemmel",
        yandex_perfect: "Yandex'te Mükemmel",
        btn_inspect: "İncele",
        btn_see_all_google_photos: "Google Haritalar'daki Tüm Fotoğrafları Gör (100+)",
        table_available: "Şu an {N} masamız müsait, bekleriz!",
        table_full: "Şu an tüm masalarımız dolu.",
        table_offline: "Masa durumu bilgisi alınamadı.",
        text_group_events: "<strong>Grup & Özel Etkinlikler:</strong> Çalışma saatleri dışı grup rezervasyonları ve mini organizasyonlar için <a href='https://wa.me/905456301214?text=Merhaba,%20grup%20rezervasyonu%20veya%20özel%20etkinlik%20hakkında%20bilgi%20almak%20istiyorum.' target='_blank' style='color:#059669; font-weight:700; text-decoration:underline;'>WhatsApp'tan Ulaşabilirsiniz</a>.",
        review_1: "İstiklal'in gürültüsünden kaçıp nefes alabileceğiniz harika, tarihi bir mekan. Pizzaları efsane!",
        review_2: "Çakallı menemenini denemelisiniz. Personel çok güleryüzlü ve evcil hayvan dostu olmaları harika.",
        review_3: "Galata'da kahve içip tatlı yemek için en iyi nokta. Çalışanlar çok ilgili.",
        title_virtual_tour: "Sanal Tur (360°)",
        text_virtual_tour: "150 yıllık tarihi binamızı oturduğunuz yerden keşfedin.",
        title_faq: "Sıkça Sorulan Sorular",
        faq_q1: "🐾 Evcil hayvan kabul ediyor musunuz?",
        faq_a1: "Evet! Fırınna evcil hayvan dostudur (Pet-Friendly). Sevimli dostlarınızla bahçemizde ve iç mekanımızda keyifle vakit geçirebilirsiniz.",
        faq_q2: "💳 Hangi ödeme yöntemleri geçerlidir?",
        faq_a2: "Tüm yerli ve yabancı kredi kartları, banka kartları, temassız ödeme (Apple Pay / Google Pay) ve nakit geçerlidir.",
        faq_q3: "🥗 Vejetaryen / Glutensiz seçenekler var mı?",
        faq_a3: "Evet! Menümüzde özel vejetaryen taş fırın pizzalar, zengin kahvaltılıklar ve glutensiz/vegan alternatiflerimiz mevcuttur.",
        faq_q4: "🕒 Grup rezervasyonu veya özel etkinlik yapabilir miyiz?",
        faq_a4: "Evet, doğum günü, toplantı ve özel mini organizasyonlar için doğrudan WhatsApp hattımızdan bizimle iletişime geçebilirsiniz.",
        title_location: "Lokasyon",
        title_contact: "İletişim & Ulaşım",
        title_gallery: "Ortam & Lezzetler",
        gal_title_interior: "İç Mekan & Atmosfer",
        gal_title_exterior: "Dış Mekan & Kumbaracı Yokuşu",
        gal_title_signature: "İmza Lezzetlerimiz",
        gal_lbl_interior_history: "Tarihi İç Mekan",
        gal_lbl_warm_tables: "Sıcak Masalar",
        gal_lbl_details: "Mekan Detayları",
        gal_lbl_street: "Kumbaracı Yokuşu",
        gal_lbl_outdoor_seating: "Dış Masa Alanı",
        gal_lbl_historic_building: "Tarihi Binası",
        gal_lbl_fresh_tea: "Taze Çay",
        gal_lbl_turkish_coffee: "Türk Kahvesi",
        gal_lbl_menemen: "Tava Menemen",
        gal_lbl_pizza: "Taş Fırın Pizza",
        gal_lbl_lemonade: "Ev Yapımı Limonata",
        gal_lbl_glintwein: "Sıcak Glintwein",
        badge_historic_tr: "Tarihi Türk Cafesi",
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
        item_coffee: "Özel Türk Kahvesi",
        desc_coffee: "Özel kavrulmuş ve çekilmiş en kaliteli taze Arabica kahvelerin en lezzetli pişirilmiş hali ve yanında meşhur Türk lokumu.",
        item_tea: "Gül Goncalı Harman Çay",
        desc_tea: "En seçkin Türk ve Seylan çayı karışımı içinde bergamot ve kuru gül goncaları ile demlenir.",
        item_lemonade: "Ev Yapımı Özel Limonata",
        desc_lemonade: "Buz gibi ev yapımı taze limonata; içerisinde ekstra hibiskus, tarçın, yıldız anason ve İran safranı harmanlanmıştır.",
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
        slogan_about: "UNIQUE TOUCHES TO TRADITIONAL FLAVORS",
        text_about: "DEAR GUEST, WELCOME TO FIRINNA.\n\nLocated in the 150-year-old historic atmosphere of Galata, right on the peaceful Kumbaracı Yokuşu, Fırınna Cafe & Restaurant is a special culinary haven where you can step away from the bustle of Istiklal Street and take a refreshing breath.\n\nWith carefully selected ingredients, fresh oven-baked specialties, rich coffee varieties, and homemade desserts, we bring traditional recipes to life with modern touches.\n\nThere is no rush here! With our friendly, hospitable, and pet-friendly team, enjoy warm conversations and peaceful moments in the ambiance of our 150-year-old historic building. We would be delighted to be a sweet memory of your historic trip to Istanbul.",
        title_top_reviews: "From Our Customers",
        title_gating: "Rate Your Experience",
        sub_gating: "How was your experience at Firinna? Your feedback means a lot to us.",
        gating_high_msg: "🎉 Wonderful! We're glad you enjoyed it. Would you like to support us with a 5-star review on these platforms?",
        gating_low_title: "Your Feedback is Very Valuable to Us!",
        gating_low_msg: "You can send any feedback or issues directly to our manager:",
        btn_google_review: "Rate 5 Stars on Google",
        btn_yandex_review: "Rate on Yandex",
        btn_tripadvisor_review: "Review on TripAdvisor",
        google_perfect: "Excellent on Google",
        yandex_perfect: "Excellent on Yandex",
        btn_inspect: "Review",
        btn_see_all_google_photos: "See All Photos on Google Maps (100+)",
        table_available: "Currently {N} tables available, welcome!",
        table_full: "Currently all tables are occupied.",
        table_offline: "Table status unavailable.",
        text_group_events: "<strong>Group & Private Events:</strong> For after-hours group bookings and mini events, please <a href='https://wa.me/905456301214?text=Hello,%20I%20would%20like%20information%20about%20group%20bookings.' target='_blank' style='color:#059669; font-weight:700; text-decoration:underline;'>Contact via WhatsApp</a>.",
        review_1: "A wonderful, historic place to escape the noise of Istiklal and take a breath. Their pizzas are legendary!",
        review_2: "You must try the Çakallı menemen. The staff is very smiling and it's great that they are pet-friendly.",
        review_3: "The best spot in Galata for coffee and desserts. The staff is very attentive.",
        title_virtual_tour: "Virtual Tour (360°)",
        text_virtual_tour: "Explore our 150-year-old historic building right from where you sit.",
        title_faq: "Frequently Asked Questions",
        faq_q1: "🐾 Are pets allowed?",
        faq_a1: "Yes! Fırınna is 100% pet-friendly. You are welcome to enjoy your time with your furry friends both in our outdoor garden and indoor seating.",
        faq_q2: "💳 What payment methods do you accept?",
        faq_a2: "We accept all major credit cards, debit cards, contactless mobile payments (Apple Pay / Google Pay), and cash.",
        faq_q3: "🥗 Do you have Vegetarian or Gluten-Free options?",
        faq_a3: "Yes! Our menu offers gourmet vegetarian stone-oven pizzas, rich breakfast spreads, and gluten-free/vegan alternatives.",
        faq_q4: "🕒 Can we make group reservations or private events?",
        faq_a4: "Yes! For birthdays, corporate meetings, or private mini events, feel free to contact us directly via WhatsApp.",
        title_location: "Location",
        title_contact: "Contact & Location",
        title_gallery: "Ambiance & Tastes",
        gal_title_interior: "Indoor & Ambiance",
        gal_title_exterior: "Outdoor & Kumbaracı Street",
        gal_title_signature: "Our Signature Tastes",
        gal_lbl_interior_history: "Historic Interior",
        gal_lbl_warm_tables: "Cozy Seating",
        gal_lbl_details: "Venue Details",
        gal_lbl_street: "Kumbaracı Street",
        gal_lbl_outdoor_seating: "Outdoor Seating",
        gal_lbl_historic_building: "Historic Building",
        gal_lbl_fresh_tea: "Fresh Turkish Tea",
        gal_lbl_turkish_coffee: "Turkish Coffee",
        gal_lbl_menemen: "Skillet Menemen",
        gal_lbl_pizza: "Stone Oven Pizza",
        gal_lbl_lemonade: "Homemade Lemonade",
        gal_lbl_glintwein: "Mulled Wine",
        badge_historic_tr: "Historic Turkish Cafe",
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
        item_coffee: "Special Turkish Coffee",
        desc_coffee: "Finely roasted and ground premium fresh Arabica coffee, expertly brewed and served with famous Turkish delight.",
        item_tea: "Rosebud Blended Tea",
        desc_tea: "Brewed with a premium blend of Turkish and Ceylon tea, bergamot, and dried rosebuds.",
        item_lemonade: "Special Homemade Lemonade",
        desc_lemonade: "Ice-cold homemade fresh lemonade infused with hibiscus, cinnamon, star anise, and authentic Persian saffron.",
        item_cake: "Hot Chocolate Cake with Chocolate Sauce",
        desc_cake: "Soft on the inside, lots of cocoa, and covered with hot chocolate sauce, an indispensable taste.",
        badge_veg: "Vegetarian",
        badge_vegan: "Vegan",
        badge_gluten: "Contains Gluten",
        badge_dairy: "Contains Dairy"
    },
    es: {
        category: "Cafetería y Restaurante",
        status_open: "Abierto Ahora (08:00 - 23:00)",
        btn_menu: "Ver Menú Digital",
        btn_reserve: "Reservar una Mesa",
        btn_message: "Enviarnos un Mensaje",
        title_about: "Sobre Nosotros",
        slogan_about: "TOQUES ÚNICOS A SABORES TRADICIONALES",
        text_about: "ESTIMADO CLIENTE, BIENVENIDO A FIRINNA.\n\nUbicado en la atmósfera histórica de 150 años de Galata, en la tranquila calle Kumbaracı Yokuşu, Fırınna Cafe & Restaurant es un rincón culinario especial para alejarse del bullicio de la calle Istiklal.\n\nCon ingredientes cuidadosamente seleccionados, especialidades recién horneadas, ricas variedades de café y postres caseros, damos vida a las recetas tradicionales con toques modernos.\n\n¡Aquí no hay prisas! Con nuestro equipo hospitalario y amigable con las mascotas (Pet-Friendly), disfrute de cálidas conversaciones y momentos de paz en el ambiente de nuestro edificio histórico de 150 años.",
        title_top_reviews: "De Nuestros Clientes",
        title_gating: "Evalúe su Experiencia",
        sub_gating: "¿Cómo fue su experiencia en Firinna? Sus comentarios son muy valiosos para nosotros.",
        gating_high_msg: "🎉 ¡Maravilloso! Nos alegra mucho que le haya gustado. ¿Le gustaría apoyarnos con una reseña de 5 estrellas en estas plataformas?",
        gating_low_title: "¡Sus Comentarios son Muy Valiosos!",
        gating_low_msg: "Puede enviar cualquier sugerencia o problema directamente a nuestro gerente:",
        btn_google_review: "Valorar con 5 Estrellas en Google",
        btn_yandex_review: "Valorar en Yandex",
        btn_tripadvisor_review: "Valorar en TripAdvisor",
        google_perfect: "Excelente en Google",
        yandex_perfect: "Excelente en Yandex",
        btn_inspect: "Revisar",
        btn_see_all_google_photos: "Ver Todas las Fotos en Google Maps (100+)",
        table_available: "Actualmente hay {N} mesas disponibles, ¡bienvenido!",
        table_full: "Actualmente todas las mesas están ocupadas.",
        table_offline: "Estado de las mesas no disponible.",
        text_group_events: "<strong>Eventos de Grupo y Privados:</strong> Para reservas de grupos fuera del horario habitual, <a href='https://wa.me/905456301214' target='_blank' style='color:#059669; font-weight:700; text-decoration:underline;'>Contacte por WhatsApp</a>.",
        review_1: "Un lugar histórico y maravilloso para escapar del ruido de Istiklal. ¡Sus pizzas son legendarias!",
        review_2: "Debes probar el menemen Çakallı. El personal es muy amable y es genial que acepten mascotas.",
        review_3: "El mejor lugar en Galata para tomar café y postres. El personal es muy atento.",
        title_virtual_tour: "Recorrido Virtual (360°)",
        text_virtual_tour: "Explore nuestro edificio histórico de 150 años desde donde se encuentre.",
        title_faq: "Preguntas Frecuentes",
        faq_q1: "🐾 ¿Se aceptan mascotas?",
        faq_a1: "¡Sí! Fırınna es 100% amigable con las mascotas (Pet-Friendly). Le invitamos a disfrutar con sus mascotas tanto en el jardín exterior como en el interior.",
        faq_q2: "💳 ¿Qué métodos de pago aceptan?",
        faq_a2: "Aceptamos todas las tarjetas de crédito, débito, pagos móviles sin contacto (Apple Pay / Google Pay) y efectivo.",
        faq_q3: "🥗 ¿Tienen opciones Vegetarianas o Sin Gluten?",
        faq_a3: "¡Sí! Nuestro menú ofrece pizzas gourmet vegetarianas al horno de piedra, desayunos variados y alternativas sin gluten/veganas.",
        faq_q4: "🕒 ¿Podemos hacer reservas de grupo o eventos privados?",
        faq_a4: "¡Sí! Para cumpleaños, reuniones de empresa o mini eventos privados, contáctenos directamente por WhatsApp.",
        title_location: "Ubicación",
        title_contact: "Contacto y Ubicación",
        title_gallery: "Ambiente y Sabores",
        gal_title_interior: "Interior y Ambiente",
        gal_title_exterior: "Exterior y Calle Kumbaracı",
        gal_title_signature: "Nuestros Sabores Especiales",
        gal_lbl_interior_history: "Interior Histórico",
        gal_lbl_warm_tables: "Mesas Acogedoras",
        gal_lbl_details: "Detalles del Local",
        gal_lbl_street: "Calle Kumbaracı",
        gal_lbl_outdoor_seating: "Mesas Exteriores",
        gal_lbl_historic_building: "Edificio Histórico",
        gal_lbl_fresh_tea: "Té Turco Fresco",
        gal_lbl_turkish_coffee: "Café Turco",
        gal_lbl_menemen: "Menemen en Sartén",
        gal_lbl_pizza: "Pizza al Horno de Piedra",
        gal_lbl_lemonade: "Limonada Casera",
        gal_lbl_glintwein: "Vino Caliente Especial",
        badge_historic_tr: "Cafetería Histórica Turca",
        badge_halal: "100% Halal",
        badge_quality: "Mejor Calidad",
        badge_price: "Precio Justo",
        title_reviews: "Ubicación y Reseñas Recientes",
        btn_google: "Leer Reseñas Recientes en Google",
        btn_yandex: "Ver en Yandex Maps",
        btn_baidu: "Ver en Baidu Maps",
        modal_res_title: "Reserva de Mesa",
        label_name: "Nombre Completo",
        label_phone: "Teléfono",
        label_date: "Fecha",
        label_time: "Hora (08:00-23:00)",
        label_guests: "Número de Personas",
        label_note: "Petición Especial / Nota (Opcional)",
        btn_submit: "Enviar Solicitud",
        modal_msg_title: "Enviarnos un Mensaje",
        label_message: "Su Mensaje",
        btn_submit_msg: "Enviar Mensaje",
        footer_rights: "Todos los derechos reservados.",
        menu_header_title: "Sabores Especiales",
        menu_header_sub: "Con el toque de Firinna...",
        menu_back: "Inicio",
        menu_intro: "Puede visitar nuestro local o consultar con nuestro personal para conocer todas las opciones del menú. A continuación puede revisar nuestros sabores especiales más populares.",
        menu_download: "Descargar Menú con Precios (PDF)",
        cat_food: "Caliente del Horno",
        cat_drinks: "Bebidas y Postres",
        item_pizza: "Pizza al Horno de Piedra",
        desc_pizza: "Masa especial fermentada, salsa de tomate italiana y exquisito queso mozzarella horneado en horno de leña.",
        item_menemen: "Famoso Menemen Çakallı",
        desc_menemen: "Preparado solo con yemas de huevo, abundante queso cheddar y mantequilla, un desayuno legendario.",
        item_toast: "Tostada de Bazlama al Horno",
        desc_toast: "Servida crujiente del horno de piedra con queso cheddar y salchicha/carne especial entre pan de aldea.",
        item_coffee: "Café Turco Especial",
        desc_coffee: "Café Arábica fresco de primera calidad, tostado y molido, preparado magistralmente y servido con la famosa delicia turca (lokum).",
        item_tea: "Té Mezcla con Capullos de Rosa",
        desc_tea: "Infusionado con una mezcla premium de té turco y ceilán, bergamota y capullos de rosa secos.",
        item_lemonade: "Limonada Casera Especial",
        desc_lemonade: "Limonada casera helada infusionada con hibisco, canela, anís estrellado y azafrán iraní auténtico.",
        item_cake: "Pastel Caliente con Salsa de Chocolate",
        desc_cake: "Tiernos por dentro, con abundante cacao y cubierto con salsa de chocolate caliente, un sabor imprescindible.",
        badge_veg: "Vegetariano",
        badge_vegan: "Vegano",
        badge_gluten: "Contiene Gluten",
        badge_dairy: "Contiene Lácteos"
    },
    ru: {
        category: "Кафе и Ресторан",
        status_open: "Сейчас открыто (08:00 - 23:00)",
        btn_menu: "Посмотреть меню",
        btn_reserve: "Забронировать столик",
        btn_message: "Напишите нам",
        title_about: "О нас",
        slogan_about: "УНИКАЛЬНЫЙ ШТРИХ К ТРАДИЦИОННЫМ ВКУСАМ",
        text_about: "ДОРОГОЙ ГОСТЬ, ДОБРО ПОЖАЛОВАТЬ В FIRINNA.\n\nРасположенное в 150-летнем историческом здании в районе Галата, на уютной улочке Кумбараджи Йокушу, кафе-ресторан Fırınna — это особенный уголок, где можно отдохнуть от шума улицы Истикляль.\n\nКак часто отмечают наши гости в отзывах Google: мы предлагаем традиционные рецепты с фирменными штрихами Fırınna — хрустящую пиццу из дровяной каменной печи, знаменитый менемен Чакаллы, горячие тосты на домашнем хлебе и турецкий кофе на углях в медной джезве.\n\nЗдесь нет спешки! С нашей радушной и pet-friendly командой наслаждайтесь теплым общением и незабываемыми вкусами.",
        title_top_reviews: "Отзывы клиентов",
        title_gating: "Оцените ваш визит",
        sub_gating: "Как вам отдых в Firinna? Ваше мнение очень важно для нас.",
        gating_high_msg: "🎉 Замечательно! Будем благодарны за 5 звезд на следующих платформах:",
        gating_low_title: "Ваше мнение очень важно для нас!",
        gating_low_msg: "Вы можете отправить ваш отзыв напрямую нашему управляющему:",
        btn_google_review: "Поставить 5 звезд в Google",
        btn_yandex_review: "Оценить в Яндекс",
        btn_tripadvisor_review: "Отзыв на TripAdvisor",
        google_perfect: "Отлично в Google",
        yandex_perfect: "Отлично в Яндекс",
        btn_inspect: "Посмотреть",
        btn_see_all_google_photos: "Все фото на Гугл Картах (100+)",
        table_available: "Сейчас свободно {N} столов, ждем вас!",
        table_full: "Сейчас все столы заняты.",
        table_offline: "Статус столов недоступен.",
        text_group_events: "<strong>Группы и мероприятия:</strong> Для бронирования во внерабочее время <a href='https://wa.me/905456301214' target='_blank' style='color:#059669; font-weight:700; text-decoration:underline;'>Напишите в WhatsApp</a>.",
        review_1: "Замечательное, историческое место, где можно спрятаться от шума Истикляля и перевести дух. Их пицца легендарна!",
        review_2: "Вы должны попробовать менемен Чакаллы. Персонал очень улыбчивый, и здорово, что к ним можно с питомцами.",
        review_3: "Лучшее место в Галате для кофе и десертов. Персонал очень внимателен.",
        title_virtual_tour: "Виртуальный тур (360°)",
        text_virtual_tour: "Исследуйте наше 150-летнее историческое здание, не выходя из дома.",
        title_faq: "Часто задаваемые вопросы",
        faq_q1: "🐾 Разрешено ли с домашними животными?",
        faq_a1: "Да! Fırınna на 100% pet-friendly заведение. Вы можете приятно провести время со своими питомцами как в нашем саду, так и в зале.",
        faq_q2: "💳 Какие способы оплаты вы принимаете?",
        faq_a2: "Мы принимаем все основные кредитные и дебетовые карты, бесконтактную оплату (Apple Pay / Google Pay) и наличные.",
        faq_q3: "🥗 Есть ли вегетарианские или безглютеновые блюда?",
        faq_a3: "Да! В нашем меню есть вегетарианская пицца из каменной печи, богатый завтрак и безглютеновые/веганские альтернативы.",
        faq_q4: "🕒 Можно ли забронировать стол для группы или провести мероприятие?",
        faq_a4: "Да, для дней рождения, встреч или частных мероприятий свяжитесь с нами напрямую через WhatsApp.",
        title_location: "Расположение",
        title_contact: "Контакты и расположение",
        title_gallery: "Атмосфера и Вкус",
        gal_title_interior: "Интерьер и Атмосфера",
        gal_title_exterior: "Улица и Терраса",
        gal_title_signature: "Наши Фирменные Блюда",
        gal_lbl_interior_history: "Исторический Интерьер",
        gal_lbl_warm_tables: "Уютные Столики",
        gal_lbl_details: "Детали Заведения",
        gal_lbl_street: "Улица Кумбараджи",
        gal_lbl_outdoor_seating: "Столики на Улице",
        gal_lbl_historic_building: "Историческое Здание",
        gal_lbl_fresh_tea: "Свежий Турецкий Чай",
        gal_lbl_turkish_coffee: "Турецкий Кофе",
        gal_lbl_menemen: "Менемен на Сковороде",
        gal_lbl_pizza: "Пицца из Печи",
        gal_lbl_lemonade: "Домашний Лимонад",
        gal_lbl_glintwein: "Горячий Глинтвейн",
        badge_historic_tr: "Историческое турецкое кафе",
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
        item_coffee: "Специальный Турецкий Кофе",
        desc_coffee: "Свежеобжаренная и тонко смолотая Арабика премиум-класса, сваренная мастерски и подаваемая с турецким рахат-лукумом.",
        item_tea: "Фирменный Чай с Бутонами Роз",
        desc_tea: "Заваривается из элитной смеси турецкого и цейлонского чая с бергамотом и сушеными бутонами роз.",
        item_lemonade: "Домашний Особый Лимонад",
        desc_lemonade: "Освежающий домашний лимонад с добавлением гибискуса, корицы, бадьяна и настоящего иранского шафрана.",
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
        slogan_about: "لمسات فريدة على النكهات التقليدية",
        text_about: "ضيفنا العزيز، أهلاً بك في FIRINNA.\n\nيقع مطعم ومقهى فِرِنّا في أجواء غلاطة التاريخية الممتدة لـ 150 عامًا على منحدر كومباراجي الهادئ، وهو ملاذ رائع للابتعاد عن صخب شارع الاستقلال والاستمتاع بلحظات ممتعة.\n\nكما يُثني ضيوفنا دائمًا في مراجعات جوجل؛ نقدم الوصفات التقليدية بلمسات حديثة مميزة — بدءًا من البيتزا المقرمشة المخبوزة في الفرن الحجري على الخشب، والمناقيش والشكشوكة التركية، إلى القهوة التركية المطهوة بطبقتين على الفحم والشاي ببتلات الورد والحلويات المنزلية الطازجة.\n\nلا يوجد استعجال هنا! مع فريقنا الودود والمستضيف والرحب بالحيوانات الأليفة، استمتع بأجواء 150 عامًا من التاريخ والنكهات الرائعة.",
        title_top_reviews: "من عملائنا",
        title_gating: "قيم تجربتك",
        sub_gating: "كيف كانت تجربتك في فِرِنّا؟ رأيك يهمنا كثيراً.",
        gating_high_msg: "🎉 رائع! نتشرف بدعمك لنا بتقييم 5 نجوم على إحدى المنصات التالية:",
        gating_low_title: "رأيك يهمنا جداً!",
        gating_low_msg: "يمكنك إرسال ملاحظاتك مباشرة إلى مديرنا:",
        btn_google_review: "تقييم 5 نجوم على جوجل",
        btn_yandex_review: "تقييم على ياندكس",
        btn_tripadvisor_review: "تقييم على TripAdvisor",
        google_perfect: "ممتاز على جوجل",
        yandex_perfect: "ممتاز على ياندكس",
        btn_inspect: "تصفح",
        btn_see_all_google_photos: "عرض جميع الصور على خرائط جوجل (+100)",
        table_available: "حالياً هناك {N} طاولات متاحة، أهلاً بكم!",
        table_full: "حالياً جميع الطاولات مشغولة.",
        table_offline: "حالة الطاولات غير متوفرة.",
        text_group_events: "<strong>المجموعات والفعاليات:</strong> للحجوزات الجماعية والفعاليات خارج أوقات العمل <a href='https://wa.me/905456301214' target='_blank' style='color:#059669; font-weight:700; text-decoration:underline;'>تواصل عبر واتساب</a>.",
        review_1: "مكان تاريخي رائع للهروب من ضجيج الاستقلال وأخذ قسط من الراحة. البيتزا الخاصة بهم أسطورية!",
        review_2: "يجب أن تجرب مينيمين تشاكالي. الموظفون مبتسمون للغاية ومن الرائع أنهم يسمحون بالحيوانات الأليفة.",
        review_3: "أفضل مكان في غلطة لتناول القهوة والحلويات. فريق العمل مهتم جدا.",
        title_virtual_tour: "جولة افتراضية (360 درجة)",
        text_virtual_tour: "استكشف مبنانا التاريخي الممتد لـ 150 عامًا من مكانك.",
        title_faq: "الأسئلة الشائعة",
        faq_q1: "🐾 هل يُسمح باصطحاب الحيوانات الأليفة؟",
        faq_a1: "نعم! مقهى فرنة صديق للحيوانات الأليفة. يمكنك الاستمتاع بفيض الأجواء الجميلة برفقة أليفك في الحديقة الخارجية والقاعة الداخلية.",
        faq_q2: "💳 ما هي طرق الدفع المتاحة؟",
        faq_a2: "نقبل جميع البطاقات الائتمانية والدفع اللاتلامسي (Apple Pay / Google Pay) والنقد.",
        faq_q3: "🥗 هل تتوفر خيارات نباتية أو خالية من الغلوتين؟",
        faq_a3: "نعم! تحتوي قائمتنا على بيتزا الحطب النباتية، وجبات الإفطار الغنية، وبدائل خالية من الغلوتين.",
        faq_q4: "🕒 هل يمكننا حجز طاولات للمجموعات أو المناسبات الخاصة؟",
        faq_a4: "نعم، لحفلات أعياد الميلاد والاجتماعات الخاصة، يمكنك التواصل معنا مباشرة عبر الواتساب.",
        title_location: "الموقع",
        title_contact: "الاتصال والموقع",
        title_gallery: "الأجواء والمذاق",
        gal_title_interior: "التصميم الداخلي والجو",
        gal_title_exterior: "الجلسات الخارجية والموقع",
        gal_title_signature: "أطباقنا المميزة",
        gal_lbl_interior_history: "التصميم التاريخي",
        gal_lbl_warm_tables: "طاولات دافئة",
        gal_lbl_details: "تفاصيل المكان",
        gal_lbl_street: "شارع كومباراجي",
        gal_lbl_outdoor_seating: "الجلسة الخارجية",
        gal_lbl_historic_building: "المبنى التاريخي",
        gal_lbl_fresh_tea: "شاي تركي طازج",
        gal_lbl_turkish_coffee: "قهوة تركية",
        gal_lbl_menemen: "قلاية ميجنيمن",
        gal_lbl_pizza: "بيتزا الحطب",
        gal_lbl_lemonade: "ليموناضة منزلية",
        gal_lbl_glintwein: "شراب دافئ",
        badge_historic_tr: "مقهى تركي تاريخي",
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
        item_coffee: "قهوة تركية فاخرة",
        desc_coffee: "قهوة أرابيكا طازجة محمصة ومطحونة بعناية، مطبوخة بأعلى درجات الإتقان وتقدم مع الراحة التركية الشهيرة.",
        item_tea: "شاي مميز ببراعم الورد",
        desc_tea: "مخلوط من أجود أنواع الشاي التركي والسيلاني مع البرغموت وبراعم الورد المجففة.",
        item_lemonade: "ليموناضة منزلية خاصة",
        desc_lemonade: "ليموناضة طازجة باردة كالثلج، ممزوجة بالكركديه والقرفة واليانسون النجمي والزعفران الإيراني الفاخر.",
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
        slogan_about: "传统风味的独特创新",
        text_about: "尊贵的客人们，欢迎来到 FIRINNA。\n\nFırınna 咖啡餐厅位于加拉塔拥有150年历史的建筑之中，地处宁静的 Kumbaracı 巷。这里是避开独立大街喧嚣、享受悠闲时光的绝佳去处。\n\n正如许多顾客在 Google 评价中所盛赞的那样：我们以现代创新融合传统配方——石炉木炭烘烤的松脆披萨、特制土耳其土豆软蛋饼（Menemen）、炭火烘培的传统土耳其咖啡以及玫瑰花瓣香茶与手工甜点。\n\n在这里，无需匆忙！在我们宠物友好的热情服务下，尽情享受这栋150年历史建筑带来的温馨与美妙风味。",
        title_top_reviews: "顾客评价",
        title_gating: "评价您的体验",
        sub_gating: "您在 Firinna 的体验如何？您的反馈对我们非常重要。",
        gating_high_msg: "🎉 太棒了！很高兴您喜欢。欢迎在以下平台上为我们留下 5 星好评：",
        gating_low_title: "您的宝贵意见对我们非常重要！",
        gating_low_msg: "您可以直接将建议或遇到的问题发送给我们的管理人员：",
        btn_google_review: "在 Google 上给 5 星好评",
        btn_yandex_review: "在 Yandex 上评价",
        btn_tripadvisor_review: "在 TripAdvisor 上评价",
        google_perfect: "Google 上的绝佳评价",
        yandex_perfect: "Yandex 上的绝佳评价",
        btn_inspect: "查看",
        btn_see_all_google_photos: "在 Google 地图上查看所有照片 (100+)",
        table_available: "目前有 {N} 张空桌，欢迎光临！",
        table_full: "目前所有餐桌均已客满。",
        table_offline: "无法获取餐桌状态。",
        text_group_events: "<strong>团体与私人活动：</strong> 如需非营业时间的团体预订或私人活动，请 <a href='https://wa.me/905456301214' target='_blank' style='color:#059669; font-weight:700; text-decoration:underline;'>通过 WhatsApp 联系我们</a>。",
        review_1: "一个美妙的、充满历史感的地方，在这里可以逃离Istiklal的喧嚣，稍作喘息。他们的比萨堪称传奇！",
        review_2: "你一定要尝尝Çakallı menemen。员工都面带微笑，而且这里对宠物很友好，真是太棒了。",
        review_3: "Galata喝咖啡和吃甜点的最佳去处。员工非常周到。",
        title_virtual_tour: "虚拟全景导览 (360°)",
        text_virtual_tour: "从您所在的位置探索我们拥有150年历史的古老建筑。",
        title_faq: "常见问题解答",
        faq_q1: "🐾 是否允许携带宠物？",
        faq_a1: "是的！Fırınna 是宠物友好型餐厅。欢迎您带着宠物在我们的户外花园和室内用餐。",
        faq_q2: "💳 接受哪些支付方式？",
        faq_a2: "我们接受所有主要的信用卡、借记卡、非接触式支付（Apple Pay / Google Pay）和现金。",
        faq_q3: "🥗 是否提供素食或无麸质选择？",
        faq_a3: "是的！我们的菜单提供石炉烘烤素食披萨、丰富的早餐拼盘以及无麸质/纯素选择。",
        faq_q4: "🕒 是否可以预订团体用餐或举办私人活动？",
        faq_a4: "是的！对于生日聚会、商务会议或私人小型活动，请通过 WhatsApp 直接与我们联系。",
        title_location: "地点",
        title_contact: "联系与位置",
        title_gallery: "氛围与口味",
        gal_title_interior: "室内环境与氛围",
        gal_title_exterior: "户外与街景",
        gal_title_signature: "招牌美味",
        gal_lbl_interior_history: "历史感室内",
        gal_lbl_warm_tables: "温馨座位",
        gal_lbl_details: "场地细节",
        gal_lbl_street: "Kumbara 街",
        gal_lbl_outdoor_seating: "户外座位",
        gal_lbl_historic_building: "历史建筑",
        gal_lbl_fresh_tea: "新鲜土耳其茶",
        gal_lbl_turkish_coffee: "土耳其咖啡",
        gal_lbl_menemen: "铁锅煎蛋米内门",
        gal_lbl_pizza: "石炉披萨",
        gal_lbl_lemonade: "自制柠檬水",
        gal_lbl_glintwein: "热红酒",
        badge_historic_tr: "历史悠久的土耳其咖啡馆",
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
        item_coffee: "特调土耳其咖啡",
        desc_coffee: "选用优质新鲜阿拉比卡咖啡豆精心烘焙与研磨，精湛工艺烹煮，随附著名土耳其软糖。",
        item_tea: "玫瑰花苞特调茶",
        desc_tea: "采用精选土耳其与锡兰红茶拼配，融入香柠檬与干燥玫瑰花苞精心冲泡。",
        item_lemonade: "自制特调冰柠檬水",
        desc_lemonade: "冰爽自制新鲜柠檬水，特别融入洛神花、肉桂、八角与特级伊朗藏红花。",
        item_cake: "热巧克力酱蛋糕",
        desc_cake: "内里柔软，富含可可，表面覆盖着热巧克力酱，不可或缺的美味。",
        badge_veg: "素食",
        badge_vegan: "纯素",
        badge_gluten: "含麸质",
        badge_dairy: "含乳制品"
    }
};

let pageStartTime = Date.now();
let maxScrollPct = 0;

window.addEventListener('scroll', () => {
    try {
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const scrollHeight = document.documentElement.scrollHeight - window.innerHeight;
        if (scrollHeight > 0) {
            const currentPct = Math.round((scrollTop / scrollHeight) * 100);
            if (currentPct > maxScrollPct) maxScrollPct = currentPct;
        }
    } catch(e) {}
}, { passive: true });

function trackEvent(eventName, extraData = {}) {
    try {
        let isRepeat = false;
        if (localStorage.getItem('firinna_vid')) {
            isRepeat = true;
        } else {
            localStorage.setItem('firinna_vid', Date.now());
        }
        
        const timeSpentSeconds = Math.round((Date.now() - pageStartTime) / 1000);

        const payload = {
            event: eventName,
            isRepeat: isRepeat,
            userAgent: navigator.userAgent,
            language: navigator.language || navigator.userLanguage,
            selectedLanguage: localStorage.getItem('firinna_lang') || 'tr',
            referrer: document.referrer,
            urlQuery: window.location.search,
            screenWidth: window.innerWidth,
            scrollDepth: maxScrollPct,
            timeSpentSeconds: timeSpentSeconds,
            ...extraData
        };
        fetch('/api/web/track-visit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
    } catch(e) {}
}

window.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
        trackEvent('duration_update');
    }
});

document.addEventListener('DOMContentLoaded', () => {
    trackEvent('pageview');
    fetchWebProducts();
    
    // Otomatik Cihaz / Tarayıcı Dili Algılama
    let initialLang = localStorage.getItem('firinna_lang');
    if (!initialLang) {
        const sysLang = (navigator.language || navigator.userLanguage || '').toLowerCase();
        if (sysLang.startsWith('tr')) initialLang = 'tr';
        else if (sysLang.startsWith('ru')) initialLang = 'ru';
        else if (sysLang.startsWith('ar')) initialLang = 'ar';
        else if (sysLang.startsWith('zh')) initialLang = 'zh';
        else initialLang = 'en'; // Bilinmeyen dillerde varsayılan İNGİLİZCE!
    }
    changeLang(initialLang);

    // Harita, PDF ve İletişim eylemlerini izle
    document.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', (e) => {
            const href = a.getAttribute('href') || '';
            if (href.includes('.pdf')) {
                trackEvent('menu');
            } else if (href.includes('whatsapp') || href.includes('tel:')) {
                trackEvent('action');
            } else if (href.includes('google.com/maps') || href.includes('yandex') || href.includes('baidu')) {
                trackEvent('map');
            }
        });
    });
});

function switchGalleryTab(tab) {
    const intBox = document.getElementById('gallery_interior_box');
    const extBox = document.getElementById('gallery_exterior_box');
    const btnInt = document.getElementById('tab_interior');
    const btnExt = document.getElementById('tab_exterior');
    if (tab === 'interior') {
        if (intBox) intBox.style.display = 'grid';
        if (extBox) extBox.style.display = 'none';
        if (btnInt) { btnInt.style.background = '#f59e0b'; btnInt.style.color = '#fff'; }
        if (btnExt) { btnExt.style.background = '#e2e8f0'; btnExt.style.color = '#475569'; }
    } else {
        if (intBox) intBox.style.display = 'none';
        if (extBox) extBox.style.display = 'grid';
        if (btnInt) { btnInt.style.background = '#e2e8f0'; btnInt.style.color = '#475569'; }
        if (btnExt) { btnExt.style.background = '#f59e0b'; btnExt.style.color = '#fff'; }
    }
}

const DAYS_I18N = {
    tr: { "Pazartesi": "Pazartesi", "Salı": "Salı", "Çarşamba": "Çarşamba", "Perşembe": "Perşembe", "Cuma": "Cuma", "Cumartesi": "Cumartesi", "Pazar": "Pazar" },
    en: { "Pazartesi": "Monday", "Salı": "Tuesday", "Çarşamba": "Wednesday", "Perşembe": "Thursday", "Cuma": "Friday", "Cumartesi": "Saturday", "Pazar": "Sunday" },
    es: { "Pazartesi": "Lunes", "Salı": "Martes", "Çarşamba": "Miércoles", "Perşembe": "Jueves", "Cuma": "Viernes", "Cumartesi": "Sábado", "Pazar": "Domingo" },
    ru: { "Pazartesi": "Понедельник", "Salı": "Вторник", "Çarşamba": "Среда", "Perşembe": "Четверг", "Cuma": "Пятница", "Cumartesi": "Суббота", "Pazar": "Воскресенье" },
    ar: { "Pazartesi": "الإثنين", "Salı": "الثلاثاء", "Çarşamba": "الأربعاء", "Perşembe": "الخميس", "Cuma": "الجمعة", "Cumartesi": "السبت", "Pazar": "الأحد" },
    zh: { "Pazartesi": "星期一", "Salı": "星期二", "Çarşamba": "星期三", "Perşembe": "星期四", "Cuma": "星期五", "Cumartesi": "星期六", "Pazar": "星期日" }
};

const STATUS_I18N = {
    tr: { today: "(Bugün)", today_closed: "(Bugün - Kapalı)", closed: "Kapalı" },
    en: { today: "(Today)", today_closed: "(Today - Closed)", closed: "Closed" },
    es: { today: "(Hoy)", today_closed: "(Hoy - Cerrado)", closed: "Cerrado" },
    ru: { today: "(Сегодня)", today_closed: "(Сегодня - Закрыто)", closed: "Закрыто" },
    ar: { today: "(اليوم)", today_closed: "(اليوم - مغلق)", closed: "مغلق" },
    zh: { today: "(今天)", today_closed: "(今天 - 已关闭)", closed: "已关闭" }
};

let currentLang = 'tr';
let cachedTableData = null;
let latestStatusData = null;

function renderPublicScheduleTable(statusData) {
    if (!statusData) return;
    latestStatusData = statusData;
    const tableBody = document.getElementById('public-hours-table-body');
    if (!tableBody || !statusData.hours) return;

    // UPDATE HEADER BADGE
    const headerBadge = document.getElementById('today-status-header-badge');
    if (headerBadge) {
        if (statusData.is_open) {
            headerBadge.style.background = '#ecfdf5';
            headerBadge.style.color = '#065f46';
            headerBadge.style.borderColor = '#a7f3d0';
            headerBadge.innerHTML = '🟢 Bugün Açık';
        } else {
            headerBadge.style.background = '#fef2f2';
            headerBadge.style.color = '#991b1b';
            headerBadge.style.borderColor = '#fca5a5';
            headerBadge.innerHTML = '🔴 Bugün Kapalı';
        }
    }

    tableBody.innerHTML = '';
    const days = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"];
    const curLang = (typeof currentLang !== 'undefined' && DAYS_I18N[currentLang]) ? currentLang : 'tr';
    const dayMap = DAYS_I18N[curLang];
    const statMap = STATUS_I18N[curLang];

    days.forEach(d => {
        const cfg = statusData.hours[d] || { open: "08:30", close: "23:00", active: true };
        const isToday = (d === statusData.current_day);
        const tr = document.createElement('tr');
        tr.style.borderBottom = '1px solid #f1f5f9';
        
        let dot = '';
        let rowBg = '';
        let dayColor = '#334155';
        let timeColor = '#475569';
        let timeFontWeight = '600';

        if (isToday) {
            if (statusData.is_open) {
                rowBg = '#ecfdf5';
                dayColor = '#065f46';
                timeColor = '#047857';
                timeFontWeight = '800';
                dot = '<span class="pulse-dot" style="display:inline-block; vertical-align:middle; margin-right:6px;"></span> ';
            } else {
                rowBg = '#fef2f2';
                dayColor = '#991b1b';
                timeColor = '#b91c1c';
                timeFontWeight = '800';
                dot = '<span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:#ef4444; vertical-align:middle; margin-right:6px;"></span> ';
            }
            tr.style.background = rowBg;
            tr.style.fontWeight = '700';
        }
        
        const translatedDayName = dayMap[d] || d;
        const timeStr = (cfg.active !== false) ? `${cfg.open || '08:30'} - ${cfg.close || '23:00'}` : `<span style="color:#dc2626; font-weight:700;">🔴 ${statMap.closed}</span>`;
        
        tr.innerHTML = `
            <td style="padding:8px 6px; color:${dayColor}; white-space:nowrap; width:50%;">${dot}<span>${translatedDayName}</span></td>
            <td style="padding:8px 6px; text-align:right; color:${timeColor}; font-weight:${timeFontWeight}; white-space:nowrap; width:50%;"><span style="white-space:nowrap;">${timeStr}</span></td>
        `;
        tableBody.appendChild(tr);
    });
}

function changeLang(lang) {
    currentLang = lang;
    try { localStorage.setItem('firinna_lang', lang); } catch(e){}
    const elements = document.querySelectorAll('[data-i18n]');
    elements.forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (i18n[lang] && i18n[lang][key]) {
            el.innerHTML = i18n[lang][key].replace(/\n/g, "<br>");
        }
    });

    if (lang === 'ar') {
        document.body.style.direction = 'rtl';
    } else {
        document.body.style.direction = 'ltr';
    }
    
    document.querySelectorAll('.lang-selector button').forEach(btn => {
        if(btn.innerText.toLowerCase() === lang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Update PDF download link if present
    const pdfLink = document.getElementById('pdf-download-link');
    if (pdfLink) {
        pdfLink.href = `firinna_menu_${lang}.pdf`;
    }

    renderTableStatusText();
    if (latestStatusData) renderPublicScheduleTable(latestStatusData);
}

// FETCH SETTINGS
async function fetchWebSettings() {
    try {
        const res = await fetch('/api/web/settings');
        const data = await res.json();
        
        // Fetch Live Status & Hours Schedule Table
        try {
            const resStatus = await fetch('/api/web/status');
            if (resStatus.ok) {
                const statusData = await resStatus.json();
                const element = document.getElementById('dynamic_work_hours');
                if (element) {
                    if (statusData.is_open) {
                        element.innerHTML = `<span class="pulse-dot"></span> ${statusData.status_badge}`;
                        element.parentElement.style.background = '#ecfdf5';
                        element.parentElement.style.color = '#059669';
                    } else {
                        element.innerHTML = `<span class="pulse-dot" style="background:#ef4444; box-shadow:none; animation:none;"></span> ${statusData.status_badge}`;
                        element.parentElement.style.background = '#fef2f2';
                        element.parentElement.style.color = '#dc2626';
                    }
                }

                // Render Public Schedule Table (Highlight Today in Green with Pulse Dot)
                renderPublicScheduleTable(statusData);
            }
        } catch(stErr) { console.log('Status fetch error:', stErr); }
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
            const gatingWp = document.getElementById('dynamic_gating_whatsapp');
            if (gatingWp) {
                gatingWp.href = `https://wa.me/${data.phone}?text=Merhaba,%20Fırınna%20hakkında%20geri%20bildirimde%20bulunmak%20istiyorum.`;
            }
        }
        const googleBtn = document.getElementById('gating_google_btn');
        if (googleBtn) {
            googleBtn.href = data.google_review_url || "https://g.page/r/CYCTLUWSsIhDEBM/review";
        }
        
        const yandexBtn = document.getElementById('gating_yandex_btn');
        if (yandexBtn) {
            yandexBtn.href = data.yandex_review_url || "https://yandex.com.tr/harita/?text=Firinna+Cafe+Galata";
        }

        const tripadvisorBtn = document.getElementById('gating_tripadvisor_btn');
        if (tripadvisorBtn) {
            if (data.tripadvisor_review_url && data.tripadvisor_review_url.trim() !== '') {
                tripadvisorBtn.href = data.tripadvisor_review_url;
                tripadvisorBtn.style.display = 'inline-flex';
            } else {
                tripadvisorBtn.style.display = 'none';
            }
        }
    } catch (err) {
        console.error("Failed to fetch settings:", err);
    }
}
// Live Table Status Logic
function renderTableStatusText() {
    const statusEl = document.getElementById('live-table-status');
    if (!statusEl) return;
    const iconEl = statusEl.previousElementSibling;

    if (!cachedTableData || !cachedTableData.success) {
        statusEl.innerText = (i18n[currentLang] && i18n[currentLang].table_offline) || "Masa durumu alınamadı.";
        return;
    }

    if (cachedTableData.empty > 0) {
        let msg = (i18n[currentLang] && i18n[currentLang].table_available) || "Şu an {N} masamız müsait, bekleriz!";
        statusEl.innerText = msg.replace("{N}", cachedTableData.empty);
        statusEl.style.color = '#27ae60';
        if (iconEl) iconEl.style.color = '#2ecc71';
    } else {
        statusEl.innerText = (i18n[currentLang] && i18n[currentLang].table_full) || "Şu an tüm masalarımız dolu.";
        statusEl.style.color = '#e74c3c';
        if (iconEl) iconEl.style.color = '#e74c3c';
    }
}

function fetchTableStatus() {
    fetch('/api/web/tables-status')
        .then(response => response.json())
        .then(data => {
            cachedTableData = data;
            renderTableStatusText();
        })
        .catch(err => {
            console.error('Masa durumu hatası:', err);
            cachedTableData = { success: false };
            renderTableStatusText();
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

// Interactive Review Gating Function
function rateExperience(stars) {
    const starIcons = document.querySelectorAll('.interactive-stars i');
    starIcons.forEach((star, idx) => {
        if (idx < stars) {
            star.style.color = '#f59e0b';
        } else {
            star.style.color = '#cbd5e1';
        }
    });

    const highBox = document.getElementById('gating-high');
    const lowBox = document.getElementById('gating-low');

    if (stars === 5) {
        if (highBox) highBox.style.display = 'block';
        if (lowBox) lowBox.style.display = 'none';
        trackEvent('review_5star');
    } else {
        if (highBox) highBox.style.display = 'none';
        if (lowBox) lowBox.style.display = 'block';
        trackEvent('review_lowstar');
    }
}

// Dynamic Web Products Fetch & Signature Gallery Renderer
let dynamicWebProducts = [];

async function fetchWebProducts() {
    try {
        const res = await fetch('/api/web/products');
        dynamicWebProducts = await res.json();
        renderDynamicSignatureGallery();
    } catch(e) {
        console.error("Failed to fetch web products:", e);
    }
}

const FRONTEND_TAG_MAP = {
    'vegetarian': { label: '🌱 Vejetaryen', bg: '#dcfce7', color: '#15803d' },
    'vegan': { label: '🥑 Vegan', bg: '#ecfdf5', color: '#166534' },
    'gluten': { label: '🌾 Gluten', bg: '#fff7ed', color: '#c2410c' },
    'gluten_free': { label: '🌾🚫 Glutensiz', bg: '#f0fdf4', color: '#047857' },
    'dairy': { label: '🥛 Süt Ürünü', bg: '#f0f9ff', color: '#0369a1' },
    'nuts': { label: '🥜 Kuruyemiş', bg: '#fef3c7', color: '#b45309' },
    'spicy': { label: '🌶️ Acı', bg: '#fef2f2', color: '#b91c1c' },
    'halal': { label: '🥩 Helal', bg: '#ecfdf5', color: '#065f46' },
    'sugar_free': { label: '🍯 Şekersiz', bg: '#fdf4ff', color: '#86198f' }
};

function goToMenuProduct(prodId) {
    window.location.href = `menu.html?product=${encodeURIComponent(prodId)}`;
}

function renderDynamicSignatureGallery() {
    const signatureGrid = document.getElementById('signature-gallery-grid');
    if (!signatureGrid) return;

    const signatureProducts = dynamicWebProducts.filter(p => p.is_signature && p.is_active !== false);
    if (!signatureProducts || signatureProducts.length === 0) return;

    signatureGrid.innerHTML = signatureProducts.map(p => {
        const img = p.image_url.startsWith('http') || p.image_url.startsWith('drink_') || p.image_url.startsWith('prod_') || p.image_url.startsWith('food_') ? p.image_url : p.image_url;

        return `
            <div class="gallery-item-wrapper" style="position: relative; overflow: hidden; border-radius: 12px; height: 220px; cursor:pointer; box-shadow:0 4px 15px rgba(0,0,0,0.1); transition:all 0.3s ease;" onclick="goToMenuProduct('${p.id}')" title="${p.title} - Menüde İncele">
                <img src="${img}" alt="${p.title}" class="gallery-img" style="width:100%; height:100%; object-fit:cover; object-position:center; transition:transform 0.3s ease;">
                <span style="position:absolute; top:8px; right:8px; background:#f59e0b; color:#fff; font-size:0.75rem; font-weight:800; padding:3px 8px; border-radius:12px; box-shadow:0 2px 6px rgba(0,0,0,0.2);">⭐ İmza Lezzet</span>
                <div style="position:absolute; bottom:0; left:0; right:0; background:linear-gradient(to top, rgba(15,23,42,0.92), transparent); padding:20px 10px 8px; color:#fff;">
                    <div style="font-size:0.92rem; font-weight:800; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${p.title}</div>
                    <div style="font-size:0.72rem; color:#fde68a; font-weight:600; display:flex; align-items:center; gap:4px; margin-top:2px;">
                        <span>Menüde Gör</span> <i class="ph-bold ph-arrow-right"></i>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function openLightbox(src, captionKeyOrText, descText, tagsStr = '') {
    const modal = document.getElementById('lightboxModal');
    const img = document.getElementById('lightboxImg');
    const caption = document.getElementById('lightboxCaption');
    if (modal && img) {
        img.src = src;
        if (caption) {
            let title = captionKeyOrText || '';
            if (i18n[currentLang] && i18n[currentLang][captionKeyOrText]) {
                title = i18n[currentLang][captionKeyOrText];
            }
            let html = `<div style="font-size:1.2rem; font-weight:700; margin-bottom:6px; color:#fbbf24;">${title}</div>`;

            if (tagsStr) {
                const tagList = tagsStr.split(',').filter(Boolean);
                if (tagList.length > 0) {
                    html += `<div style="display:flex; justify-content:center; flex-wrap:wrap; gap:6px; margin-bottom:10px;">`;
                    tagList.forEach(t => {
                        const info = FRONTEND_TAG_MAP[t] || { label: t, bg: '#334155', color: '#f8fafc' };
                        html += `<span style="background:${info.bg}; color:${info.color}; font-size:0.75rem; font-weight:700; padding:3px 8px; border-radius:12px;">${info.label}</span>`;
                    });
                    html += `</div>`;
                }
            }

            if (descText) {
                html += `<div style="font-size:0.95rem; font-weight:400; color:#e2e8f0; max-width:600px; line-height:1.5; margin:0 auto;">${descText}</div>`;
            }
            caption.innerHTML = html;
        }
        modal.style.display = 'flex';
    }
}

// ----------------------------------------------------
// ⚡ PWA SERVICE WORKER KAYDI (İnternetsiz Menü Desteği)
// ----------------------------------------------------
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(reg => console.log('Fırınna PWA Service Worker aktif:', reg.scope))
            .catch(err => console.log('PWA Service Worker hatası:', err));
    });
}

// ----------------------------------------------------
// ⭐ GOOGLE REVIEWS SLIDER CAROUSEL MANTIĞI
// ----------------------------------------------------
let currentReviewSlide = 0;
const totalReviewSlides = 10;
let reviewAutoTimer = null;

function updateReviewSlider() {
    const track = document.getElementById('reviews-track');
    const dots = document.querySelectorAll('#review-dots .dot');
    if (track) {
        track.style.transform = `translateX(-${currentReviewSlide * 100}%)`;
    }
    if (dots) {
        dots.forEach((d, idx) => {
            if (idx === currentReviewSlide) {
                d.style.background = '#2563eb';
                d.style.width = '24px';
                d.style.borderRadius = '10px';
            } else {
                d.style.background = '#cbd5e1';
                d.style.width = '10px';
                d.style.borderRadius = '50%';
            }
        });
    }
}

function nextReviewSlide() {
    currentReviewSlide = (currentReviewSlide + 1) % totalReviewSlides;
    updateReviewSlider();
    resetReviewAutoTimer();
}

function prevReviewSlide() {
    currentReviewSlide = (currentReviewSlide - 1 + totalReviewSlides) % totalReviewSlides;
    updateReviewSlider();
    resetReviewAutoTimer();
}

function goToReviewSlide(index) {
    currentReviewSlide = index;
    updateReviewSlider();
    resetReviewAutoTimer();
}

function resetReviewAutoTimer() {
    if (reviewAutoTimer) clearInterval(reviewAutoTimer);
    reviewAutoTimer = setInterval(() => {
        currentReviewSlide = (currentReviewSlide + 1) % totalReviewSlides;
        updateReviewSlider();
    }, 5000);
}

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('reviews-track')) {
        updateReviewSlider();
        resetReviewAutoTimer();
    }
});

// ----------------------------------------------------
// 🔍 YAPIŞKAN ARAMA & DİYET FİLTRE HAPLARI MANTIĞI
// ----------------------------------------------------
let activeDietaryFilter = 'all';

function setDietaryFilter(filter, btn) {
    activeDietaryFilter = filter;
    document.querySelectorAll('.diet-chip').forEach(b => {
        b.style.background = '#fff';
        b.style.color = '#334155';
        b.style.border = '1px solid #cbd5e1';
        b.style.fontWeight = '600';
    });
    if (btn) {
        btn.style.background = '#2563eb';
        btn.style.color = '#fff';
        btn.style.border = 'none';
        btn.style.fontWeight = '700';
    }
    filterMenuInteractive();
}

function filterMenuInteractive() {
    const searchInput = document.getElementById('menu-search-input');
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';

    const menuItems = document.querySelectorAll('#dynamic-full-menu .menu-item, .card-item, .menu-card');
    menuItems.forEach(item => {
        const text = item.innerText.toLowerCase();
        let matchesSearch = !query || text.includes(query);
        let matchesDiet = true;

        if (activeDietaryFilter === 'halal') {
            matchesDiet = text.includes('helal') || text.includes('halal') || true; // All items are %100 Halal
        } else if (activeDietaryFilter === 'veggie') {
            matchesDiet = text.includes('vejetaryen') || text.includes('peynir') || text.includes('sebze') || text.includes('omlet') || text.includes('tatlı') || text.includes('çikolata');
        } else if (activeDietaryFilter === 'glutenfree') {
            matchesDiet = text.includes('glutensiz') || text.includes('fit') || text.includes('salata') || text.includes('yumurta') || text.includes('kahve') || text.includes('çay');
        } else if (activeDietaryFilter === 'signature') {
            matchesDiet = text.includes('imza') || item.innerHTML.includes('ph-star') || text.includes('çakallı') || text.includes('pizza') || text.includes('tost');
        }

        if (matchesSearch && matchesDiet) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// ----------------------------------------------------
// 🗺️ OPENFREEMAP 3D VECTOR HARİTA BAŞLATICI (MAPLIBRE GL 3D EXTRUSION)
// ----------------------------------------------------
function initOpenFreeMap3D() {
    var mapElem = document.getElementById('osm-3d-map');
    if (!mapElem) return;

    if (typeof maplibregl !== 'undefined' && typeof maplibregl.supported === 'function' && maplibregl.supported()) {
        try {
            mapElem.innerHTML = '';
            var map = new maplibregl.Map({
                container: 'osm-3d-map',
                style: 'https://tiles.openfreemap.org/styles/liberty',
                center: [28.976906, 41.028328],
                zoom: 16.8,
                pitch: 60,
                bearing: -35,
                antialias: true
            });

            map.addControl(new maplibregl.NavigationControl(), 'top-right');

            // Restoranim.net Style Orange Marker Pin
            var pinEl = document.createElement('div');
            pinEl.className = 'marker-pin';
            pinEl.style.width = '36px';
            pinEl.style.height = '36px';
            pinEl.style.background = '#d97706';
            pinEl.style.borderRadius = '50% 50% 50% 0';
            pinEl.style.transform = 'rotate(-45deg)';
            pinEl.style.display = 'flex';
            pinEl.style.alignItems = 'center';
            pinEl.style.justifyContent = 'center';
            pinEl.style.boxShadow = '0 6px 16px rgba(0,0,0,0.35)';
            pinEl.style.border = '2px solid #ffffff';
            pinEl.style.cursor = 'pointer';
            pinEl.innerHTML = '<span style="transform: rotate(45deg); font-size: 1.05rem; color: #ffffff;">📍</span>';

            var popup = new maplibregl.Popup({ offset: 25 }).setHTML(
                '<div style="text-align:center; font-family:sans-serif; padding:4px;">' +
                '<b style="color:#0f172a; font-size:0.95rem;">Fırınna Cafe & Restaurant</b><br>' +
                '<span style="font-size:0.8rem; color:#64748b;">Kumbaracı Yokuşu No: 41A, Beyoğlu</span>' +
                '</div>'
            );

            new maplibregl.Marker({ element: pinEl })
                .setLngLat([28.976906, 41.028328])
                .setPopup(popup)
                .addTo(map);

            map.on('load', function() {
                map.resize();
                
                // Add 3D Extruded Buildings (Matching restoranim.net 222.png)
                try {
                    var layers = map.getStyle().layers;
                    var labelLayerId;
                    for (var i = 0; i < layers.length; i++) {
                        if (layers[i].type === 'symbol' && layers[i].layout && layers[i].layout['text-field']) {
                            labelLayerId = layers[i].id;
                            break;
                        }
                    }

                    if (!map.getLayer('3d-buildings')) {
                        map.addLayer({
                            'id': '3d-buildings',
                            'source': 'openmaptiles',
                            'source-layer': 'building',
                            'type': 'fill-extrusion',
                            'minzoom': 13,
                            'paint': {
                                'fill-extrusion-color': '#d1d5db',
                                'fill-extrusion-height': [
                                    'interpolate', ['linear'], ['zoom'],
                                    14, 0,
                                    14.05, ['get', 'render_height']
                                ],
                                'fill-extrusion-base': [
                                    'interpolate', ['linear'], ['zoom'],
                                    14, 0,
                                    14.05, ['get', 'render_min_height']
                                ],
                                'fill-extrusion-opacity': 0.82
                            }
                        }, labelLayerId);
                    }
                } catch(e) { console.log('3D Buildings layer info:', e); }
            });

            window.addEventListener('resize', function() { map.resize(); });
            setTimeout(function() { map.resize(); }, 300);
            setTimeout(function() { map.resize(); }, 1000);

        } catch(e) {
            console.warn('MapLibre GL error:', e);
        }
    }
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initOpenFreeMap3D);
} else {
    initOpenFreeMap3D();
}

