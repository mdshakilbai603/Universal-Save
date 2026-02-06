import os
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

# ভিডিও ডাউনলোডের জন্য উন্নত কনফিগারেশন
YDL_OPTIONS = {
    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'no_color': True,
    'add_header': [
        'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language: en-US,en;q=0.5',
    ],
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "লিঙ্ক দেওয়া হয়নি!"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # ভিডিও তথ্য সংগ্রহ
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({"error": "ভিডিওর তথ্য পাওয়া যায়নি!"}), 404
                
            video_data = {
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail', ''),
                "download_url": info.get('url'), # সরাসরি ডাউনলোডের লিঙ্ক
                "site": info.get('extractor_key', 'Unknown')
            }
            return jsonify(video_data)
            
    except Exception as e:
        return jsonify({"error": "সার্ভার লিঙ্কটি প্রসেস করতে পারছে না। সঠিক লিঙ্ক দিন।"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
