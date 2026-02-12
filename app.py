import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# ডেইলি-মোশন ও তেরাবক্সের জন্য স্পেশাল কনফিগারেশন
YDL_OPTIONS = {
    'format': 'bestvideo+bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
    'extract_flat': False, # তেরাবক্সের জন্য এটি False রাখা জরুরি
}

@app.route('/healthz')
def health():
    return "Global Downloader Running", 200

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    if not url:
        return jsonify({"success": False, "error": "লিঙ্ক দিন"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # ভিডিওর সরাসরি লিঙ্ক ফিল্টার করা
            video_url = info.get('url')
            if not video_url and 'entries' in info:
                video_url = info['entries'][0].get('url')

            return jsonify({
                "success": True,
                "title": info.get('title', 'Video Found'),
                "url": video_url,
                "thumb": info.get('thumbnail', ''),
                "site": info.get('extractor_key', 'Dailymotion/Terabox')
            })
    except Exception as e:
        return jsonify({"success": False, "error": "এই লিঙ্কটি প্রসেস করা যাচ্ছে না"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
