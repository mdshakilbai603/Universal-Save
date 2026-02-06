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

    # একদম শক্তিশালী কনফিগারেশন (API ছাড়া সব সাইট বাইপাস করার জন্য)
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'geo_bypass': True,
        'cachedir': False,
        # এই পার্টটি সার্ভার ব্লকিং এড়াতে সাহায্য করবে (Proxy ছাড়া সেরা উপায়)
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ভিডিওর আসল তথ্য টেনে বের করা
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"error": "ভিডিওর তথ্য পাওয়া যায়নি!"}), 404

            # সরাসরি ডাউনলোড লিঙ্ক খোঁজা
            download_url = info.get('url')
            
            # যদি সরাসরি লিঙ্ক না থাকে (যেমন ইউটিউব বা টিকটকের ক্ষেত্রে)
            if not download_url and 'formats' in info:
                for f in reversed(info['formats']):
                    # ভিডিও এবং অডিও দুটোই আছে এমন ফাইল খোঁজা
                    if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                        download_url = f.get('url')
                        break

            if not download_url:
                return jsonify({"error": "ডাউনলোড লিঙ্ক জেনারেট করা সম্ভব হয়নি।"}), 404

            return jsonify({
                "title": info.get('title', 'Universal Video'),
                "thumbnail": info.get('thumbnail', ''),
                "download_url": download_url
            })

    except Exception as e:
        return jsonify({"error": "সার্ভার এই ভিডিওটি প্রসেস করতে পারছে না। সঠিক লিঙ্ক দিন।"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
