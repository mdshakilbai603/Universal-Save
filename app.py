import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# গ্লোবাল কনফিগারেশন: বিশ্বের সব সাইট সাপোর্ট করার জন্য
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/'
}

# ১. বটকে জাগিয়ে রাখা (যাতে Not Found না আসে)
@app.route('/healthz')
def health():
    return "OK", 200

# ২. হোম পেজ (সরাসরি index.html দেখাবে)
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# ৩. তোমার অ্যাডমিন প্যানেল (shakil-admin-pro)
@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

# ৪. ভিডিও ফেচ করার মেইন এপিআই
@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    if not url:
        return jsonify({"success": False, "error": "লিঙ্ক দেওয়া হয়নি"}), 400
    
    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url') or (info.get('entries')[0].get('url') if 'entries' in info else None)
            
            return jsonify({
                "success": True,
                "title": info.get('title', 'Video Found'),
                "url": video_url,
                "thumb": info.get('thumbnail', '')
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    # রেন্ডার সার্ভারের জন্য পোর্ট কনফিগারেশন
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
