# ১. অফিশিয়াল লাইটওয়েট পাইথন ইমেজ ব্যবহার করা হচ্ছে
FROM python:3.10-slim

# ২. yt-dlp এর জন্য সিস্টেমে ffmpeg এবং অন্যান্য প্রয়োজনীয় টুলস ইনস্টল করা
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ৩. কন্টেইনারের ভেতরে ওয়ার্কিং ডিরেক্টরি সেট করা
WORKDIR /app

# ৪. ডিপেনডেন্সি ফাইল কপি এবং ইনস্টল করা
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ৫. প্রজেক্টের বাকি সব ফাইল কন্টেইনারে কপি করা
COPY . .

# ৬. ইমেজ আপলোডের জন্য uploads ফোল্ডার এবং ডেটাবেজের জন্য database.json তৈরি করা
RUN mkdir -px uploads && touch database.json && touch cookies.txt

# ৭. ফ্ল্যাস্ক অ্যাপ্লিকেশনের পোর্ট এক্সপোজ করা
EXPOSE 5000

# ৮. অ্যাপ্লিকেশন রান করার কমান্ড
CMD ["python", "app.py"]
