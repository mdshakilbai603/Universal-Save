FROM python:3.12-slim

# সিস্টেম ডিপেন্ডেন্সি ইনস্টল (ffmpeg খুব জরুরি yt-dlp এর জন্য)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# প্রথমে requirements কপি করে ইনস্টল (লেয়ার ক্যাশিং এর জন্য)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# অ্যাপ্লিকেশন ফাইল কপি
COPY . .

# নন-রুট ইউজার তৈরি (সিকিউরিটির জন্য)
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 5000

# হেলথচেক
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/healthz || exit 1

# গুনিকর্ন দিয়ে রান (প্রোডাকশনের জন্য ভালো)
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT:-5000}", \
     "--workers", "2", \
     "--threads", "4", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "app:app"]
