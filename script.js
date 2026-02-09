async function getDownload() {
    const url = document.getElementById('urlInput').value;
    const resDiv = document.getElementById('result');
    if(!url) return alert("অনুগ্রহ করে একটি লিঙ্ক দিন!");

    resDiv.innerHTML = "প্রসেসিং... দয়া করে অপেক্ষা করুন।";

    try {
        const response = await fetch('https://your-app.onrender.com/api/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        const data = await response.json();
        if(data.success) {
            resDiv.innerHTML = `<a href="${data.download_url}" target="_blank" style="display:block; padding:10px; background:#22c55e; color:white; border-radius:8px; text-decoration:none;">ভিডিওটি ডাউনলোড করুন</a>`;
        } else {
            resDiv.innerHTML = "দুঃখিত! এই ভিডিওটি সাপোর্ট করছে না।";
        }
    } catch (e) {
        resDiv.innerHTML = "সার্ভার এরর! আবার চেষ্টা করুন।";
    }
}
