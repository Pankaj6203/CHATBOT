import re
import os

with open('p:/CHATBOT/app.py', 'r', encoding='utf-8') as f:
    text = f.read()

route_str = '''@app.route('/', methods=['GET'])
def index():
    """Serve main website"""
    try:
        return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), 'index.html')
    except:
        # Fallback if static file not found
        return jsonify({
            "status": "success",
            "message": "Umesh Sweets Chatbot is LIVE!",
            "api": "Try POST /api/chat"
        }), 200

@app.route('/about', methods=['GET'])
def about():
    try:
        return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), 'about.html')
    except:
        return "About Page", 200

@app.route('/contact', methods=['GET'])
def contact():
    try:
        return send_from_directory(os.path.join(os.path.dirname(__file__), 'static'), 'contact.html')
    except:
        return "Contact Page", 200'''

text = re.sub(r"@app\.route\('/', methods=\['GET'\]\).*?\}\), 200", route_str, text, flags=re.DOTALL)

with open('p:/CHATBOT/app.py', 'w', encoding='utf-8') as f:
    f.write(text)
