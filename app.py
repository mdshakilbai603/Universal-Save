import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# গ্লোবাল কনফিগারেশন: যা তেরাবক্স ও টিকটকের ব্লক এড়াতে সাহায্য করবে
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'extract_flat': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
    'http_headers': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
    }
}

@app.route('/healthz')
def health():
    return "Global Engine is Running", 200

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    
    # ইনপুট বক্স খালি থাকলে সার্ভার এরর দিবে না
    if not url or len(url.strip()) < 5:
        return jsonify({"success": False, "error": "সঠিক লিঙ্ক দিন"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # তেরাবক্স বা টেলিগ্রামের জন্য তথ্য বের করার চেষ্টা
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"success": False, "error": "ভিডিও খুঁজে পাওয়া যায়নি"}), 404
            
            # ভিডিওর আসল লিঙ্ক ফিল্টার করা
            video_url = info.get('url') or (info.get('entries')[0].get('url') if info.get('entries') else None)
            
            return jsonify({
                "success": True,
                "title": info.get('title', 'Universal Video'),
                "url": video_url,
                "thumb": info.get('thumbnail', ''),
                "site": info.get('extractor_key', 'Unknown')
            })
    except Exception as e:
        return jsonify({"success": False, "error": "সার্ভার এই লিঙ্কটি প্রসেস করতে পারছে না"}), 500

@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
