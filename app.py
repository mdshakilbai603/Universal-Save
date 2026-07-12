import os
import time
import json
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import yt_dlp

app = Flask(__name__, static_url_path='', static_folder='.')

# আপলোড করা ছবির ফোল্ডার সেটআপ
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ডেটাবেজ ফাইল পাথ (পণ্য ও অর্ডারের জন্য)
DATA_FILE = 'database.json'

def init_db():
    """ডেটাবেজ ফাইল না থাকলে তৈরি করে"""
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({"products": [], "orders": []}, f, ensure_ascii=False, indent=4)

def read_db():
    init_db()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_db(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/healthz')
def keep_alive():
    return "Universal Save Pro - 1800+ Sites | Status: Active", 200

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# ==================== CORE FETCHER & GOOGLE SEARCH ENGINE ====================

@app.route('/api/fetch', methods=['POST'])
def handle_fetch():
    url = request.json.get('url', '').strip()
    if not url:
        return jsonify({"success": False, "error": "লিংক অথবা সার্চ কুয়েরি দাও!"}), 400

    start = time.time()
    print(f"[START] Processing: {url}")

    # চেক করা হচ্ছে এটি সাধারণ লিংক নাকি সার্চ করার জন্য টেক্সট (Google Search Bar Logic)
    is_search = not (url.startswith('http://') or url.startswith('https://'))
    
    # যদি সাধারণ টেক্সট হয়, তবে সেটিকে yt-dlp এর মাধ্যমে সার্চ কুয়েরিতে রূপান্তর করা হবে
    final_query = f"ytsearch1:{url}" if is_search else url

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'noplaylist': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'http_headers': {
            'Referer': 'https://www.google.com/' if is_search else url,
            'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
        },
        'simulate': True,
    }

    # সাইট ভিত্তিক উন্নত ট্রাফিক হ্যান্ডলিং
    lower_url = url.lower()
    if 'tiktok' in lower_url:
        ydl_opts['http_headers']['Referer'] = 'https://www.tiktok.com/'
    elif any(x in lower_url for x in ['terabox', '1024tera']):
        ydl_opts['http_headers']['Referer'] = 'https://www.terabox.com/'
    elif 'instagram' in lower_url:
        ydl_opts['http_headers']['Referer'] = 'https://www.instagram.com/'
    elif 'facebook' in lower_url or 'fb.watch' in lower_url:
        ydl_opts['http_headers']['Referer'] = 'https://www.facebook.com/'
    elif 'youtube' in lower_url or 'youtu.be' in lower_url:
        ydl_opts['extractor_args'] = {'youtube': {'player_client': ['android', 'ios', 'web']}}
    elif 'twitter' in lower_url or 'x.com' in lower_url:
        ydl_opts['http_headers']['Referer'] = 'https://twitter.com/'

    # প্রথমবার কুকিজ ফাইল দিয়ে চেষ্টা করার জন্য
    if os.path.exists('cookies.txt'):
        ydl_opts['cookiefile'] = 'cookies.txt'
        print("[INFO] cookies.txt loaded for primary attempt")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(final_query, download=False)
            except Exception as e:
                # যদি কুকিজের কারণে ফেসবুক/ইউটিউবে কোনো এরর আসে, তবে কুকিজ ছাড়া আরেকবার চেষ্টা (Fallback Strategy)
                if 'cookie' in str(e).lower() and 'cookiefile' in ydl_opts:
                    print("[WARN] Cookie error detected. Retrying without cookies...")
                    del ydl_opts['cookiefile']
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl_retry:
                        info = ydl_retry.extract_info(final_query, download=False)
                else:
                    raise e

            if not info:
                return jsonify({"success": False, "error": "কোনো রেজাল্ট পাওয়া যায়নি!"}), 404

            # সার্চ কুয়েরি হলে প্রথম রেজাল্ট এক্সট্রাক্ট করা
            if 'entries' in info and info['entries']:
                info = info['entries'][0]

            # ডাইরেক্ট ভিডিও বা বেস্ট ফরম্যাট ইউআরএল খোঁজার অ্যালগরিদম
            video_url = info.get('url')
            if not video_url and 'formats' in info:
                formats = sorted(info['formats'], key=lambda f: (
                    f.get('height', 0),
                    f.get('filesize') or 0,
                    f.get('vcodec', '') != 'none',
                    f.get('acodec', '') != 'none'
                ), reverse=True)
                video_url = next((f.get('url') for f in formats if f.get('url')), None)

            if not video_url:
                return jsonify({"success": False, "error": "ডাইরেক্ট ডাউনলোড লিংক পাওয়া যায়নি!"}), 400

            print(f"[SUCCESS] {info.get('extractor_key', 'Search')} | Time: {round(time.time()-start, 2)}s")

            return jsonify({
                "success": True,
                "title": info.get('title', 'Requested File'),
                "url": video_url,
                "thumb": info.get('thumbnail', ''),
                "site": info.get('extractor_key', 'Search Engine'),
                "duration": info.get('duration_string', 'N/A')
            })

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"success": False, "error": f"সার্ভার প্রসেসিং এরর: {str(e)[:150]}"}), 500


# ==================== DYNAMIC STOREFRONT & ORDER SYSTEM ====================

@app.route('/api/data', methods=['GET'])
def get_data():
    db = read_db()
    return jsonify(db)

@app.route('/api/add-product', methods=['POST'])
def add_product():
    try:
        name = request.form.get('name')
        price = request.form.get('price')
        image = request.files.get('image')

        if not name or not price or not image:
            return jsonify({"success": False, "error": "সবগুলো ফিল্ড পূরণ করো!"}), 400

        filename = secure_filename(image.filename)
        unique_filename = f"{int(time.time())}_{filename}"
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))

        db = read_db()
        new_product = {
            "id": int(time.time()),
            "name": name,
            "price": price,
            "img": f"/uploads/{unique_filename}"
        }
        db['products'].append(new_product)
        write_db(db)

        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/delete-product/<int:prod_id>', methods=['DELETE'])
def delete_product(prod_id):
    db = read_db()
    db['products'] = [p for p in db['products'] if p['id'] != prod_id]
    write_db(db)
    return jsonify({"success": True})

@app.route('/api/place-order', methods=['POST'])
def place_order():
    item = request.json.get('item')
    phone = request.json.get('phone')

    if not item or not phone:
        return jsonify({"success": False, "error": "প্রোডাক্ট এবং ফোন নাম্বার লাগবে"}), 400

    db = read_db()
    new_order = {
        "id": int(time.time()),
        "item": item,
        "phone": phone,
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }
    db['orders'].append(new_order)
    write_db(db)

    return jsonify({"success": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("=== Universal Save Pro Started - Powered by Shakil ===")
    app.run(host='0.0.0.0', port=port)