import os
import json
import logging
import tempfile
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, template_folder='.')
CORS(app)

# লগিং কনফিগারেশন
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# রেন্ডার বা ডকার কন্টেনারের জন্য নিরাপদ রাইট-পারমিশন ডিরেক্টরি (/tmp) ব্যবহার করা হয়েছে
BASE_TMP_DIR = tempfile.gettempdir()
UPLOAD_FOLDER = os.path.join(BASE_TMP_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DB_FILE = os.path.join(BASE_TMP_DIR, 'database.json')

# ১. ডেটাবেজ ফাইল পড়ার নিরাপদ ফাংশন
def read_db():
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        return {}
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading DB: {e}")
        return {}

# ২. ডেটাবেজ ফাইলে লেখার নিরাপদ ফাংশন
def write_db(data):
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error writing to DB: {str(e)}")

# ৩. প্রোগ্রেস হুক ফাংশন
def my_hook(d):
    try:
        if d.get('status') == 'downloading':
            total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
            downloaded = d.get('downloaded_bytes', 0)
            
            total_int = int(total) if total is not None else 0
            downloaded_int = int(downloaded) if downloaded is not None else 0
            
            if total_int > 0:
                percentage = (downloaded_int / total_int) * 100
                logger.info(f"Downloading: {percentage:.2f}%")
            else:
                logger.info(f"Downloaded bytes: {downloaded_int}")
        elif d.get('status') == 'finished':
            logger.info('Done downloading, now post-processing...')
    except Exception as e:
        logger.error(f"Hook error ignored: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(read_db())

@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.get_json() or {}
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL প্রদান করা হয়নি'}), 400

    # yt-dlp এর জন্য লিনাক্স সার্ভার ফ্রেন্ডলি ও নিরাপদ কনফিগারেশন
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(UPLOAD_FOLDER, '%(title)s.%(ext)s'),
        'progress_hooks': [my_hook],
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': True,
        'quiet': False,
        'prefer_insecure': True
    }

    # cookies.txt কারেন্ট ডিরেক্টরিতে রিড-অনলি হিসেবে চেক করা হবে
    cookie_path = os.path.join(os.getcwd(), 'cookies.txt')
    if os.path.exists(cookie_path) and os.path.getsize(cookie_path) > 0:
        ydl_opts['cookiefile'] = cookie_path

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return jsonify({'error': 'ভিডিওর তথ্য পাওয়া যায়নি বা লিংকটি সাপোর্ট করছে না'}), 400
                
            filename = ydl.prepare_filename(info)
            basename = os.path.basename(filename)
            
            # ডেটাবেজে ডাটা সংরক্ষণ
            db = read_db()
            video_id = info.get('id', 'unknown')
            db[video_id] = {
                'title': info.get('title', 'Unknown Title'),
                'filename': basename,
                'url': url
            }
            write_db(db)
            
            return jsonify({
                'success': True,
                'message': 'ডাউনলোড সফল হয়েছে!',
                'filename': basename
            })
            
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        # ফ্রন্টএন্ডে মূল এরর মেসেজটি পাস করা হচ্ছে যাতে ডিবাগ করা সহজ হয়
        return jsonify({'error': f"ডাউনলোড প্রসেস করতে সমস্যা হয়েছে! ডিটেইলস: {str(e)}"}), 500

@app.route('/uploads/<path:filename>')
def download_file(filename):
    # /tmp/uploads ডিরেক্টরি থেকে ফাইল ইউজারের ব্রাউজারে পাঠানো হবে
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
