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

# জাভাস্ক্রিপ্টের ৪0৪ এরর এড়াতে এই ডামি বা গেট ডাটা রাউটটি সচল রাখা হলো
@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify({"status": "active"})

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
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', # স্ট্যান্ডার্ড mp4 ফরম্যাট ফোর্স করা হয়েছে
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

            # ফেসবুক বা অন্য সাইটের ডিরেক্ট ভিডিওর সোর্স ইউআরএল
            raw_video_url = video_data.get('url', '')
            
            if not raw_video_url:
                # যদি নির্দিষ্ট ফরম্যাটে লিংক না পাওয়া যায় তবে ব্যাকআপ লিংক চেক করবে
                formats = video_data.get('formats', [])
                for f in reversed(formats):
                    if f.get('url'):
                        raw_video_url = f['url']
                        break

            # প্রক্সি ইউআরএল তৈরি
            proxied_video_url = f"/api/proxy_video?stream_url={requests.utils.quote(raw_video_url)}" if raw_video_url else ""

            # ফ্রন্টএন্ডে দুরকম নামেই পাঠানো হলো যাতে কোনোভাবেই 'undefined' না হয়
            response_data = {
                'success': True,
                'title': video_data.get('title', 'Unknown Title'),
                'thumbnail': video_data.get('thumbnail', ''),
                'duration': video_data.get('duration', 0),
                'uploader': video_data.get('uploader', 'Unknown'),
                'video_url': proxied_video_url,
                'url': proxied_video_url, # ওল্ড জাভাস্ক্রিপ্ট কোডের ব্যাকআপের জন্য
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
            'Range': request.headers.get('Range', '') # ভিডিওর টেনে টুনে দেখার (Seeking) জন্য রেঞ্জ সাপোর্ট
        }
        
        r = requests.get(stream_url, headers=req_headers, stream=True, timeout=20)
        
        # প্রক্সি হেডার তৈরি
        response_headers = {
            'Content-Type': r.headers.get('Content-Type', 'video/mp4'),
            'Content-Length': r.headers.get('Content-Length', ''),
            'Accept-Ranges': 'bytes'
        }
        if r.headers.get('Content-Range'):
            response_headers['Content-Range'] = r.headers.get('Content-Range')

        def generate():
            for chunk in r.iter_content(chunk_size=256*1024): # স্মুথ প্লেব্যাকের জন্য ২৫৬KB চাঙ্ক
                if chunk:
                    yield chunk

        return Response(generate(), status=r.status_code, headers=response_headers)
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        return "Error streaming video", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False)
