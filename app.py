from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import datetime

app = Flask(__name__, static_url_path='', static_folder='.')

# অ্যাডমিন সেটিংস ডাটা (তুমি চাইলে ডাটাবেসে রাখতে পারো)
ADMIN_DATA = {
    "is_public": True,
    "free_limit": 10,
    "premium_price": 99,
    "orders": [],
    "products": [
        {"id": 1, "name": "Apple MacBook Pro", "price": "1,45,000 BDT", "img": "https://images.unsplash.com/photo-1517336712468-0776482cb068?w=400"},
        {"id": 2, "name": "Premium Cotton Hoodie", "price": "1,250 BDT", "img": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=400"}
    ]
}

@app.route('/')
def home(): return send_from_directory('.', 'index.html')

@app.route('/shakil-admin-hub')
def admin(): return send_from_directory('.', 'admin.html')

@app.route('/api/config')
def get_config(): return jsonify(ADMIN_DATA)

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL({'format': 'best', 'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({"success": True, "title": info['title'], "url": info['url'], "thumb": info['thumbnail']})
    except: return jsonify({"success": False})

@app.route('/api/place-order', methods=['POST'])
def order():
    data = request.json
    data['time'] = str(datetime.datetime.now())
    ADMIN_DATA['orders'].append(data)
    return jsonify({"success": True, "msg": "Order Placed!"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
