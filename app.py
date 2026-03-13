import os
import requests
import json
import time
import re
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

class SuperDownloaderEngine:
    def __init__(self):
        # প্রো-লেভেল কনফিগারেশন যা ব্রাউজারের মতো আচরণ করবে
        self.base_opts = {
            'format': 'bestvideo+bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'extract_flat': False,
            'wait_for_video': (5, 30),
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.terabox.com/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Connection': 'keep-alive',
            }
        }

    def bypass_terabox(self, url):
        # তেরাবক্সের জন্য বিশেষ কুকিজ এবং হেডার হ্যান্ডলিং
        if "1024tera" in url or "terabox" in url:
            # তেরাবক্সের শর্ট লিঙ্ককে লং লিঙ্কে রূপান্তরের চেষ্টা
            self.base_opts['http_headers']['Referer'] = url
            return True
        return False

    def extract(self, url):
        is_tera = self.bypass_terabox(url)
        
        try:
            with yt_dlp.YoutubeDL(self.base_opts) as ydl:
                # তেরাবক্স অনেক সময় ফোল্ডার হিসেবে ডাটা দেয়, তাই ডিপ স্ক্যান করা হচ্ছে
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return {"success": False, "error": "ভিডিওর তথ্য পাওয়া যায়নি।"}

                # রেজাল্ট ফিল্টার করা
                video_url = info.get('url')
                if not video_url and 'entries' in info:
                    # যদি প্লে-লিস্ট বা ফোল্ডার হয়, তবে প্রথম ভিডিওটি নেওয়া হবে
                    video_url = info['entries'][0].get('url') or info['entries'][0].get('webpage_url')
                
                if not video_url:
                    return {"success": False, "error": "সরাসরি ফাইল লিঙ্ক পাওয়া যায়নি।"}

                return {
                    "success": True,
                    "title": info.get('title', 'Universal-Save Video'),
                    "url": video_url,
                    "thumb": info.get('thumbnail', ''),
                    "site": info.get('extractor_key', 'Global Engine'),
                    "duration": info.get('duration', 0)
                }
        except Exception as e:
            return {"success": False, "error": f"ইঞ্জিন এরর: {str(e)}"}

# ইঞ্জিন চালু করা
engine = SuperDownloaderEngine()

# --- রাউটিং শুরু ---

@app.route('/healthz')
def keep_alive():
    return "Engine Status: Online & Stable", 200

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

# অ্যাডমিন ডাটা হ্যান্ডলিং
@app.route('/api/data')
def get_admin_data():
    return jsonify({
        "products": [], # তোমার আপলোড করা প্রোডাক্ট এখানে আসবে
        "orders": []
    })

@app.route('/api/fetch', methods=['POST'])
def handle_fetch():
    target_url = request.json.get('url')
    if not target_url:
        return jsonify({"success": False, "error": "লিঙ্ক দেওয়া হয়নি"}), 400
    
    # পাওয়ারফুল ইঞ্জিন দিয়ে ভিডিও বের করা
    response = engine.extract(target_url)
    return jsonify(response)

# রেন্ডার সার্ভারের জন্য ডাইনামিক পোর্ট
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
