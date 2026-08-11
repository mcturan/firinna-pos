function initAdmin() {
    if (document.getElementById('loginOverlay')) document.getElementById('loginOverlay').style.display = 'none';
    if (document.getElementById('adminMain')) document.getElementById('adminMain').style.display = 'flex';
    fetchSettings();
    fetchAnalytics();
    loadWebCategories();
    loadWebProducts();

    if (document.getElementById('settingsForm')) {
        document.getElementById('settingsForm').addEventListener('submit', saveSettings);
    }
    
    // Manual Status Toggle Events
    document.querySelectorAll('input[name="manual_status"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            if(e.target.value === 'closed') {
                if (document.getElementById('closed_until_div')) document.getElementById('closed_until_div').style.display = 'block';
                if (document.getElementById('closed_until')) document.getElementById('closed_until').required = true;
            } else {
                if (document.getElementById('closed_until_div')) document.getElementById('closed_until_div').style.display = 'none';
                if (document.getElementById('closed_until')) document.getElementById('closed_until').required = false;
            }
        });
    });
    
    // Sekme (Tab) Değiştirme Mantığı
    const navItems = document.querySelectorAll('.nav-item[data-target]');
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            navItems.forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
            
            document.querySelectorAll('.admin-section').forEach(sec => sec.style.display = 'none');
            
            const targetId = item.getAttribute('data-target');
            if (document.getElementById(targetId)) document.getElementById(targetId).style.display = 'block';
            
            if (document.querySelector('.topbar h1')) {
                document.querySelector('.topbar h1').innerText = item.innerText.trim();
            }

            if (targetId === 'dashboard') {
                fetchAnalytics();
            } else if (targetId === 'products-mgmt') {
                loadWebCategories();
                loadWebProducts();
            }
        });
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAdmin);
} else {
    initAdmin();
}

// Her 5 saniyede bir analitikleri otomatik canlı tazele
setInterval(() => {
    fetchAnalytics();
}, 5000);

function checkLogin() {
    const user = document.getElementById('admin_user').value;
    const pass = document.getElementById('admin_pass').value;
    if(user === 'admin' && pass === 'FirinnaPos2026!') {
        sessionStorage.setItem('firinna_admin', 'true');
        document.getElementById('loginOverlay').style.display = 'none';
        document.getElementById('adminMain').style.display = 'flex';
        fetchSettings();
        fetchAnalytics();
    } else {
        document.getElementById('loginError').style.display = 'block';
    }
}

// Analitikleri API'den Çek
async function fetchAnalytics() {
    try {
        const res = await fetch('/api/web/analytics');
        const data = await res.json();
        
        const setText = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.innerText = val || 0;
        };

        setText('stat-today', data.today);
        setText('stat-month', data.month);
        setText('stat-total', data.total);
        setText('stat-menu', data.menu);
        setText('stat-actions', data.actions);
        setText('stat-repeat', data.repeat_visitors);
        setText('stat-map', data.map_clicks);
        
        // Fill Lists
        const renderList = (elementId, dataObj = {}) => {
            const el = document.getElementById(elementId);
            if (!el) return;
            el.innerHTML = '';
            const entries = Object.entries(dataObj || {}).sort((a,b) => b[1] - a[1]);
            if (entries.length === 0) {
                el.innerHTML = '<li style="display:flex; justify-content:space-between; margin-bottom:6px; color:#94a3b8;"><span>Henüz Veri Yok</span> <strong>0</strong></li>';
                return;
            }
            entries.forEach(([key, val]) => {
                el.innerHTML += `<li style="display:flex; justify-content:space-between; margin-bottom:6px;"><span>${key}</span> <strong>${val}</strong></li>`;
            });
        };
        
        renderList('list-referrers', data.referrers);
        renderList('list-hours', data.peak_hours);
        
        // Combine Devices, OS, and Browsers
        const devicesAndBrowsers = {...(data.devices || {}), ...(data.os || {}), ...(data.browsers || {})};
        renderList('list-devices', devicesAndBrowsers);
        
        renderList('list-countries', data.countries);
        
        // Render Recent Visitors Log Table
        const tableEl = document.getElementById('table-recent-visitors');
        if (tableEl) {
            if (data.recent_visitors && data.recent_visitors.length > 0) {
                tableEl.innerHTML = '';
                data.recent_visitors.forEach(v => {
                    const row = document.createElement('tr');
                    row.style.borderBottom = '1px solid #f1f5f9';
                    row.innerHTML = `
                        <td style="padding:10px; font-weight:600; color:#334155;">${v.time || '-'}</td>
                        <td style="padding:10px; font-family:monospace; color:#2563eb; font-weight:600;">${v.ip || '-'}</td>
                        <td style="padding:10px;">${v.country || '-'}</td>
                        <td style="padding:10px;">${v.device || '-'}</td>
                        <td style="padding:10px; color:#475569;">${v.browser || '-'}</td>
                        <td style="padding:10px;"><span style="background:#f1f5f9; color:#0f172a; padding:3px 8px; border-radius:6px; font-weight:600; font-size:0.8rem;">${v.action || 'Ziyaret'}</span></td>
                    `;
                    tableEl.appendChild(row);
                });
            } else {
                tableEl.innerHTML = '<tr><td colspan="6" style="padding:16px; text-align:center; color:#94a3b8;">Henüz canlı ziyaretçi verisi bulunmuyor.</td></tr>';
            }
        }
    } catch (e) {
        console.error("Analitikler yüklenemedi", e);
    }
}

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
        if (data.google_review_url) document.getElementById('google_review_url').value = data.google_review_url;
        if (data.yandex_review_url) document.getElementById('yandex_review_url').value = data.yandex_review_url;
        if (data.tripadvisor_review_url) document.getElementById('tripadvisor_review_url').value = data.tripadvisor_review_url;
        if (data.group_event_text && document.getElementById('group_event_text')) document.getElementById('group_event_text').value = data.group_event_text;
        
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
            google_review_url: document.getElementById('google_review_url').value,
            yandex_review_url: document.getElementById('yandex_review_url').value,
            tripadvisor_review_url: document.getElementById('tripadvisor_review_url').value,
            group_event_text: document.getElementById('group_event_text') ? document.getElementById('group_event_text').value : '',
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
            setTimeout(() => {
                resultMsg.style.display = 'none';
            }, 3000);
        } else {
            alert("Kaydetme işlemi başarısız oldu.");
        }
    } catch (e) {
        console.error("Ayarlar kaydedilemedi", e);
    }
}

// İstatistikleri Sıfırla
async function resetAnalyticsData() {
    if (!confirm("Tüm ziyaretçi ve analitik verilerini sıfırlamak istediğinize emin misiniz? Bu işlem geri alınamaz.")) return;
    try {
        const res = await fetch('/api/web/reset-analytics', { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            alert("Analitik verileri başarıyla sıfırlandı.");
            fetchAnalytics();
        } else {
            alert("Hata: " + (data.error || "Sıfırlanamadı"));
        }
    } catch(e) {
        alert("Bağlantı hatası");
    }
}

// Mekan Fotoğrafı Yükle
async function uploadGalleryPhoto(slot) {
    const fileInput = document.getElementById(`gal_${slot}`);
    if (!fileInput || !fileInput.files[0]) {
        alert("Lütfen önce bir fotoğraf seçin.");
        return;
    }
    const formData = new FormData();
    formData.append('slot', slot);
    formData.append('file', fileInput.files[0]);

    try {
        const res = await fetch('/api/web/upload-gallery-photo', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        const resEl = document.getElementById('galleryUploadResult');
        if (data.success) {
            resEl.innerText = `${slot} fotoğrafı başarıyla yüklendi!`;
            resEl.style.display = 'block';
            setTimeout(() => { resEl.style.display = 'none'; }, 4000);
        } else {
            alert("Hata: " + (data.error || "Yüklenemedi"));
        }
    } catch(e) {
        alert("Fotoğraf yüklenirken bağlantı hatası oluştu.");
    }
}

// Şifre Değiştir
async function changeAdminPassword(e) {
    e.preventDefault();
    const old_password = document.getElementById('old_password').value;
    const new_password = document.getElementById('new_password').value;
    const pwdResult = document.getElementById('pwdResult');

    try {
        const res = await fetch('/api/web/change-password', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ old_password, new_password })
        });
        const data = await res.json();
        if (data.success) {
            pwdResult.style.color = '#166534';
            pwdResult.innerText = "Şifreniz başarıyla değiştirildi!";
            pwdResult.style.display = 'block';
            document.getElementById('changePasswordForm').reset();
        } else {
            pwdResult.style.color = '#dc2626';
            pwdResult.innerText = data.error || "Hata oluştu!";
            pwdResult.style.display = 'block';
        }
    } catch(e) {
        pwdResult.style.color = '#dc2626';
        pwdResult.innerText = "Bağlantı hatası!";
        pwdResult.style.display = 'block';
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

// --- KATEGORİ & ÜRÜN YÖNETİMİ ---
let cachedWebCategories = [];
let cachedWebProducts = [];

async function loadWebCategories() {
    try {
        const res = await fetch('/api/web/categories');
        cachedWebCategories = await res.json();
        renderCategoryBadges();
        populateCategoryDropdowns();
    } catch(e) {
        console.error("Failed to load categories:", e);
    }
}

function renderCategoryBadges() {
    const container = document.getElementById('category-badges-container');
    if (!container) return;
    if (!cachedWebCategories || cachedWebCategories.length === 0) {
        container.innerHTML = '<span style="color:#94a3b8; font-size:0.85rem;">Henüz kategori bulunmuyor.</span>';
        return;
    }

    container.innerHTML = cachedWebCategories.map(c => `
        <span style="background:#fff; border:1px solid #fed7aa; color:#9a3412; padding:4px 10px; border-radius:16px; font-size:0.82rem; font-weight:700; display:inline-flex; align-items:center; gap:6px;">
            📁 ${c.name}
            <button onclick="editCategory('${c.id}')" title="Düzenle" style="background:none; border:none; color:#2563eb; cursor:pointer; font-size:0.85rem; padding:0;"><i class="ph-bold ph-pencil-simple"></i></button>
            <button onclick="deleteCategory('${c.id}')" title="Sil" style="background:none; border:none; color:#dc2626; cursor:pointer; font-size:0.85rem; padding:0;"><i class="ph-bold ph-x"></i></button>
        </span>
    `).join('');
}

function populateCategoryDropdowns() {
    const formSelect = document.getElementById('prod_category');
    const filterSelect = document.getElementById('prod-category-filter');

    if (formSelect) {
        formSelect.innerHTML = cachedWebCategories.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
    }

    if (filterSelect) {
        filterSelect.innerHTML = `<option value="ALL">Tüm Kategoriler</option>` + 
            cachedWebCategories.map(c => `<option value="${c.name}">${c.name}</option>`).join('');
    }
}

function resetCategoryForm() {
    document.getElementById('categoryForm').reset();
    document.getElementById('cat_id').value = '';
}

function editCategory(id) {
    const c = cachedWebCategories.find(x => x.id === id);
    if (!c) return;
    document.getElementById('cat_id').value = c.id;
    document.getElementById('cat_name').value = c.name;
    document.getElementById('cat_name').focus();
}

async function saveWebCategory(e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append('id', document.getElementById('cat_id').value);
    formData.append('name', document.getElementById('cat_name').value);

    try {
        const res = await fetch('/api/web/categories', { method: 'POST', body: formData });
        const data = await res.json();
        if (data.success) {
            resetCategoryForm();
            loadWebCategories();
            loadWebProducts();
        } else {
            alert("Hata: " + data.error);
        }
    } catch(err) {
        alert("Bağlantı hatası: " + err.message);
    }
}

async function deleteCategory(id) {
    if (!confirm("Bu kategoriyi silmek istediğinize emin misiniz?")) return;
    try {
        const res = await fetch(`/api/web/categories/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            loadWebCategories();
            loadWebProducts();
        }
    } catch(err) {
        console.error("Delete category error:", err);
    }
}

async function loadWebProducts() {
    try {
        const res = await fetch('/api/web/products');
        cachedWebProducts = await res.json();
        filterAdminProducts();
    } catch(e) {
        console.error("Failed to load products:", e);
    }
}

function filterAdminProducts() {
    const searchEl = document.getElementById('prod-search-input');
    const catEl = document.getElementById('prod-category-filter');
    const search = searchEl ? searchEl.value.toLowerCase() : '';
    const cat = catEl ? catEl.value : 'ALL';
    
    renderAdminProductsGrid(search, cat);
}

const TAG_MAP = {
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

async function toggleProductActive(id) {
    try {
        const res = await fetch(`/api/web/products/${id}/toggle-active`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            loadWebProducts();
        }
    } catch(e) {
        console.error("Toggle active error:", e);
    }
}

function renderAdminProductsGrid(filterSearch = '', filterCat = 'ALL') {
    const activeGrid = document.getElementById('admin-products-grid');
    const inactiveGrid = document.getElementById('admin-inactive-products-grid');
    if (!activeGrid) return;
    
    try {
        let list = cachedWebProducts || [];
        
        if (filterCat !== 'ALL') {
            list = list.filter(p => p && p.category === filterCat);
        }
        
        if (filterSearch) {
            list = list.filter(p => p && ((p.title || '').toLowerCase().includes(filterSearch) || (p.description || '').toLowerCase().includes(filterSearch)));
        }

        const activeList = list.filter(p => p && p.is_active !== false);
        const inactiveList = list.filter(p => p && p.is_active === false);

        // --- RENDER ACTIVE PRODUCTS ---
        if (activeList.length === 0) {
            activeGrid.innerHTML = '<div style="color:#94a3b8; font-size:0.9rem; grid-column:1/-1;">Satışta olan aktif ürün bulunmuyor.</div>';
        } else {
            activeGrid.innerHTML = activeList.map(p => renderSingleProductCard(p, true)).join('');
        }

        // --- RENDER INACTIVE PRODUCTS ---
        if (inactiveGrid) {
            if (inactiveList.length === 0) {
                inactiveGrid.innerHTML = '<div style="color:#94a3b8; font-size:0.9rem; grid-column:1/-1;">Pasif / devre dışı kalmış ürün bulunmuyor.</div>';
            } else {
                inactiveGrid.innerHTML = inactiveList.map(p => renderSingleProductCard(p, false)).join('');
            }
        }
    } catch(err) {
        console.error("renderAdminProductsGrid error:", err);
        activeGrid.innerHTML = '<div style="color:#ef4444; font-size:0.9rem; grid-column:1/-1;">Ürünler işlenirken bir hata oluştu.</div>';
    }
}

function renderSingleProductCard(p, isActive) {
    if (!p) return '';
    const isSig = !!p.is_signature;
    const sigBadgeBg = isSig ? '#dcfce7' : '#f1f5f9';
    const sigBadgeColor = isSig ? '#15803d' : '#64748b';
    const sigBtnText = isSig ? '⭐ İmza' : '☆ İmza';
    const rawImg = p.image_url || '';
    const img = (typeof rawImg === 'string' && rawImg.length > 0) ? rawImg : 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80';

    const tagsHtml = (Array.isArray(p.tags) ? p.tags : []).map(t => {
        const info = TAG_MAP[t] || { label: t, bg: '#f1f5f9', color: '#475569' };
        return `<span style="background:${info.bg}; color:${info.color}; font-size:0.72rem; font-weight:700; padding:2px 6px; border-radius:4px;">${info.label}</span>`;
    }).join(' ');

    const cardOpacity = isActive ? '1' : '0.65';
    const cardBorder = isActive ? '1px solid #e2e8f0' : '1px dashed #fca5a5';
    const activeStatusBadge = isActive 
        ? `<span style="position:absolute; top:8px; left:8px; background:#dcfce7; color:#15803d; font-size:0.75rem; font-weight:700; padding:3px 8px; border-radius:12px; border:1px solid #bbf7d0;">✅ Satışta</span>`
        : `<span style="position:absolute; top:8px; left:8px; background:#fee2e2; color:#991b1b; font-size:0.75rem; font-weight:700; padding:3px 8px; border-radius:12px; border:1px solid #fca5a5;">⏸️ Pasif</span>`;

    return `
        <div style="background:#fff; border:${cardBorder}; opacity:${cardOpacity}; border-radius:8px; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="height:140px; position:relative; overflow:hidden; background:#f8fafc;">
                <img src="${img}" alt="${p.title || ''}" style="width:100%; height:100%; object-fit:cover;">
                ${activeStatusBadge}
                <span style="position:absolute; top:8px; right:8px; background:${sigBadgeBg}; color:${sigBadgeColor}; font-size:0.75rem; font-weight:700; padding:3px 8px; border-radius:12px; border:1px solid ${isSig ? '#bbf7d0' : '#e2e8f0'};">
                    ${isSig ? '⭐ İmza Lezzet' : 'Standart'}
                </span>
            </div>
            <div style="padding:14px; flex:1; display:flex; flex-direction:column; justify-content:space-between;">
                <div>
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:8px; margin-bottom:4px;">
                        <h5 style="margin:0; font-size:1rem; color:#0f172a; font-weight:700;">${p.title || ''}</h5>
                        <span style="font-size:0.85rem; font-weight:800; color:#d97706; white-space:nowrap;">${p.price || ''}</span>
                    </div>
                    <div style="font-size:0.75rem; color:#64748b; margin-bottom:6px; font-weight:600;">📁 ${p.category || 'Genel'}</div>
                    <div style="display:flex; flex-wrap:wrap; gap:4px; margin-bottom:8px;">${tagsHtml}</div>
                    <p style="font-size:0.82rem; color:#475569; margin:0 0 12px 0; line-height:1.4; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden;">
                        ${p.description || ''}
                    </p>
                </div>
                <div style="display:flex; flex-direction:column; gap:8px; border-top:1px solid #f1f5f9; padding-top:10px; margin-top:6px;">
                    <div style="display:flex; align-items:center; justify-content:space-between; background:#f8fafc; padding:6px 10px; border-radius:6px; border:1px solid #e2e8f0;">
                        <span style="font-size:0.78rem; font-weight:700; color:${isActive ? '#15803d' : '#991b1b'};">
                            ${isActive ? '✅ Sitede Aktif' : '⏸️ Sitede Gizli'}
                        </span>
                        <button onclick="toggleProductActive('${p.id}')" class="btn" style="background:${isActive ? '#fee2e2' : '#dcfce7'}; color:${isActive ? '#991b1b' : '#15803d'}; border:1px solid ${isActive ? '#fca5a5' : '#bbf7d0'}; font-size:0.75rem; font-weight:700; padding:3px 8px; border-radius:4px; cursor:pointer;">
                            ${isActive ? 'Pasife Al ⬇️' : 'Etkinleştir ⬆️'}
                        </button>
                    </div>

                    <div style="display:flex; gap:6px;">
                        <button class="btn" onclick="toggleProductSignature('${p.id}')" style="flex:1; background:${isSig ? '#fef3c7' : '#f1f5f9'}; color:${isSig ? '#b45309' : '#475569'}; border:1px solid ${isSig ? '#fde68a' : '#cbd5e1'}; font-size:0.78rem; font-weight:700; padding:6px 8px; border-radius:6px; cursor:pointer;">
                            ${sigBtnText}
                        </button>
                        <button class="btn" onclick="editProduct('${p.id}')" title="Düzenle" style="background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; font-size:0.78rem; padding:6px 10px; border-radius:6px; cursor:pointer;">
                            <i class="ph-bold ph-pencil-simple"></i>
                        </button>
                        <button class="btn" onclick="deleteProduct('${p.id}')" title="Sil" style="background:#fef2f2; color:#b91c1c; border:1px solid #fecaca; font-size:0.78rem; padding:6px 10px; border-radius:6px; cursor:pointer;">
                            <i class="ph-bold ph-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
}

function resetProductForm() {
    document.getElementById('webProductForm').reset();
    document.getElementById('prod_id').value = '';
    document.getElementById('prod_image_url').value = '';
    if (document.getElementById('prod_is_active')) document.getElementById('prod_is_active').checked = true;
    document.querySelectorAll('.prod-tag-cb').forEach(cb => cb.checked = false);
    document.getElementById('prod-form-heading').innerHTML = '<i class="ph-bold ph-pencil-simple" style="color:#3b82f6;"></i> Yeni Ürün Girişi';
    document.getElementById('prodSaveResult').style.display = 'none';
}

function editProduct(id) {
    const p = cachedWebProducts.find(x => x.id === id);
    if (!p) return;
    document.getElementById('prod_id').value = p.id;
    document.getElementById('prod_title').value = p.title || '';
    document.getElementById('prod_category').value = p.category || '';
    document.getElementById('prod_price').value = p.price || '';
    document.getElementById('prod_description').value = p.description || '';
    document.getElementById('prod_image_url').value = p.image_url || '';
    document.getElementById('prod_is_signature').checked = !!p.is_signature;
    if (document.getElementById('prod_is_active')) document.getElementById('prod_is_active').checked = p.is_active !== false;

    const tags = p.tags || [];
    document.querySelectorAll('.prod-tag-cb').forEach(cb => {
        cb.checked = tags.includes(cb.value);
    });

    document.getElementById('prod-form-heading').innerHTML = `<i class="ph-bold ph-note-pencil" style="color:#d97706;"></i> Ürünü Düzenle: ${p.title}`;
    document.getElementById('product-form-card').scrollIntoView({ behavior: 'smooth' });
}

async function saveWebProduct(e) {
    e.preventDefault();
    const saveRes = document.getElementById('prodSaveResult');
    saveRes.style.display = 'none';

    const selectedTags = [];
    document.querySelectorAll('.prod-tag-cb:checked').forEach(cb => selectedTags.push(cb.value));

    const formData = new FormData();
    formData.append('id', document.getElementById('prod_id').value);
    formData.append('title', document.getElementById('prod_title').value);
    formData.append('category', document.getElementById('prod_category').value);
    formData.append('price', document.getElementById('prod_price').value);
    formData.append('description', document.getElementById('prod_description').value);
    formData.append('image_url', document.getElementById('prod_image_url').value);
    formData.append('is_signature', document.getElementById('prod_is_signature').checked);
    formData.append('is_active', document.getElementById('prod_is_active') ? document.getElementById('prod_is_active').checked : true);
    formData.append('tags', selectedTags.join(','));

    const fileInput = document.getElementById('prod_image_file');
    if (fileInput.files && fileInput.files[0]) {
        formData.append('image_file', fileInput.files[0]);
    }

    try {
        const res = await fetch('/api/web/products', {
            method: 'POST',
            body: formData
        });
        const data = await res.json();
        if (data.success) {
            saveRes.innerText = "Ürün başarıyla kaydedildi!";
            saveRes.style.display = 'block';
            resetProductForm();
            loadWebProducts();
        } else {
            alert("Hata: " + (data.error || "Bilinmeyen hata"));
        }
    } catch(err) {
        alert("Bağlantı hatası: " + err.message);
    }
}

async function toggleProductSignature(id) {
    try {
        const res = await fetch(`/api/web/products/${id}/toggle-signature`, { method: 'POST' });
        const data = await res.json();
        if (data.success) {
            loadWebProducts();
        }
    } catch(e) {
        console.error("Toggle error:", e);
    }
}

async function deleteProduct(id) {
    if (!confirm("Bu ürünü silmek istediğinize emin misiniz?")) return;
    try {
        const res = await fetch(`/api/web/products/${id}`, { method: 'DELETE' });
        const data = await res.json();
        if (data.success) {
            loadWebProducts();
        }
    } catch(e) {
        console.error("Delete error:", e);
    }
}
