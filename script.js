// তোমার index.html এর স্ক্রিপ্ট বা script.js ফাইলে এটি আপডেট করো
const response = await fetch('/api/download', { 
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: url })
});
