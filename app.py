import os
import requests
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# তেরাবক্স বাইপাস করার জন্য বিশেষ হেডার্স
YDL_OPTIONS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'extract_flat': False, # তেরাবক্সের ভেতরের ফাইল দেখার জন্য এটি False হওয়া জরুরি
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'http_headers': {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Referer': 'https://www.terabox.com/',
    }
}

@app.route('/healthz')
def health(): return "Server Alive", 200

@app.route('/')
def home(): return send_from_directory('.', 'index.html')

@app.route('/shakil-admin-pro')
def admin(): return send_from_directory('.', 'admin.html')

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "URL দিন"}), 400

    # তেরাবক্সের বিশেষ হ্যান্ডলিং
    if "1024tera" in url or "terabox" in url:
        YDL_OPTIONS['referer'] = url

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # তেরাবক্সের সেই জটিল লিঙ্ক থেকে ভিডিও বের করা
            info = ydl.extract_info(url, download=False)
            
            # তেরাবক্স অনেক সময় 'entries' হিসেবে রেজাল্ট দেয়
            if 'entries' in info:
                video_url = info['entries'][0].get('url')
                title = info['entries'][0].get('title')
                thumb = info['entries'][0].get('thumbnail')
            else:
                video_url = info.get('url')
                title = info.get('title')
                thumb = info.get('thumbnail')

            return jsonify({
                "success": True,
                "title": title or "Universal Video",
                "url": video_url,
                "thumb": thumb or ""
            })
    except Exception as e:
        return jsonify({"success": False, "error": "লিঙ্কটি কাজ করছে না। আবার চেষ্টা করুন।"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
