import os
import time
import requests
import json
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# মাস্টার কনফিগারেশন: যা সিকিউরিটি বাইপাস করতে সাহায্য করবে
YDL_OPTIONS = {
    'format': 'bestvideo+bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'extract_flat': 'in_playlist',
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
def health():
    return "Universal-Save Engine: Fully Operational", 200

# ২. মেইন পেজসমূহ
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

# ৩. তোমার অ্যাডমিন প্যানেলের ব্যাকএন্ড ডাটা (admin.html এর জন্য)
@app.route('/api/data')
def get_admin_data():
    # এখানে ডিফল্ট কিছু ডাটা দেওয়া হলো যাতে পেজ খালি না দেখায়
    return jsonify({
        "products": [
            {"id": 1, "name": "Global Premium Link", "price": "150", "img": "https://via.placeholder.com/150"}
        ],
        "orders": []
    })

# ৪. ইউনিভার্সাল ভিডিও ফেচিং মেকানিজম (সবচেয়ে শক্তিশালী পার্ট)
@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    data = request.json
    url = data.get('url')

    if not url or len(url.strip()) < 10:
        return jsonify({"success": False, "error": "সঠিক লিঙ্ক দিন"}), 400

    # তেরাবক্স বিশেষ হ্যান্ডলিং: ডাইনামিক রেফারার সেট করা
    if "1024tera" in url or "terabox" in url:
        YDL_OPTIONS['referer'] = url
        YDL_OPTIONS['extract_flat'] = False # তেরাবক্সের জন্য এটি জরুরি

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # ভিডিওর আসল ডাটা টেনে আনা
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"success": False, "error": "ভিডিওর তথ্য পাওয়া যায়নি"}), 404

            # ডাউনলোড লিঙ্ক ফিল্টার করা
            video_url = None
            if 'url' in info:
                video_url = info['url']
            elif 'entries' in info and len(info['entries']) > 0:
                video_url = info['entries'][0].get('url') or info['entries'][0].get('webpage_url')
            elif 'formats' in info:
                # সবচেয়ে ভালো কোয়ালিটি ফিল্টার
                video_url = info['formats'][-1].get('url')

            if not video_url:
                return jsonify({"success": False, "error": "ডাউনলোড লিঙ্ক খুঁজে পাওয়া যায়নি"}), 500

            return jsonify({
                "success": True,
                "title": info.get('title', 'Universal Video'),
                "url": video_url,
                "thumb": info.get('thumbnail', 'https://via.placeholder.com/300'),
                "site": info.get('extractor_key', 'Generic Cloud'),
                "quality": "Ultra HD"
            })
            
    except Exception as e:
        print(f"Server Debug Error: {str(e)}")
        return jsonify({"success": False, "error": "এই লিঙ্কটি প্রসেস করতে একটু সময় লাগছে। আবার চেষ্টা করুন।"}), 500

# ৫. পোর্ট কনফিগারেশন (রেন্ডার সাপোর্ট)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
