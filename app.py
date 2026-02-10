import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# ১. বটকে জাগিয়ে রাখার জন্য এই রুটটি অবশ্যই লাগবে (Not Found দূর করবে)
@app.route('/healthz')
def health():
    return "OK", 200

# ২. হোম পেজ রুট
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# ৩. ভিডিও জেনারেটর এপিআই
@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    if not url or url.strip() == "":
        return jsonify({"success": False, "error": "Invalid URL"}), 400
    try:
        ydl_opts = {'format': 'best', 'quiet': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True,
                "title": info.get('title'),
                "url": info.get('url'),
                "thumb": info.get('thumbnail')
            })
    except:
        return jsonify({"success": False, "error": "Server Error"}), 500

# ৪. অ্যাডমিন প্যানেল রুট
@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
