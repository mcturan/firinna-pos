import re

content = open('app.py').read()

new_index = """
@app.route('/')
def index():
    response = make_response(render_template('index.html'))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response
"""

content = re.sub(r"@app.route\('/'\)\s*def index\(\):\s*return render_template\('index\.html'\)", new_index, content)

with open('app.py', 'w') as f:
    f.write(content)

