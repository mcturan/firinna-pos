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
        cat_1: "Menemen",
        p_m1: "Geleneksel Menemen",
        desc_m1: "Özel ezilmiş domatesler ve eriyen peynirle hazırlanan ikonik Türk kahvaltısı. (Çakallı usulü)",
        p_m2: "Kaşarlı Menemen",
        desc_m2: "Ekstra bol kaşar peynirli ikonik Türk menemeni.",
        p_m3: "Etli / Sucuklu / Tavuklu Menemen",
        desc_m3: "Geleneksel menemen tabanının üzerine; özel marine edilmiş yaprak Et Döner, Tavuk Döner veya Sucuk.",
        p_m4: "Karışık Şölen Menemen",
        desc_m4: "Seçtiğiniz iki farklı proteinin sıcak menemenle efsanevi buluşması.",
        cat_2: "Omlet",
        p_o1: "Geleneksel Sahanda Omlet",
        desc_o1: "Köy tereyağında pişmiş nefis sahanda omlet",
        p_o2: "Kaşarlı Omlet",
        desc_o2: "Eriyen bol kaşar peyniri dolgulu omlet",
        p_o3: "Etli / Sucuklu / Tavuklu Omlet",
        desc_o3: "Tercihinize göre protein eklentili doyurucu omlet",
        p_o4: "Karışık Şölen Omlet",
        desc_o4: "Et, sucuk, tavuk ve kaşarlı dev omlet",
        cat_3: "Bazlama",
        p_b1: "Geleneksel Bazlama Tost",
        desc_b1: "Köy bazlaması arasına kaşar peyniriyle hazırlanan çıtır lezzet",
        p_b2: "Etli / Sucuklu / Tavuklu Bazlama",
        desc_b2: "Kaşar peynirine ek olarak tercih ettiğiniz proteinle zenginleştirilmiş tost",
        p_b3: "İki Seçenekli Bazlama",
        desc_b3: "İstediğiniz iki protein seçeneği ve bol kaşar",
        cat_4: "Pizza",
        p_p1: "Pizza Margarita",
        desc_p1: "Taş fırında pişen gerçek Napoli usulü, özel karışım pizza sosumuz ve taze mozzarella harikası.",
        p_p2: "Pizza (Etli / Sucuklu / Tavuklu)",
        desc_p2: "Margarita tabanı üzerine dilediğiniz özel lezzet: Özel marine Et Döner, Tavuk Döner veya Sucuk.",
        p_p3: "Full Karışık Pizza",
        desc_p3: "Et, sucuk, tavuk ve bol mozzarella ile fırınlanmış efsane pizza",
        cat_5: "Sıcak içecekler",
        p_s1: "Özel Karışım Çay",
        desc_s1: "Özenle seçilmiş çay yapraklarının bergamotla tatlandırılıp, kuru gül yapraklarıyla harmanlanmış özel hali.",
        p_s2: "Türk Kahvesi",
        desc_s2: "Ağır ağır pişen, bol köpüklü, yanında lokum ile servis edilen geleneksel Türk Kahvesi.",
        p_s3: "Kahve Americano",
        desc_s3: "Taze çekilmiş çekirdeklerden sert kahve",
        p_s4: "Kahve Latte",
        desc_s4: "Bol sütlü espresso",
        p_s5: "Kahve Cappucino",
        desc_s5: "Süt köpüklü İtalyan klasiği",
        cat_6: "Soğuk içecekler",
        p_c2: "Madensuyu",
        desc_c2: "Doğal mineralli su",
        p_c3: "Hibiscuslu Safranlı Limonata",
        desc_c3: "Buz gibi limonata temeli üzerinde; tarçın, hibiscus ve İran safranının eşsiz birleşimiyle hazırlanan özel iksir.",
        cat_7: "Tatlı",
        p_t1: "Dondurmalı Sıcak Çikolatalı Kek",
        desc_t1: "Fırından yeni çıkmış sıcak çikolatalı kekin üzerine meşhur Maraş dondurması, çikolata sosu ve hindistan cevizi dokunuşu.",
        tag_vegan: "Vegan",
        tag_gluten: "Gluten",
        tag_gluten_free: "Glutensiz",
        tag_halal: "Helal",
        tag_dairy: "Süt Ürünü",
        tag_vegetarian: "Vejetaryen",
        category: "Cafe & Restaurant",
        status_open: "Şu An Açık (08:00 - 23:00)",
        btn_menu: "📖 Dijital Menüyü İncele",
        btn_gezi: "🗺️ İstanbul Gezi Rehberi & Rota",
        btn_reserve: "Hemen Masa Ayırt",
        btn_message: "Yöneticiye Mesaj İlet (Telegram)",
        title_about: "Hakkımızda",
        slogan_about: "GELENEKSEL LEZZETLER, BENZERSİZ TARİFLERLE SADECE FIRINNA'DA",
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
        title_social: "Sosyal Sorumluluk",
        social_intro: "Fırınna Cafe olarak kazancımızı ve sizden gelen tüm bahşişleri doğrudan toplumsal faydaya dönüştürüyoruz.",
        social_student_title: "Beyoğlu Öğrenci'Ye Projesi",
        social_student_desc: "Beyoğlu Belediyesi'nin Öğrenci'Ye projesinin gururlu bir destekçisiyiz. Üniversite öğrencilerimize ücretsiz yemek desteği sağlıyoruz.",
        social_animal_title: "Sokak Canları Dostu",
        social_animal_desc: "Sokağımızdaki patili dostlarımızın mama, su ve veteriner giderlerini karşılıyoruz. İşletmemiz tamamen hayvan dostudur (Pet-Friendly).",

        search_placeholder: "🔍 Menüde lezzet ara... (örn: Menemen, Pizza)",
        filter_all: "✨ Tüm Menü",
        filter_halal: "☪️ %100 Helal",
        filter_veggie: "🌿 Vejetaryen",
        filter_glutenfree: "🌾 Glutensiz / Fit",
        filter_signature: "⭐ İmza Lezzetler",
        badge_stone_oven: "🍕 Taş Fırın",
        title_pizza_napo: "Napoliten Pizza",
        badge_famous: "🍳 Meşhur",
        title_menemen_cakal: "Çakallı Menemeni",
        badge_traditional: "☕ Geleneksel",
        title_coffee: "Közde Türk Kahvesi",
        whatsapp_manager: "WhatsApp Yöneticisi",
        btn_send_msg2: "Mesaj Gönder",

        filter_dairyfree: "🚫 Süt / Kazein İçermez",


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
        badge_dairy: "Süt Ürünü",
        title_work_hours: "Çalışma Günleri & Saatleri",
        status_now_open: "🟢 Şu An Açık",
        status_now_closed: "🔴 Şu An Kapalı",
        signature_intro: "Özenle seçilen en sevilen lezzetlerimiz. İncelemek istediğiniz ürüne tıklayarak menüdeki detaylarına gidebilirsiniz.",
        signature_loading: "İmza lezzetler yükleniyor...",
        title_location_yandex: "Konum & Ulaşım (Yandex Haritalar)",
        badge_live_traffic: "🔴 Canlı Trafik & 3D Binalar",
        address_full: "<strong>Adres:</strong> Şahkulu Mah. Kumbaracı Yokuşu Sok. No:41A, 34421 Beyoğlu/İstanbul (İstiklal Caddesi & Galata Kulesi Yakını)",
        btn_yandex_nav: "Yandex Navigasyon",
        btn_panorama: "360° Kumbaracı Yokuşu Panorama",
        title_social_media: "Sosyal Medyada Ne Meşhur?",
        badge_tour_videos: "🎬 Tur & Hazırlık Videoları",
        title_amenities: "Mekan Özellikleri & Olanakları",
        amenity_pet: "🐾 Evcil Hayvan Dostu",
        amenity_halal: "🕌 %100 Helal Gıda",
        amenity_wifi: "📶 Ücretsiz Yüksek Hızlı Wi-Fi",
        amenity_oven: "🍕 Geleneksel Taş Fırın",
        amenity_historic: "🏛️ 150 Yıllık Tarihi Atmosfer",
        amenity_nfc: "💳 Temassız / NFC Ödeme",
        amenity_veg: "🌿 Vejetaryen Alternatifler",
        amenity_gluten: "🌾 Glutensiz / Fit Seçenekler",
        amenity_family: "👶 Aileler & Çocuklar İçin Uygun",
        amenity_tea: "☕ Özel Harman Gül Çayı",
        google_review_desc: "Google üzerindeki tüm gerçek misafir yorumlarını ve puanlamaları doğrudan inceleyin.",
        yandex_review_desc: "Yandex Haritalar üzerindeki konum ve değerlendirme kayıtlarını görün.",
        badge_satisfaction: "Müşteri Memnuniyeti",
    },
    en: {
        category: "Cafe & Restaurant",
        status_open: "Open Now (08:00 - 23:00)",
        btn_menu: "📖 View Digital Menu",
        btn_gezi: "🗺️ Istanbul Travel Guide & Route",
        btn_reserve: "Book a Table",
        btn_message: "Send us a Message",
        title_about: "About Us",
        slogan_about: "TRADITIONAL FLAVORS, UNIQUE RECIPES ONLY AT FIRINNA",
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
        review_2: "You must try the menemen. The staff is very smiling and it's great that they are pet-friendly.",
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
        desc_t1: "Hot chocolate cake fresh from the oven topped with famous Maraş ice cream, chocolate sauce, and a touch of coconut.",
        p_t1: "Hot Chocolate Cake with Ice Cream",
        desc_c3: "A refreshing special potion prepared with the unique combination of cinnamon, hibiscus, and Iranian saffron on an ice-cold lemonade base.",
        p_c3: "Hibiscus Saffron Lemonade",
        desc_c2: "Natural mineral water.",
        p_c2: "Mineral Water",
        desc_c1: "Refreshing water.",
        p_c1: "Water",
        desc_s5: "Italian classic with milk foam.",
        p_s5: "Cappuccino",
        desc_s4: "Espresso with plenty of milk.",
        p_s4: "Latte",
        desc_s3: "Strong coffee from freshly ground beans.",
        p_s3: "Americano",
        desc_s2: "Traditional Turkish Coffee, slow-cooked, very frothy, served with Turkish delight.",
        p_s2: "Turkish Coffee",
        desc_s1: "A special blend of carefully selected tea leaves flavored with bergamot and softened with dry rose petals.",
        p_s1: "Special Blend Tea",
        desc_p3: "Magnificent festival pizza baked with beef döner, chicken döner, sausage, and plenty of mozzarella.",
        p_p3: "Full Mixed Feast Pizza",
        desc_p2: "Your special flavor on a Margherita base: Special marinated Beef Döner, Chicken Döner, or Sausage.",
        p_p2: "Protein Pizza",
        desc_p1: "Real Neapolitan style dough baked in a stone oven, our special mix pizza sauce and fresh mozzarella.",
        p_p1: "Pizza Margherita",
        desc_b3: "A hearty and quick classic! Hot meeting of your two chosen proteins in crispy bazlama bread.",
        p_b3: "Mixed Bazlama Toast",
        desc_b2: "Toast enriched with your chosen protein along with melting cheese.",
        p_b2: "Protein Bazlama",
        desc_b1: "Traditional Turkish Village Bread toast, crispy on the outside, filled with melting cheese.",
        p_b1: "Traditional Bazlama Toast",
        desc_o4: "A giant portion omelette made just for you with two flavors of your choice.",
        p_o4: "Mixed Feast Omelette",
        desc_o3: "Filling omelette with your choice of Beef Döner, Chicken Döner, or Traditional Sausage.",
        p_o3: "Special Protein Omelette",
        desc_o2: "Omelette filled with melting cheese.",
        p_o2: "Omelette with Cheese",
        desc_o1: "Soft classic omelette cooked carefully in a pan.",
        p_o1: "Traditional Pan Omelette",
        desc_m4: "The legendary meeting of your two chosen proteins with hot menemen.",
        p_m4: "Mixed Feast Menemen",
        desc_m3: "Traditional menemen base topped with your choice of specially marinated sliced Beef Döner, Chicken Döner, or Sausage.",
        p_m3: "Menemen with Beef / Sausage / Chicken",
        desc_m2: "Iconic Turkish menemen with extra cheese.",
        p_m2: "Menemen with Cheese",
        desc_m1: "Iconic Turkish breakfast prepared with crushed tomatoes and melting cheese.",
        p_m1: "Traditional Menemen",
        cat_food: "Hot from the Oven",
        cat_drinks: "Beverages & Desserts",
        item_pizza: "Stone-baked Pizza",
        desc_pizza: "Specially fermented dough, Italian tomato sauce, and exquisite mozzarella cheese baked in a wood-fired oven.",
        item_menemen: "Famous Menemen",
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
        badge_dairy: "Contains Dairy",
        title_work_hours: "Working Days & Hours",
        status_now_open: "🟢 Open Now",
        status_now_closed: "🔴 Closed Now",
        signature_intro: "Our most loved, carefully selected flavors. Click on any item to see its menu details.",
        signature_loading: "Loading signature flavors...",
        title_location_yandex: "Location & Directions (Yandex Maps)",
        badge_live_traffic: "🔴 Live Traffic & 3D Buildings",
        address_full: "<strong>Address:</strong> Şahkulu Mah. Kumbaracı Yokuşu Sok. No:41A, 34421 Beyoğlu/İstanbul (Near Istiklal Street & Galata Tower)",
        btn_yandex_nav: "Yandex Navigation",
        btn_panorama: "360° Kumbaracı Street Panorama",
        title_social_media: "What's Popular on Social Media?",
        badge_tour_videos: "🎬 Tour & Preparation Videos",
        title_amenities: "Venue Features & Amenities",
        amenity_pet: "🐾 Pet-Friendly",
        amenity_halal: "🕌 100% Halal Food",
        amenity_wifi: "📶 Free High-Speed Wi-Fi",
        amenity_oven: "🍕 Traditional Stone Oven",
        amenity_historic: "🏛️ 150-Year Historic Atmosphere",
        amenity_nfc: "💳 Contactless / NFC Payment",
        amenity_veg: "🌿 Vegetarian Options",
        amenity_gluten: "🌾 Gluten-Free / Healthy Options",
        amenity_family: "👶 Family & Child Friendly",
        amenity_tea: "☕ Special Rosebud Blend Tea",
        google_review_desc: "View all real guest reviews and ratings directly on Google.",
        yandex_review_desc: "View location and review records on Yandex Maps.",
        badge_satisfaction: "Customer Satisfaction",
        title_social: "Social Responsibility",
        social_intro: "As Fırınna Cafe, we share our earnings and love with our neighborhood.",
        social_student_title: "Student Project in Beyoğlu",
        social_student_desc: "We support university students in Beyoğlu with free meals.",
        social_animal_title: "Street Animals Friendly",
        social_animal_desc: "We provide food and water for our furry friends on our street every day.",
        search_placeholder: "🔍 Search the menu...",
        filter_all: "✨ All Menu",
        filter_halal: "☪️ 100% Halal",
        filter_veggie: "🌿 Vegetarian",
        filter_glutenfree: "🌾 Gluten-Free",
        filter_signature: "⭐ Signature",
        badge_stone_oven: "🍕 Stone Oven",
        title_pizza_napo: "Neapolitan Pizza",
        badge_famous: "🍳 Famous",
        title_menemen_cakal: "Menemen",
        badge_traditional: "☕ Traditional",
        title_coffee: "Turkish Coffee",
        whatsapp_manager: "WhatsApp Manager",
        btn_send_msg2: "Send Message",
        filter_dairyfree: "🚫 Dairy-Free",
    },
    es: {
        category: "Cafetería y Restaurante",
        status_open: "Abierto Ahora (08:00 - 23:00)",
        btn_menu: "📖 Ver Menú Digital",
        btn_gezi: "🗺️ Guía y Ruta de Estambul",
        btn_reserve: "Reservar una Mesa",
        btn_message: "Enviarnos un Mensaje",
        title_about: "Sobre Nosotros",
        slogan_about: "SABORES TRADICIONALES, RECETAS ÚNICAS SOLO EN FIRINNA",
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
        review_2: "Debes probar el menemen. El personal es muy amable y es genial que acepten mascotas.",
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
        title_social: "Responsabilidad Social",
        social_intro: "En Firinna Cafe, convertimos nuestras ganancias y todas las propinas que nos deja directamente en beneficio social.",
        social_student_title: "Proyecto Beyoglu Para Estudiantes",
        social_student_desc: "Somos un orgulloso patrocinador del proyecto 'Öğrenci'Ye' de la municipalidad de Beyoglu. Brindamos comidas gratuitas a estudiantes universitarios.",
        social_animal_title: "Amigo de los Animales Callejeros",
        social_animal_desc: "Cubrimos los gastos de comida, agua y veterinario de nuestros amigos peludos en la calle. Nuestra cafetería admite mascotas.",

        search_placeholder: "🔍 Buscar en menú... (ej: Menemen, Pizza)",
        filter_all: "✨ Todo el Menú",
        filter_halal: "☪️ 100% Halal",
        filter_veggie: "🌿 Vegetariano",
        filter_glutenfree: "🌾 Sin Gluten / Fit",
        filter_signature: "⭐ Sabores Especiales",
        badge_stone_oven: "🍕 Horno de Piedra",
        title_pizza_napo: "Pizza Napolitana",
        badge_famous: "🍳 Famoso",
        title_menemen_cakal: "Menemen",
        badge_traditional: "☕ Tradicional",
        title_coffee: "Café Turco",
        whatsapp_manager: "Gerente WhatsApp",
        btn_send_msg2: "Enviar Mensaje",

        filter_dairyfree: "🚫 Sin Lácteos / Caseína",


        cat_food: "Caliente del Horno",
        cat_drinks: "Bebidas y Postres",
        item_pizza: "Pizza al Horno de Piedra",
        desc_pizza: "Masa especial fermentada, salsa de tomate italiana y exquisito queso mozzarella horneado en horno de leña.",
        item_menemen: "Famoso Menemen",
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
        badge_dairy: "Contiene Lácteos",
        title_work_hours: "Días y Horarios de Trabajo",
        status_now_open: "🟢 Abierto Ahora",
        status_now_closed: "🔴 Cerrado Ahora",
        signature_intro: "Nuestros sabores más queridos y cuidadosamente seleccionados. Haga clic en cualquier producto para ver sus detalles.",
        signature_loading: "Cargando sabores exclusivos...",
        title_location_yandex: "Ubicación y Direcciones (Yandex Maps)",
        badge_live_traffic: "🔴 Tráfico en Vivo y Edificios 3D",
        address_full: "<strong>Dirección:</strong> Şahkulu Mah. Kumbaracı Yokuşu Sok. No:41A, 34421 Beyoğlu/Estambul (Cerca de Calle Istiklal y Torre Galata)",
        btn_yandex_nav: "Navegación Yandex",
        btn_panorama: "360° Panorama Calle Kumbaracı",
        title_social_media: "¿Qué es Popular en Redes Sociales?",
        badge_tour_videos: "🎬 Videos de Tour y Preparación",
        title_amenities: "Características y Comodidades",
        amenity_pet: "🐾 Admite Mascotas",
        amenity_halal: "🕌 100% Comida Halal",
        amenity_wifi: "📶 Wi-Fi Gratis de Alta Velocidad",
        amenity_oven: "🍕 Horno de Piedra Tradicional",
        amenity_historic: "🏛️ Atmósfera Histórica de 150 Años",
        amenity_nfc: "💳 Pago Sin Contacto / NFC",
        amenity_veg: "🌿 Opciones Vegetarianas",
        amenity_gluten: "🌾 Opciones Sin Gluten / Saludables",
        amenity_family: "👶 Apto para Familias y Niños",
        amenity_tea: "☕ Té Especial con Capullos de Rosa",
        google_review_desc: "Vea todas las reseñas y calificaciones reales directamente en Google.",
        yandex_review_desc: "Vea los registros de ubicación y reseñas en Yandex Maps.",
        badge_satisfaction: "Satisfacción del Cliente",
        desc_t1: "Pastel de chocolate caliente recién salido del horno cubierto con el famoso helado de Maraş, salsa de chocolate y un toque de coco.",
        p_t1: "Pastel de chocolate caliente con helado",
        desc_c3: "Una refrescante poción especial preparada con la combinación única de canela, hibisco y azafrán iraní sobre una base de limonada helada.",
        p_c3: "Limonada De Hibisco Y Azafrán",
        desc_c2: "Agua mineral natural.",
        p_c2: "Agua mineral",
        desc_c1: "Refreshing water.",
        p_c1: "Water",
        desc_s5: "Clásico italiano con espuma de leche.",
        p_s5: "Capuchino",
        desc_s4: "Espresso con mucha leche.",
        p_s4: "café con leche",
        desc_s3: "Café fuerte elaborado con granos recién molidos.",
        p_s3: "americano",
        desc_s2: "Café turco tradicional, cocinado a fuego lento, muy espumoso, servido con delicias turcas.",
        p_s2: "Café turco",
        desc_s1: "Una mezcla especial de hojas de té cuidadosamente seleccionadas, aromatizadas con bergamota y suavizadas con pétalos de rosa secos.",
        p_s1: "Té de mezcla especial",
        desc_p3: "Magnífica pizza festiva horneada con döner de ternera, döner de pollo, salchicha y abundante mozzarella.",
        p_p3: "Pizza de fiesta mixta completa",
        desc_p2: "Tu sabor especial sobre base Margherita: Döner de Res marinado especial, Döner de Pollo o Salchicha.",
        p_p2: "Pizza Proteica",
        desc_p1: "Masa auténtica al estilo napolitano horneada en horno de piedra, nuestra mezcla especial de salsa para pizza y mozzarella fresca.",
        p_p1: "Pizza Margarita",
        desc_b3: "¡Un clásico abundante y rápido! Encuentro caliente de las dos proteínas elegidas en pan bazlama crujiente.",
        p_b3: "Tostada Bazlama Mixta",
        desc_b2: "Tostadas enriquecidas con la proteína de tu elección junto con queso derretido.",
        p_b2: "Base proteica",
        desc_b1: "Tostada de pan de pueblo tradicional turco, crujiente por fuera, rellena de queso derretido.",
        p_b1: "Tostada Bazlama Tradicional",
        desc_o4: "Una tortilla de porción gigante hecha solo para ti con dos sabores a tu elección.",
        p_o4: "Tortilla de fiesta mixta",
        desc_o3: "Relleno de tortilla con su elección de Beef Döner, Chicken Döner o Salchicha Tradicional.",
        p_o3: "Tortilla Proteica Especial",
        desc_o2: "Tortilla rellena de queso derretido.",
        p_o2: "Tortilla con Queso",
        desc_o1: "Tortilla clásica suave cocinada cuidadosamente en una sartén.",
        p_o1: "Tortilla De Pan Tradicional",
        desc_m4: "El encuentro legendario de tus dos proteínas elegidas con menemen caliente.",
        p_m4: "Fiesta Mixta Menemen",
        desc_m3: "Base de menemen tradicional cubierta con su elección de Döner de res, Döner de pollo o salchicha en rodajas especialmente marinadas.",
        p_m3: "Menemen con Carne de Res / Chorizo ​​/ Pollo",
        desc_m2: "Menemen turco icónico con queso extra.",
        p_m2: "Menemen con Queso",
        desc_m1: "Icónico desayuno turco preparado con tomates triturados y queso derretido.",
        p_m1: "Menemen Tradicional",
        desc_pizza: "Masa especialmente fermentada, salsa de tomate italiana y exquisito queso mozzarella horneado en horno de leña.",
        desc_menemen: "Preparado únicamente con yemas de huevo, mucho queso cheddar y mantequilla, un sabor de desayuno regional legendario.",
        desc_toast: "Servido crujiente al horno de piedra con queso cheddar y salchicha/ternera especial entre pan de pueblo.",
        desc_coffee: "Café Arábica fresco de primera calidad, finamente tostado y molido, elaborado por expertos y servido con las famosas delicias turcas.",
        desc_tea: "Elaborada con una mezcla premium de té turco y de Ceilán, bergamota y capullos de rosa secos.",
        desc_lemonade: "Limonada fresca casera helada con hibisco, canela, anís estrellado y auténtico azafrán persa.",
        desc_cake: "Suave por dentro, mucho cacao y cubierto con salsa de chocolate caliente, un sabor indispensable.",
    },
    ru: {
        category: "Кафе и Ресторан",
        status_open: "Сейчас открыто (08:00 - 23:00)",
        btn_menu: "📖 Посмотреть меню",
        btn_gezi: "🗺️ Путеводитель и Маршрут по Стамбулу",
        btn_reserve: "Забронировать столик",
        btn_message: "Напишите нам",
        title_about: "О нас",
        slogan_about: "ТРАДИЦИОННЫЕ ВКУСЫ, УНИКАЛЬНЫЕ РЕЦЕПТЫ ТОЛЬКО В FIRINNA",
        text_about: "ДОРОГОЙ ГОСТЬ, ДОБРО ПОЖАЛОВАТЬ В FIRINNA.\n\nРасположенное в 150-летнем историческом здании в районе Галата, на уютной улочке Кумбараджи Йокушу, кафе-ресторан Fırınna — это особенный уголок, где можно отдохнуть от шума улицы Истикляль.\n\nКак часто отмечают наши гости в отзывах Google: мы предлагаем традиционные рецепты с фирменными штрихами Fırınna — хрустящую пиццу из дровяной каменной печи, знаменитый менемен, горячие тосты на домашнем хлебе и турецкий кофе на углях в медной джезве.\n\nЗдесь нет спешки! С нашей радушной и pet-friendly командой наслаждайтесь теплым общением и незабываемыми вкусами.",
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
        review_2: "Вы должны попробовать менемен. Персонал очень улыбчивый, и здорово, что к ним можно с питомцами.",
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
        title_social: "Социальная ответственность",
        social_intro: "В кафе Firinna мы превращаем наши доходы и все ваши чаевые в социальную пользу.",
        social_student_title: "Проект Beyoglu для студентов",
        social_student_desc: "Мы являемся гордым сторонником проекта «Öğrenci'Ye» муниципалитета Бейоглу. Мы предоставляем бесплатное питание студентам.",
        social_animal_title: "Забота о бездомных животных",
        social_animal_desc: "Мы оплачиваем еду, воду и ветеринарные услуги для наших пушистых друзей на улице. Наше кафе дружелюбно к животным.",

        search_placeholder: "🔍 Поиск в меню... (напр. Менемен, Пицца)",
        filter_all: "✨ Все меню",
        filter_halal: "☪️ 100% Халяль",
        filter_veggie: "🌿 Вегетарианское",
        filter_glutenfree: "🌾 Без глютена / Фит",
        filter_signature: "⭐ Фирменные блюда",
        badge_stone_oven: "🍕 Каменная печь",
        title_pizza_napo: "Неаполитанская пицца",
        badge_famous: "🍳 Знаменитый",
        title_menemen_cakal: "Менемен",
        badge_traditional: "☕ Традиционный",
        title_coffee: "Турецкий кофе",
        whatsapp_manager: "Менеджер WhatsApp",
        btn_send_msg2: "Отправить сообщение",

        filter_dairyfree: "🚫 Без молока / казеина",


        cat_food: "Горячее из печи",
        cat_drinks: "Напитки и десерты",
        item_pizza: "Пицца на камне",
        desc_pizza: "Особо ферментированное тесто, итальянский томатный соус и изысканный сыр моцарелла, запеченные в дровяной печи.",
        item_menemen: "Знаменитый Менемен",
        desc_menemen: "Легендарный региональный вкус для завтрака, приготовленный только из яичных желтков, с большим количеством чеддера и сливочного масла.",
        item_toast: "Тост Базлама из Печи",
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
        badge_dairy: "Содержит молочные продукты",
        title_work_hours: "Дни и Часы Работы",
        status_now_open: "🟢 Сейчас Открыто",
        status_now_closed: "🔴 Сейчас Закрыто",
        signature_intro: "Наши самые любимые, тщательно отобранные блюда. Нажмите на любой продукт, чтобы увидеть подробности.",
        signature_loading: "Загрузка фирменных блюд...",
        title_location_yandex: "Расположение и Маршрут (Яндекс Карты)",
        badge_live_traffic: "🔴 Живой трафик и 3D-здания",
        address_full: "<strong>Адрес:</strong> Шахкулу Мах. Кумбараджи Йокушу Сок. No:41A, 34421 Бейоглу/Стамбул (Рядом с ул. Истикляль и Галатской Башней)",
        btn_yandex_nav: "Яндекс Навигация",
        btn_panorama: "360° Панорама Кумбараджи Йокушу",
        title_social_media: "Что популярно в соцсетях?",
        badge_tour_videos: "🎬 Видео Туров и Приготовления",
        title_amenities: "Удобства и Возможности",
        amenity_pet: "🐾 С домашними животными",
        amenity_halal: "🕌 100% Халяль",
        amenity_wifi: "📶 Бесплатный скоростной Wi-Fi",
        amenity_oven: "🍕 Традиционная каменная печь",
        amenity_historic: "🏛️ 150-летняя историческая атмосфера",
        amenity_nfc: "💳 Бесконтактная оплата / NFC",
        amenity_veg: "🌿 Вегетарианские блюда",
        amenity_gluten: "🌾 Безглютеновые / Фитнес блюда",
        amenity_family: "👶 Для семей с детьми",
        amenity_tea: "☕ Фирменный чай с бутонами роз",
        google_review_desc: "Просмотрите все реальные отзывы и оценки гостей прямо на Google.",
        yandex_review_desc: "Посмотрите расположение и отзывы на Яндекс Картах.",
        badge_satisfaction: "Удовлетворённость Клиентов",
        desc_t1: "Горячий шоколадный торт, только что вынутый из духовки, покрытый знаменитым мороженым Мараш, шоколадным соусом и кокосовой стружкой.",
        p_t1: "Горячий шоколадный торт с мороженым",
        desc_c3: "Специальное освежающее зелье, приготовленное из уникального сочетания корицы, гибискуса и иранского шафрана на ледяной лимонадной основе.",
        p_c3: "Гибискус Шафрановый Лимонад",
        desc_c2: "Природная минеральная вода.",
        p_c2: "Минеральная вода",
        desc_c1: "Refreshing water.",
        p_c1: "Water",
        desc_s5: "Итальянская классика с молочной пеной.",
        p_s5: "Капучино",
        desc_s4: "Эспрессо с большим количеством молока.",
        p_s4: "Латте",
        desc_s3: "Крепкий кофе из свежемолотых зерен.",
        p_s3: "Американо",
        desc_s2: "Традиционный турецкий кофе, медленно приготовленный, очень пенистый, подается с рахат-лукумом.",
        p_s2: "Турецкий кофе",
        desc_s1: "Особая смесь тщательно отобранных чайных листьев, ароматизированная бергамотом и смягченная сухими лепестками розы.",
        p_s1: "Специальный купажированный чай",
        desc_p3: "Великолепная фестивальная пицца, запеченная с донером из говядины, курицей, колбасой и большим количеством моцареллы.",
        p_p3: "Полная смешанная праздничная пицца",
        desc_p2: "Ваш особый вкус на основе Маргариты: специальный маринованный донер из говядины, куриный донер или колбаса.",
        p_p2: "Протеиновая пицца",
        desc_p1: "Настоящее неаполитанское тесто, запеченное в каменной печи, наш специальный соус для пиццы и свежая моцарелла.",
        p_p1: "Пицца Маргарита",
        desc_b3: "Сытная и быстрая классика! Горячая встреча двух выбранных вами белков в хрустящей базламе.",
        p_b3: "Смешанный тост Базлама",
        desc_b2: "Тосты, обогащенные выбранным вами белком и плавящимся сыром.",
        p_b2: "Базлама с Мясом",
        desc_b1: "Традиционный турецкий деревенский тост, хрустящий снаружи, с начинкой из тающего сыра.",
        p_b1: "Традиционный тост Базлама",
        desc_o4: "Огромная порция омлета, приготовленная специально для вас, с двумя вкусами на ваш выбор.",
        p_o4: "Смешанный праздничный омлет",
        desc_o3: "Начинка омлета донером из говядины, курицы или традиционной колбасой на ваш выбор.",
        p_o3: "Специальный протеиновый омлет",
        desc_o2: "Омлет с начинкой из плавящегося сыра.",
        p_o2: "Омлет с сыром",
        desc_o1: "Мягкий классический омлет, тщательно приготовленный на сковороде.",
        p_o1: "Традиционный омлет на сковороде",
        desc_m4: "Легендарная встреча двух твоих избранных протеинов с горячим менеменом.",
        p_m4: "Смешанный Менемен",
        desc_m3: "Традиционная основа менемена, увенчанная специально маринованными ломтиками говяжьего донера, куриного донера или колбасы на ваш выбор.",
        p_m3: "Менемен с Мясом/Курицей",
        desc_m2: "Легендарный турецкий менемен с добавлением сыра.",
        p_m2: "Менемен с Сыром",
        desc_m1: "Легендарный турецкий завтрак, приготовленный из измельченных помидоров и плавящегося сыра.",
        p_m1: "Традиционный Менемен",
        desc_pizza: "Тесто особой ферментации, итальянский томатный соус и изысканный сыр моцарелла, запеченные в дровяной печи.",
        desc_menemen: "Приготовлен только из яичных желтков, большого количества чеддера и сливочного масла, вкус легендарного регионального завтрака.",
        desc_toast: "Подается хрустящим из каменной печи с сыром чеддер и фирменной колбасой/говядиной между деревенским хлебом.",
        desc_coffee: "Прекрасно обжаренный и молотый свежий кофе Арабика премиум-класса, искусно сваренный и подаваемый со знаменитыми турецкими деликатесами.",
        desc_tea: "Сварен из премиальной смеси турецкого и цейлонского чая, бергамота и сушеных бутонов роз.",
        desc_lemonade: "Ледяной домашний свежий лимонад, наполненный гибискусом, корицей, звездчатым анисом и настоящим персидским шафраном.",
        desc_cake: "Мягкий внутри, много какао и покрыт горячим шоколадным соусом, незаменимый вкус.",
    },
    ar: {
        category: "مقهى ومطعم",
        status_open: "مفتوح الآن (08:00 - 23:00)",
        btn_menu: "📖 عرض القائمة الرقمية",
        btn_gezi: "🗺️ دليل ومسار رحلة إسطنبول",
        btn_reserve: "احجز طاولة",
        btn_message: "ارسل لنا رسالة",
        title_about: "معلومات عنا",
        slogan_about: "نكهات تقليدية، وصفات فريدة فقط في فيرنا",
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
        review_2: "يجب أن تجرب مينيمين. الموظفون مبتسمون للغاية ومن الرائع أنهم يسمحون بالحيوانات الأليفة.",
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
        gal_lbl_menemen: "مينيمين في المقلاة",
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
        title_social: "المسؤولية الاجتماعية",
        social_intro: "في مقهى فيرنا، نحول أرباحنا وجميع البقشيش الذي تتركه إلى فائدة اجتماعية مباشرة.",
        social_student_title: "مشروع بيوغلو للطلاب",
        social_student_desc: "نحن داعمون فخورون لمشروع 'Öğrenci'Ye' التابع لبلدية بيوغلو. نقدم وجبات مجانية لطلاب الجامعات.",
        social_animal_title: "أصدقاء حيوانات الشوارع",
        social_animal_desc: "نغطي تكاليف الطعام والماء والخدمات البيطرية لأصدقائنا ذوي الفراء في الشارع. مقهانا يرحب بالحيوانات الأليفة.",

        search_placeholder: "🔍 ابحث في القائمة... (مثل: منمن، بيتزا)",
        filter_all: "✨ كل القائمة",
        filter_halal: "☪️ حلال ١٠٠٪",
        filter_veggie: "🌿 نباتي",
        filter_glutenfree: "🌾 خالي من الغلوتين / صحي",
        filter_signature: "⭐ نكهاتنا المميزة",
        badge_stone_oven: "🍕 فرن حجري",
        title_pizza_napo: "بيتزا نابولي",
        badge_famous: "🍳 مشهور",
        title_menemen_cakal: "مينيمين",
        badge_traditional: "☕ تقليدي",
        title_coffee: "قهوة تركية",
        whatsapp_manager: "مدير الواتساب",
        btn_send_msg2: "إرسال رسالة",

        filter_dairyfree: "🚫 خالي من منتجات الألبان / الكازين",


        cat_food: "ساخن من الفرن",
        cat_drinks: "المشروبات والحلويات",
        item_pizza: "بيتزا مخبوزة على الحجر",
        desc_pizza: "عجينة مخمرة بشكل خاص، صلصة طماطم إيطالية، وجبن موزاريلا رائع يخبز في فرن الحطب.",
        item_menemen: "مينيمين الشهير",
        desc_menemen: "محضر فقط بصفار البيض والكثير من الشيدر والزبدة، طعم إفطار إقليمي أسطوري.",
        item_toast: "توست بازلاما من الفرن",
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
        badge_dairy: "يحتوي على منتجات الألبان",
        title_work_hours: "أيام وساعات العمل",
        status_now_open: "🟢 مفتوح الآن",
        status_now_closed: "🔴 مغلق الآن",
        signature_intro: "ألذ وأشهر أطباقنا المختارة بعناية. انقر على أي منتج لعرض تفاصيله في القائمة.",
        signature_loading: "جاري تحميل النكهات المميزة...",
        title_location_yandex: "الموقع والاتجاهات (خرائط ياندكس)",
        badge_live_traffic: "🔴 حركة مرور مباشرة ومباني 3D",
        address_full: "<strong>العنوان:</strong> شاهكولو مح. كومباراجي يوكوشو سوك. رقم:41A، 34421 بيوغلو/إسطنبول (بالقرب من شارع الاستقلال وبرج غلطة)",
        btn_yandex_nav: "ملاحة ياندكس",
        btn_panorama: "بانوراما 360° شارع كومباراجي",
        title_social_media: "ما الأكثر شهرة على وسائل التواصل؟",
        badge_tour_videos: "🎬 فيديوهات الجولة والتحضير",
        title_amenities: "مميزات ومرافق المكان",
        amenity_pet: "🐾 صديق للحيوانات الأليفة",
        amenity_halal: "🕌 طعام حلال 100%",
        amenity_wifi: "📶 واي فاي مجاني عالي السرعة",
        amenity_oven: "🍕 فرن حجري تقليدي",
        amenity_historic: "🏛️ أجواء تاريخية عمرها 150 عامًا",
        amenity_nfc: "💳 دفع لاتلامسي / NFC",
        amenity_veg: "🌿 خيارات نباتية",
        amenity_gluten: "🌾 خيارات خالية من الغلوتين / صحية",
        amenity_family: "👶 مناسب للعائلات والأطفال",
        amenity_tea: "☕ شاي خاص بمزيج براعم الورد",
        google_review_desc: "اطلع على جميع تقييمات ومراجعات الضيوف الحقيقية مباشرة على جوجل.",
        yandex_review_desc: "اطلع على سجلات الموقع والتقييمات على خرائط ياندكس.",
        badge_satisfaction: "رضا العملاء",
        desc_t1: "كعكة الشوكولاتة الساخنة الطازجة من الفرن مغطاة بآيس كريم مرعش الشهير وصلصة الشوكولاتة ولمسة من جوز الهند.",
        p_t1: "كعكة الشوكولاتة الساخنة مع الآيس كريم",
        desc_c3: "جرعة خاصة منعشة محضرة بمزيج فريد من القرفة والكركديه والزعفران الإيراني على قاعدة عصير الليمون المثلج.",
        p_c3: "عصير الليمون والكركديه والزعفران",
        desc_c2: "مياه معدنية طبيعية.",
        p_c2: "مياه معدنية",
        desc_c1: "Refreshing water.",
        p_c1: "Water",
        desc_s5: "الكلاسيكية الإيطالية مع رغوة الحليب.",
        p_s5: "كابتشينو",
        desc_s4: "إسبريسو مع الكثير من الحليب.",
        p_s4: "لاتيه",
        desc_s3: "قهوة قوية من حبوب مطحونة طازجة.",
        p_s3: "أمريكانو",
        desc_s2: "القهوة التركية التقليدية، مطبوخة ببطء، ذات رغوة شديدة، تقدم مع البهجة التركية.",
        p_s2: "قهوة تركية",
        desc_s1: "مزيج خاص من أوراق الشاي المختارة بعناية بنكهة البرغموت والمخففة ببتلات الورد الجافة.",
        p_s1: "شاي مزيج خاص",
        desc_p3: "بيتزا رائعة للمهرجانات مخبوزة مع دونر اللحم البقري، دونر الدجاج، السجق، والكثير من جبن الموتزاريلا.",
        p_p3: "بيتزا العيد المشكلة الكاملة",
        desc_p2: "نكهتك الخاصة على قاعدة المارجريتا: دونر لحم بقري متبل خاص، أو دونر دجاج، أو سجق.",
        p_p2: "بيتزا البروتين",
        desc_p1: "عجينة نابولية حقيقية مخبوزة في فرن حجري، صلصة البيتزا الخاصة بنا وجبنة الموزاريلا الطازجة.",
        p_p1: "بيتزا مارجريتا",
        desc_b3: "الكلاسيكية القلبية وسريعة! لقاء ساخن بين اثنين من البروتينات المختارة في خبز البزلمة المقرمش.",
        p_b3: "توست بازلاما مشكل",
        desc_b2: "خبز محمص غني بالبروتين الذي اخترته مع الجبن الذائب.",
        p_b2: "بازلاما باللحم",
        desc_b1: "خبز القرية التركي التقليدي، مقرمش من الخارج ومحشو بالجبنة الذائبة.",
        p_b1: "توست بازلاما تقليدي",
        desc_o4: "عجة كبيرة الحجم مصنوعة خصيصًا لك بنكهتين من اختيارك.",
        p_o4: "أومليت العيد المختلط",
        desc_o3: "حشوة الأومليت باختيارك من دونر لحم البقر، أو دونر الدجاج، أو السجق التقليدي.",
        p_o3: "أومليت بروتين خاص",
        desc_o2: "أومليت مملوء بالجبنة الذائبة.",
        p_o2: "أومليت بالجبنة",
        desc_o1: "عجة كلاسيكية ناعمة مطبوخة بعناية في مقلاة.",
        p_o1: "عجة عموم التقليدية",
        desc_m4: "اللقاء الأسطوري بين البروتينات التي اخترتها مع المينمين الساخن.",
        p_m4: "مينيمين مشكل",
        desc_m3: "قاعدة مينمين تقليدية مغطاة باختيارك من شرائح لحم البقر المتبلة بشكل خاص أو دونر الدجاج أو السجق.",
        p_m3: "مينيمين باللحم/الدجاج",
        desc_m2: "مينمين تركي مميز مع جبنة إضافية.",
        p_m2: "مينيمين بالجبن",
        desc_m1: "وجبة إفطار تركية مميزة محضرة بالطماطم المهروسة والجبن الذائب.",
        p_m1: "مينيمين تقليدي",
        desc_pizza: "عجينة مخمرة خاصة، صلصة طماطم إيطالية، وجبنة موزاريلا رائعة مخبوزة في فرن الحطب.",
        desc_menemen: "يتم تحضيره فقط بصفار البيض والكثير من جبنة الشيدر والزبدة، وهو مذاق إفطار إقليمي أسطوري.",
        desc_toast: "يقدم مقرمش من الفرن الحجري مع جبنة الشيدر والسجق المميز/اللحم البقري بين خبز القرية.",
        desc_coffee: "قهوة أرابيكا الطازجة المحمصة جيدًا والمطحونة، المخمرة بخبرة وتقدم مع البهجة التركية الشهيرة.",
        desc_tea: "مخمر بمزيج فاخر من الشاي التركي والسيلاني والبرغموت وبراعم الورد المجففة.",
        desc_lemonade: "عصير ليمون طازج منزلي الصنع مثلج ومملوء بالكركديه والقرفة واليانسون والزعفران الفارسي الأصيل.",
        desc_cake: "طرية من الداخل، كثيرة الكاكاو، ومغطاة بصوص الشوكولاتة الساخنة، طعم لا غنى عنه.",
    },
    zh: {
        category: "咖啡厅与餐厅",
        status_open: "营业中 (08:00 - 23:00)",
        btn_menu: "📖 查看电子菜单",
        btn_gezi: "🗺️ 伊斯坦布尔智能指南与路线",
        btn_reserve: "预订餐桌",
        btn_message: "给我们留言",
        title_about: "关于我们",
        slogan_about: "传统风味，独特配方，尽在Fırınna",
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
        review_2: "你一定要尝尝 menemen。员工都面带微笑，而且这里对宠物很友好，真是太棒了。",
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
        title_social: "社会责任",
        social_intro: "在 Firinna Cafe，我们将我们的收入和您留下的所有小费直接转化为社会福利。",
        social_student_title: "贝伊奥卢学生项目",
        social_student_desc: "我们是贝伊奥卢市政府“Öğrenci'Ye”项目的自豪支持者。我们为大学生提供免费餐点。",
        social_animal_title: "关爱流浪动物",
        social_animal_desc: "我们负责街头流浪动物的食物、水和兽医费用。我们的咖啡馆完全允许携带宠物。",

        search_placeholder: "🔍 搜索菜单...（例如：Menemen，披萨）",
        filter_all: "✨ 所有菜单",
        filter_halal: "☪️ 100% 清真",
        filter_veggie: "🌿 素食",
        filter_glutenfree: "🌾 无麸质 / 健康",
        filter_signature: "⭐ 招牌美味",
        badge_stone_oven: "🍕 石窑",
        title_pizza_napo: "那不勒斯披萨",
        badge_famous: "🍳 著名",
        title_menemen_cakal: "煎蛋",
        badge_traditional: "☕ 传统",
        title_coffee: "土耳其咖啡",
        whatsapp_manager: "WhatsApp 经理",
        btn_send_msg2: "发送消息",

        filter_dairyfree: "🚫 不含乳制品 / 酪蛋白",


        cat_food: "新鲜出炉",
        cat_drinks: "饮料与甜点",
        item_pizza: "石烤披萨",
        desc_pizza: "特制发酵面团，意大利番茄酱，搭配精美马苏里拉奶酪，在柴火烤炉中烘烤而成。",
        item_menemen: "著名的 Menemen",
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
        badge_dairy: "含乳制品",
        title_work_hours: "营业日期与时间",
        status_now_open: "🟢 营业中",
        status_now_closed: "🔴 已打烊",
        signature_intro: "精心挑选的最受喜爱的风味。点击任何产品查看菜单详情。",
        signature_loading: "正在加载招牌美味...",
        title_location_yandex: "位置与导航（Yandex 地图）",
        badge_live_traffic: "🔴 实时交通与3D建筑",
        address_full: "<strong>地址：</strong>Şahkulu Mah. Kumbaracı Yokuşu Sok. No:41A, 34421 Beyoğlu/伊斯坦布尔（靠近独立大街和加拉塔塔）",
        btn_yandex_nav: "Yandex 导航",
        btn_panorama: "360° 库姆巴拉哲街全景",
        title_social_media: "社交媒体上最热门的是什么？",
        badge_tour_videos: "🎬 导览与制作视频",
        title_amenities: "场地特色与设施",
        amenity_pet: "🐾 宠物友好",
        amenity_halal: "🕌 100%清真食品",
        amenity_wifi: "📶 免费高速Wi-Fi",
        amenity_oven: "🍕 传统石炉",
        amenity_historic: "🏛️ 150年历史氛围",
        amenity_nfc: "💳 非接触式/NFC支付",
        amenity_veg: "🌿 素食选择",
        amenity_gluten: "🌾 无麸质/健康选择",
        amenity_family: "👶 适合家庭与儿童",
        amenity_tea: "☕ 特制玫瑰花茶",
        google_review_desc: "直接在 Google 上查看所有真实客人评价和评分。",
        yandex_review_desc: "在 Yandex 地图上查看位置和评价记录。",
        badge_satisfaction: "顾客满意度",
        cat_1: "梅内门",
        p_m1: "传统梅尼曼",
        desc_m1: "标志性的土耳其早餐由特殊的碎西红柿和融化的奶酪制成。 （恰卡利风格）",
        p_m2: "梅内门与卡沙尔",
        desc_m2: "标志性的土耳其 menemen 含有大量切达干酪。",
        p_m3: "梅内曼肉/香肠/鸡肉",
        desc_m3: "在传统的menemen底座之上；特别腌制的肉馅饼、鸡肉馅饼或香肠。",
        p_m4: "梅尼曼混合盛宴",
        desc_m4: "您选择的两种不同蛋白质与热梅尼曼的传奇相遇。",
        cat_2: "吐司",
        p_o1: "传统煎蛋卷",
        desc_o1: "用乡村黄油烹制的美味煎蛋卷",
        p_o2: "切达煎蛋卷",
        desc_o2: "煎蛋卷充满融化的切达干酪",
        p_o3: "肉/香肠/鸡肉煎蛋卷",
        desc_o3: "丰盛的煎蛋卷，添加您选择的蛋白质",
        p_o4: "混合盛宴煎蛋卷",
        desc_o4: "巨型煎蛋卷，配肉、香肠、鸡肉和卡沙尔",
        cat_3: "比萨",
        p_b1: "传统巴兹拉马吐司",
        desc_b1: "乡村大饼之间夹有卡沙尔奶酪，口感酥脆",
        p_b2: "肉/香肠/鸡肉面包",
        desc_b2: "除了切达干酪之外，还富含您选择的蛋白质的吐司",
        p_b3: "两种选择基础",
        desc_b3: "您选择的两种蛋白质选择和大量切达干酪",
        cat_4: "冷热饮品",
        p_p1: "玛格丽塔披萨",
        desc_p1: "真正那不勒斯风格的奇迹，我们的特殊混合披萨酱和新鲜马苏里拉奶酪在石炉中烹制。",
        p_p2: "披萨（肉/香肠/鸡肉）",
        desc_p2: "您可以选择以玛格丽塔为基础的特殊口味：特制腌制肉馅饼、鸡肉馅饼或苏库克。",
        p_p3: "全混合披萨",
        desc_p3: "用肉、香肠、鸡肉和大量马苏里拉奶酪烘烤的传奇披萨",
        cat_5: "甜点",
        p_s1: "特调拼配茶",
        desc_s1: "精心挑选的茶叶的特殊版本，以佛手柑调味并与干玫瑰花瓣混合。",
        p_s2: "土耳其咖啡",
        desc_s2: "传统的土耳其咖啡，慢煮，泡沫丰富，搭配土耳其软糖。",
        p_s3: "美式咖啡",
        desc_s3: "来自现磨咖啡豆的浓咖啡",
        p_s4: "拿铁咖啡",
        desc_s4: "浓缩咖啡加大量牛奶",
        p_s5: "卡布奇诺咖啡",
        desc_s5: "意大利经典奶泡",
        cat_6: "冷饮",
        p_c2: "玛登苏尤",
        desc_c2: "天然矿泉水",
        p_c3: "芙蓉藏红花柠檬水",
        desc_c3: "以冰镇柠檬水为基础；采用肉桂、木槿和伊朗藏红花的独特组合配制而成的特殊灵丹妙药。",
        cat_7: "甜的",
        p_t1: "热巧克力蛋糕配冰淇淋",
        desc_t1: "新鲜出炉的热巧克力蛋糕上有著名的马拉什冰淇淋、巧克力酱和少许椰子。",
        tag_vegan: "素食主义者",
        tag_gluten: "麸质",
        tag_gluten_free: "不含麸质",
        tag_halal: "清真",
        tag_dairy: "乳制品",
        tag_vegetarian: "素食",
    },
    uk: {
        category: "Кафе та ресторан",
        status_open: "Відчинено зараз (08:00 - 23:00)",
        btn_menu: "📖 Переглянути цифрове меню",
        btn_gezi: "🗺️ Путівник і маршрут по Стамбулу",
        btn_reserve: "Забронюйте столик",
        btn_message: "Надішліть нам повідомлення",
        title_about: "Про нас",
        slogan_about: "ТРАДИЦІЙНІ СМАКИ, УНІКАЛЬНІ РЕЦЕПТИ ТІЛЬКИ У FIRINNA",
        text_about: "ШАНОВНИЙ ГОСТЕ, ЛАСКАВО ПРОСИМО ДО FIRINNA.\n\nРозташоване в 150-річній історичній атмосфері Галати, прямо на тихому Кумбарачі Йокушу, Fırınna Cafe & Restaurant є особливим кулінарним притулком, де ви можете відійти від метушні вулиці Істікляль і відпочити.\n\nЗ ретельно відібраними інгредієнтами, свіжоспеченими в духовці. фірмові страви, багаті сорти кави та домашні десерти, ми втілюємо в життя традиційні рецепти з сучасними штрихами.\n\nТут нікуди поспішати! З нашою доброзичливою, гостинною командою, яка підтримує домашніх тварин, ви зможете насолодитися теплими розмовами та спокійними моментами в атмосфері нашої 150-річної історичної будівлі. Ми будемо раді залишити приємний спогад про вашу історичну подорож до Стамбула.",
        title_top_reviews: "Від наших клієнтів",
        title_gating: "Оцініть ваш досвід",
        sub_gating: "Який ваш досвід у Firinna? Ваш відгук дуже важливий для нас.",
        gating_high_msg: "🎉 Чудово! Ми раді, що вам сподобалось. Чи бажаєте ви підтримати нас 5-зірковим оглядом на цих платформах?",
        gating_low_title: "Ваш відгук дуже цінний для нас!",
        gating_low_msg: "Ви можете надіслати будь-який відгук або питання безпосередньо нашому менеджеру:",
        btn_google_review: "Оцініть 5 зірок у Google",
        btn_yandex_review: "Оцінка на Яндекс",
        btn_tripadvisor_review: "Огляд на TripAdvisor",
        google_perfect: "Відмінно в Google",
        yandex_perfect: "Відмінно на Яндекс",
        btn_inspect: "огляд",
        btn_see_all_google_photos: "Переглянути всі фотографії на Картах Google (100+)",
        table_available: "На даний момент доступно {N} столів, ласкаво просимо!",
        table_full: "Наразі всі столики зайняті.",
        table_offline: "Статус таблиці недоступний.",
        text_group_events: "<strong>Group & Private Events:</strong> For after-hours group bookings and mini events, please <a href='https://wa.me/905456301214?text=Hello,%20I%20would%20like%20information%20about%20group%20bookings.' target='_blank' style='color:#059669; font-weight:700; text-decoration:underline;'>Contact via WhatsApp</a>.",
        review_1: "Чудове історичне місце, де можна втекти від шуму Істікляль і перевести подих. Їхня піца легендарна!",
        review_2: "Ви повинні спробувати menemen. Персонал дуже усміхнений, і чудово, що вони доброзичливі до домашніх тварин.",
        review_3: "Найкраще місце в Галаті для кави та десертів. Персонал дуже уважний.",
        title_virtual_tour: "Віртуальний тур (360°)",
        text_virtual_tour: "Дослідіть нашу 150-річну історичну будівлю прямо з місця, де ви сидите.",
        title_faq: "Часті питання",
        faq_q1: "🐾 Чи дозволені домашні тварини?",
        faq_a1: "так! Fırınna на 100% дружній до домашніх тварин. Запрошуємо вас провести час зі своїми пухнастими друзями як у нашому відкритому саду, так і в приміщенні.",
        faq_q2: "💳 Які способи оплати ви приймаєте?",
        faq_a2: "Ми приймаємо всі основні кредитні картки, дебетові картки, безконтактні мобільні платежі (Apple Pay / Google Pay) і готівку.",
        faq_q3: "🥗 У вас є вегетаріанські або безглютенові страви?",
        faq_a3: "так! У нашому меню представлені вишукані вегетаріанські піци в кам’яній печі, багаті сніданки та безглютенові/веганські альтернативи.",
        faq_q4: "🕒 Чи можемо ми забронювати групові або приватні заходи?",
        faq_a4: "так! Для днів народжень, корпоративних зустрічей або приватних міні-заходів не соромтеся зв’язуватися з нами безпосередньо через WhatsApp.",
        title_location: "Розташування",
        title_contact: "Контакт і місцезнаходження",
        title_gallery: "Атмосфера та смаки",
        gal_title_interior: "Приміщення та атмосфера",
        gal_title_exterior: "На відкритому повітрі та вулиця Кумбараджи",
        gal_title_signature: "Наші фірмові смаки",
        gal_lbl_interior_history: "Історичний інтер'єр",
        gal_lbl_warm_tables: "Затишне сидіння",
        gal_lbl_details: "Деталі місця проведення",
        gal_lbl_street: "Вулиця Кумбараджи",
        gal_lbl_outdoor_seating: "Відкритий стіл",
        gal_lbl_historic_building: "Історична будівля",
        gal_lbl_fresh_tea: "Свіжий турецький чай",
        gal_lbl_turkish_coffee: "Турецька кава",
        gal_lbl_menemen: "Сковорода Менемен",
        gal_lbl_pizza: "Піца з кам'яної печі",
        gal_lbl_lemonade: "Домашній лимонад",
        gal_lbl_glintwein: "Глінтвейн",
        badge_historic_tr: "Історичне турецьке кафе",
        badge_halal: "100% Халяль",
        badge_quality: "Найкраща якість",
        badge_price: "Справедлива ціна",
        title_reviews: "Розташування та останні відгуки",
        btn_google: "Читайте останні відгуки Google",
        btn_yandex: "Переглянути на Яндекс Картах",
        btn_baidu: "Переглянути на Картах Baidu",
        modal_res_title: "Бронювання столиків",
        label_name: "ПІБ",
        label_phone: "Номер телефону",
        label_date: "Дата",
        label_time: "Час (08:00-23:00)",
        label_guests: "Кількість гостей",
        label_note: "Спеціальний запит / примітка (необов'язково)",
        btn_submit: "Надіслати запит",
        modal_msg_title: "Надішліть нам повідомлення",
        label_message: "Ваше повідомлення",
        btn_submit_msg: "Надіслати повідомлення",
        footer_rights: "Всі права захищені.",
        menu_header_title: "Фірмові страви",
        menu_header_sub: "З дотиком Фіріни...",
        menu_back: "Головна",
        menu_intro: "Ви можете відвідати наш магазин або отримати детальну інформацію про всі варіанти меню у наших співробітників. Нижче ви можете переглянути наші найулюбленіші авторські смаки.",
        menu_download: "Завантажити меню з цінами (PDF)",
        desc_t1: "Гарячий шоколадний пиріг, щойно випечений у духовці, зі знаменитим морозивом Maraş, шоколадним соусом і ноткою кокосу.",
        p_t1: "Гарячий шоколадний торт",
        desc_c3: "Особливе освіжаюче зілля, приготоване з унікальним поєднанням кориці, гібіскусу та іранського шафрану на крижаній основі лимонаду.",
        p_c3: "Шафрановий лимонад з гібіскусу",
        desc_c2: "Натуральна мінеральна вода.",
        p_c2: "Мінеральна вода",
        desc_c1: "Освіжаюча вода.",
        p_c1: "Вода",
        desc_s5: "Італійська класика з молочною пінкою.",
        p_s5: "Капучіно",
        desc_s4: "Еспресо з великою кількістю молока.",
        p_s4: "Латте",
        desc_s3: "Міцна кава зі свіжозмелених зерен.",
        p_s3: "Американо",
        desc_s2: "Традиційна турецька кава, варена повільно, дуже піниста, подається з лукумом.",
        p_s2: "Турецька кава",
        desc_s1: "Особлива суміш ретельно відібраних листя чаю з ароматом бергамоту і пом'якшена сухими пелюстками троянд.",
        p_s1: "Чай спеціальної суміші",
        desc_p3: "Чудова фестивальна піца, запечена з донером з яловичини, донером з курки, ковбасою та великою кількістю моцарели.",
        p_p3: "Повна змішана піца",
        desc_p2: "Ваш особливий смак на основі Маргарити: особливий маринований яловичий донер, курячий донер або ковбаса.",
        p_p2: "Протеїнова піца",
        desc_p1: "Справжнє неаполітанське тісто, випечене в кам’яній печі, наша спеціальна суміш соусу для піци та свіжої моцарелли.",
        p_p1: "Піца Маргарита",
        desc_b3: "Ситна і швидка класика! Гаряча зустріч двох обраних білків у хрусткому хлібі базалама.",
        p_b3: "Змішані грінки Базлама",
        desc_b2: "Тост, збагачений вибраним білком разом із сиром, що плавиться.",
        p_b2: "Білкова Базлама",
        desc_b1: "Традиційний турецький сільський хлібний тост, хрусткий зовні, начинений сиром, що плавиться.",
        p_b1: "Традиційний тост Базлама",
        desc_o4: "Величезний порційний омлет, виготовлений спеціально для вас із двома смаками на ваш вибір.",
        p_o4: "Змішаний святковий омлет",
        desc_o3: "Заправний омлет із яловичим донером, курячим донером або традиційною ковбасою на вибір.",
        p_o3: "Особливий білковий омлет",
        desc_o2: "Омлет з начинкою з плавиться сиру.",
        p_o2: "Омлет з сиром",
        desc_o1: "М'який класичний омлет акуратно приготований на сковороді.",
        p_o1: "Традиційний омлет на пан",
        desc_m4: "Легендарна зустріч двох ваших обраних білок з гарячим менеменом.",
        p_m4: "Змішане свято Менемен",
        desc_m3: "Традиційна основа менемен, увінчана спеціальним маринованим нарізаним яловичим донером, курячим донером або ковбасою на ваш вибір.",
        p_m3: "Менемен з яловичиною / ковбасою / куркою",
        desc_m2: "Культовий турецький менемен з додатковим сиром.",
        p_m2: "Менемен з сиром",
        desc_m1: "Культовий турецький сніданок, приготований з подрібненими помідорами та плавким сиром.",
        p_m1: "Традиційний Менемен",
        cat_food: "Гаряче з духовки",
        cat_drinks: "Напої та десерти",
        item_pizza: "Піца в камені",
        desc_pizza: "Тісто спеціальної ферментації, італійський томатний соус та вишуканий сир моцарела, запечений у дров’яній печі.",
        item_menemen: "Відомий Менемен",
        desc_menemen: "Приготований лише з яєчних жовтків, великої кількості чеддеру та масла, легендарний регіональний смак сніданку.",
        item_toast: "Запечені грінки Базлама",
        desc_toast: "Подається хрустким з кам'яної печі з сиром чеддер і спеціальною ковбасою/яловичиною між сільським хлібом.",
        item_coffee: "Особлива турецька кава",
        desc_coffee: "Тонко обсмажена та мелена свіжа кава арабіка преміум-класу, майстерно зварена та подана зі знаменитим лукумом.",
        item_tea: "Змішаний чай Бутон троянди",
        desc_tea: "Зварений із першокласної суміші турецького та цейлонського чаю, бергамоту та висушених бутонів троянд.",
        item_lemonade: "Спеціальний домашній лимонад",
        desc_lemonade: "Крижаний домашній свіжий лимонад з гібіскусом, корицею, бадьяном і справжнім перським шафраном.",
        item_cake: "Гарячий шоколадний пиріг з шоколадним соусом",
        desc_cake: "М'яка всередині, з великою кількістю какао, вкрита гарячим шоколадним соусом, незамінний смак.",
        badge_veg: "Вегетаріанська",
        badge_vegan: "Веганський",
        badge_gluten: "Містить глютен",
        badge_dairy: "Містить молочні продукти",
        title_work_hours: "Робочі дні та години",
        status_now_open: "🟢 Відкрити зараз",
        status_now_closed: "🔴 Зараз закрито",
        signature_intro: "Наші найулюбленіші, ретельно відібрані смаки. Клацніть будь-який пункт, щоб переглянути деталі його меню.",
        signature_loading: "Завантаження фірмових смаків...",
        title_location_yandex: "Розташування та маршрут (Яндекс Карти)",
        badge_live_traffic: "🔴 Живий трафік і 3D-будівлі",
        address_full: "<strong>Address:</strong> Şahkulu Mah. Kumbaracı Yokuşu Sok. No:41A, 34421 Beyoğlu/İstanbul (Near Istiklal Street & Galata Tower)",
        btn_yandex_nav: "Яндекс навігація",
        btn_panorama: "360° Панорама вулиці Кумбараджи",
        title_social_media: "Що популярно в соціальних мережах?",
        badge_tour_videos: "🎬 Відео про тур і підготовку",
        title_amenities: "Особливості та зручності місця проведення",
        amenity_pet: "🐾 Розміщення домашніх тварин",
        amenity_halal: "🕌 100% халяльна їжа",
        amenity_wifi: "📶 Безкоштовний високошвидкісний Wi-Fi",
        amenity_oven: "🍕 Традиційна кам'яна піч",
        amenity_historic: "🏛️ 150-річна історична атмосфера",
        amenity_nfc: "💳 Безконтактна оплата / NFC",
        amenity_veg: "🌿 Вегетаріанські варіанти",
        amenity_gluten: "🌾 Безглютенові/здорові страви",
        amenity_family: "👶 Зручно для сім'ї та дітей",
        amenity_tea: "☕ Спеціальний чай з бутонів троянд",
        google_review_desc: "Переглядайте всі справжні відгуки та рейтинги гостей безпосередньо в Google.",
        yandex_review_desc: "Переглядайте місцезнаходження та переглядайте записи на Яндекс Картах.",
        badge_satisfaction: "Задоволеність клієнтів",
        title_social: "Соціальна відповідальність",
        social_intro: "Як Fırınna Cafe, ми ділимося своїми прибутками та любов’ю з нашими сусідами.",
        social_student_title: "Студентський проект у Бейоглу",
        social_student_desc: "Ми підтримуємо студентів університету в Бейоглу безкоштовним харчуванням.",
        social_animal_title: "Дружнє ставлення до вуличних тварин",
        social_animal_desc: "Ми щодня забезпечуємо їжею та водою наших пухнастиків на нашій вулиці.",
        search_placeholder: "🔍 Пошук в меню...",
        filter_all: "✨ Все меню",
        filter_halal: "☪️ 100% Халяль",
        filter_veggie: "🌿 Вегетаріанська",
        filter_glutenfree: "🌾 Без глютену",
        filter_signature: "⭐ Підпис",
        badge_stone_oven: "🍕 Кам'яна піч",
        title_pizza_napo: "Неаполітанська піца",
        badge_famous: "🍳 Знаменитий",
        title_menemen_cakal: "Menemen",
        badge_traditional: "☕ Традиційний",
        title_coffee: "Турецька кава",
        whatsapp_manager: "Менеджер WhatsApp",
        btn_send_msg2: "Надіслати повідомлення",
        filter_dairyfree: "🚫 Без молочних продуктів",
        cat_1: "Менемен",
        cat_2: "Тости",
        cat_3: "Піца",
        cat_4: "Гарячі та холодні напої",
        cat_5: "Десерти",
        cat_6: "холодні напої",
        cat_7: "Солодкий",
        tag_vegan: "Веганський",
        tag_gluten: "глютен",
        tag_gluten_free: "без глютену",
        tag_halal: "халяль",
        tag_dairy: "Молочний продукт",
        tag_vegetarian: "Вегетаріанська",
    },
    de: {
        category: "Café & Restaurant",
        status_open: "Jetzt geöffnet (08:00 - 23:00)",
        btn_menu: "📖 Digitale Speisekarte",
        btn_gezi: "🗺️ Istanbul Reiseführer und Route",
        btn_reserve: "Reservieren Sie einen Tisch",
        btn_message: "Senden Sie uns eine Nachricht",
        title_about: "Über uns",
        slogan_about: "TRADITIONELLE AROMEN, EINZIGARTIGE REZEPTE NUR BEI FIRINNA",
        text_about: "LIEBER GAST, WILLKOMMEN BEI FIRINNA.\n\nDas Fırınna Cafe & Restaurant liegt in der 150 Jahre alten historischen Atmosphäre von Galata, direkt am ruhigen Kumbaracı Yokuşu und ist eine besondere kulinarische Oase, in der Sie dem Trubel der Istiklal-Straße entfliehen und einen erfrischenden Atemzug nehmen können.\n\nMit sorgfältig ausgewählten Zutaten, frischen, im Ofen gebackenen Spezialitäten, reichhaltigen Kaffeesorten und hausgemachten Desserts bieten wir Ihnen Traditionelle Rezepte werden mit modernen Akzenten zum Leben erweckt.\n\nHier gibt es keine Eile! Genießen Sie mit unserem freundlichen, gastfreundlichen und haustierfreundlichen Team herzliche Gespräche und friedliche Momente im Ambiente unseres 150 Jahre alten historischen Gebäudes. Wir würden uns freuen, eine schöne Erinnerung an Ihre historische Reise nach Istanbul zu sein.",
        title_top_reviews: "Von unseren Kunden",
        title_gating: "Bewerten Sie uns",
        sub_gating: "Wie war Ihre Erfahrung bei Firinna? Ihr Feedback bedeutet uns sehr viel.",
        gating_high_msg: "🎉 Wunderbar! Wir freuen uns, dass es Ihnen gefallen hat. Möchten Sie uns mit einer 5-Sterne-Bewertung auf diesen Plattformen unterstützen?",
        gating_low_title: "Ihr Feedback ist für uns sehr wertvoll!",
        gating_low_msg: "Sie können Feedback oder Probleme direkt an unseren Manager senden:",
        btn_google_review: "Bewerten Sie 5 Sterne bei Google",
        btn_yandex_review: "Bewerten Sie auf Yandex",
        btn_tripadvisor_review: "Bewertung auf TripAdvisor",
        google_perfect: "Hervorragend bei Google",
        yandex_perfect: "Ausgezeichnet auf Yandex",
        btn_inspect: "Rezension",
        btn_see_all_google_photos: "Alle Fotos auf Google Maps anzeigen (100+)",
        table_available: "Derzeit sind {N} Tische verfügbar, herzlich willkommen!",
        table_full: "Derzeit sind alle Tische besetzt.",
        table_offline: "Tabellenstatus nicht verfügbar.",
        text_group_events: "<strong>Group & Private Events:</strong> For after-hours group bookings and mini events, please <a href='https://wa.me/905456301214?text=Hello,%20I%20would%20like%20information%20about%20group%20bookings.' target='_blank' style='color:#059669; font-weight:700; text-decoration:underline;'>Contact via WhatsApp</a>.",
        review_1: "Ein wunderbarer, historischer Ort, um dem Lärm des Istiklal zu entfliehen und durchzuatmen. Ihre Pizzen sind legendär!",
        review_2: "Sie müssen unbedingt die-Menemen probieren. Das Personal lächelt sehr und es ist toll, dass Haustiere willkommen sind.",
        review_3: "Der beste Ort in Galata für Kaffee und Desserts. Das Personal ist sehr aufmerksam.",
        title_virtual_tour: "Virtueller Rundgang",
        text_virtual_tour: "Erkunden Sie unser 150 Jahre altes historisches Gebäude direkt von Ihrem Sitzplatz aus.",
        title_faq: "Häufig gestellte Fragen",
        faq_q1: "🐾 Sind Haustiere erlaubt?",
        faq_a1: "Ja! Fırınna ist 100 % haustierfreundlich. Gerne können Sie Ihre Zeit mit Ihren vierbeinigen Freunden sowohl in unserem Außengarten als auch auf den Sitzplätzen im Innenbereich genießen.",
        faq_q2: "💳 Welche Zahlungsmethoden akzeptieren Sie?",
        faq_a2: "Wir akzeptieren alle gängigen Kreditkarten, Debitkarten, kontaktloses mobiles Bezahlen (Apple Pay / Google Pay) und Bargeld.",
        faq_q3: "🥗 Haben Sie vegetarische oder glutenfreie Optionen?",
        faq_a3: "Ja! Unsere Speisekarte bietet vegetarische Gourmet-Pizza aus dem Steinofen, reichhaltige Frühstücksaufstriche und glutenfreie/vegane Alternativen.",
        faq_q4: "🕒 Können wir Gruppenreservierungen oder private Veranstaltungen vornehmen?",
        faq_a4: "Ja! Für Geburtstage, Firmenmeetings oder private Mini-Events können Sie uns gerne direkt über WhatsApp kontaktieren.",
        title_location: "Standort",
        title_contact: "Kontakt & Standort",
        title_gallery: "Ambiente und Geschmack",
        gal_title_interior: "Innenbereich und Ambiente",
        gal_title_exterior: "Outdoor & Kumbaracı-Straße",
        gal_title_signature: "Unser unverkennbarer Geschmack",
        gal_lbl_interior_history: "Historisches Interieur",
        gal_lbl_warm_tables: "Gemütliche Sitzgelegenheiten",
        gal_lbl_details: "Details zum Veranstaltungsort",
        gal_lbl_street: "Kumbaracı-Straße",
        gal_lbl_outdoor_seating: "Sitzplätze im Freien",
        gal_lbl_historic_building: "Historisches Gebäude",
        gal_lbl_fresh_tea: "Frischer türkischer Tee",
        gal_lbl_turkish_coffee: "Türkischer Kaffee",
        gal_lbl_menemen: "Pfanne Menemen",
        gal_lbl_pizza: "Steinofenpizza",
        gal_lbl_lemonade: "Hausgemachte Limonade",
        gal_lbl_glintwein: "Glühwein",
        badge_historic_tr: "Historisches türkisches Café",
        badge_halal: "100 % Halal",
        badge_quality: "Beste Qualität",
        badge_price: "Fairer Preis",
        title_reviews: "Standort und aktuelle Bewertungen",
        btn_google: "Lesen Sie aktuelle Google-Bewertungen",
        btn_yandex: "Auf Yandex Maps anzeigen",
        btn_baidu: "Auf Baidu Maps anzeigen",
        modal_res_title: "Tischreservierung",
        label_name: "Vollständiger Name",
        label_phone: "Telefonnummer",
        label_date: "Datum",
        label_time: "Zeit (08:00-23:00)",
        label_guests: "Anzahl der Gäste",
        label_note: "Sonderwunsch/Hinweis (optional)",
        btn_submit: "Anfrage senden",
        modal_msg_title: "Senden Sie uns eine Nachricht",
        label_message: "Ihre Nachricht",
        btn_submit_msg: "Nachricht senden",
        footer_rights: "Alle Rechte vorbehalten.",
        menu_header_title: "Unsere Spezialitäten",
        menu_header_sub: "Mit Firinnas Touch...",
        menu_back: "Startseite",
        menu_intro: "Sie können unseren Laden besuchen oder sich von unseren Mitarbeitern ausführlich über alle Menüoptionen informieren lassen. Unten können Sie unsere beliebtesten Signature-Geschmacksrichtungen ansehen.",
        menu_download: "Menü mit Preisen herunterladen (PDF)",
        desc_t1: "Heißer Schokoladenkuchen frisch aus dem Ofen, garniert mit dem berühmten Maraş-Eis, Schokoladensauce und einem Hauch Kokosnuss.",
        p_t1: "Heißer Schokoladenkuchen",
        desc_c3: "Ein erfrischender Spezialtrank, zubereitet mit der einzigartigen Kombination aus Zimt, Hibiskus und iranischem Safran auf einer eiskalten Limonadenbasis.",
        p_c3: "Hibiskus-Safran-Limonade",
        desc_c2: "Natürliches Mineralwasser.",
        p_c2: "Mineralwasser",
        desc_c1: "Erfrischendes Wasser.",
        p_c1: "Wasser",
        desc_s5: "Italienischer Klassiker mit Milchschaum.",
        p_s5: "Cappuccino",
        desc_s4: "Espresso mit viel Milch.",
        p_s4: "Latte",
        desc_s3: "Kräftiger Kaffee aus frisch gemahlenen Bohnen.",
        p_s3: "Americano",
        desc_s2: "Traditioneller türkischer Kaffee, langsam gegart, sehr schaumig, serviert mit türkischem Genuss.",
        p_s2: "Türkischer Kaffee",
        desc_s1: "Eine spezielle Mischung aus sorgfältig ausgewählten Teeblättern, aromatisiert mit Bergamotte und abgerundet mit trockenen Rosenblättern.",
        p_s1: "Spezielle Teemischung",
        desc_p3: "Herrliche Festivalpizza gebacken mit Rinder-Döner, Hähnchen-Döner, Wurst und viel Mozzarella.",
        p_p3: "Komplette gemischte Festtagspizza",
        desc_p2: "Ihr besonderer Geschmack auf Margherita-Basis: Speziell marinierter Rinder-Döner, Hähnchen-Döner oder Wurst.",
        p_p2: "Proteinpizza",
        desc_p1: "Echter Teig nach neapolitanischer Art, im Steinofen gebacken, unsere spezielle Mischung aus Pizzasauce und frischem Mozzarella.",
        p_p1: "Pizza Margherita",
        desc_b3: "Ein herzhafter und schneller Klassiker! Heiße Begegnung Ihrer beiden ausgewählten Proteine ​​in knusprigem Bazlama-Brot.",
        p_b3: "Gemischter Bazlama-Toast",
        desc_b2: "Toast, angereichert mit dem Protein Ihrer Wahl, zusammen mit schmelzendem Käse.",
        p_b2: "Protein-Bazlama",
        desc_b1: "Traditioneller türkischer Dorfbrottoast, außen knusprig, gefüllt mit schmelzendem Käse.",
        p_b1: "Traditioneller Bazlama-Toast",
        desc_o4: "Ein extra für Sie zubereitetes Riesenportionomelett mit zwei Geschmacksrichtungen Ihrer Wahl.",
        p_o4: "Gemischtes Festomelett",
        desc_o3: "Füllendes Omelett mit Rindfleisch-Döner, Hähnchen-Döner oder traditioneller Wurst Ihrer Wahl.",
        p_o3: "Spezielles Proteinomelett",
        desc_o2: "Omelett gefüllt mit schmelzendem Käse.",
        p_o2: "Omelette mit Käse",
        desc_o1: "Weiches klassisches Omelett, sorgfältig in einer Pfanne zubereitet.",
        p_o1: "Traditionelles Pfannenomelett",
        desc_m4: "Das legendäre Treffen Ihrer beiden auserwählten Proteine ​​​​mit heißen Menemen.",
        p_m4: "Gemischtes Fest Menemen",
        desc_m3: "Traditionelle Menemen-Basis, garniert mit speziell marinierten Rindfleisch-Döner-, Hähnchen-Döner- oder Wurstscheiben Ihrer Wahl.",
        p_m3: "Menemen mit Rindfleisch / Wurst / Huhn",
        desc_m2: "Kultige türkische Menemen mit extra Käse.",
        p_m2: "Menemen mit Käse",
        desc_m1: "Kultiges türkisches Frühstück, zubereitet mit zerdrückten Tomaten und schmelzendem Käse.",
        p_m1: "Traditionelles Menemen",
        cat_food: "Heiß aus dem Ofen",
        cat_drinks: "Getränke und Desserts",
        item_pizza: "Pizza aus dem Steinofen",
        desc_pizza: "Speziell fermentierter Teig, italienische Tomatensauce und exquisiter Mozzarella-Käse, gebacken im Holzofen.",
        item_menemen: "Berühmte Menemen",
        desc_menemen: "Nur mit Eigelb, reichlich Cheddar und Butter zubereitet, ein legendärer regionaler Frühstücksgeschmack.",
        item_toast: "Gebackener Bazlama-Toast",
        desc_toast: "Knusprig aus dem Steinofen serviert mit Cheddar-Käse und Spezialwurst/Rindfleisch zwischen Dorfbrot.",
        item_coffee: "Spezieller türkischer Kaffee",
        desc_coffee: "Fein gerösteter und gemahlener erstklassiger frischer Arabica-Kaffee, fachmännisch gebrüht und mit berühmten türkischen Köstlichkeiten serviert.",
        item_tea: "Rosenknospen-Mischtee",
        desc_tea: "Gebraut mit einer erstklassigen Mischung aus türkischem und Ceylon-Tee, Bergamotte und getrockneten Rosenknospen.",
        item_lemonade: "Besondere hausgemachte Limonade",
        desc_lemonade: "Eiskalte hausgemachte frische Limonade mit Hibiskus, Zimt, Sternanis und authentischem persischem Safran.",
        item_cake: "Heißer Schokoladenkuchen mit Schokoladensauce",
        desc_cake: "Innen weich, viel Kakao und überzogen mit heißer Schokoladensauce, ein unverzichtbarer Geschmack.",
        badge_veg: "Vegetarier",
        badge_vegan: "Vegan",
        badge_gluten: "Enthält Gluten",
        badge_dairy: "Enthält Milchprodukte",
        title_work_hours: "Arbeitstage und -stunden",
        status_now_open: "🟢 Jetzt öffnen",
        status_now_closed: "🔴Jetzt geschlossen",
        signature_intro: "Unsere beliebtesten, sorgfältig ausgewählten Geschmacksrichtungen. Klicken Sie auf ein beliebiges Element, um dessen Menüdetails anzuzeigen.",
        signature_loading: "Signature-Geschmacksrichtungen werden geladen...",
        title_location_yandex: "Standort und Wegbeschreibung (Yandex Maps)",
        badge_live_traffic: "🔴 Live-Verkehr und 3D-Gebäude",
        address_full: "<strong>Address:</strong> Şahkulu Mah. Kumbaracı Yokuşu Sok. No:41A, 34421 Beyoğlu/İstanbul (Near Istiklal Street & Galata Tower)",
        btn_yandex_nav: "Yandex-Navigation",
        btn_panorama: "360° Kumbaracı-Straßenpanorama",
        title_social_media: "Was ist in den sozialen Medien beliebt?",
        badge_tour_videos: "🎬 Tour- und Vorbereitungsvideos",
        title_amenities: "Merkmale und Annehmlichkeiten des Veranstaltungsortes",
        amenity_pet: "🐾 Haustierfreundlich",
        amenity_halal: "🕌 100 % Halal-Lebensmittel",
        amenity_wifi: "📶 Kostenloses Highspeed-WLAN",
        amenity_oven: "🍕 Traditioneller Steinofen",
        amenity_historic: "🏛️ 150-jährige historische Atmosphäre",
        amenity_nfc: "💳 Kontaktlose / NFC-Zahlung",
        amenity_veg: "🌿 Vegetarische Optionen",
        amenity_gluten: "🌾 Glutenfreie / gesunde Optionen",
        amenity_family: "👶 Familien- und kinderfreundlich",
        amenity_tea: "☕ Spezieller Rosenknospenmischungstee",
        google_review_desc: "Sehen Sie sich alle echten Gästebewertungen und -bewertungen direkt auf Google an.",
        yandex_review_desc: "Sehen Sie sich Standorte an und überprüfen Sie Datensätze auf Yandex Maps.",
        badge_satisfaction: "Kundenzufriedenheit",
        title_social: "Soziale Verantwortung",
        social_intro: "Als Fırınna Café teilen wir unsere Einnahmen und unsere Liebe mit unserer Nachbarschaft.",
        social_student_title: "Studentenprojekt in Beyoğlu",
        social_student_desc: "Wir unterstützen Universitätsstudenten in Beyoğlu mit kostenlosen Mahlzeiten.",
        social_animal_title: "Straßentierfreundlich",
        social_animal_desc: "Wir versorgen unsere pelzigen Freunde auf unserer Straße jeden Tag mit Futter und Wasser.",
        search_placeholder: "🔍 Durchsuchen Sie das Menü...",
        filter_all: "✨Alles Menü",
        filter_halal: "☪️ 100 % Halal",
        filter_veggie: "🌿 Vegetarisch",
        filter_glutenfree: "🌾 Glutenfrei",
        filter_signature: "⭐ Unterschrift",
        badge_stone_oven: "🍕 Steinofen",
        title_pizza_napo: "Neapolitanische Pizza",
        badge_famous: "🍳 Berühmt",
        title_menemen_cakal: "Menemen",
        badge_traditional: "☕ Traditionell",
        title_coffee: "Türkischer Kaffee",
        whatsapp_manager: "WhatsApp-Manager",
        btn_send_msg2: "Nachricht senden",
        filter_dairyfree: "🚫 Milchfrei",
        cat_1: "Menemen",
        cat_2: "Toasts",
        cat_3: "Pizzen",
        cat_4: "Heiße & Kalte Getränke",
        cat_5: "Desserts",
        cat_6: "kalte Getränke",
        cat_7: "Süß",
        tag_vegan: "Vegan",
        tag_gluten: "Gluten",
        tag_gluten_free: "glutenfrei",
        tag_halal: "Halal",
        tag_dairy: "Milchprodukt",
        tag_vegetarian: "Vegetarier",
    },
    fr: {
        category: "Café et restaurant",
        status_open: "Ouvert maintenant (08h00 - 23h00)",
        btn_menu: "📖 Voir le Menu Numérique",
        btn_gezi: "🗺️ Guide de voyage et itinéraire d'Istanbul",
        btn_reserve: "Réserver une table",
        btn_message: "Envoyez-nous un message",
        title_about: "À Propos de Nous",
        slogan_about: "SAVEURS TRADITIONNELLES, RECETTES UNIQUES UNIQUEMENT CHEZ FIRINNA",
        text_about: "CHER INVITÉ, BIENVENUE À FIRINNA.\n\nSitué dans l'atmosphère historique de Galata vieille de 150 ans, directement sur le paisible Kumbaracı Yokuşu, le Fırınna Cafe & Restaurant est un havre culinaire spécial où vous pouvez vous éloigner de l'agitation de la rue Istiklal et prendre une respiration rafraîchissante.\n\nAvec des ingrédients soigneusement sélectionnés, des spécialités fraîches cuites au four, de riches variétés de café et des desserts faits maison, nous donnons vie aux recettes traditionnelles avec touches modernes.\n\nIl n'y a pas de précipitation ici ! Avec notre équipe amicale, hospitalière et acceptant les animaux de compagnie, profitez de conversations chaleureuses et de moments paisibles dans l'ambiance de notre bâtiment historique vieux de 150 ans. Nous serions ravis de garder un doux souvenir de votre voyage historique à Istanbul.",
        title_top_reviews: "Avis de nos clients",
        title_gating: "Évaluez votre expérience",
        sub_gating: "Comment s’est passée votre expérience chez Firinna ? Vos commentaires comptent beaucoup pour nous.",
        gating_high_msg: "🎉 Merveilleux ! Nous sommes heureux que vous ayez apprécié. Souhaitez-vous nous soutenir avec un avis 5 étoiles sur ces plateformes ?",
        gating_low_title: "Vos commentaires nous sont très précieux !",
        gating_low_msg: "Vous pouvez envoyer tout commentaire ou problème directement à notre responsable :",
        btn_google_review: "Notez 5 étoiles sur Google",
        btn_yandex_review: "Tarif sur Yandex",
        btn_tripadvisor_review: "Avis sur TripAdvisor",
        google_perfect: "Excellent sur Google",
        yandex_perfect: "Excellent sur Yandex",
        btn_inspect: "Revoir",
        btn_see_all_google_photos: "Voir toutes les photos sur Google Maps (100+)",
        table_available: "Actuellement {N} tables disponibles, bienvenue !",
        table_full: "Actuellement toutes les tables sont occupées.",
        table_offline: "État de la table indisponible.",
        text_group_events: "<strong>Group & Private Events:</strong> For after-hours group bookings and mini events, please <a href='https://wa.me/905456301214?text=Hello,%20I%20would%20like%20information%20about%20group%20bookings.' target='_blank' style='color:#059669; font-weight:700; text-decoration:underline;'>Contact via WhatsApp</a>.",
        review_1: "Un endroit merveilleux et historique pour échapper au bruit d'Istiklal et respirer. Leurs pizzas sont légendaires !",
        review_2: "Vous devez essayer les menemen. Le personnel est très souriant et c'est super qu'ils acceptent les animaux.",
        review_3: "Le meilleur endroit à Galata pour le café et les desserts. Le personnel est très attentif.",
        title_virtual_tour: "Visite Virtuelle (360°)",
        text_virtual_tour: "Explorez notre bâtiment historique vieux de 150 ans depuis votre siège.",
        title_faq: "Questions fréquentes",
        faq_q1: "🐾 Les animaux sont-ils autorisés ?",
        faq_a1: "Oui! Fırınna accepte à 100 % les animaux domestiques. Vous êtes invités à profiter de votre temps avec vos amis à quatre pattes dans notre jardin extérieur et dans nos sièges intérieurs.",
        faq_q2: "💳 Quels modes de paiement acceptez-vous ?",
        faq_a2: "Nous acceptons toutes les principales cartes de crédit, cartes de débit, paiements mobiles sans contact (Apple Pay/Google Pay) et espèces.",
        faq_q3: "🥗 Avez-vous des options végétariennes ou sans gluten ?",
        faq_a3: "Oui! Notre menu propose des pizzas végétariennes gastronomiques cuites au four sur pierre, de riches tartinades pour le petit-déjeuner et des alternatives sans gluten/végétaliennes.",
        faq_q4: "🕒 Pouvons-nous faire des réservations de groupe ou des événements privés ?",
        faq_a4: "Oui! Pour des anniversaires, des réunions d'entreprise ou des mini-événements privés, n'hésitez pas à nous contacter directement via WhatsApp.",
        title_location: "Emplacement",
        title_contact: "Contact et localisation",
        title_gallery: "Ambiance & Goûts",
        gal_title_interior: "Intérieur & Ambiance",
        gal_title_exterior: "Rue extérieure et Kumbaracı",
        gal_title_signature: "Nos goûts signatures",
        gal_lbl_interior_history: "Intérieur historique",
        gal_lbl_warm_tables: "Sièges confortables",
        gal_lbl_details: "Détails du lieu",
        gal_lbl_street: "Rue Kumbaracı",
        gal_lbl_outdoor_seating: "Sièges extérieurs",
        gal_lbl_historic_building: "Bâtiment historique",
        gal_lbl_fresh_tea: "Thé turc frais",
        gal_lbl_turkish_coffee: "Café Turc",
        gal_lbl_menemen: "Menemen à la poêle",
        gal_lbl_pizza: "Pizza au Feu de Bois",
        gal_lbl_lemonade: "Limonade Maison",
        gal_lbl_glintwein: "Vin chaud",
        badge_historic_tr: "Café turc historique",
        badge_halal: "100% Halal",
        badge_quality: "Meilleure qualité",
        badge_price: "Juste prix",
        title_reviews: "Emplacement et avis récents",
        btn_google: "Lire les avis récents de Google",
        btn_yandex: "Voir sur Yandex Maps",
        btn_baidu: "Afficher sur les cartes Baidu",
        modal_res_title: "Réservation de table",
        label_name: "Nom et prénom",
        label_phone: "Numéro de téléphone",
        label_date: "Date",
        label_time: "Heure (08h00-23h00)",
        label_guests: "Nombre d'invités",
        label_note: "Demande spéciale/Remarque (facultatif)",
        btn_submit: "Envoyer la demande",
        modal_msg_title: "Envoyez-nous un message",
        label_message: "Votre message",
        btn_submit_msg: "Envoyer un message",
        footer_rights: "Tous droits réservés.",
        menu_header_title: "Nos Spécialités",
        menu_header_sub: "Avec le contact de Firinna...",
        menu_back: "Accueil",
        menu_intro: "You can visit our store or get detailed information from our staff for all menu options. Ci-dessous, vous pouvez consulter nos goûts signatures les plus appréciés.",
        menu_download: "Télécharger le menu avec prix (PDF)",
        desc_t1: "Gâteau au chocolat chaud fraîchement sorti du four garni de la célèbre glace Maraş, d'une sauce au chocolat et d'une touche de noix de coco.",
        p_t1: "Gâteau au chocolat chaud",
        desc_c3: "Une potion spéciale rafraîchissante préparée avec la combinaison unique de cannelle, d'hibiscus et de safran iranien sur une base de limonade glacée.",
        p_c3: "Limonade Hibiscus Safran",
        desc_c2: "Eau minérale naturelle.",
        p_c2: "Eau Minérale",
        desc_c1: "Eau rafraîchissante.",
        p_c1: "Eau",
        desc_s5: "Classique italien avec mousse de lait.",
        p_s5: "Cappuccino",
        desc_s4: "Expresso avec beaucoup de lait.",
        p_s4: "Latté",
        desc_s3: "Café fort à base de grains fraîchement moulus.",
        p_s3: "Américain",
        desc_s2: "Café turc traditionnel, mijoté, très mousseux, accompagné de délices turcs.",
        p_s2: "Café Turc",
        desc_s1: "Un mélange spécial de feuilles de thé soigneusement sélectionnées, parfumées à la bergamote et adoucies par des pétales de roses secs.",
        p_s1: "Thé de mélange spécial",
        desc_p3: "Magnifique pizza de festival cuite avec un döner au bœuf, un döner au poulet, des saucisses et beaucoup de mozzarella.",
        p_p3: "Pizza festin mixte complète",
        desc_p2: "Votre saveur spéciale sur une base de Margherita : Döner de bœuf mariné spécial, Döner de poulet ou saucisse.",
        p_p2: "Pizza Protéinée",
        desc_p1: "Véritable pâte de style napolitain cuite au four en pierre, notre mélange spécial sauce à pizza et mozzarella fraîche.",
        p_p1: "Pizza Marguerite",
        desc_b3: "Un classique copieux et rapide ! Rencontre chaude de vos deux protéines choisies dans du pain bazlama croustillant.",
        p_b3: "Toasts Bazlama mélangés",
        desc_b2: "Toast enrichi de la protéine de votre choix accompagnée de fromage fondant.",
        p_b2: "Bazlama protéiné",
        desc_b1: "Pain grillé traditionnel du village turc, croustillant à l'extérieur, rempli de fromage fondant.",
        p_b1: "Toast traditionnel Bazlama",
        desc_o4: "Une omelette géante faite juste pour vous avec deux saveurs de votre choix.",
        p_o4: "Omelette de festin mixte",
        desc_o3: "Omelette garnie avec votre choix de Döner au bœuf, Döner au poulet ou à la saucisse traditionnelle.",
        p_o3: "Omelette Spéciale Protéinée",
        desc_o2: "Omelette fourrée au fromage fondant.",
        p_o2: "Omelette au Fromage",
        desc_o1: "Omelette classique moelleuse cuite soigneusement à la poêle.",
        p_o1: "Omelette traditionnelle à la poêle",
        desc_m4: "La rencontre légendaire de vos deux protéines choisies avec des menemen chauds.",
        p_m4: "Fête mixte Menemen",
        desc_m3: "Base de menemen traditionnelle garnie de votre choix de tranches de bœuf Döner, de poulet Döner ou de saucisses spécialement marinées.",
        p_m3: "Menemen au Bœuf / Saucisse / Poulet",
        desc_m2: "Menemen turcs emblématiques avec du fromage supplémentaire.",
        p_m2: "Menemen au fromage",
        desc_m1: "Petit-déjeuner turc emblématique préparé avec des tomates concassées et du fromage fondant.",
        p_m1: "Menemen Traditionnel",
        cat_food: "Chaud du four",
        cat_drinks: "Boissons et desserts",
        item_pizza: "Pizza cuite sur pierre",
        desc_pizza: "Pâte spécialement fermentée, sauce tomate italienne et fromage mozzarella exquis cuit au four à bois.",
        item_menemen: "Les célèbres Menemen",
        desc_menemen: "Préparé uniquement avec des jaunes d'œufs, beaucoup de cheddar et de beurre, un goût régional légendaire pour le petit-déjeuner.",
        item_toast: "Toasts Bazlama cuits au four",
        desc_toast: "Servi croustillant au four en pierre avec du cheddar et des saucisses/bœuf spéciaux entre le pain du village.",
        item_coffee: "Café turc spécial",
        desc_coffee: "Café Arabica frais de première qualité finement torréfié et moulu, savamment infusé et servi avec les célèbres délices turcs.",
        item_tea: "Thé mélangé aux boutons de rose",
        desc_tea: "Infusé avec un mélange haut de gamme de thé turc et de Ceylan, de bergamote et de boutons de rose séchés.",
        item_lemonade: "Limonade Spéciale Maison",
        desc_lemonade: "Limonade fraîche maison glacée infusée d'hibiscus, de cannelle, d'anis étoilé et de safran persan authentique.",
        item_cake: "Gâteau au chocolat chaud avec sauce au chocolat",
        desc_cake: "Moelleux à l'intérieur, beaucoup de cacao et recouvert d'une sauce au chocolat chaud, un goût indispensable.",
        badge_veg: "Végétarien",
        badge_vegan: "Végétalien",
        badge_gluten: "Contient du gluten",
        badge_dairy: "Contient des produits laitiers",
        title_work_hours: "Jours et heures ouvrables",
        status_now_open: "🟢 Ouvert maintenant",
        status_now_closed: "🔴 Fermé maintenant",
        signature_intro: "Nos saveurs les plus appréciées et soigneusement sélectionnées. Cliquez sur n'importe quel élément pour voir les détails de son menu.",
        signature_loading: "Chargement des saveurs signatures...",
        title_location_yandex: "Emplacement et directions (cartes Yandex)",
        badge_live_traffic: "🔴 Trafic en direct et bâtiments 3D",
        address_full: "<strong>Address:</strong> Şahkulu Mah. Kumbaracı Yokuşu Sok. No:41A, 34421 Beyoğlu/İstanbul (Near Istiklal Street & Galata Tower)",
        btn_yandex_nav: "Navigation Yandex",
        btn_panorama: "Panorama à 360° de la rue Kumbaracı",
        title_social_media: "Qu'est-ce qui est populaire sur les réseaux sociaux ?",
        badge_tour_videos: "🎬 Vidéos de visite et de préparation",
        title_amenities: "Caractéristiques et commodités du site",
        amenity_pet: "🐾 Animaux acceptés",
        amenity_halal: "🕌 Nourriture 100% Halal",
        amenity_wifi: "📶 Wi-Fi haut débit gratuit",
        amenity_oven: "🍕 Four traditionnel en pierre",
        amenity_historic: "🏛️ Ambiance historique de 150 ans",
        amenity_nfc: "💳 Paiement sans contact / NFC",
        amenity_veg: "🌿 Options végétariennes",
        amenity_gluten: "🌾 Options sans gluten/saines",
        amenity_family: "👶 Adapté aux familles et aux enfants",
        amenity_tea: "☕ Thé spécial mélange de boutons de rose",
        google_review_desc: "Consultez tous les vrais avis et notes des clients directement sur Google.",
        yandex_review_desc: "Affichez l'emplacement et examinez les enregistrements sur Yandex Maps.",
        badge_satisfaction: "Satisfaction client",
        title_social: "Responsabilité Sociale",
        social_intro: "En tant que Fırınna Café, nous partageons nos revenus et notre amour avec notre quartier.",
        social_student_title: "Projet étudiant à Beyoğlu",
        social_student_desc: "Nous soutenons les étudiants universitaires de Beyoğlu avec des repas gratuits.",
        social_animal_title: "Animaux de la rue respectueux",
        social_animal_desc: "Nous fournissons chaque jour de la nourriture et de l’eau à nos amis à quatre pattes dans notre rue.",
        search_placeholder: "🔍 Recherchez dans le menu...",
        filter_all: "✨ Tous les menus",
        filter_halal: "☪️ 100% Halal",
        filter_veggie: "🌿 Végétarien",
        filter_glutenfree: "🌾 Sans gluten",
        filter_signature: "⭐Signature",
        badge_stone_oven: "🍕 Four en pierre",
        title_pizza_napo: "Pizza napolitaine",
        badge_famous: "🍳 Célèbre",
        title_menemen_cakal: "Menemen",
        badge_traditional: "☕ Traditionnel",
        title_coffee: "Café Turc",
        whatsapp_manager: "Gestionnaire WhatsApp",
        btn_send_msg2: "Envoyer un message",
        filter_dairyfree: "🚫 Sans produits laitiers",
        cat_1: "Menemen",
        cat_2: "Toasts",
        cat_3: "Pizzas",
        cat_4: "Boissons Chaudes & Froides",
        cat_5: "Desserts",
        cat_6: "boissons froides",
        cat_7: "Doux",
        tag_vegan: "Végétalien",
        tag_gluten: "Gluten",
        tag_gluten_free: "sans gluten",
        tag_halal: "halal",
        tag_dairy: "Produit laitier",
        tag_vegetarian: "Végétarien",
    },
    fa: {
        category: "کافه و رستوران",
        status_open: "اکنون باز است (08:00 - 23:00)",
        btn_menu: "📖 مشاهده منوی دیجیتال",
        btn_gezi: "🗺️ راهنمای سفر و مسیر استانبول",
        btn_reserve: "یک میز رزرو کنید",
        btn_message: "برای ما پیام ارسال کنید",
        title_about: "درباره ما",
        slogan_about: "طعم های سنتی، دستور العمل های منحصر به فرد فقط در FIRINNA",
        text_about: "مهمان عزیز، به FIRINNA خوش آمدید.\n\nدر فضای تاریخی 150 ساله گالاتا، درست بر روی کومباراجی یوکوشو آرام، کافه و رستوران Fırınna یک بهشت آشپزی ویژه است که در آن می توانید از شلوغی خیابان استقلال فاصله بگیرید و با موادی با طراوت و با طراوت انتخاب کنید. غذاهای تخصصی، انواع قهوه غنی، و دسرهای خانگی، دستور العمل های سنتی را با تغییرات مدرن زنده می کنیم.\n\nاینجا عجله ای وجود ندارد! با تیم دوستانه، مهمان نواز و دوستدار حیوانات خانگی ما، از گفتگوهای گرم و لحظات آرام در فضای ساختمان تاریخی 150 ساله ما لذت ببرید. خوشحال می شویم که خاطره ای شیرین از سفر تاریخی شما به استانبول باشیم.",
        title_top_reviews: "از مشتریان ما",
        title_gating: "تجربه خود را ارزیابی کنید",
        sub_gating: "تجربه شما در فیرینا چگونه بود؟ نظرات شما برای ما بسیار مهم است.",
        gating_high_msg: "🎉 فوق العاده! خوشحالیم که از آن لذت بردید. آیا می خواهید با بررسی 5 ستاره در این پلتفرم ها از ما حمایت کنید؟",
        gating_low_title: "بازخورد شما برای ما بسیار ارزشمند است!",
        gating_low_msg: "شما می توانید هر گونه بازخورد یا مشکلی را مستقیماً برای مدیر ما ارسال کنید:",
        btn_google_review: "رتبه 5 ستاره در گوگل",
        btn_yandex_review: "نرخ در Yandex",
        btn_tripadvisor_review: "بررسی در تریپ ادوایزر",
        google_perfect: "عالی در گوگل",
        yandex_perfect: "عالی در Yandex",
        btn_inspect: "بررسی کنید",
        btn_see_all_google_photos: "مشاهده همه عکس‌ها در Google Maps (100+)",
        table_available: "در حال حاضر {N} جدول موجود است، خوش آمدید!",
        table_full: "در حال حاضر تمام میزها اشغال شده است.",
        table_offline: "وضعیت جدول در دسترس نیست.",
        text_group_events: "<strong>Group & Private Events:</strong> For after-hours group bookings and mini events, please <a href='https://wa.me/905456301214?text=Hello,%20I%20would%20like%20information%20about%20group%20bookings.' target='_blank' style='color:#059669; font-weight:700; text-decoration:underline;'>Contact via WhatsApp</a>.",
        review_1: "مکانی شگفت انگیز و تاریخی برای فرار از هیاهوی استقلال و نفس کشیدن. پیتزاهایشان افسانه ای است!",
        review_2: "شما باید منمن چاکالی را امتحان کنید. کارکنان بسیار خندان هستند و بسیار خوب است که آنها حیوانات خانگی دوست هستند.",
        review_3: "بهترین نقطه در گالاتا برای قهوه و دسر. پرسنل بسیار مراقب هستند.",
        title_virtual_tour: "تور مجازی (360 درجه)",
        text_virtual_tour: "ساختمان تاریخی 150 ساله ما را درست از همان جایی که نشسته اید کاوش کنید.",
        title_faq: "سوالات متداول",
        faq_q1: "🐾 آیا حیوانات خانگی مجاز هستند؟",
        faq_a1: "بله! Fırınna 100٪ حیوان خانگی دوست است. خوش آمدید از وقت خود با دوستان پشمالوی خود در باغچه بیرونی و صندلی های داخلی ما لذت ببرید.",
        faq_q2: "💳 چه روش های پرداختی را می پذیرید؟",
        faq_a2: "ما همه کارت‌های اعتباری اصلی، کارت‌های نقدی، پرداخت‌های تلفن همراه بدون تماس (Apple Pay / Google Pay) و پول نقد را می‌پذیریم.",
        faq_q3: "🥗 آیا گزینه های گیاهخواری یا بدون گلوتن دارید؟",
        faq_a3: "بله! منوی ما پیتزاهای گیاهی لذیذ در اجاق سنگی، پخش‌کننده‌های صبحانه غنی، و جایگزین‌های بدون گلوتن/وگان را ارائه می‌دهد.",
        faq_q4: "🕒 آیا می توانیم رزرو گروهی یا رویدادهای خصوصی انجام دهیم؟",
        faq_a4: "بله! برای تولدها، جلسات شرکتی یا رویدادهای کوچک خصوصی، مستقیماً از طریق واتس اپ با ما تماس بگیرید.",
        title_location: "مکان",
        title_contact: "تماس و مکان",
        title_gallery: "محیط و طعم",
        gal_title_interior: "فضای داخلی و محیط",
        gal_title_exterior: "فضای باز و خیابان کومباراجی",
        gal_title_signature: "سلیقه امضای ما",
        gal_lbl_interior_history: "داخلی تاریخی",
        gal_lbl_warm_tables: "صندلی دنج",
        gal_lbl_details: "جزئیات محل برگزاری",
        gal_lbl_street: "خیابان کومباراچی",
        gal_lbl_outdoor_seating: "نشستن در فضای باز",
        gal_lbl_historic_building: "بنای تاریخی",
        gal_lbl_fresh_tea: "چای ترکی تازه",
        gal_lbl_turkish_coffee: "قهوه ترک",
        gal_lbl_menemen: "منمن تابه ای",
        gal_lbl_pizza: "پیتزا تنوری",
        gal_lbl_lemonade: "لیموناد خانگی",
        gal_lbl_glintwein: "شراب مولد",
        badge_historic_tr: "کافه تاریخی ترکیه",
        badge_halal: "100% حلال",
        badge_quality: "بهترین کیفیت",
        badge_price: "قیمت منصفانه",
        title_reviews: "مکان و بررسی های اخیر",
        btn_google: "بررسی های اخیر گوگل را بخوانید",
        btn_yandex: "مشاهده در نقشه های Yandex",
        btn_baidu: "مشاهده در نقشه های Baidu",
        modal_res_title: "رزرو میز",
        label_name: "نام کامل",
        label_phone: "شماره تلفن",
        label_date: "تاریخ",
        label_time: "زمان (08:00 الی 23:00)",
        label_guests: "تعداد مهمانان",
        label_note: "درخواست ویژه / توجه (اختیاری)",
        btn_submit: "ارسال درخواست",
        modal_msg_title: "برای ما پیام ارسال کنید",
        label_message: "پیام شما",
        btn_submit_msg: "ارسال پیام",
        footer_rights: "تمامی حقوق محفوظ است.",
        menu_header_title: "طعم های ویژه",
        menu_header_sub: "با لمس فیرینا...",
        menu_back: "خانه",
        menu_intro: "می توانید از فروشگاه ما دیدن کنید یا اطلاعات دقیقی را از کارکنان ما برای همه گزینه های منو دریافت کنید. در زیر می توانید محبوب ترین طعم های امضای ما را مرور کنید.",
        menu_download: "دانلود منوی قیمت دار (PDF)",
        desc_t1: "کیک شکلاتی داغ تازه از فر با بستنی معروف Maraş، سس شکلات و کمی نارگیل روی آن قرار داده شده است.",
        p_t1: "کیک شکلاتی داغ",
        desc_c3: "معجون مخصوص با طراوت که با ترکیب بی نظیر دارچین، ترش و زعفران ایرانی روی پایه لیموناد یخی تهیه شده است.",
        p_c3: "لیموناد زعفرانی هیبیسکوس",
        desc_c2: "آب معدنی طبیعی.",
        p_c2: "آب معدنی",
        desc_c1: "آب گوارا.",
        p_c1: "آب",
        desc_s5: "کلاسیک ایتالیایی با فوم شیر.",
        p_s5: "کاپوچینو",
        desc_s4: "اسپرسو با شیر فراوان.",
        p_s4: "لاته",
        desc_s3: "قهوه قوی از دانه های تازه آسیاب شده.",
        p_s3: "آمریکانو",
        desc_s2: "قهوه ترکی سنتی، آهسته پخته، بسیار کف آلود، با لذیذ ترکی سرو می شود.",
        p_s2: "قهوه ترک",
        desc_s1: "ترکیبی خاص از برگ‌های چای با دقت انتخاب شده با طعم ترنج و نرم شده با گلبرگ‌های گل رز خشک.",
        p_s1: "چای ترکیبی ویژه",
        desc_p3: "پیتزای جشنواره باشکوه با دونر گوشت گاو، دونر مرغ، سوسیس و مقدار زیادی موزارلا پخته شده است.",
        p_p3: "پیتزای فست ترکیبی کامل",
        desc_p2: "طعم خاص شما روی پایه مارگریتا: دونر گوشت گاو مخصوص ترشی شده، دونر مرغ یا سوسیس.",
        p_p2: "پیتزای پروتئینی",
        desc_p1: "خمیر سبک ناپلی واقعی پخته شده در اجاق سنگی، مخلوط مخصوص سس پیتزا و موزارلای تازه.",
        p_p1: "پیتزا مارگریتا",
        desc_b3: "یک کلاسیک دلچسب و سریع! ملاقات داغ دو پروتئین انتخابی شما در نان بازلامای ترد.",
        p_b3: "تست بازلاما مخلوط",
        desc_b2: "نان تست غنی شده با پروتئین انتخابی شما همراه با ذوب پنیر.",
        p_b2: "بازلاما با گوشت",
        desc_b1: "نان تست سنتی روستایی ترک، بیرونی ترد، پر از پنیر در حال ذوب شدن.",
        p_b1: "تست بازلاما سنتی",
        desc_o4: "املت بزرگی که فقط برای شما با دو طعم دلخواه درست شده است.",
        p_o4: "املت جشن مخلوط",
        desc_o3: "املت را با گوشت گاو دونر، مرغ دونر یا سوسیس سنتی انتخاب کنید.",
        p_o3: "املت پروتئینی ویژه",
        desc_o2: "املت پر شده با پنیر در حال ذوب.",
        p_o2: "املت با پنیر",
        desc_o1: "املت کلاسیک نرم با دقت در تابه پخته شده است.",
        p_o1: "املت تابه ای سنتی",
        desc_m4: "ملاقات افسانه ای دو پروتئین منتخب شما با منمن داغ.",
        p_m4: "منمن مخلوط",
        desc_m3: "پایه منمن سنتی با انتخاب شما از گوشت گاو، دونر مرغ، یا سوسیس ترشی شده خاص.",
        p_m3: "منمن با گوشت/مرغ",
        desc_m2: "منمن ترکی نمادین با پنیر اضافی.",
        p_m2: "منمن با پنیر",
        desc_m1: "صبحانه نمادین ترکی تهیه شده با گوجه فرنگی له شده و پنیر آب شده. (سبک چاکالی)",
        p_m1: "منمن سنتی",
        cat_food: "داغ از فر",
        cat_drinks: "نوشیدنی و دسر",
        item_pizza: "پیتزای سنگی",
        desc_pizza: "خمیر مخصوص تخمیر شده، سس گوجه فرنگی ایتالیایی و پنیر موزارلای نفیس پخته شده در اجاق هیزمی.",
        item_menemen: "منمن معروف",
        desc_menemen: "فقط با زرده تخم مرغ، مقدار زیادی چدار و کره، یک طعم افسانه ای صبحانه منطقه ای تهیه می شود.",
        item_toast: "تست بازلاما تنوری",
        desc_toast: "در فر سنگی با پنیر چدار و سوسیس و گوشت گاو مخصوص بین نان روستایی سرو می شود.",
        item_coffee: "قهوه ترک مخصوص",
        desc_coffee: "قهوه عربیکا تازه درجه یک ریز برشته و آسیاب شده، ماهرانه دم شده و با لذیذ معروف ترکی سرو می شود.",
        item_tea: "چای مخلوط گل رز",
        desc_tea: "دم کرده با ترکیبی عالی از چای ترکی و سیلان، ترنج و غنچه های رز خشک.",
        item_lemonade: "لیموناد خانگی مخصوص",
        desc_lemonade: "لیموناد تازه خانگی یخی دم کرده با هبیسکوس، دارچین، بادیان ستاره ای و زعفران اصیل ایرانی.",
        item_cake: "کیک شکلاتی داغ با سس شکلاتی",
        desc_cake: "در داخل نرم، مقدار زیادی کاکائو، و پوشیده از سس شکلات داغ، طعمی ضروری است.",
        badge_veg: "گیاهخواری",
        badge_vegan: "وگان",
        badge_gluten: "حاوی گلوتن",
        badge_dairy: "حاوی لبنیات",
        title_work_hours: "روزها و ساعات کاری",
        status_now_open: "🢢 اکنون باز کنید",
        status_now_closed: "🔴 هم اکنون بسته است",
        signature_intro: "دوست داشتنی ترین طعم های ما که با دقت انتخاب شده اند. روی هر مورد کلیک کنید تا جزئیات منوی آن را ببینید.",
        signature_loading: "در حال بارگیری طعم های امضا...",
        title_location_yandex: "مکان و مسیرها (نقشه های Yandex)",
        badge_live_traffic: "🔴 ترافیک زنده و ساختمان های سه بعدی",
        address_full: "<strong>Address:</strong> Şahkulu Mah. Kumbaracı Yokuşu Sok. No:41A, 34421 Beyoğlu/İstanbul (Near Istiklal Street & Galata Tower)",
        btn_yandex_nav: "ناوبری Yandex",
        btn_panorama: "پانورامای 360 درجه خیابان Kumbaracı",
        title_social_media: "چه چیزی در رسانه های اجتماعی محبوب است؟",
        badge_tour_videos: "🎬 فیلم های تور و آماده سازی",
        title_amenities: "ویژگی ها و امکانات محل برگزاری",
        amenity_pet: "🐾 دوستدار حیوانات خانگی",
        amenity_halal: "🕌 غذای 100% حلال",
        amenity_wifi: "📶 وای فای پرسرعت رایگان",
        amenity_oven: "🍕 اجاق سنگی سنتی",
        amenity_historic: "🏛️ جو تاریخی 150 ساله",
        amenity_nfc: "💳 پرداخت بدون تماس / NFC",
        amenity_veg: "🌿 گزینه های گیاهخواری",
        amenity_gluten: "🌾 گزینه های بدون گلوتن / سالم",
        amenity_family: "👶 خانواده و کودک دوستانه",
        amenity_tea: "☕ چای مخلوط گل سرخ مخصوص",
        google_review_desc: "تمام نظرات و رتبه‌بندی‌های مهمان واقعی را مستقیماً در Google مشاهده کنید.",
        yandex_review_desc: "مشاهده مکان و بررسی سوابق در نقشه های Yandex.",
        badge_satisfaction: "رضایت مشتری",
        title_social: "مسئولیت اجتماعی",
        social_intro: "ما به عنوان کافه Fırınna، درآمد و عشق خود را با محله خود به اشتراک می گذاریم.",
        social_student_title: "پروژه دانشجویی در بی اوغلو",
        social_student_desc: "ما از دانشجویان دانشگاه بی اوغلو با وعده های غذایی رایگان حمایت می کنیم.",
        social_animal_title: "دوستدار حیوانات خیابانی",
        social_animal_desc: "ما هر روز برای دوستان پشمالوی خود در خیابان خود غذا و آب تهیه می کنیم.",
        search_placeholder: "🔍 جستجو در منو...",
        filter_all: "✨ منوی همه",
        filter_halal: "☪️ 100% حلال",
        filter_veggie: "🌿 گیاهخواری",
        filter_glutenfree: "🌾 بدون گلوتن",
        filter_signature: "⭐ امضاء",
        badge_stone_oven: "🍕 فر سنگی",
        title_pizza_napo: "پیتزا ناپل",
        badge_famous: "🍳 مشهور",
        title_menemen_cakal: "منمن",
        badge_traditional: "☕ سنتی",
        title_coffee: "قهوه ترک",
        whatsapp_manager: "مدیر WhatsApp",
        btn_send_msg2: "ارسال پیام",
        filter_dairyfree: "🚫 بدون لبنیات",
        cat_1: "منمن",
        cat_2: "تست",
        cat_3: "پیتزا",
        cat_4: "نوشیدنی های گرم و سرد",
        cat_5: "دسرها",
        cat_6: "نوشیدنی های سرد",
        cat_7: "شیرین",
        tag_vegan: "وگان",
        tag_gluten: "گلوتن",
        tag_gluten_free: "بدون گلوتن",
        tag_halal: "حلال",
        tag_dairy: "محصولات لبنی",
        tag_vegetarian: "گیاهخواری",
    },
    it: {
        category: "Cafe & Restaurant",
        status_open: "Open Now (08:00 - 23:00)",
        btn_menu: "📖 Menu Digitale",
        btn_gezi: "🗺️ Istanbul Travel Guide & Route",
        btn_reserve: "Book a Table",
        btn_message: "Send us a Message",
        title_about: "Chi Siamo",
        slogan_about: "TRADITIONAL FLAVORS, UNIQUE RECIPES ONLY AT FIRINNA",
        text_about: "DEAR GUEST, WELCOME TO FIRINNA.\n\nLocated in the 150-year-old historic atmosphere of Galata, right on the peaceful Kumbaracı Yokuşu, Fırınna Cafe & Restaurant is a special culinary haven where you can step away from the bustle of Istiklal Street and take a refreshing breath.\n\nWith carefully selected ingredients, fresh oven-baked specialties, rich coffee varieties, and homemade desserts, we bring traditional recipes to life with modern touches.\n\nThere is no rush here! With our friendly, hospitable, and pet-friendly team, enjoy warm conversations and peaceful moments in the ambiance of our 150-year-old historic building. We would be delighted to be a sweet memory of your historic trip to Istanbul.",
        title_top_reviews: "Dai nostri clienti",
        title_gating: "Valuta la tua esperienza",
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
        review_2: "You must try the menemen. The staff is very smiling and it's great that they are pet-friendly.",
        review_3: "The best spot in Galata for coffee and desserts. The staff is very attentive.",
        title_virtual_tour: "Tour Virtuale (360°)",
        text_virtual_tour: "Explore our 150-year-old historic building right from where you sit.",
        title_faq: "Domande Frequenti",
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
        gal_lbl_turkish_coffee: "Caffè Turco",
        gal_lbl_menemen: "Skillet Menemen",
        gal_lbl_pizza: "Pizza al Forno a Legna",
        gal_lbl_lemonade: "Limonata Fatta in Casa",
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
        menu_header_title: "Le Nostre Specialità",
        menu_header_sub: "With Firinna's Touch...",
        menu_back: "Home",
        menu_intro: "You can visit our store or get detailed information from our staff for all menu options. Below you can review our most loved signature tastes.",
        menu_download: "Scarica il menu con i prezzi (PDF)",
        desc_t1: "Torta al cioccolato caldo appena sfornata condita con il famoso gelato Maraş, salsa al cioccolato e un tocco di cocco.",
        p_t1: "Torta al cioccolato calda",
        desc_c3: "Una pozione speciale rinfrescante preparata con la combinazione unica di cannella, ibisco e zafferano iraniano su una base di limonata ghiacciata.",
        p_c3: "Limonata allo zafferano e ibisco",
        desc_c2: "Acqua minerale naturale.",
        p_c2: "Acqua Minerale",
        desc_c1: "Refreshing water.",
        p_c1: "Acqua",
        desc_s5: "Classico italiano con schiuma di latte.",
        p_s5: "Cappuccino",
        desc_s4: "Espresso con abbondante latte.",
        p_s4: "Latte macchiato",
        desc_s3: "Caffè forte ottenuto da chicchi appena macinati.",
        p_s3: "Americano",
        desc_s2: "Caffè turco tradizionale, cotto a fuoco lento, molto schiumoso, servito con delizie turche.",
        p_s2: "Caffè Turco",
        desc_s1: "Una speciale miscela di foglie di tè accuratamente selezionate aromatizzate al bergamotto e ammorbidite con petali di rosa essiccati.",
        p_s1: "Miscela speciale di tè",
        desc_p3: "Magnifica pizza da festival cotta con döner di manzo, döner di pollo, salsiccia e abbondante mozzarella.",
        p_p3: "Pizza Completa Mista Da Festa",
        desc_p2: "Il tuo gusto speciale su base Margherita: Döner speciale di manzo marinato, Döner di pollo o salsiccia.",
        p_p2: "Pizza Proteica",
        desc_p1: "Vero impasto alla napoletana cotto nel forno a pietra, il nostro speciale mix di salsa per pizza e mozzarella fresca.",
        p_p1: "Pizza Margherita",
        desc_b3: "Un classico sostanzioso e veloce! Caldo incontro delle due proteine ​​scelte nel croccante pane bazlama.",
        p_b3: "Pane tostato misto di Bazlama",
        desc_b2: "Toast arricchito con le proteine ​​scelte insieme al formaggio fuso.",
        p_b2: "Base proteica",
        desc_b1: "Pane tostato tradizionale turco del villaggio, croccante all'esterno, ripieno di formaggio fuso.",
        p_b1: "Toast tradizionale di Bazlama",
        desc_o4: "Una frittata in porzione gigante fatta apposta per te con due gusti a tua scelta.",
        p_o4: "Frittata Mista",
        desc_o3: "Frittata farcita con Döner di manzo, Döner di pollo o salsiccia tradizionale a tua scelta.",
        p_o3: "Frittata Proteica Speciale",
        desc_o2: "Frittata ripiena di formaggio fuso.",
        p_o2: "Frittata con formaggio",
        desc_o1: "Morbida frittata classica cotta con cura in padella.",
        p_o1: "Frittata Tradizionale In Pan",
        desc_m4: "Il leggendario incontro delle tue due proteine ​​scelte con menemen caldi.",
        p_m4: "Menemen della festa mista",
        desc_m3: "Base menemen tradizionale condita con la vostra scelta di Döner di manzo, Döner di pollo o salsiccia a fette appositamente marinati.",
        p_m3: "Menemen con Manzo/Salsiccia/Pollo",
        desc_m2: "Iconici menemen turchi con formaggio extra.",
        p_m2: "Menemen con formaggio",
        desc_m1: "Iconica colazione turca preparata con pomodori schiacciati e formaggio fuso.",
        p_m1: "Menemen Tradizionale",
        cat_food: "Caldo dal forno",
        cat_drinks: "Bevande e dessert",
        item_pizza: "Pizza cotta su pietra",
        desc_pizza: "Impasto appositamente fermentato, salsa di pomodoro italiana e squisita mozzarella cotta nel forno a legna.",
        item_menemen: "Menemen famosi",
        desc_menemen: "Preparato solo con tuorli d'uovo, abbondante cheddar e burro, un leggendario gusto regionale per la colazione.",
        item_toast: "Toast Bazlama al forno",
        desc_toast: "Servito croccante dal forno in pietra con formaggio cheddar e salsiccia/manzo speciale tra pane del villaggio.",
        item_coffee: "Caffè turco speciale",
        desc_coffee: "Caffè Arabica fresco di prima qualità finemente tostato e macinato, preparato con perizia e servito con la famosa delizia turca.",
        item_tea: "Tè miscelato ai boccioli di rosa",
        desc_tea: "Prodotta con una miscela premium di tè turco e di Ceylon, bergamotto e boccioli di rosa essiccati.",
        item_lemonade: "Limonata speciale fatta in casa",
        desc_lemonade: "Limonata fresca fatta in casa ghiacciata, infusa con ibisco, cannella, anice stellato e autentico zafferano persiano.",
        item_cake: "Torta Calda Al Cioccolato Con Salsa Al Cioccolato",
        desc_cake: "Morbidi dentro, tanto cacao, e ricoperti con salsa di cioccolata calda, un gusto irrinunciabile.",
        badge_veg: "Vegetarian",
        badge_vegan: "Vegan",
        badge_gluten: "Contains Gluten",
        badge_dairy: "Contains Dairy",
        title_work_hours: "Working Days & Hours",
        status_now_open: "🟢 Open Now",
        status_now_closed: "🔴 Closed Now",
        signature_intro: "Our most loved, carefully selected flavors. Click on any item to see its menu details.",
        signature_loading: "Loading signature flavors...",
        title_location_yandex: "Location & Directions (Yandex Maps)",
        badge_live_traffic: "🔴 Live Traffic & 3D Buildings",
        address_full: "<strong>Address:</strong> Şahkulu Mah. Kumbaracı Yokuşu Sok. No:41A, 34421 Beyoğlu/İstanbul (Near Istiklal Street & Galata Tower)",
        btn_yandex_nav: "Yandex Navigation",
        btn_panorama: "360° Kumbaracı Street Panorama",
        title_social_media: "What's Popular on Social Media?",
        badge_tour_videos: "🎬 Tour & Preparation Videos",
        title_amenities: "Venue Features & Amenities",
        amenity_pet: "🐾 Pet-Friendly",
        amenity_halal: "🕌 100% Halal Food",
        amenity_wifi: "📶 Free High-Speed Wi-Fi",
        amenity_oven: "🍕 Traditional Stone Oven",
        amenity_historic: "🏛️ 150-Year Historic Atmosphere",
        amenity_nfc: "💳 Contactless / NFC Payment",
        amenity_veg: "🌿 Vegetarian Options",
        amenity_gluten: "🌾 Gluten-Free / Healthy Options",
        amenity_family: "👶 Family & Child Friendly",
        amenity_tea: "☕ Special Rosebud Blend Tea",
        google_review_desc: "View all real guest reviews and ratings directly on Google.",
        yandex_review_desc: "View location and review records on Yandex Maps.",
        badge_satisfaction: "Customer Satisfaction",
        title_social: "Responsabilità Sociale",
        social_intro: "As Fırınna Cafe, we share our earnings and love with our neighborhood.",
        social_student_title: "Student Project in Beyoğlu",
        social_student_desc: "We support university students in Beyoğlu with free meals.",
        social_animal_title: "Street Animals Friendly",
        social_animal_desc: "We provide food and water for our furry friends on our street every day.",
        search_placeholder: "🔍 Search the menu...",
        filter_all: "✨ All Menu",
        filter_halal: "☪️ 100% Halal",
        filter_veggie: "🌿 Vegetarian",
        filter_glutenfree: "🌾 Gluten-Free",
        filter_signature: "⭐ Signature",
        badge_stone_oven: "🍕 Stone Oven",
        title_pizza_napo: "Neapolitan Pizza",
        badge_famous: "🍳 Famous",
        title_menemen_cakal: "Menemen",
        badge_traditional: "☕ Traditional",
        title_coffee: "Caffè Turco",
        whatsapp_manager: "WhatsApp Manager",
        btn_send_msg2: "Send Message",
        filter_dairyfree: "🚫 Dairy-Free",
        cat_1: "Menemen",
        cat_2: "Toast",
        cat_3: "Pizze",
        cat_4: "Bevande Calde e Fredde",
        cat_5: "Dolci",
        cat_6: "bevande fredde",
        cat_7: "Dolce",
        tag_vegan: "Vegano",
        tag_gluten: "Glutine",
        tag_gluten_free: "senza glutine",
        tag_halal: "halal",
        tag_dairy: "Prodotto lattiero-caseario",
        tag_vegetarian: "Vegetariano",
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
    zh: { "Pazartesi": "星期一", "Salı": "星期二", "Çarşamba": "星期三", "Perşembe": "星期四", "Cuma": "星期五", "Cumartesi": "星期六", "Pazar": "星期日" },
    uk: { "Pazartesi": "Понеділок", "Salı": "Вівторок", "Çarşamba": "Середа", "Perşembe": "Четвер", "Cuma": "П'ятниця", "Cumartesi": "Субота", "Pazar": "Неділя" },
    de: { "Pazartesi": "Montag", "Salı": "Dienstag", "Çarşamba": "Mittwoch", "Perşembe": "Donnerstag", "Cuma": "Freitag", "Cumartesi": "Samstag", "Pazar": "Sonntag" },
    fr: { "Pazartesi": "Lundi", "Salı": "Mardi", "Çarşamba": "Mercredi", "Perşembe": "Jeudi", "Cuma": "Vendredi", "Cumartesi": "Samedi", "Pazar": "Dimanche" },
    fa: { "Pazartesi": "دوشنبه", "Salı": "سه‌شنبه", "Çarşamba": "چهارشنبه", "Perşembe": "پنج‌شنبه", "Cuma": "جمعه", "Cumartesi": "شنبه", "Pazar": "یک‌شنبه" },
    it: { "Pazartesi": "Lunedì", "Salı": "Martedì", "Çarşamba": "Mercoledì", "Perşembe": "Giovedì", "Cuma": "Venerdì", "Cumartesi": "Sabato", "Pazar": "Domenica" }
};

const STATUS_I18N = {
    tr: { today: "(Bugün)", today_closed: "(Bugün - Kapalı)", closed: "Kapalı" },
    en: { today: "(Today)", today_closed: "(Today - Closed)", closed: "Closed" },
    es: { today: "(Hoy)", today_closed: "(Hoy - Cerrado)", closed: "Cerrado" },
    ru: { today: "(Сегодня)", today_closed: "(Сегодня - Закрыто)", closed: "Закрыто" },
    ar: { today: "(اليوم)", today_closed: "(اليوم - مغلق)", closed: "مغلق" },
    zh: { today: "(今天)", today_closed: "(今天 - 已关闭)", closed: "已关闭" },
    uk: { today: "(Сьогодні)", today_closed: "(Сьогодні - Зачинено)", closed: "Зачинено" },
    de: { today: "(Heute)", today_closed: "(Heute - Geschlossen)", closed: "Geschlossen" },
    fr: { today: "(Aujourd'hui)", today_closed: "(Aujourd'hui - Fermé)", closed: "Fermé" },
    fa: { today: "(امروز)", today_closed: "(امروز - بسته)", closed: "بسته" },
    it: { today: "(Oggi)", today_closed: "(Oggi - Chiuso)", closed: "Chiuso" }
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
            headerBadge.innerHTML = (i18n[currentLang] && i18n[currentLang].status_now_open) || '🟢 Şu An Açık';
        } else {
            headerBadge.style.background = '#fef2f2';
            headerBadge.style.color = '#991b1b';
            headerBadge.style.borderColor = '#fca5a5';
            headerBadge.innerHTML = (i18n[currentLang] && i18n[currentLang].status_now_closed) || '🔴 Şu An Kapalı';
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
    const placeholders = document.querySelectorAll('[data-i18n-placeholder]');
    placeholders.forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (i18n[lang] && i18n[lang][key]) {
            el.placeholder = i18n[lang][key];
        }
    });

    if (lang === 'ar') {
        document.body.style.direction = 'rtl';
    } else {
        document.body.style.direction = 'ltr';
    }
    
    document.querySelectorAll('.lang-selector button').forEach(btn => {
        if(btn.getAttribute('data-lang') === lang) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Update PDF download link if present
    const pdfLink = document.getElementById('pdf-download-link');
    if (pdfLink) {
        
    const availablePdfs = ["tr", "en", "ru", "ar", "zh"];
    const pdfLang = availablePdfs.includes(lang) ? lang : "en";
    pdfLink.href = `menu_${pdfLang}.pdf`;
    
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
        const res = await fetch('yeni_menu.json');
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
    const gallery = document.getElementById('signature-gallery');
    if (!gallery || !dynamicWebProducts) return;

    let allProducts = [];
    if (Array.isArray(dynamicWebProducts)) {
        if (dynamicWebProducts.length > 0 && dynamicWebProducts[0].products) {
            // Grouped format
            dynamicWebProducts.forEach(cat => {
                if (cat.products) allProducts.push(...cat.products);
            });
        } else {
            allProducts = dynamicWebProducts;
        }
    }

    const signatures = allProducts.filter(p => p.is_signature || p.title.toLowerCase().includes('menemen') || p.title.toLowerCase().includes('pizza'));
    // Select top 6
    const topSigs = signatures.slice(0, 6);

    let html = '';
    topSigs.forEach(p => {
        const rawImg = p.image_url || p.image || '';
        const img = (typeof rawImg === 'string' && rawImg.length > 0) ? rawImg : 'food_placeholder.jpg';
        
        html += `
            <div class="gallery-item" onclick="window.location.href='menu.html?product=${p.id}'" style="cursor:pointer;">
                <img src="${img}" alt="${p.title}" loading="lazy">
                <div class="gallery-overlay">
                    <span class="gallery-title" data-i18n="p_${p.id}">${p.title}</span>
                </div>
            </div>
        `;
    });

    gallery.innerHTML = html;
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
        } else if (activeDietaryFilter === 'dairyfree') {
            const hasDairy = text.includes('peynir') || text.includes('kaşar') || text.includes('süt') || text.includes('tereyağ') || text.includes('krema') || text.includes('yoğurt') || text.includes('mozzarella') || text.includes('dairy');
            matchesDiet = !hasDairy;
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

