function initAdmin() {
    if (!sessionStorage.getItem('firinna_token')) {
        if (document.getElementById('loginOverlay')) document.getElementById('loginOverlay').style.display = 'flex';
        if (document.getElementById('adminMain')) document.getElementById('adminMain').style.display = 'none';
    } else {
        if (document.getElementById('loginOverlay')) document.getElementById('loginOverlay').style.display = 'none';
        if (document.getElementById('adminMain')) document.getElementById('adminMain').style.display = 'flex';
        fetchSettings();
        fetchAnalytics();
        loadWebCategories();
        loadWebProducts();
    }

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
            } else if (targetId === 'settings') {
                fetchSettings();
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

const originalFetch = window.fetch;
window.fetch = async function() {
    let [resource, config] = arguments;
    if (typeof resource === 'string' && resource.startsWith('/api/') && sessionStorage.getItem('firinna_token')) {
        config = config || {};
        config.headers = config.headers || {};
        config.headers['X-Admin-Token'] = sessionStorage.getItem('firinna_token');
    }
    return await originalFetch(resource, config);
};

async function checkLogin() {
    const user = document.getElementById('admin_user').value;
    const pass = document.getElementById('admin_pass').value;
    if (user !== 'admin') {
        document.getElementById('loginError').style.display = 'block';
        return;
    }
    try {
        const res = await originalFetch('/api/web/admin-login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ password: pass })
        });
        const data = await res.json();
        if (data.success) {
            sessionStorage.setItem('firinna_admin', 'true');
            sessionStorage.setItem('firinna_token', data.token);
            document.getElementById('loginOverlay').style.display = 'none';
            document.getElementById('adminMain').style.display = 'flex';
            fetchSettings();
            fetchAnalytics();
        } else {
            document.getElementById('loginError').style.display = 'block';
        }
    } catch (e) {
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
        
        const referrersAndSources = {...(data.traffic_sources || {}), ...(data.referrers || {})};
        renderList('list-referrers', referrersAndSources);
        renderList('list-hours', data.peak_hours);
        
        // Combine Devices, OS, and Browsers
        const devicesAndBrowsers = {...(data.devices || {}), ...(data.os || {}), ...(data.browsers || {})};
        renderList('list-devices', devicesAndBrowsers);
        
        const locationsAndCountries = {...(data.locations || {}), ...(data.countries || {})};
        renderList('list-countries', locationsAndCountries);
        
        // Save raw visitors & render call-log grouped table
        currentRawVisitors = data.recent_visitors || [];
        renderGroupedVisitors();

        // Render Chart.js Visual Charts
        renderAnalyticsCharts(data);
    } catch (e) {
        console.error("Analitikler yüklenemedi", e);
    }
}

let trendChartInstance = null;
let trafficChartInstance = null;
let devicesChartInstance = null;
let locationsChartInstance = null;

function renderAnalyticsCharts(data) {
    if (typeof Chart === 'undefined') return;

    // 1. Ziyaret Trend Grafiği (Son Günler)
    const dateCounts = {};
    const visitors = data.recent_visitors || [];
    visitors.forEach(v => {
        const iso = v.iso_date || (v.raw_time ? v.raw_time.split(' ')[0] : '');
        if (iso) {
            dateCounts[iso] = (dateCounts[iso] || 0) + 1;
        }
    });

    const sortedDates = Object.keys(dateCounts).sort();
    const recentDates = sortedDates.slice(-14);
    const trendLabels = recentDates.map(d => {
        const parts = d.split('-');
        return parts.length === 3 ? `${parts[2]}.${parts[1]}` : d;
    });
    const trendValues = recentDates.map(d => dateCounts[d]);

    const ctxTrend = document.getElementById('chart-visit-trend');
    if (ctxTrend) {
        if (trendChartInstance) trendChartInstance.destroy();
        trendChartInstance = new Chart(ctxTrend, {
            type: 'line',
            data: {
                labels: trendLabels.length ? trendLabels : ['Bugün'],
                datasets: [{
                    label: 'Ziyaretçi Sayısı',
                    data: trendValues.length ? trendValues : [data.today || 0],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.12)',
                    fill: true,
                    tension: 0.35,
                    borderWidth: 3,
                    pointBackgroundColor: '#2563eb',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, ticks: { stepSize: 1 } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // 2. Trafik Kaynakları Doughnut Chart
    const trafficData = {...(data.traffic_sources || {}), ...(data.referrers || {})};
    const trafficLabels = Object.keys(trafficData);
    const trafficValues = Object.values(trafficData);
    const trafficColors = ['#d97706', '#2563eb', '#10b981', '#ec4899', '#8b5cf6', '#64748b'];

    const ctxTraffic = document.getElementById('chart-traffic-sources');
    if (ctxTraffic) {
        if (trafficChartInstance) trafficChartInstance.destroy();
        trafficChartInstance = new Chart(ctxTraffic, {
            type: 'doughnut',
            data: {
                labels: trafficLabels.length ? trafficLabels : ['Henüz Veri Yok'],
                datasets: [{
                    data: trafficValues.length ? trafficValues : [1],
                    backgroundColor: trafficColors.slice(0, Math.max(trafficLabels.length, 1))
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                }
            }
        });
    }

    // 3. Cihaz & Tarayıcı Bar Chart
    const devData = {...(data.devices || {}), ...(data.browsers || {})};
    const devLabels = Object.keys(devData).slice(0, 6);
    const devValues = devLabels.map(k => devData[k]);

    const ctxDev = document.getElementById('chart-devices');
    if (ctxDev) {
        if (devicesChartInstance) devicesChartInstance.destroy();
        devicesChartInstance = new Chart(ctxDev, {
            type: 'bar',
            data: {
                labels: devLabels.length ? devLabels : ['Henüz Veri Yok'],
                datasets: [{
                    label: 'Kullanım Sayısı',
                    data: devValues.length ? devValues : [0],
                    backgroundColor: '#10b981',
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: { x: { beginAtZero: true } }
            }
        });
    }

    // 4. Şehir / Konum Doughnut Chart
    const locData = {...(data.locations || {}), ...(data.countries || {})};
    const locLabels = Object.keys(locData).slice(0, 6);
    const locValues = locLabels.map(k => locData[k]);
    const locColors = ['#ec4899', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#64748b'];

    const ctxLoc = document.getElementById('chart-locations');
    if (ctxLoc) {
        if (locationsChartInstance) locationsChartInstance.destroy();
        locationsChartInstance = new Chart(ctxLoc, {
            type: 'doughnut',
            data: {
                labels: locLabels.length ? locLabels : ['Henüz Veri Yok'],
                datasets: [{
                    data: locValues.length ? locValues : [1],
                    backgroundColor: locColors.slice(0, Math.max(locLabels.length, 1))
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } }
                }
            }
        });
    }
}

// ARMA KAYDI MODELİ İLE ZİYARETÇİ GRUPLAMA VE FİLTRELEME MANTIĞI
let currentRawVisitors = [];
let visitorFilterMode = 'all';
let filterStartDate = '';
let filterEndDate = '';
let groupedVisitorsMap = {};

function setVisitorFilter(mode) {
    visitorFilterMode = mode;
    document.querySelectorAll('.btn-filter, #btn-filter-all, #btn-filter-today, #btn-filter-range').forEach(btn => {
        btn.style.background = '#fff';
        btn.style.color = '#475569';
        btn.style.border = '1px solid #cbd5e1';
    });

    const activeBtn = document.getElementById(`btn-filter-${mode}`);
    if (activeBtn) {
        activeBtn.style.background = '#2563eb';
        activeBtn.style.color = '#fff';
        activeBtn.style.border = 'none';
    }

    const rangeContainer = document.getElementById('range-picker-container');
    if (rangeContainer) {
        rangeContainer.style.display = (mode === 'range') ? 'inline-flex' : 'none';
    }

    renderGroupedVisitors();
}

function applyCustomRangeFilter() {
    filterStartDate = document.getElementById('filter-start-date').value;
    filterEndDate = document.getElementById('filter-end-date').value;
    if (!filterStartDate || !filterEndDate) {
        alert("Lütfen başlangıç ve bitiş tarihlerini seçin.");
        return;
    }
    renderGroupedVisitors();
}

function renderGroupedVisitors() {
    const tableEl = document.getElementById('table-recent-visitors');
    if (!tableEl) return;

    if (!currentRawVisitors || currentRawVisitors.length === 0) {
        tableEl.innerHTML = '<tr><td colspan="7" style="padding:16px; text-align:center; color:#94a3b8;">Henüz canlı ziyaretçi verisi bulunmuyor.</td></tr>';
        return;
    }

    const todayStr = new Date().toISOString().split('T')[0];

    // Raw ziyaretçileri seçilen zaman filtresine göre süz
    let filteredVisitors = currentRawVisitors.filter(v => {
        const iso = v.iso_date || '';
        if (visitorFilterMode === 'today') {
            return iso === todayStr || (v.time && v.time.includes('Ağustos')); // bugün kontrolü
        } else if (visitorFilterMode === 'range') {
            if (filterStartDate && filterEndDate && iso) {
                return iso >= filterStartDate && iso <= filterEndDate;
            }
        }
        return true;
    });

    if (filteredVisitors.length === 0) {
        tableEl.innerHTML = '<tr><td colspan="7" style="padding:16px; text-align:center; color:#94a3b8;">Seçilen zaman filtresinde ziyaretçi verisi bulunamadı.</td></tr>';
        return;
    }

    // IP + Cihaz + Tarayıcı kombinasyonuna göre GRUPLA (Telefondaki Arama Kaydı Mantığı)
    groupedVisitorsMap = {};
    filteredVisitors.forEach(v => {
        const key = `${v.ip || 'Gizli IP'}___${v.device || ''}___${v.browser || ''}`;
        if (!groupedVisitorsMap[key]) {
            groupedVisitorsMap[key] = {
                key: key,
                ip: v.ip || 'Gizli IP',
                country: v.location || v.country || '-',
                location: v.location || v.country || '-',
                traffic_source: v.traffic_source || v.store_mode || '🔗 Doğrudan (Direct)',
                device: v.device || '-',
                browser: v.browser || '-',
                latest_time: v.time || '-',
                visits: []
            };
        }
        groupedVisitorsMap[key].visits.push(v);
    });

    const groups = Object.values(groupedVisitorsMap);

    tableEl.innerHTML = '';
    groups.forEach((g) => {
        const count = g.visits.length;
        const row = document.createElement('tr');
        row.style.borderBottom = '1px solid #f1f5f9';
        row.style.transition = 'background 0.2s ease';
        row.onmouseenter = () => row.style.background = '#f8fafc';
        row.onmouseleave = () => row.style.background = '#ffffff';

        row.innerHTML = `
            <td style="padding:10px;">
                <span onclick="showVisitorGroupDetails('${g.key}')" title="Tüm giriş detaylarını gör" style="background:#e0f2fe; color:#0369a1; border:1px solid #bae6fd; font-weight:700; padding:4px 10px; border-radius:12px; font-size:0.82rem; cursor:pointer; display:inline-flex; align-items:center; gap:6px;">
                    <i class="ph-bold ph-phone-incoming" style="font-size:0.95rem;"></i> ${count} Ziyaret / Giriş
                </span>
            </td>
            <td style="padding:10px; font-family:monospace; color:#2563eb; font-weight:700; cursor:pointer;" onclick="showVisitorGroupDetails('${g.key}')">${g.ip}</td>
            <td style="padding:10px; font-weight:600; color:#1e293b;">${g.location}</td>
            <td style="padding:10px;"><span style="background:#fef3c7; color:#92400e; padding:3px 8px; border-radius:6px; font-weight:700; font-size:0.8rem;">${g.traffic_source}</span></td>
            <td style="padding:10px; color:#334155;">${g.device}</td>
            <td style="padding:10px; color:#475569;">${g.browser}</td>
            <td style="padding:10px; font-weight:600; color:#475569;">${g.latest_time}</td>
            <td style="padding:10px; text-align:center;">
                <button class="btn btn-primary" onclick="showVisitorGroupDetails('${g.key}')" style="font-size:0.78rem; padding:5px 12px; border-radius:6px; background:#2563eb; font-weight:600;">
                    <i class="ph-bold ph-list-magnifying-glass"></i> Detaylar (${count})
                </button>
            </td>
        `;
        tableEl.appendChild(row);
    });
}

function showVisitorGroupDetails(key) {
    const group = groupedVisitorsMap[key];
    if (!group) return;

    const summaryEl = document.getElementById('visitor-details-summary');
    if (summaryEl) {
        summaryEl.innerHTML = `
            <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:10px;">
                <div><strong>IP Adresi:</strong> <span style="color:#2563eb; font-family:monospace; font-weight:700;">${group.ip}</span></div>
                <div><strong>📍 Konum:</strong> <span style="color:#0f172a; font-weight:700;">${group.location}</span></div>
                <div><strong>🎯 Kaynak:</strong> <span style="color:#b45309; font-weight:700;">${group.traffic_source}</span></div>
                <div><strong>Cihaz:</strong> ${group.device}</div>
                <div><strong>Tarayıcı:</strong> ${group.browser}</div>
                <div><strong>Toplam Giriş:</strong> <span style="color:#047857; font-weight:700;">${group.visits.length} Kez</span></div>
            </div>
        `;
    }

    const tbody = document.getElementById('visitor-details-table-body');
    if (tbody) {
        tbody.innerHTML = '';
        group.visits.forEach(v => {
            const tr = document.createElement('tr');
            tr.style.borderBottom = '1px solid #f1f5f9';
            tr.innerHTML = `
                <td style="padding:8px 10px; font-weight:600; color:#334155;">${v.time || '-'}</td>
                <td style="padding:8px 10px;"><span style="background:#eff6ff; color:#1d4ed8; padding:3px 8px; border-radius:6px; font-weight:600; font-size:0.8rem;">${v.action || 'Ziyaret'}</span></td>
                <td style="padding:8px 10px; color:#64748b; font-size:0.82rem;">${v.type || '-'} ${v.scroll_depth ? `| Kaydırma: ${v.scroll_depth}` : ''} ${v.time_spent ? `| Süre: ${v.time_spent}` : ''}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    const modal = document.getElementById('visitorDetailsModal');
    if (modal) modal.style.display = 'flex';
}

function closeVisitorDetailsModal() {
    const modal = document.getElementById('visitorDetailsModal');
    if (modal) modal.style.display = 'none';
}

function openResetAnalyticsModal() {
    const modal = document.getElementById('resetAnalyticsModal');
    if (modal) modal.style.display = 'flex';
}

function closeResetAnalyticsModal() {
    const modal = document.getElementById('resetAnalyticsModal');
    if (modal) modal.style.display = 'none';
}

function toggleResetScopeInputs() {
    const selected = document.querySelector('input[name="resetScope"]:checked').value;
    const inputsDiv = document.getElementById('reset-range-inputs');
    if (inputsDiv) {
        inputsDiv.style.display = (selected === 'range') ? 'flex' : 'none';
    }
}

async function confirmResetAnalytics() {
    const scope = document.querySelector('input[name="resetScope"]:checked').value;
    const startDate = document.getElementById('reset-start-date').value;
    const endDate = document.getElementById('reset-end-date').value;

    if (scope === 'range' && (!startDate || !endDate)) {
        alert("Lütfen sıfırlanacak başlangıç ve bitiş tarihlerini seçin.");
        return;
    }

    if (!confirm("Seçilen kapsamdaki istatistik verilerini sıfırlamak istediğinize emin misiniz?")) {
        return;
    }

    try {
        const adminPass = sessionStorage.getItem('firinna_pass') || 'FirinnaPos2026!';
        const res = await fetch('/api/web/reset-analytics', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Basic ' + btoa('admin:' + adminPass)
            },
            body: JSON.stringify({
                scope: scope,
                startDate: startDate,
                endDate: endDate
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(data.message || "İstatistikler sıfırlandı.");
            closeResetAnalyticsModal();
            fetchAnalytics();
        } else {
            alert("Hata: " + (data.error || "Sıfırlanamadı"));
        }
    } catch (e) {
        alert("Bir hata oluştu: " + e.message);
    }
}

const DAYS_LIST = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"];

function renderAdminSchedule(dailyHours = {}) {
    const container = document.getElementById('weekly-schedule-container');
    if (!container) return;

    container.innerHTML = '';
    DAYS_LIST.forEach(day => {
        const cfg = dailyHours[day] || { open: "08:30", close: "23:00", active: true };
        const row = document.createElement('div');
        row.style.cssText = "display:flex; align-items:center; gap:12px; padding:10px 14px; background:#ffffff; border:1px solid #cbd5e1; border-radius:8px; flex-wrap:wrap;";
        
        const isChecked = cfg.active !== false;
        
        row.innerHTML = `
            <label style="display:flex; align-items:center; gap:8px; width:130px; font-weight:700; color:#0f172a; cursor:pointer;">
                <input type="checkbox" id="day_active_${day}" ${isChecked ? 'checked' : ''} onchange="toggleDayRow('${day}')">
                <span>${day}</span>
            </label>
            <div id="day_inputs_${day}" style="display:${isChecked ? 'flex' : 'none'}; align-items:center; gap:8px;">
                <input type="time" id="day_open_${day}" class="form-control" style="width:130px;" value="${cfg.open || '08:30'}">
                <span style="color:#64748b; font-weight:bold;">-</span>
                <input type="time" id="day_close_${day}" class="form-control" style="width:130px;" value="${cfg.close || '23:00'}">
            </div>
            <span id="day_closed_badge_${day}" style="display:${!isChecked ? 'inline-block' : 'none'}; color:#dc2626; font-weight:700; font-size:0.85rem; background:#fef2f2; padding:4px 10px; border-radius:6px; border:1px solid #fecaca;">
                🔴 KAPALI
            </span>
            <button type="button" class="btn" onclick="copyScheduleFromDay('${day}')" title="${day} saatlerini ve durumunu diğer tüm günlere kopyala" style="background:#eff6ff; color:#1d4ed8; border:1px solid #bfdbfe; font-weight:600; font-size:0.78rem; padding:4px 10px; border-radius:6px; margin-left:auto; cursor:pointer; display:inline-flex; align-items:center; gap:4px;"><i class="ph-bold ph-copy"></i> Tüm Günlere Kopyala</button>
        `;
        container.appendChild(row);
    });
}

function toggleDayRow(day) {
    const active = document.getElementById(`day_active_${day}`).checked;
    document.getElementById(`day_inputs_${day}`).style.display = active ? 'flex' : 'none';
    document.getElementById(`day_closed_badge_${day}`).style.display = !active ? 'inline-block' : 'none';
}

function copyScheduleFromDay(sourceDay) {
    const isChecked = document.getElementById(`day_active_${sourceDay}`).checked;
    const openVal = document.getElementById(`day_open_${sourceDay}`).value;
    const closeVal = document.getElementById(`day_close_${sourceDay}`).value;
    
    DAYS_LIST.forEach(targetDay => {
        if (targetDay !== sourceDay) {
            const chk = document.getElementById(`day_active_${targetDay}`);
            if (chk) chk.checked = isChecked;
            const openInp = document.getElementById(`day_open_${targetDay}`);
            if (openInp) openInp.value = openVal;
            const closeInp = document.getElementById(`day_close_${targetDay}`);
            if (closeInp) closeInp.value = closeVal;
            toggleDayRow(targetDay);
        }
    });
    
    const statusTxt = isChecked ? `${openVal} - ${closeVal}` : 'Kapalı';
    alert(`✅ ${sourceDay} gününün çalışma saatleri (${statusTxt}) diğer tüm günlere başarıyla kopyalandı! Kaydetmek için sayfanın altındaki "Değişiklikleri Kaydet" butonuna basabilirsiniz.`);
}

// Ayarları API'den Çek
async function fetchSettings() {
    try {
        const res = await fetch('/api/web/settings');
        const data = await res.json();
        
        renderAdminSchedule(data.daily_hours || {});
        
        if (data.address && document.getElementById('address')) document.getElementById('address').value = data.address;
        if (data.phone && document.getElementById('phone')) document.getElementById('phone').value = data.phone;
        if (data.instagram && document.getElementById('instagram')) document.getElementById('instagram').value = data.instagram;
        if (data.google_review_url && document.getElementById('google_review_url')) document.getElementById('google_review_url').value = data.google_review_url;
        if (data.yandex_review_url && document.getElementById('yandex_review_url')) document.getElementById('yandex_review_url').value = data.yandex_review_url;
        if (data.tripadvisor_review_url && document.getElementById('tripadvisor_review_url')) document.getElementById('tripadvisor_review_url').value = data.tripadvisor_review_url;
        if (data.group_event_text && document.getElementById('group_event_text')) document.getElementById('group_event_text').value = data.group_event_text;
        
        if (data.manual_status && document.querySelector(`input[name="manual_status"][value="${data.manual_status}"]`)) {
            document.querySelector(`input[name="manual_status"][value="${data.manual_status}"]`).checked = true;
            if(data.manual_status === 'closed' && document.getElementById('closed_until_div')) {
                document.getElementById('closed_until_div').style.display = 'block';
            }
        }
        if (data.closed_until && document.getElementById('closed_until')) {
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
        
        const daily_hours = {};
        DAYS_LIST.forEach(day => {
            const active = document.getElementById(`day_active_${day}`).checked;
            const openVal = document.getElementById(`day_open_${day}`).value || "08:30";
            const closeVal = document.getElementById(`day_close_${day}`).value || "23:00";
            daily_hours[day] = { open: openVal, close: closeVal, active: active };
        });

        // Generate work_hours summary string (e.g. 08:30 - 23:00)
        const pazartesiCfg = daily_hours["Pazartesi"] || { open: "08:30", close: "23:00" };
        const workHoursSummary = `${pazartesiCfg.open} - ${pazartesiCfg.close}`;
        
        const payload = {
            ...existingData,
            work_hours: workHoursSummary,
            daily_hours: daily_hours,
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
            alert("Ayarlar kaydedilirken hata oluştu!");
        }
    } catch (e) {
        console.error("Kaydetme hatası", e);
        alert("Kaydetme hatası!");
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
    const rawImg = p.image_url || '';
    const img = (typeof rawImg === 'string' && rawImg.length > 0) ? rawImg : 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?auto=format&fit=crop&w=600&q=80';

    const tagsHtml = (Array.isArray(p.tags) ? p.tags : []).map(t => {
        const info = TAG_MAP[t] || { label: t, bg: '#f1f5f9', color: '#475569' };
        return `<span style="background:${info.bg}; color:${info.color}; font-size:0.72rem; font-weight:700; padding:2px 6px; border-radius:4px;">${info.label}</span>`;
    }).join(' ');

    const cardOpacity = isActive ? '1' : '0.65';
    const cardBorder = isActive ? '1px solid #e2e8f0' : '1px dashed #fca5a5';
    
    // Top-left status badge
    const activeBadge = isActive 
        ? `<span style="position:absolute; top:8px; left:8px; background:#dcfce7; color:#15803d; font-size:0.72rem; font-weight:700; padding:2px 8px; border-radius:12px; border:1px solid #bbf7d0;">✅ Satışta</span>`
        : `<span style="position:absolute; top:8px; left:8px; background:#fee2e2; color:#991b1b; font-size:0.72rem; font-weight:700; padding:2px 8px; border-radius:12px; border:1px solid #fca5a5;">⏸️ Pasif</span>`;

    // Top-right signature badge (if active)
    const sigBadge = isSig 
        ? `<span style="position:absolute; top:8px; right:8px; background:#fef3c7; color:#b45309; font-size:0.72rem; font-weight:700; padding:2px 8px; border-radius:12px; border:1px solid #fde68a;">⭐ İmza Lezzet</span>`
        : '';

    // Sleek Icon-Only Buttons with native Tooltips (title="..." attribute)
    const activeToggleBtn = isActive 
        ? `<button onclick="toggleProductActive('${p.id}')" title="Ürün Satışta (Pasife Almak İçin Tıklayın)" class="btn" style="background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; width:34px; height:34px; border-radius:6px; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; font-size:1.05rem;"><i class="ph-bold ph-eye"></i></button>`
        : `<button onclick="toggleProductActive('${p.id}')" title="Ürün Pasif (Satışa Açmak İçin Tıklayın)" class="btn" style="background:#fee2e2; color:#dc2626; border:1px solid #fecaca; width:34px; height:34px; border-radius:6px; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; font-size:1.05rem;"><i class="ph-bold ph-eye-slash"></i></button>`;

    const sigToggleBtn = isSig
        ? `<button onclick="toggleProductSignature('${p.id}')" title="İmza Lezzet (Kaldırmak İçin Tıklayın)" class="btn" style="background:#fef3c7; color:#d97706; border:1px solid #fde68a; width:34px; height:34px; border-radius:6px; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; font-size:1.05rem;"><i class="ph-fill ph-star"></i></button>`
        : `<button onclick="toggleProductSignature('${p.id}')" title="İmza Lezzet Yap" class="btn" style="background:#f8fafc; color:#94a3b8; border:1px solid #cbd5e1; width:34px; height:34px; border-radius:6px; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; font-size:1.05rem;"><i class="ph-bold ph-star"></i></button>`;

    const editBtn = `<button onclick="editProduct('${p.id}')" title="Ürünü Düzenle" class="btn" style="background:#eff6ff; color:#2563eb; border:1px solid #bfdbfe; width:34px; height:34px; border-radius:6px; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; font-size:1.05rem;"><i class="ph-bold ph-pencil-simple"></i></button>`;
    
    const deleteBtn = `<button onclick="deleteProduct('${p.id}')" title="Ürünü Kalıcı Olarak Sil" class="btn" style="background:#fef2f2; color:#dc2626; border:1px solid #fecaca; width:34px; height:34px; border-radius:6px; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; font-size:1.05rem;"><i class="ph-bold ph-trash"></i></button>`;

    return `
        <div style="background:#fff; border:${cardBorder}; opacity:${cardOpacity}; border-radius:8px; overflow:hidden; display:flex; flex-direction:column; box-shadow:0 1px 3px rgba(0,0,0,0.05); transition:all 0.2s ease;">
            <div style="height:140px; position:relative; overflow:hidden; background:#f8fafc;">
                <img src="${img}" alt="${p.title || ''}" style="width:100%; height:100%; object-fit:cover;">
                ${activeBadge}
                ${sigBadge}
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
                
                <!-- SLEEK COMPACT TOOLBAR -->
                <div style="display:flex; align-items:center; justify-content:space-between; border-top:1px solid #f1f5f9; padding-top:10px; margin-top:6px;">
                    <span style="font-size:0.78rem; font-weight:700; color:${isActive ? '#15803d' : '#991b1b'};">
                        ${isActive ? '● Satışta' : '○ Pasif'}
                    </span>
                    <div style="display:flex; gap:6px;">
                        ${activeToggleBtn}
                        ${sigToggleBtn}
                        ${editBtn}
                        ${deleteBtn}
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
