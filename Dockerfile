# ১. একটি উপযুক্ত বেস ইমেজ ব্যবহার করা (যেমন পাইথনের জন্য)
FROM python:3.10-slim

# ২. সিস্টেমের প্রয়োজনীয় টুলস এবং ffmpeg ইনস্টল করা (আপনার লগ অনুযায়ী)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ৩. ওয়ার্কিং ডিরেক্টরি সেট করা
WORKDIR /app

# ৪. ডিপেন্ডেন্সি ফাইল কপি করা
COPY requirements.txt .

# ৫. পাইথন প্যাকেজগুলো ইনস্টল করা
RUN pip install --no-cache-dir -r requirements.txt

# ৬. ইমেজ আপলোডের জন্য uploads ফোল্ডার এবং ডেটাবেজের জন্য database.json তৈরি করা
# (এখানে -px পরিবর্তন করে -p করা হয়েছে)
RUN mkdir -p uploads && touch database.json && touch cookies.txt

# ৭. বাকি সব সোর্স ফাইল কপি করা
COPY . .

# ৮. ফ্ল্যাস্ক অ্যাপ্লিকেশনের পোর্ট এক্সপোজ করা
EXPOSE 5000

# ৯. অ্যাপ্লিকেশন রান করার কমান্ড
CMD ["python", "app.py"]
