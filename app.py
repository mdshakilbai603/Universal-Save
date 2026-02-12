import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# তেরাবক্স ও ডেইলি-মোশন এর জন্য অ্যাডভান্সড কনফিগারেশন
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
    'extract_flat': 'in_playlist',  # তেরাবক্সের ফোল্ডার লিঙ্ক হ্যান্ডেল করার জন্য
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
    if not url or len(url.strip()) < 5:
        return jsonify({"success": False, "error": "সঠিক লিঙ্ক দিন"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # ভিডিওর আসল লিঙ্ক ফিল্টার করা
            if 'entries' in info:
                video_url = info['entries'][0].get('url') or info['entries'][0].get('webpage_url')
            else:
                video_url = info.get('url')

            return jsonify({
                "success": True,
                "title": info.get('title', 'Video Found'),
                "url": video_url,
                "thumb": info.get('thumbnail', ''),
                "site": info.get('extractor_key', 'Unknown')
            })
    except Exception as e:
        return jsonify({"success": False, "error": "সার্ভার এই লিঙ্কটি প্রসেস করতে পারছে না"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
