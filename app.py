import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# স্পিড বাড়ানোর জন্য ক্যাশ
cache = {}

# প্রাথমিক পণ্য (যাতে রিস্টার্ট হলেও এগুলো না মুছে যায়)
db = {
    "products": [
        {"id": 1, "name": "Premium Smartphone", "price": "25000", "img": "https://via.placeholder.com/150"},
        {"id": 2, "name": "8K Video Converter", "price": "1500", "img": "https://via.placeholder.com/150"}
    ]
}

@app.route('/api/fetch', methods=['POST'])
def fetch_fast():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"}), 400

    if url in cache: return jsonify(cache[url]) # ক্যাশ থেকে দ্রুত রিটার্ন

    try:
        with yt_dlp.YoutubeDL({'format': 'best', 'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            res = {"success": True, "title": info.get('title'), "url": info.get('url'), "thumb": info.get('thumbnail')}
            cache[url] = res
            return jsonify(res)
    except:
        return jsonify({"success": False}), 500

@app.route('/api/data')
def get_data(): return jsonify(db)
