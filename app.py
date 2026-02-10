from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# ডাটাবেস ছাড়াই পাওয়ারফুল কন্ট্রোল সিস্টেম
SITE_CONFIG = {
    "free_limit": 5,      # প্রতিদিন কয়টা ভিডিও ফ্রি ডাউনলোড হবে
    "premium_price": 99,   # প্রিমিয়াম চার্জ
    "is_public": True,     # সাইট কি সবার জন্য খোলা? 
    "shop_items": [
        {"id": 1, "name": "Gaming Laptop", "price": "75000 BDT", "img": "laptop.jpg"},
        {"id": 2, "name": "Cotton T-Shirt", "price": "550 BDT", "img": "shirt.jpg"}
    ]
}

@app.route('/')
def home(): return send_from_directory('.', 'index.html')

@app.route('/api/config')
def get_config(): return jsonify(SITE_CONFIG)

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL({'format': 'best', 'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({"success": True, "title": info['title'], "url": info['url'], "thumb": info['thumbnail']})
    except: return jsonify({"success": False})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
