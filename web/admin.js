document.addEventListener('DOMContentLoaded', () => {
    fetchSettings();
    document.getElementById('settingsForm').addEventListener('submit', saveSettings);
    
    // Manual Status Toggle Events
    document.querySelectorAll('input[name="manual_status"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if(e.target.value === 'closed') {
                document.getElementById('closed_until_div').style.display = 'block';
                document.getElementById('closed_until').required = true;
            } else {
                document.getElementById('closed_until_div').style.display = 'none';
                document.getElementById('closed_until').required = false;
            }
        });
    });
    
    // Sekme (Tab) Değiştirme Mantığı
    const navItems = document.querySelectorAll('.nav-item[data-target]');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            // Aktif sınıfını güncelle
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            // Tüm bölümleri gizle
            document.querySelectorAll('.admin-section').forEach(sec => sec.style.display = 'none');
            
            // Seçilen bölümü göster
            const targetId = item.getAttribute('data-target');
            document.getElementById(targetId).style.display = 'block';
            
            // Üst başlığı güncelle
            document.querySelector('.topbar h1').innerText = item.innerText.trim();
        });
    });
});

// Ayarları API'den Çek
async function fetchSettings() {
    try {
        const res = await fetch('/api/web/settings');
        const data = await res.json();
        
        if (data.work_hours) {
            const parts = data.work_hours.split('-');
            if(parts.length === 2) {
                document.getElementById('work_hours_start').value = parts[0].trim();
                document.getElementById('work_hours_end').value = parts[1].trim();
            }
        }
        if (data.address) document.getElementById('address').value = data.address;
        if (data.phone) document.getElementById('phone').value = data.phone;
        if (data.instagram) document.getElementById('instagram').value = data.instagram;
        
        if (data.manual_status) {
            document.querySelector(`input[name="manual_status"][value="${data.manual_status}"]`).checked = true;
            if(data.manual_status === 'closed') {
                document.getElementById('closed_until_div').style.display = 'block';
            }
        }
        if (data.closed_until) {
            document.getElementById('closed_until').value = data.closed_until;
        }
    } catch (e) {
        console.error("Ayarlar yüklenemedi", e);
    }
}

// Ayarları API'ye Kaydet
async function saveSettings(e) {
    e.preventDefault();
    
    // Yalnızca ekrandaki değerleri okuyup gönderirsek diğer mevcut ayarları silebiliriz (örn: baidu).
    // O yüzden önce eskileri alıp üzerlerine yazalım.
    try {
        const res = await fetch('/api/web/settings');
        const existingData = await res.json();
        
        const startH = document.getElementById('work_hours_start').value;
        const endH = document.getElementById('work_hours_end').value;
        
        const payload = {
            ...existingData,
            work_hours: `${startH} - ${endH}`,
            address: document.getElementById('address').value,
            phone: document.getElementById('phone').value,
            instagram: document.getElementById('instagram').value,
            manual_status: document.querySelector('input[name="manual_status"]:checked').value,
            closed_until: document.getElementById('closed_until').value
        };
        
        const saveRes = await fetch('/api/web/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        if (saveRes.ok) {
            const resultMsg = document.getElementById('saveResult');
            resultMsg.style.display = 'block';
            
            // 3 saniye sonra mesajı gizle
            setTimeout(() => {
                resultMsg.style.display = 'none';
            }, 3000);
        } else {
            alert("Kaydetme işlemi başarısız oldu.");
        }
    } catch (e) {
        alert("Bağlantı hatası: " + e.message);
    }
}

// Menü Yükleme Fonksiyonu
async function uploadMenu(lang) {
    const fileInput = document.getElementById(`menu_file_${lang}`);
    if (!fileInput.files || fileInput.files.length === 0) {
        alert("Lütfen bir dosya seçin.");
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('lang', lang);
    
    try {
        const res = await fetch('/api/web/upload-menu', {
            method: 'POST',
            body: formData
        });
        
        const result = await res.json();
        if (result.success) {
            const msg = document.getElementById('uploadResult');
            msg.style.display = 'block';
            setTimeout(() => msg.style.display = 'none', 3000);
            fileInput.value = ""; // clear input
        } else {
            alert("Hata: " + (result.error || "Bilinmeyen hata"));
        }
    } catch (e) {
        alert("Yükleme sırasında hata: " + e.message);
    }
}
