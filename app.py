import os
from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    if not url:
        return jsonify({"error": "লিঙ্ক দিন!"}), 400

    # সব সাইট বাইপাস করার জন্য আল্টিমেট কনফিগারেশন
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'extract_flat': False,
        'youtube_include_dash_manifest': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # বিজি-লিপি বা ইউটিউব থেকে ডেটা নেওয়া
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"error": "ভিডিওর তথ্য পাওয়া যায়নি!"}), 404

            # ডাউনলোড লিঙ্ক খুঁজে বের করা
            download_url = info.get('url')
            if not download_url and 'formats' in info:
                for f in reversed(info['formats']):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        download_url = f.get('url')
                        break

            return jsonify({
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail', ''),
                "download_url": download_url
            })

    except Exception as e:
        return jsonify({"error": "লিঙ্কটি প্রসেস করা যাচ্ছে না। সম্ভবত সাইটটি ব্লক করছে।"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
