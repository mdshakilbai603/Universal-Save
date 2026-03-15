import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import traceback

app = Flask(__name__, static_url_path='', static_folder='.')

@app.route('/healthz')
def keep_alive():
    return "Engine Status: Online & Stable", 200

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

# Dummy routes যাতে তোমার frontend error না দেয়
@app.route('/api/config')
def get_config():
    return jsonify({"shop_items": []})

@app.route('/api/data')
def get_admin_data():
    return jsonify({"products": [], "orders": []})

@app.route('/api/fetch', methods=['POST'])
def handle_fetch():
    target_url = request.json.get('url')
    if not target_url:
        return jsonify({"success": False, "error": "লিংক দেওয়া হয়নি!"}), 400
    
    # ==================== সম্পূর্ণ আপডেটেড ydl_opts ====================
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',  # m4a audio priority (সাউন্ড জোরে আসে)
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
            'Referer': target_url,
        },
        'simulate': True,
        'get_url': True,
        'extract_flat': False,
        
        # ==================== সাউন্ড কমে যাওয়ার সমস্যার সমাধান ====================
        # loudnorm দিয়ে ভলিউম স্বয়ংক্রিয়ভাবে বুস্ট + normalize করা হবে (YouTube/FB/IG/TikTok-এ কাজ করে)
        'postprocessor_args': [
            '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11'   # এটা সবচেয়ে ভালো কাজ করে, আগের মতো জোরে সাউন্ড আসবে
        ],
        
        # Terabox / 1024terabox special
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None
    }

    # Terabox extra headers
    if any(x in target_url.lower() for x in ['1024tera', 'terabox', '1024terabox']):
        ydl_opts['http_headers']['Referer'] = 'https://www.terabox.com/'
        ydl_opts['http_headers']['Origin'] = 'https://www.terabox.com'

    # Facebook / Instagram / TikTok extra
    if any(x in target_url.lower() for x in ['facebook', 'fb.watch', 'instagram', 'tiktok']):
        ydl_opts['http_headers']['Referer'] = 'https://www.facebook.com/'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=False)
            
            if not info:
                return jsonify({"success": False, "error": "কোনো তথ্য পাওয়া যায়নি।"}), 400

            # Best direct URL
            video_url = info.get('url')
            if not video_url and 'formats' in info:
                formats = sorted(info['formats'], key=lambda f: (
                    f.get('vcodec', '') != 'none',
                    f.get('acodec', '') != 'none',
                    f.get('filesize') or f.get('filesize_approx') or 0
                ), reverse=True)
                video_url = next((f['url'] for f in formats if f.get('url')), None)

            if not video_url:
                return jsonify({"success": False, "error": "Direct link পাওয়া যায়নি।"}), 400

            return jsonify({
                "success": True,
                "title": info.get('title', 'Video/File Found'),
                "url": video_url,
                "thumb": info.get('thumbnail') or '',
                "site": info.get('extractor_key', 'Universal'),
                "duration": info.get('duration_string', 'N/A'),
                "size": info.get('filesize_approx') or info.get('filesize')
            })

    except Exception as e:
        error_msg = str(e) + "\n" + traceback.format_exc()[:400]
        return jsonify({"success": False, "error": f"সার্ভার এরর: {error_msg}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
