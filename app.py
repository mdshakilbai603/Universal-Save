import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

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

# index.html এর জাভাস্ক্রিপ্ট এরর দূর করতে এই এপিআইটি যোগ করা হলো
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
        return jsonify({"success": False, "error": "লিঙ্ক দেওয়া হয়নি"}), 400
    
    # প্রতি রিকোয়েস্টের জন্য ফ্রেশ কনফিগারেশন
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'extract_flat': False,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'http_headers': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Referer': 'https://www.google.com/',
        }
    }

    # তেরাবক্সের জন্য বিশেষ কুকিজ এবং হেডার হ্যান্ডলিং
    if "1024tera" in target_url or "terabox" in target_url:
        ydl_opts['http_headers']['Referer'] = target_url

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=False)
            
            if not info:
                return jsonify({"success": False, "error": "ভিডিওর তথ্য পাওয়া যায়নি।"})

            video_url = info.get('url')
            if not video_url and 'entries' in info and len(info['entries']) > 0:
                video_url = info['entries'][0].get('url') or info['entries'][0].get('webpage_url')
            
            if not video_url:
                return jsonify({"success": False, "error": "সরাসরি ফাইল লিঙ্ক পাওয়া যায়নি।"})

            return jsonify({
                "success": True,
                "title": info.get('title', 'Video Found'),
                "url": video_url,
                "thumb": info.get('thumbnail', ''),
                "site": info.get('extractor_key', 'Engine')
            })
    except Exception as e:
        return jsonify({"success": False, "error": f"ইঞ্জিন এরর: {str(e)}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
