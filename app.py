from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# তেরাবক্স ও ফেসবুকের অ্যাপ রিডাইরেক্ট বন্ধ করার জন্য বিশেষ অপশন
YDL_OPTS = {
    'format': 'best',
    'quiet': True,
    'no_warnings': True,
    'nocheckcertificate': True,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'referer': 'https://www.google.com/' # এটি দিলে ফেসবুক অ্যাপে না পাঠিয়ে ব্রাউজারে ডাটা দিবে
}

@app.route('/healthz')
def health(): return "Server Alive", 200

@app.route('/')
def home(): return send_from_directory('.', 'index.html')

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    if not url: return jsonify({"success": False, "error": "No URL"}), 400

    try:
        with yt_dlp.YoutubeDL(YDL_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)
            # অ্যাপ লিঙ্ক নয়, সরাসরি ভিডিও ফাইল লিঙ্ক খোঁজা
            direct_link = info.get('url') or (info.get('entries')[0].get('url') if 'entries' in info else None)
            
            return jsonify({
                "success": True,
                "title": info.get('title', 'Video Found'),
                "url": direct_link, # এটিই সরাসরি ডাউনলোড করবে
                "thumb": info.get('thumbnail', '')
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
