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
        return jsonify({"error": "লিঙ্ক দেওয়া হয়নি!"}), 400

    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail', ''),
                "download_url": info.get('url')
            })
    except Exception as e:
        return jsonify({"error": "লিঙ্কটি কাজ করছে না। সঠিক লিঙ্ক দিন।"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
