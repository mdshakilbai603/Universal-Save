from flask import Flask, request, jsonify, send_from_directory
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# অ্যাডমিন সেটিংস (এগুলো তুমি প্যানেল থেকে কন্ট্রোল করবে)
config = {
    "download_limit": 5,
    "is_public": True,
    "premium_price": "99 BDT"
}

@app.route('/')
def home(): return send_from_directory('.', 'index.html')

@app.route('/api/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    try:
        with yt_dlp.YoutubeDL({'format': 'best', 'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                "success": True, 
                "title": info.get('title'), 
                "url": info.get('url'), 
                "thumb": info.get('thumbnail')
            })
    except: return jsonify({"success": False})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
