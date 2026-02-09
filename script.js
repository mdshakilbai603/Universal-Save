async function startDownload() {
    const url = document.getElementById('videoUrl').value;
    const resCard = document.getElementById('resultCard');
    if(!url) return alert("Please paste a link!");

    document.querySelector('button').innerText = "Processing...";

    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        const data = await response.json();
        if(data.success) {
            resCard.style.display = "block";
            document.getElementById('videoTitle').innerText = data.title;
            document.getElementById('thumb').src = data.thumb;
            document.getElementById('dlLink').href = data.url;
        } else {
            alert("Error: Video not found!");
        }
    } catch (e) {
        alert("Server Busy!");
    } finally {
        document.querySelector('button').innerText = "Download";
    }
}
