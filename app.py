import os
from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__, static_url_path='', static_folder='.')

# আপলোড করা ছবি রাখার ফোল্ডার সেটআপ
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ডাটাবেস (মেমোরিতে থাকবে, রেন্ডার রিস্টার্ট দিলে এটি রিসেট হতে পারে)
db = {
    "products": [],
    "orders": []
}

@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

# অ্যাডমিন প্যানেল রুট
@app.route('/shakil-admin-pro')
def admin():
    return send_from_directory('.', 'admin.html')

# হেলথ চেক (বটের জন্য)
@app.route('/healthz')
def health():
    return "OK", 200

# ছবিসহ পণ্য আপলোড করার এপিআই
@app.route('/api/add-product', methods=['POST'])
def add_product():
    name = request.form.get('name')
    price = request.form.get('price')
    file = request.files.get('image')
    
    if file and name and price:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        img_url = f"/uploads/{filename}"
        
        new_p = {
            "id": len(db['products']) + 1,
            "name": name,
            "price": price,
            "img": img_url
        }
        db['products'].append(new_p)
        return jsonify({"success": True})
    return jsonify({"success": False, "msg": "তথ্য অসম্পূর্ণ"})

# পণ্য ডিলিট করার এপিআই
@app.route('/api/delete-product/<int:p_id>', methods=['DELETE'])
def delete_product(p_id):
    db['products'] = [p for p in db['products'] if p['id'] != p_id]
    return jsonify({"success": True})

# কাস্টমার অর্ডার করার এপিআই
@app.route('/api/place-order', methods=['POST'])
def place_order():
    db['orders'].append(request.json)
    return jsonify({"success": True})

# সব ডাটা পাওয়ার এপিআই
@app.route('/api/data')
def get_data():
    return jsonify(db)

# আপলোড করা ছবি দেখানোর রুট
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
