from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# ডাটাবেসের বদলে আমরা এই লিস্টটি ব্যবহার করবো যা তুমি অ্যাডমিন থেকে এডিট করতে পারবে
DATABASE = {
    "products": [
        {"id": 1, "name": "Computer Pro", "price": "45000", "img": "https://via.placeholder.com/150"},
        {"id": 2, "name": "Premium Shirt", "price": "1200", "img": "https://via.placeholder.com/150"}
    ],
    "orders": []
}

@app.route('/')
def home(): return send_from_directory('.', 'index.html')

@app.route('/shakil-admin-pro')
def admin(): return send_from_directory('.', 'admin.html')

# পণ্য ডিলিট করার এপিআই
@app.route('/api/delete-product/<int:id>', methods=['DELETE'])
def delete_product(id):
    DATABASE['products'] = [p for p in DATABASE['products'] if p['id'] != id]
    return jsonify({"success": True})

# পণ্য যোগ করার এপিআই
@app.route('/api/add-product', methods=['POST'])
def add_product():
    new_p = request.json
    new_p['id'] = len(DATABASE['products']) + 1
    DATABASE['products'].append(new_p)
    return jsonify({"success": True})

@app.route('/api/data')
def get_data(): return jsonify(DATABASE)

# ভিডিও জেনারেটর (যাতে বন্ধ না হয় সেজন্য try-except)
@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL({'format': 'best', 'quiet': True, 'no_warnings': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({"success": True, "title": info['title'], "url": info['url'], "thumb": info['thumbnail']})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False) # Debug False দিলে সাইট স্টেবল থাকে
