import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# মাস্টার কনফিগারেশন: যা সিকিউরিটি বাইপাস করতে সাহায্য করবে
YDL_OPTIONS = {
    'format': 'bestvideo+bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
    'extract_flat': False, # সব সাইটের ভেতরের লিঙ্ক বের করার জন্য False রাখা জরুরি
    'force_generic_extractor': False,
}

@app.route('/healthz')
def health():
    return "Global Server Active", 200

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    if not url or len(url.strip()) < 5:
        return jsonify({"success": False, "error": "সঠিক লিঙ্ক দিন"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # ভিডিওর আসল ডাটা টেনে আনা
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"success": False, "error": "ভিডিও ডাটা পাওয়া যায়নি"}), 404

            # বিভিন্ন সাইটের জন্য ভিডিও লিঙ্ক খোঁজার লজিক
            video_url = None
            if 'url' in info:
                video_url = info['url']
            elif 'entries' in info:
                video_url = info['entries'][0].get('url')
            elif 'formats' in info:
                # সবচেয়ে ভালো কোয়ালিটির লিঙ্ক নেওয়া
                video_url = info['formats'][-1].get('url')

            return jsonify({
                "success": True,
                "title": info.get('title', 'Video Found'),
                "url": video_url,
                "thumb": info.get('thumbnail', ''),
                "site": info.get('extractor_key', 'Unknown')
            })
    except Exception as e:
        return jsonify({"success": False, "error": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
