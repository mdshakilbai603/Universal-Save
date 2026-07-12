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

@app.route('/api/fetch', methods=['POST'])
def fetch_video_data():
    data = request.get_json() or {}
    url_or_keyword = data.get('url')
    
    if not url_or_keyword:
        return jsonify({'error': 'লিংক বা কিউওয়ার্ড প্রদান করা হয়নি'}), 400

    ydl_opts = {
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
        'format': 'best',
    }

    if not url_or_keyword.startswith(('http://', 'https://')):
        url_or_keyword = f"ytsearch1:{url_or_keyword}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_or_keyword, download=False)
            
            if not info:
                return jsonify({'error': 'কোনো তথ্য পাওয়া যায়নি'}), 404
            
            if 'entries' in info:
                entries = list(info['entries'])
                if len(entries) > 0 and entries[0] is not None:
                    video_data = entries[0]
                else:
                    return jsonify({'error': 'কোনো ফলাফল পাওয়া যায়নি'}), 404
            else:
                video_data = info

            raw_video_url = video_data.get('url', '')
            video_id = video_data.get('id', 'unknown')

            # ফেসবুক/ইউটিউবের ডিরেক্ট লিংক ব্লক এড়াতে আমাদের নিজস্ব প্রক্সি লিংক তৈরি করা হলো
            proxied_video_url = f"/api/proxy_video?stream_url={requests.utils.quote(raw_video_url)}"

            response_data = {
                'success': True,
                'title': video_data.get('title', 'Unknown Title'),
                'thumbnail': video_data.get('thumbnail', ''),
                'duration': video_data.get('duration', 0),
                'uploader': video_data.get('uploader', 'Unknown'),
                'video_url': proxied_video_url, # ফ্রন্টএন্ডে এখন এই নিরাপদ লিংকটি যাবে
                'original_url': video_data.get('webpage_url', '')
            }
            
            return jsonify(response_data)

    except Exception as e:
        logger.error(f"Fetch error: {str(e)}")
        return jsonify({'error': f"তথ্য খোঁজার প্রসেসটি ব্যর্থ হয়েছে। এরর: {str(e)}"}), 500

# ৩. নতুন ভিডিও প্রক্সি রাউট (যা ফেসবুক/ইউটিউবের ভিডিও ব্লকিং বাইপাস করবে)
@app.route('/api/proxy_video')
def proxy_video():
    stream_url = request.args.get('stream_url')
    if not stream_url:
        return "Missing URL", 400
    
    try:
        # রেন্ডার সার্ভার নিজে ভিডিও স্ট্রিমটি রিকোয়েস্ট করছে
        req_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        r = requests.get(stream_url, headers=req_headers, stream=True, timeout=15)
        
        # ব্রাউজারে ডাটা চাংক বা খণ্ড আকারে স্ট্রিম করে পাঠানো হচ্ছে
        def generate():
            for chunk in r.iter_content(chunk_size=1024*1024): # 1MB chunks
                if chunk:
                    yield chunk

        return Response(generate(), content_type=r.headers.get('Content-Type', 'video/mp4'))
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return "Error streaming video", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False)
