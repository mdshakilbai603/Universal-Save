import os
import time
import requests
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# মাস্টার কনফিগারেশন: যা তেরাবক্স এবং জটিল সাইটগুলো বাইপাস করবে
YDL_OPTIONS = {
    'format': 'bestvideo+bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'extract_flat': 'in_playlist',
    'wait_for_video': (5, 30),
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'http_headers': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.google.com/',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Connection': 'keep-alive',
    }
}

# ১. ওয়েবসাইটকে ঘুমানো থেকে বাঁচানোর জন্য Keep-Alive
@app.route('/healthz')
def health():
    return "Engine Status: Fully Operational", 200

# ২. মেইন হোম পেজ
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# ৩. অ্যাডমিন প্যানেল (shakil-admin-pro)
@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

# ৪. তোমার অ্যাডমিন প্যানেলের জন্য প্রয়োজনীয় ব্যাকএন্ড ডাটা [cite: 1]
@app.route('/api/data')
def get_admin_data():
    # এখানে তোমার ডাটাবেস বা ফাইল থেকে ডাটা আসবে
    return jsonify({
        "products": [
            {"id": 1, "name": "Global Premium Access", "price": "500", "img": "https://via.placeholder.com/150"}
        ],
        "orders": []
    })

# ৫. ইউনিভার্সাল ভিডিও ফেচিং এপিআই (The Core Engine)
@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    if not url or len(url.strip()) < 5:
        return jsonify({"success": False, "error": "অনুগ্রহ করে একটি সঠিক লিঙ্ক দিন"}), 400

    # তেরাবক্সের বিশেষ হ্যান্ডলিং
    if "1024tera" in url or "terabox" in url:
        # তেরাবক্স অনেক সময় সরাসরি কাজ করে না, তাই হেডার আপডেট করা হয়
        YDL_OPTIONS['referer'] = url
    
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # ভিডিওর গভীর থেকে তথ্য বের করার চেষ্টা
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"success": False, "error": "ভিডিওর তথ্য পাওয়া যায়নি"}), 404

            # সঠিক ডাউনলোড লিঙ্ক ফিল্টার করা
            video_url = None
            if 'url' in info:
                video_url = info['url']
            elif 'entries' in info and len(info['entries']) > 0:
                video_url = info['entries'][0].get('url') or info['entries'][0].get('webpage_url')
            elif 'formats' in info:
                # সবচেয়ে ভালো কোয়ালিটির লিঙ্ক বাছাই
                video_url = info['formats'][-1].get('url')

            if not video_url:
                return jsonify({"success": False, "error": "সরাসরি ফাইল লিঙ্ক পাওয়া যায়নি"}), 500

            return jsonify({
                "success": True,
                "title": info.get('title', 'Universal Video Found'),
                "url": video_url,
                "thumb": info.get('thumbnail', 'https://via.placeholder.com/300'),
                "duration": info.get('duration', 0),
                "site": info.get('extractor_key', 'Cloud Link')
            })
            
    except Exception as e:
        return jsonify({"success": False, "error": f"সার্ভার এরর: {str(e)}"}), 500

# ৬. নতুন প্রোডাক্ট অ্যাড করার এপিআই (অ্যাডমিন প্যানেলের জন্য)
@app.route('/api/add-product', methods=['POST'])
def add_product():
    # এখানে প্রোডাক্ট সেভ করার কোড বসানো যাবে
    return jsonify({"success": True, "message": "Product added successfully"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
