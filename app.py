import os
import json
import logging
import requests
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, template_folder='.')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    # ইউটিউবের বট সনাক্তকরণ এবং ফেসবুকের কম্বাইন্ড ফরম্যাট একসাথে হ্যান্ডেল করার অপশন
    ydl_opts = {
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
        'format': 'best[ext=mp4]/best', # ফেসবুক ও অন্যান্যদের জন্য কমপ্লিট অডিও-ভিডিও ট্র্যাক
        
        # ইউটিউব বট প্রোটেকশন বাইপাস করার জন্য আইওএস ও অ্যান্ড্রয়েড ক্লায়েন্ট ফোর্স করা হলো
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'android', 'web_embedded'],
                'skip': ['webpage', 'authcheck']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
    }

    if not url_or_keyword.startswith(('http://', 'https://')):
        url_or_keyword = f"ytsearch1:{url_or_keyword}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_or_keyword, download=False)
            
            if not info:
                return jsonify({'error': 'কোনো তথ্য পাওয়া যায়নি বা সাইটটি সাময়িকভাবে ব্লক করেছে'}), 404
            
            if 'entries' in info:
                entries = list(info['entries'])
                if len(entries) > 0 and entries[0] is not None:
                    video_data = entries[0]
                else:
                    return jsonify({'error': 'কোনো ফলাফল পাওয়া যায়নি'}), 404
            else:
                video_data = info

            raw_video_url = None
            formats = video_data.get('formats', [])
            
            # ফেসবুক/ইনস্টাগ্রাম কম্বাইন্ড অডিও-ভিডিও ট্র্যাক ফিল্টারিং
            for f in reversed(formats):
                if f.get('url') and f.get('acodec') != 'none' and f.get('vcodec') != 'none':
                    raw_video_url = f['url']
                    break
            
            if not raw_video_url:
                raw_video_url = video_data.get('url', '')

            if not raw_video_url:
                return jsonify({'error': 'ভিডিওর প্লেব্যাক লিংক পাওয়া যায়নি'}), 404

            proxied_video_url = f"/api/proxy_video?stream_url={requests.utils.quote(raw_video_url)}"

            response_data = {
                'success': True,
                'title': video_data.get('title', 'Unknown Title'),
                'thumbnail': video_data.get('thumbnail', ''),
                'duration': video_data.get('duration', 0),
                'uploader': video_data.get('uploader', 'Unknown'),
                'video_url': proxied_video_url,
                'url': proxied_video_url,
                'filename': video_data.get('title', 'video') + '.mp4'
            }
            
            return jsonify(response_data)

    except Exception as e:
        logger.error(f"Fetch error: {str(e)}")
        return jsonify({'error': f"তথ্য খোঁজার প্রসেসটি ব্যর্থ হয়েছে। এরর: {str(e)}"}), 500

@app.route('/api/proxy_video')
def proxy_video():
    stream_url = request.args.get('stream_url')
    if not stream_url:
        return "Missing URL", 400
    
    try:
        req_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
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
