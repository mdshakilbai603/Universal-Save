from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# ডাটা স্টোর (এখানে পণ্য এবং অর্ডার জমা থাকবে)
db = {
    "products": [
        {"id": 1, "name": "Computer Pro", "price": "45000", "img": "https://via.placeholder.com/150"}
    ],
    "orders": []
}

@app.route('/')
def home(): return send_from_directory('.', 'index.html')

@app.route('/shakil-admin-pro')
def admin(): return send_from_directory('.', 'admin.html')

@app.route('/healthz')
def health(): return "OK", 200

# পণ্য আপলোড এপিআই
@app.route('/api/add-product', methods=['POST'])
def add_p():
    new_p = request.json
    new_p['id'] = len(db['products']) + 1
    db['products'].append(new_p)
    return jsonify({"success": True})

# পণ্য ডিলিট এপিআই
@app.route('/api/delete-product/<int:p_id>', methods=['DELETE'])
def delete_p(p_id):
    db['products'] = [p for p in db['products'] if p['id'] != p_id]
    return jsonify({"success": True})

# অর্ডার দেওয়ার এপিআই
@app.route('/api/place-order', methods=['POST'])
def place_order():
    db['orders'].append(request.json)
    return jsonify({"success": True})

# সব ডাটা দেখার এপিআই (অ্যাডমিন ও ইউজার দুইজনের জন্যই)
@app.route('/api/data')
def get_data(): return jsonify(db)

@app.route('/api/fetch', methods=['POST'])
def fetch_api():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL({'format': 'best', 'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({"success": True, "title": info.get('title'), "url": info.get('url'), "thumb": info.get('thumbnail')})
    except: return jsonify({"success": False})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
