import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# মেমোরি ক্যাশ (স্পিড বাড়ানোর জন্য)
video_cache = {}

db = {
    "products": [
        {"id": 1, "name": "Premium Laptop", "price": "55000", "img": "/uploads/laptop.jpg"}
    ],
    "orders": []
}

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    if not url:
        return jsonify({"success": False, "error": "Empty URL"}), 400
    
    # ক্যাশ চেক (যদি আগে এই ভিডিও কেউ ডাউনলোড করে থাকে তবে ১ সেকেন্ডে আসবে)
    if url in video_cache:
        return jsonify(video_cache[url])

    try:
        ydl_opts = {'format': 'best', 'quiet': True, 'no_warnings': True, 'extract_flat': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            data = {
                "success": True, 
                "title": info.get('title'), 
                "url": info.get('url'), 
                "thumb": info.get('thumbnail')
            }
            video_cache[url] = data # ক্যাশে সেভ করা হলো
            return jsonify(data)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/data')
def get_data():
    return jsonify(db)

# বাকি রুটগুলো আগের মতোই থাকবে...
