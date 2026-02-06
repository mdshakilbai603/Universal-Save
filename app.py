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

    # সব ওয়েবসাইট সাপোর্ট করার জন্য পাওয়ারফুল অপশন
    ydl_opts = {
        'format': 'best', # সবচেয়ে ভালো কোয়ালিটি
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ভিডিওর সব তথ্য বের করা
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"error": "ভিডিও পাওয়া যায়নি!"}), 404

            # ইউটিউব বা ফেসবুকের জন্য সরাসরি ডাউনলোড লিঙ্ক খুঁজে বের করা
            download_url = info.get('url')
            
            # যদি সরাসরি লিঙ্ক না পাওয়া যায় (যেমন ইউটিউবে অনেকগুলো ফরম্যাট থাকে)
            if not download_url and 'formats' in info:
                for f in info['formats']:
                    if f.get('ext') == 'mp4' or f.get('vcodec') != 'none':
                        download_url = f.get('url')
                        break

            return jsonify({
                "title": info.get('title', 'Universal Video'),
                "thumbnail": info.get('thumbnail', ''),
                "download_url": download_url
            })
    except Exception as e:
        return jsonify({"error": "এই লিঙ্কটি প্রসেস করা যাচ্ছে না।"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
