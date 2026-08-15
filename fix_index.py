import re

content = open('templates/index.html').read()

# 1. Remove split section from Payment Modal
payment_split_regex = r'<!-- Hesabı böl -->[\s\S]*?</div>\s*</div>\s*<!-- Bahşiş'
content = re.sub(payment_split_regex, '<!-- Bahşiş', content)

# 2. Modify Order Modal buttons
# Replace "Ürün Aktar", "Masayı Böl" with a single "Adisyonu Böl" button
order_modal_buttons_regex = r'<button class="btn" onclick="openItemTransferModal\(\)".*?↔ Ürün Aktar</button>\s*</div>\s*<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.5rem;">\s*<button class="btn" onclick="openMergeModal\(\)".*?⊕ Birleştir</button>\s*<button class="btn" onclick="promptSplitTable\(\)".*?✂ Masayı Böl</button>'
replacement = """<button class="btn" onclick="openItemSplitModal()" style="background:#718096;color:white;" title="Seçilen ürünleri yeni bir adisyona (Part 2 vb.) ayır">✂ Adisyonu Böl</button>
                        </div>
                        <div style="display: grid; grid-template-columns: 1fr; gap: 0.5rem; margin-top: 0.5rem;">
                            <button class="btn" onclick="openMergeModal()" style="background:#718096;color:white;" title="Siparişleri Birleştir">⊕ Birleştir</button>"""
content = re.sub(order_modal_buttons_regex, replacement, content)

# 3. Change `applyItemSplit()` logic
# Old applyItemSplit adds a payment entry. New one will call `/api/orders/<id>/split-ticket`
old_apply_split = r'async function applyItemSplit\(\) \{[\s\S]*?showToast\(`Seçilen ürünler için kısmi ödeme eklendi \(\$\{fmtTL\(total\)\}\)`, \'success\'\);\s*\}'

new_apply_split = """async function applyItemSplit() {
        const inputs = document.querySelectorAll('.item-split-qty');
        let itemsToMove = [];
        inputs.forEach(inp => {
            const qty = parseInt(inp.value)||0;
            if (qty > 0) {
                itemsToMove.push({id: inp.dataset.id, quantity: qty});
            }
        });

        if (itemsToMove.length === 0) {
            return showToast('Aktarılacak ürün seçmediniz!', 'warn');
        }

        const btn = document.querySelector('#itemSplitModal .btn-success');
        btn.disabled = true;
        btn.textContent = 'Bölünüyor...';

        try {
            const res = await fetch(`/api/orders/${currentOrder.id}/split-ticket`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({items: itemsToMove})
            }).then(r => r.json());

            if (res.success) {
                showToast('Adisyon başarıyla bölündü!', 'success');
                document.getElementById('itemSplitModal').style.display = 'none';
                
                // Refresh modal and background
                refreshZone();
                if (res.source_deleted) {
                    document.getElementById('orderModal').style.display = 'none';
                } else {
                    openTable(currentTable, document.getElementById('modalTableName').textContent);
                }
            } else {
                showToast('Hata: ' + res.error, 'error');
            }
        } catch (e) {
            showToast('Hata oluştu', 'error');
        }
        
        btn.disabled = false;
        btn.textContent = 'Böl ve Yeni Adisyon Aç';
    }"""
content = re.sub(old_apply_split, new_apply_split, content)

# 4. Change UI text for itemSplitModal
content = content.replace("<h2>Kısmi Ödeme (Ürün Seç)</h2>", "<h2>✂ Adisyonu Böl</h2>")
content = content.replace("Kısmi Ödeme Ekle", "Böl ve Yeni Adisyon Aç")
content = content.replace("onclick=\"applyItemSplit()\">Kısmi Ödeme Ekle</button>", "onclick=\"applyItemSplit()\">Böl ve Yeni Adisyon Aç</button>")

# 5. Fix `openItemSplitModal()` to include `data-id` for inputs since they are needed for the API
old_open_item_split = r'function openItemSplitModal\(\) \{[\s\S]*?\} \/\/ openItemSplitModal end'
new_open_item_split = """function openItemSplitModal() {
            const list = document.getElementById('itemSplitList');
            if (!currentOrder || !currentOrder.items) return;
            
            list.innerHTML = currentOrder.items.map(i =>
                `<div style="display:flex;align-items:center;gap:.5rem;padding:.5rem;border-bottom:1px solid var(--border);">
                    <input type="number" class="item-split-qty" data-id="${i.id}" data-price="${i.price||0}" data-complimentary="${i.is_complimentary ? '1' : '0'}" value="0" min="0" max="${i.quantity}" oninput="recalcItemSplitTotal()" onchange="recalcItemSplitTotal()" style="width:50px;padding:.3rem;border:1px solid #ccc;border-radius:4px;text-align:center;">
                    <span style="flex:1;cursor:pointer;" onclick="toggleItemSplitQty(this)">x ${i.product_name||i.name||''} (${i.quantity} adet)</span>
                    <span style="font-weight:600;">${i.is_complimentary ? 'İkram' : fmtTL(i.price||0)}</span>
                </div>`
            ).join('');
            recalcItemSplitTotal();
            document.getElementById('itemSplitModal').style.display = 'flex';
        }"""
content = re.sub(r'function openItemSplitModal\(\) \{[\s\S]*?recalcItemSplitTotal\(\);\s*document\.getElementById\(\'itemSplitModal\'\)\.style\.display = \'flex\';\s*\}', new_open_item_split, content)


with open('templates/index.html', 'w') as f:
    f.write(content)

