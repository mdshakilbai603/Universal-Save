import os
import json
import logging
import requests
from flask import Flask, request, jsonify, render_template, Response, redirect, url_for
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, template_folder='.')
app.secret_key = os.environ.get('SECRET_KEY', 'universal_save_super_secret_key')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN_FILE = 'youtube_oauth_cache.json'
pending_oauth_data = {}

def custom_oauth_hook(action, data):
    global pending_oauth_data
    if action == 'pre_auth':
        pending_oauth_data = {
            'code': data.get('user_code'),
            'url': data.get('verification_url')
        }

# ১. চেক করা হবে ইউজার আগে লগইন করেছে কি না
@app.route('/')
def index():
    if not os.path.exists(TOKEN_FILE):
        # যদি লগইন টোকেন না থাকে, তবে সরাসরি লগইন পেজে পাঠিয়ে দেবে
        return render_template('login.html')
    return render_template('index.html')

# ২. গুগলের ওওথ কোড জেনারেট করার রুট
@app.route('/api/start-login', methods=['GET'])
def start_login():
    global pending_oauth_data
    pending_oauth_data = {}
    
    ydl_opts = {
        'extractor_args': {
            'youtube': {
                'oauth': True,
                'oauth_cache': TOKEN_FILE
            }
        }
    }
    ydl_opts['extractor_args']['youtube']['oauth_hook'] = custom_oauth_hook
    
    try:
        # এটি গুগলের কাছ থেকে কোডটি টেনে আনবে
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.extract_info('https://www.youtube.com/watch?v=dQw4w9WgXcQ', download=False)
            except Exception:
                pass # কোড জেনারেট হয়ে গেলে এরর আসলেও সমস্যা নেই
        
        if pending_oauth_data and 'code' in pending_oauth_data:
            return jsonify({
                'success': True,
                'google_code': pending_oauth_data['code'],
                'redirect_url': pending_oauth_data['url']
            })
        return jsonify({'success': False, 'error': 'গুগল কোড জেনারেট করতে পারেনি। আবার চেষ্টা করুন।'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ৩. লগইন সম্পন্ন হয়েছে কি না তা চেক করার রুট
@app.route('/api/check-login-status', methods=['GET'])
def check_login_status():
    if os.path.exists(TOKEN_FILE):
        return jsonify({'logged_in': True})
    return jsonify({'logged_in': False})

# ৪. মূল ভিডিও ফেচ করার রুট
@app.route('/api/fetch', methods=['POST'])
def fetch_video_data():
    if not os.path.exists(TOKEN_FILE):
        return jsonify({'error': 'দয়া করে আগে গুগল লগইন সম্পন্ন করুন।'}), 401

    data = request.get_json() or {}
    url_or_keyword = data.get('url')
    
    if not url_or_keyword:
        return jsonify({'error': 'লিংক বা কিуওয়ার্ড প্রদান করা হয়নি'}), 400

    ydl_opts = {
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'quiet': False,
        'format': 'best[ext=mp4]/best',
        'extractor_args': {
            'youtube': {
                'oauth': True,
                'oauth_cache': TOKEN_FILE
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }
    }

    if not url_or_keyword.startswith(('http://', 'https://')):
        url_or_keyword = f"ytsearch1:{url_or_keyword}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_or_keyword, download=False)
            
            if 'entries' in info:
                entries = list(info['entries'])
                video_data = entries[0] if entries and entries[0] is not None else info
            else:
                video_data = info

            raw_video_url = None
            formats = video_data.get('formats', [])
            for f in reversed(formats):
                if f.get('url') and f.get('acodec') != 'none' and f.get('vcodec') != 'none':
                    if "manifest" not in f['url']:
                        raw_video_url = f['url']
                        break
            
            if not raw_video_url:
                raw_video_url = video_data.get('url', '')

            if not raw_video_url:
                return jsonify({'error': 'ভিডিওর প্লেব্যাক লিংক পাওয়া যায়নি'}), 404

            proxied_video_url = f"/api/proxy_video?stream_url={requests.utils.quote(raw_video_url)}"

            return jsonify({
                'success': True,
                'title': video_data.get('title', 'Unknown Title'),
                'thumbnail': video_data.get('thumbnail', ''),
                'duration': video_data.get('duration', 0),
                'uploader': video_data.get('uploader', 'Unknown'),
                'video_url': proxied_video_url,
                'url': proxied_video_url,
                'filename': video_data.get('title', 'video') + '.mp4'
            })

    except Exception as e:
        return jsonify({'error': f"ব্যর্থ হয়েছে। কারণ: {str(e)}"}), 500

@app.route('/api/proxy_video')
def proxy_video():
    stream_url = request.args.get('stream_url')
    if not stream_url:
        return "Missing URL", 400
    try:
        req_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Range': request.headers.get('Range', '')
        }
        r = requests.get(stream_url, headers=req_headers, stream=True, timeout=20)
        response_headers = {
            'Content-Type': r.headers.get('Content-Type', 'video/mp4'),
            'Content-Length': r.headers.get('Content-Length', ''),
            'Accept-Ranges': 'bytes'
        }
        if r.headers.get('Content-Range'):
            response_headers['Content-Range'] = r.headers.get('Content-Range')

        def generate():
            for chunk in r.iter_content(chunk_size=256*1024):
                if chunk:
                    yield chunk
        return Response(generate(), status=r.status_code, headers=response_headers)
    except Exception as e:
        return "Error streaming video", 500

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"status": "active", "products": [], "orders": []})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False)
