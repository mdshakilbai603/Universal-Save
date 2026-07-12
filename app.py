import os
import json
import logging
import requests
import re
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, template_folder='.')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN_FILE = 'youtube_oauth_cache.json'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"status": "active"})

@app.route('/api/fetch', methods=['POST'])
def fetch_video_data():
    data = request.get_json() or {}
    url_or_keyword = data.get('url')
    
    if not url_or_keyword:
        return jsonify({'error': 'লিংক বা কিউওয়ার্ড প্রদান করা হয়নি'}), 400

    # ওঅথ (OAuth) মেকানিজম জোরপূর্বক রান করানোর জন্য কনফিগারেশন
    ydl_opts = {
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'no_warnings': False,
        'quiet': False,
        'format': 'best[ext=mp4]/best',
        'extractor_args': {
            'youtube': {
                'player_client': ['tv'], # TV ক্লায়েন্ট ওঅথ কোড জেনারেশনকে বাধ্য করে
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
        err_msg = str(e)
        logger.error(f"Fetch Error Raw: {err_msg}")
        
        # যদি ইউটিউব সাইন-ইন বা বট ভেরিফিকেশন চায় (সব ধরণের এরর ফিল্টার করা হচ্ছে)
        if "confirm you're not a bot" in err_msg or "Sign in" in err_msg or "oauth" in err_msg.lower():
            # রেগুলার এক্সপ্রেশন দিয়ে কোড খোঁজার চেষ্টা, যদি তাও ব্যর্থ হয় তবে ইউজারকে ডিরেক্ট ইনস্ট্রাকশন দেওয়া
            code_match = re.search(r'enter the code\s+([A-Z0-9\-]+)', err_msg)
            display_code = code_match.group(1) if code_match else "রেন্ডার লগে পাঠানো হয়েছে"
            
            return jsonify({
                'error': 'গুগল ভেরিফিকেশন প্রয়োজন',
                'oauth_needed': True,
                'verification_url': 'https://google.com/device',
                'user_code': display_code,
                'message': 'ইউটিউব বট প্রোটেকশন বাইপাস করতে আপনার জিমেইল অ্যাকাউন্ট দিয়ে একবার ভেরিফাই করে নিন। নিচে দেওয়া লিংকে ক্লিক করে কোডটি বসান।'
            }), 401
            
        return jsonify({'error': f"ব্যর্থ হয়েছে। কারণ: {err_msg}"}), 500

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
        logger.error(f"Proxy error: {e}")
        return "Error streaming video", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False)
