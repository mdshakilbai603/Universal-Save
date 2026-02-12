import os
from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# গ্লোবাল কনফিগারেশন: যা তেরাবক্স, টিকটক ও ডেইলি-মোশনের ব্লকিং এড়াবে
YDL_OPTIONS = {
    'format': 'bestvideo+bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'ignoreerrors': True,
    # কম্পিউটার ব্রাউজার হিসেবে পরিচয় দিবে যাতে সরাসরি অ্যাপে না পাঠায়
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/',
    'extract_flat': 'in_playlist',  # তেরাবক্স ফোল্ডার লিঙ্কের জন্য জরুরি
}

# ১. বট বা ক্রন-জবের জন্য (যাতে সাইট সব সময় জেগে থাকে)
@app.route('/healthz')
def health():
    return "Global Downloader is Active", 200

# ২. হোম পেজ (index.html)
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# ৩. অ্যাডমিন প্যানেল (shakil-admin-pro) - যা এখন Not Found দেখাবে না
@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

# ৪. ভিডিও ডাউনলোড এপিআই (বিশ্বের সব সাইটের জন্য)
@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    data = request.json
    url = data.get('url')
    
    # ইউআরএল ভ্যালিডেশন (খালি লিঙ্ক দিলে এরর হ্যান্ডেল করবে)
    if not url or len(url.strip()) < 5:
        return jsonify({"success": False, "error": "অনুগ্রহ করে একটি সঠিক লিঙ্ক দিন"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            # ভিডিওর অরিজিনাল ডাটা বের করা
            info = ydl.extract_info(url, download=False)
            
            if not info:
                return jsonify({"success": False, "error": "ভিডিওর তথ্য পাওয়া যায়নি"}), 404

            # সরাসরি ফাইল লিঙ্ক খুঁজে বের করা (তেরাবক্স ডিকোডার মেথড)
            video_url = info.get('url')
            if not video_url and 'entries' in info:
                video_url = info['entries'][0].get('url') or info['entries'][0].get('webpage_url')

            return jsonify({
                "success": True,
                "title": info.get('title', 'Universal Video'),
                "url": video_url,
                "thumb": info.get('thumbnail', ''),
                "site": info.get('extractor_key', 'Unknown')
            })
    except Exception as e:
        return jsonify({"success": False, "error": "সার্ভার এই লিঙ্কটি প্রসেস করতে পারছে না"}), 500

if __name__ == "__main__":
    # পোর্ট ৫০০৯ ব্যবহার করা হয়েছে যা রেন্ডারের জন্য আদর্শ
    app.run(host='0.0.0.0', port=10000)
