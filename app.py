import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# গ্লোবাল কনফিগারেশন যা ব্লক এড়াবে এবং সার্ভার সচল রাখবে
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
    'extract_flat': 'in_playlist'
}

# ১. এই রুটটি ওয়েবসাইটকে অফ হওয়া থেকে বাঁচাবে (Keep-Alive)
@app.route('/healthz')
def health():
    return "Global Engine Active", 200

# ২. মেইন পেজসমূহ
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

# ৩. তোমার অ্যাডমিন প্যানেলের জন্য প্রয়োজনীয় ডাটা এপিআই (যা আগে মিসিং ছিল)
@app.route('/api/data')
def get_data():
    return jsonify({"products": [], "orders": []})

@app.route('/api/config')
def get_config():
    return jsonify({"shop_items": []})

# ৪. ইউনিভার্সাল ভিডিও ফেচিং এপিআই
@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    if not url:
        return jsonify({"success": False, "error": "URL missing"}), 400
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
