import os
import json
import logging
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, template_folder='.')
CORS(app)

# লগিং কনফিগারেশন
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ডিরেক্টরি তৈরি নিশ্চিত করা
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

DB_FILE = 'database.json'

# ১. ডেটাবেজ ফাইল পড়ার ফাংশন (JSON Decode Error এর স্থায়ী সমাধান)
def read_db():
    if not os.path.exists(DB_FILE) or os.path.getsize(DB_FILE) == 0:
        return {}
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception):
        return {}

# ২. ডেটাবেজ ফাইলে লেখার ফাংশন
def write_db(data):
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_stdout=False)
    except Exception as e:
        logger.error(f"Error writing to DB: {str(e)}")

# ৩. প্রোগ্রেস হুক ফাংশন (NoneType < int এরর এর স্থায়ী সমাধান)
def my_hook(d):
    if d['status'] == 'downloading':
        # এখানে safely ডিকশনারি থেকে ডেটা নেওয়া হচ্ছে, না থাকলে ডিফল্ট ০ বা None সেট হবে
        total = d.get('total_bytes') or d.get('total_bytes_estimate') or 0
        downloaded = d.get('downloaded_bytes', 0)
        
        # safely None টাইপ চেক করে ইন্টিজারে রূপান্তর
        total_int = int(total) if total is not None else 0
        downloaded_int = int(downloaded) if downloaded is not None else 0
        
        if total_int > 0:
            percentage = (downloaded_int / total_int) * 100
            logger.info(f"Downloading: {percentage:.2f}%")
        else:
            logger.info(f"Downloaded bytes: {downloaded_int}")
            
    elif d['status'] == 'finished':
        logger.info('Done downloading, now post-processing...')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    db = read_db()
    return jsonify(db)

@app.route('/api/download', methods=['POST'])
def download_video():
    data = request.get_json() or {}
    url = data.get('url')
    
    if not url:
        return jsonify({'error': 'URL প্রদান করা হয়নি'}), 400

    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(UPLOAD_FOLDER, '%(title)s.%(ext)s'),
        'progress_hooks': [my_hook],
        'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
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
        return jsonify({'error': f"সার্ভার প্রসেসিং এরর: {str(e)}"}), 500

@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
