import re

content = open('templates/index.html').read()

# Fix m1, m2, m3, m4 logic to match exactly or with " - Part"
search_logic = """
                let m1 = tables.find(t => t.name === '1' || t.name === 'Masa 1');
                let m2 = tables.find(t => t.name === '2' || t.name === 'Masa 2');
                let m3 = tables.find(t => t.name === '3' || t.name === 'Masa 3');
                let m4 = tables.find(t => t.name === '4' || t.name === 'Masa 4');
"""

replace_logic = """
                const isMatch = (t, base) => t.name === base || t.name === 'Masa ' + base || t.name.startsWith(base + ' - Part') || t.name.startsWith('Masa ' + base + ' - Part');
                
                // İlk parçayı ana masaya koyalım
                let m1 = tables.find(t => isMatch(t, '1'));
                let m2 = tables.find(t => isMatch(t, '2'));
                let m3 = tables.find(t => isMatch(t, '3'));
                let m4 = tables.find(t => isMatch(t, '4'));
                
                const tkw = tables.find(t => t.id == 9 || t.name.toLowerCase() === 'takeaway');
                
                const extraTables = tables.filter(t => 
                    t !== m1 && t !== m2 && t !== m3 && t !== m4 && t !== tkw
                );
"""

content = content.replace(search_logic, replace_logic)

# Replace the TakeAway fetch block which we moved
content = re.sub(r'const allTbls.*?const tkwStatusStyle = .*?;', '', content, flags=re.DOTALL)
content = content.replace('const tkw = allTbls.find(t => t.id == 9 || t.name.toLowerCase() === \'takeaway\');', '')

# Redefine tkw variables before rendering
tkw_vars = """
                const tkwHasOrder = tkw && tkw.has_order > 0;
                const tkwDur = tkwHasOrder ? calcDuration(tkw.order_started_at) : null;
                const tkwStatusStyle = tkwHasOrder ? 'background:#fed7d7; border-color:#e53e3e;' : '';
"""

content = content.replace("tablesGrid.innerHTML = `", tkw_vars + "\n                tablesGrid.innerHTML = `")

# Append extra tables below blueprint
extra_html = """
                    </div>
                    
                    ${extraTables.length > 0 ? `
                    <div style="margin-top: 2rem; border-top: 2px dashed var(--border); padding-top: 1rem;">
                        <h3 style="color: var(--ink-2); margin-bottom: 1rem;">Ek Adisyonlar (Bölünmüş / Diğer Masalar)</h3>
                        <div class="tables-grid">
                            ${extraTables.map(table => {
                                const hasOrder = table.has_order > 0;
                                const status = hasOrder ? 'occupied' : 'empty';
                                const dur = hasOrder ? calcDuration(table.order_started_at) : null;
                                return \`
                                    <div class="table-card \${status}" onclick="openTable(\${table.id}, '\${table.name}')">
                                        \${dur ? \`<span class="dur-badge \${dur.cls}">\${dur.text}</span>\` : ''}
                                        <div class="table-icon">🍽️</div>
                                        <div class="table-name">\${table.name}\${table.table_note ? ' 📝' : ''}</div>
                                        \${hasOrder ? \`<div class="table-total">\${fmtTL(table.order_total||0)}</div>\` : ''}
                                    </div>
                                \`;
                            }).join('')}
                        </div>
                    </div>
                    ` : ''}
                `;
"""

content = content.replace("</div>\n                        </div>\n                    </div>\n                `;", "</div>\n                        </div>\n                    </div>\n" + extra_html)

with open('templates/index.html', 'w') as f:
    f.write(content)

