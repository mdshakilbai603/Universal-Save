from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')
CORS(app)

@app.route('/')
def home(): return send_from_directory('.', 'index.html')

@app.route('/preview')
def preview(): return send_from_directory('.', 'preview.html')

@app.route('/download-page')
def download_page(): return send_from_directory('.', 'download.html')

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True,
                "title": info.get('title'),
                "url": info.get('url'),
                "thumb": info.get('thumbnail')
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
