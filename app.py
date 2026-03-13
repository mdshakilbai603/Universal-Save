import os
import requests
import json
import time
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# মাস্টার কনফিগারেশন: যা তেরাবক্সের সিকিউরিটি ভাঙবে
class UniversalEngine:
    def __init__(self):
        self.ydl_opts = {
            'format': 'best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'extract_flat': False,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Referer': 'https://www.terabox.com/',
            }
        }

    def fetch(self, url):
        # তেরাবক্স বিশেষ হ্যান্ডলিং
        if "1024tera" in url or "terabox" in url:
            self.ydl_opts['referer'] = url
            
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    res = info['entries'][0]
                else:
                    res = info
                
                return {
                    "success": True,
                    "title": res.get('title', 'Universal Video'),
                    "url": res.get('url'),
                    "thumb": res.get('thumbnail', ''),
                    "site": info.get('extractor_key', 'Cloud Engine')
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

engine = UniversalEngine()

@app.route('/healthz')
def health():
    return "Engine Active", 200

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/api/fetch', methods=['POST'])
def api_fetch():
    url = request.json.get('url')
    if not url:
        return jsonify({"success": False, "error": "No URL"}), 400
    
    result = engine.fetch(url)
    return jsonify(result)

if __name__ == "__main__":
    # রেন্ডার পোর্টের জন্য ডাইনামিক সেটআপ
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
