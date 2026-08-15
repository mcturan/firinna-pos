with open('templates/index.html', 'r') as f:
    text = f.read()

bad = """                        </div>
                    </div>
                    ` : ''}
                `;"""
good = """                `;"""

if bad in text:
    text = text.replace(bad, good)
    with open('templates/index.html', 'w') as f:
        f.write(text)
    print("Fixed html")
else:
    print("Could not find bad block")
