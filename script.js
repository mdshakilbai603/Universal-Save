async function startDownload() {
    const url = document.getElementById('videoUrl').value;
    const btn = document.querySelector('button'); // তোমার ডাউনলোড বাটন
    const resultCard = document.getElementById('resultCard');

    if (!url) {
        alert("Please paste a valid link first!");
        return;
    }

    // বাটন এনিমেশন
    btn.innerHTML = `<span class="loader"></span> Processing...`;
    btn.disabled = true;

    try {
        // ব্যাকএন্ডে রিকোয়েস্ট পাঠানো
        const response = await fetch('/api/fetch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        
        const data = await response.json();

        if (data.success) {
            // ডাটা সেট করা
            document.getElementById('videoTitle').innerText = data.title;
            document.getElementById('videoThumb').src = data.thumb;
            document.getElementById('downloadBtn').href = data.url;

            // প্রিভিউ বক্সটি সুন্দর করে দেখানো
            resultCard.style.display = 'block';
            resultCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
            alert("Sorry, could not fetch video. Check the link!");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("Server Busy! Try again later.");
    } finally {
        btn.innerHTML = "Download";
        btn.disabled = false;
    }
}
