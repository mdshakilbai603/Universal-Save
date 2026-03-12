import os
import time
import requests
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# তেরাবক্স এবং ডেইলি-মোশনের জন্য হাই-লেভেল কনফিগারেশন
YDL_OPTIONS = {
    'format': 'bestvideo+bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'extract_flat': 'in_playlist',
    'wait_for_video': (1, 5),
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'http_headers': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'Connection': 'keep-alive',
    }
}

# ১. কিপ-অ্যালাইভ সিস্টেম (যাতে রেন্ডার থেকে অফ না হয়)
@app.route('/healthz')
def health_check():
    return "Universal-Save Engine: Active", 200

# ২. পেজ রাউটিং
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/shakil-admin-pro')
def admin_panel():
    return send_from_directory('.', 'admin.html')

# ৩. অ্যাডমিন প্যানেলের ডাটা (তোমার admin.html এর জন্য)
@app.route('/api/data')
def admin_data():
    return jsonify({
        "products": [
            {"id": 1, "name": "Premium Downloader", "price": "99", "img": "https://via.placeholder.com/150"}
        ],
        "orders": []
    })

# ৪. মেইন ভিডিও ফেচিং ইঞ্জিন (সবচেয়ে শক্তিশালী অংশ)
@app.route('/api/fetch', methods=['POST'])
def fetch_global_video():
    payload = request.json
    video_url = payload.get('url')

    if not video_url or len(video_url.strip()) < 10:
        return jsonify({"success": False, "error": "অনুগ্রহ করে একটি সঠিক লিঙ্ক দিন"}), 400

    # তেরাবক্স বিশেষ হ্যান্ডলিং (1024tera ফিক্স)
    if "1024tera" in video_url or "terabox" in video_url:
        YDL_OPTIONS['referer'] = video_url
        YDL_OPTIONS['extract_flat'] = False # তেরাবক্সের জন্য এটি জরুরি

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # ভিডিওর ডাটা এক্সট্রাক্ট করা
            meta = ydl.extract_info(video_url, download=False)
            
            if not meta:
                return jsonify({"success": False, "error": "ভিডিওর তথ্য পাওয়া যায়নি"}), 404

            # সঠিক ডাউনলোড লিঙ্ক বাছাই
            download_link = meta.get('url')
            if not download_link and 'entries' in meta:
                download_link = meta['entries'][0].get('url') or meta['entries'][0].get('webpage_url')
            
            # রেজাল্ট পাঠানো
            return jsonify({
                "success": True,
                "title": meta.get('title', 'Global Video'),
                "url": download_link,
                "thumb": meta.get('thumbnail', 'https://via.placeholder.com/300'),
                "site": meta.get('extractor_key', 'Generic'),
                "quality": "HD"
            })
            
    except Exception as e:
        # এরর লগিং যাতে রেন্ডার ড্যাশবোর্ডে দেখা যায়
        print(f"Extraction Error: {str(e)}")
        return jsonify({"success": False, "error": "সার্ভার এই ভিডিওটি প্রসেস করতে পারছে না। কিছুক্ষণ পর আবার চেষ্টা করুন।"}), 500

# ৫. অ্যাডমিন প্রোডাক্ট সিস্টেম
@app.route('/api/add-product', methods=['POST'])
def add_product():
    return jsonify({"success": True, "message": "Product Linked"})

if __name__ == "__main__":
    # রেন্ডারের ডাইনামিক পোর্ট সাপোর্ট
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
