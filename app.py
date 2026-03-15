import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import traceback

app = Flask(__name__, static_url_path='', static_folder='.')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# Dummy routes যাতে frontend error না দেয়
@app.route('/api/config')
def config():
    return jsonify({"shop_items": []})

@app.route('/api/data')
def data():
    return jsonify({"products": [], "orders": []})

@app.route('/api/fetch', methods=['POST'])
def fetch():
    url = request.json.get('url')
    if not url:
        return jsonify({"success": False, "error": "লিংক দাও!"}), 400

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'http_headers': {
            'Referer': url,
            'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
        },
        'simulate': True,
        'get_url': True,
        'extract_flat': False,
    }

    # Terabox / file host special
    if any(x in url.lower() for x in ['terabox', '1024tera', '1024terabox']):
        ydl_opts['http_headers']['Referer'] = 'https://www.terabox.com/'
        ydl_opts['http_headers']['Origin'] = 'https://www.terabox.com'
        if os.path.exists('cookies.txt'):
            ydl_opts['cookiefile'] = 'cookies.txt'  # Render-এ upload করো

    # Social media extra headers
    if any(x in url for x in ['facebook', 'instagram', 'fb.watch', 'tiktok', 'twitter', 'x.com']):
        ydl_opts['http_headers']['Referer'] = 'https://www.facebook.com/' if 'facebook' in url else url

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if 'url' not in info and 'formats' not in info:
                return jsonify({"success": False, "error": "ভিডিও/ফাইল পাওয়া যায়নি। সাইট সাপোর্ট করে না বা login দরকার।"}), 400

            # Best direct URL খোঁজা
            video_url = info.get('url')
            if not video_url and 'formats' in info:
                formats = sorted(info['formats'], key=lambda f: (
                    f.get('vcodec', 'none') != 'none',
                    f.get('acodec', 'none') != 'none',
                    f.get('filesize') or f.get('filesize_approx') or 0
                ), reverse=True)
                video_url = next((f['url'] for f in formats if f.get('url')), None)

            if not video_url:
                return jsonify({"success": False, "error": "Direct link extract হয়নি। yt-dlp আপডেট দরকার হতে পারে।"}), 400

            return jsonify({
                "success": True,
                "title": info.get('title', 'No Title'),
                "url": video_url,
                "thumb": info.get('thumbnail') or '',
                "site": info.get('extractor_key', 'Universal'),
                "duration": info.get('duration_string', 'N/A'),
                "size": info.get('filesize_approx') or info.get('filesize')
            })

    except Exception as e:
        error = str(e)
        if "unsupported" in error.lower() or "no longer supported" in error.lower():
            return jsonify({"success": False, "error": "এই সাইট yt-dlp-এ সাপোর্ট করে না বা piracy related বলে ব্লক করা হয়েছে।"}), 400
        return jsonify({"success": False, "error": f"Error: {error}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
