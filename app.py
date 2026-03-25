import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import traceback
import time

app = Flask(__name__, static_url_path='', static_folder='.')

@app.route('/healthz')
def keep_alive():
    return "Universal Save Pro - 1800+ Sites | Status: Active", 200

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/api/config')
def get_config():
    return jsonify({"status": "Universal Downloader Running"})

@app.route('/api/data')
def get_admin_data():
    return jsonify({"products": [], "supported": "1800+ sites"})

@app.route('/api/fetch', methods=['POST'])
def handle_fetch():
    url = request.json.get('url', '').strip()
    if not url:
        return jsonify({"success": False, "error": "লিংক দাও!"}), 400

    start = time.time()
    print(f"[START] Processing: {url}")

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'quiet': False,
        'no_warnings': False,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'http_headers': {
            'Referer': url,
            'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
        },
        'simulate': True,
        'get_url': True,
        'postprocessor_args': ['-af', 'loudnorm=I=-16:TP=-1.5:LRA=11'],
    }

    # Cookies Support (সবচেয়ে গুরুত্বপূর্ণ)
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'
        print("[INFO] cookies.txt loaded successfully")

    # ==================== আলাদা আলাদা সাইট হ্যান্ডলিং ====================
    lower_url = url.lower()

    if 'tiktok' in lower_url:
        ydl_opts['http_headers'].update({
            'Referer': 'https://www.tiktok.com/',
            'Origin': 'https://www.tiktok.com',
            'Sec-Fetch-Site': 'same-origin'
        })
        print("[TIKTOK] Special headers applied")

    elif any(x in lower_url for x in ['terabox', '1024tera', '1024terabox']):
        ydl_opts['http_headers'].update({
            'Referer': 'https://www.terabox.com/',
            'Origin': 'https://www.terabox.com'
        })
        print("[TERABOX] Special handling + cookies")

    elif 't.me' in lower_url or 'telegram' in lower_url:
        ydl_opts['http_headers']['Referer'] = 'https://t.me/'

    elif 'instagram' in lower_url:
        ydl_opts['http_headers']['Referer'] = 'https://www.instagram.com/'

    elif 'facebook' in lower_url or 'fb.watch' in lower_url:
        ydl_opts['http_headers']['Referer'] = 'https://www.facebook.com/'

    elif 'youtube' in lower_url or 'youtu.be' in lower_url:
        ydl_opts['extractor_args'] = {'youtube': {'player_client': ['android', 'web']}}

    elif 'dailymotion' in lower_url:
        ydl_opts['http_headers']['Referer'] = 'https://www.dailymotion.com/'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            if not info:
                return jsonify({"success": False, "error": "ভিডিও পাওয়া যায়নি"}), 400

            video_url = info.get('url')
            if not video_url and 'formats' in info:
                formats = sorted(info['formats'], key=lambda f: (
                    f.get('vcodec', 'none') != 'none',
                    f.get('acodec', 'none') != 'none',
                    f.get('filesize') or 0
                ), reverse=True)
                video_url = next((f.get('url') for f in formats if f.get('url')), None)

            if not video_url:
                return jsonify({"success": False, "error": "Direct link পাওয়া যায়নি। cookies.txt আপলোড করো"}), 400

            print(f"[SUCCESS] {info.get('extractor_key')} | Time: {round(time.time()-start, 2)}s")

            return jsonify({
                "success": True,
                "title": info.get('title', 'Video'),
                "url": video_url,
                "thumb": info.get('thumbnail', ''),
                "site": info.get('extractor_key', 'Unknown'),
                "duration": info.get('duration_string', 'N/A')
            })

    except Exception as e:
        error = str(e)
        print(f"[ERROR] {error}")
        return jsonify({"success": False, "error": f"Error: {error[:300]}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=== Universal Save Pro Started - Supporting 1800+ Sites ===")
    app.run(host='0.0.0.0', port=port)
