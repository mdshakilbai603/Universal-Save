async function downloadVideo() {
    const url = document.getElementById('urlInput').value.trim();
    if (!url) {
        alert("লিংক পেস্ট করো প্রথমে!");
        return;
    }

    const loading = document.getElementById('loading');
    const result = document.getElementById('result');
    loading.style.display = 'block';
    result.style.display = 'none';

    try {
        const res = await fetch('/api/fetch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const data = await res.json();

        loading.style.display = 'none';

        if (data.success) {
            document.getElementById('title').textContent = data.title;
            document.getElementById('thumb').src = data.thumb || 'https://via.placeholder.com/800x450?text=Thumbnail';
            document.getElementById('downloadBtn').href = data.url;
            document.getElementById('duration').textContent = data.duration;
            document.getElementById('size').textContent = data.size ? (data.size / 1048576).toFixed(2) + ' MB' : 'Unknown';
            document.getElementById('site').textContent = `From: ${data.site}`;
            result.style.display = 'block';
        } else {
            alert("Error: " + data.error);
        }
    } catch (err) {
        loading.style.display = 'none';
        alert("Network/Server Error: " + err.message);
    }
}
