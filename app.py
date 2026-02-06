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

    # সর্বোচ্চ পাওয়ারফুল কনফিগারেশন
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'geo_bypass': True,
        'extract_flat': False,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Connection': 'keep-alive',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ভিডিওর সব তথ্য সংগ্রহ
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"error": "ভিডিওর তথ্য পাওয়া যায়নি!"}), 404

            # বিভিন্ন সাইটের জন্য সঠিক ডাউনলোড লিঙ্ক খুঁজে বের করা
            download_url = None
            if 'url' in info:
                download_url = info['url']
            elif 'formats' in info:
                # সবচেয়ে ভালো MP4 ফরম্যাটটি বেছে নেওয়া
                for f in reversed(info['formats']):
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        download_url = f.get('url')
                        break

            if not download_url:
                return jsonify({"error": "সরাসরি ডাউনলোড লিঙ্ক পাওয়া যায়নি।"}), 404

            return jsonify({
                "title": info.get('title', 'Universal Video'),
                "thumbnail": info.get('thumbnail', ''),
                "download_url": download_url,
                "duration": info.get('duration'),
                "source": info.get('extractor_key')
            })

    except Exception as e:
        # এরর মেসেজটিকে আরও পরিষ্কার করা
        error_msg = str(e)
        if "Sign in" in error_msg:
            return jsonify({"error": "এই ভিডিওটি প্রাইভেট বা লগইন করা প্রয়োজন।"}), 403
        return jsonify({"error": "সার্ভার এই লিঙ্কটি প্রসেস করতে পারছে না।"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
