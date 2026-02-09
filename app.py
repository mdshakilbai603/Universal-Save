import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp

# 'static_url_path' সেট করা হয়েছে যাতে সরাসরি ফাইল পাওয়া যায়
app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

# মেইন রুট - এটি সরাসরি তোমার index.html ফাইলকে দেখাবে
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# ভিডিও ডাউনলোড করার API রুট
@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    video_url = data.get('url')
    if not video_url: 
        return jsonify({"error": "লিঙ্ক দেওয়া হয়নি!"}), 400

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            return jsonify({
                "success": True,
                "title": info.get('title'),
                "download_url": info.get('url'),
                "thumbnail": info.get('thumbnail')
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
