import os
import json
import logging
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, template_folder='.')
CORS(app)

# লগিং কনফিগারেশন
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ১. ফ্রন্টএন্ড পেজ লোড রাউট
@app.route('/')
def index():
    return render_template('index.html')

# ২. মূল রাউট যা ফ্রন্টএন্ড থেকে সার্চ বা ভিডিও লিংক রিসিভ করবে
@app.route('/api/fetch', methods=['POST'])
def fetch_video_data():
    data = request.get_json() or {}
    url_or_keyword = data.get('url') # ফ্রন্টএন্ড থেকে পাঠানো ইনপুট
    
    if not url_or_keyword:
        return jsonify({'error': 'লিংক বা কিউওয়ার্ড প্রদান করা হয়নি'}), 400

    # গুগল/ইউটিউব সার্চ বা ডিরেক্ট লিংকের জন্য কনফিগারেশন (ভিডিও ডাউনলোড হবে না, শুধু ডেটা আসবে)
    ydl_opts = {
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
        'format': 'best',
    }

    # যদি ডিরেক্ট লিংক না হয়ে নরমাল টেক্সট (সার্চ কিউওয়ার্ড) হয়, তবে ইউটিউব সার্চ সক্রিয় করবে
    if not url_or_keyword.startswith(('http://', 'https://')):
        url_or_keyword = f"ytsearch1:{url_or_keyword}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # download=False রাখা হয়েছে যাতে ফাইল সার্ভারে ডাউনলোড না হয়ে শুধু প্লে করার লিংক আসে
            info = ydl.extract_info(url_or_keyword, download=False)
            
            if not info:
                return jsonify({'error': 'কোনো তথ্য পাওয়া যায়নি! অনুগ্রহ করে সঠিক লিংক বা কিউওয়ার্ড দিন।'}), 404
            
            # সার্চ রেজাল্ট হলে প্রথম ভিডিওর ডাটা নেবে
            if 'entries' in info:
                entries = list(info['entries'])
                if len(entries) > 0 and entries[0] is not None:
                    video_data = entries[0]
                else:
                    return jsonify({'error': 'কোনো ফলাফল পাওয়া যায়নি'}), 404
            else:
                video_data = info

            # ফ্রন্টএন্ডে প্লে করার জন্য প্রয়োজনীয় ডাটা গুছিয়ে পাঠানো হচ্ছে
            response_data = {
                'success': True,
                'title': video_data.get('title', 'Unknown Title'),
                'thumbnail': video_data.get('thumbnail', ''),
                'duration': video_data.get('duration', 0),
                'uploader': video_data.get('uploader', 'Unknown'),
                'video_url': video_data.get('url', ''), # সরাসরি প্লে করার ডিরেক্ট স্ট্রিম লিংক
                'original_url': video_data.get('webpage_url', '')
            }
            
            return jsonify(response_data)

    except Exception as e:
        logger.error(f"Fetch error: {str(e)}")
        return jsonify({'error': f"তথ্য খোঁজার প্রসেসটি ব্যর্থ হয়েছে। এরর: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)), debug=False)
