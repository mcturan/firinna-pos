import re

content = open('app.py', 'r').read()

new_endpoint = """
@app.route('/api/orders/<int:order_id>/split-ticket', methods=['POST'])
def api_split_ticket(order_id):
    data = request.json or {}
    items_to_move = data.get('items', [])
    if not items_to_move:
        return jsonify({'success': False, 'error': 'Aktarılacak ürün seçilmedi.'}), 400
        
    try:
        conn = db.get_db()
        order = conn.execute("SELECT table_id FROM orders WHERE id=?", (order_id,)).fetchone()
        if not order:
            conn.close()
            return jsonify({'success': False, 'error': 'Sipariş bulunamadı'}), 404
            
        tbl = conn.execute("SELECT * FROM tables WHERE id=?", (order['table_id'],)).fetchone()
        
        base_name = tbl['name']
        if " - Part " in base_name:
            base_name = base_name.split(" - Part ")[0]
            
        existing = conn.execute("SELECT name FROM tables WHERE name LIKE ?", (f"{base_name} - Part %",)).fetchall()
        
        next_num = 2
        for ex in existing:
            try:
                num = int(ex['name'].split(" - Part ")[-1])
                if num >= next_num:
                    next_num = num + 1
            except:
                pass
                
        new_name = f"{base_name} - Part {next_num}"
        
        # If this is the first split, maybe rename original table to Part 1? 
        # Actually it's better to just leave it as is or rename it.
        # We will rename the original if it doesn't have "Part" in it.
        if " - Part " not in tbl['name']:
            conn.execute("UPDATE tables SET name = ? WHERE id = ?", (f"{base_name} - Part 1", tbl['id']))
            
        conn.execute('INSERT INTO tables (name, zone_id) VALUES (?, ?)', (new_name, tbl['zone_id']))
        new_table_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        conn.close()
        
        target_order_id, source_deleted = db.transfer_order_items(order_id, new_table_id, items_to_move)
        
        return jsonify({
            'success': True,
            'target_order_id': target_order_id,
            'source_deleted': source_deleted
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

"""

# Insert right before /api/orders/<id>/transfer-items
content = content.replace(
    "@app.route('/api/orders/<int:order_id>/transfer-items', methods=['POST'])",
    new_endpoint + "\n@app.route('/api/orders/<int:order_id>/transfer-items', methods=['POST'])"
)

with open('app.py', 'w') as f:
    f.write(content)

