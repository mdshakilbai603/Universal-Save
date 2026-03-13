# পাইথন ইমেজ ব্যবহার করা হচ্ছে
FROM python:3.10-slim

# কাজের ডিরেক্টরি সেট করা
WORKDIR /app

# প্রয়োজনীয় সিস্টেম লাইব্রেরি ইনস্টল (ভিডিও প্রসেসিং এর জন্য)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# ফাইলগুলো কপি করা
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# গুনিকর্ন দিয়ে অ্যাপ রান করা
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
