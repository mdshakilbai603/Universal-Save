async function startDownload() {
    const url = document.getElementById('videoUrl').value;
    const btn = document.querySelector('button');
    
    if(!url) return alert("অনুগ্রহ করে একটি লিঙ্ক দিন!");
    
    btn.innerText = "Processing...";
    btn.disabled = true;

    try {
        const response = await fetch('/api/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        const data = await response.json();
        
        if(data.success) {
            let resDiv = document.getElementById('result-area');
            if(!resDiv){
                resDiv = document.createElement('div');
                resDiv.id = 'result-area';
                resDiv.style.cssText = "margin-top:20px; background:rgba(255,255,255,0.1); padding:20px; border-radius:15px; color:#fff; border: 1px solid #3b82f6;";
                document.querySelector('.container').appendChild(resDiv);
            }
            resDiv.innerHTML = `
                <img src="${data.thumb}" width="100%" style="border-radius:10px; max-width:300px;">
                <h3 style="font-size:16px; margin:10px 0;">${data.title}</h3>
                <a href="${data.url}" target="_blank" style="display:inline-block; background:#22c55e; color:white; padding:12px 25px; border-radius:30px; text-decoration:none; font-weight:bold;">Download Now</a>
            `;
        } else {
            alert("দুঃখিত, ভিডিওটি পাওয়া যায়নি!");
        }
    } catch (e) {
        alert("সার্ভার ব্যস্ত আছে! আবার চেষ্টা করুন।");
    } finally {
        btn.innerText = "Download";
        btn.disabled = false;
    }
}

function openPayment() {
    // গ্লোবাল পেমেন্ট গেটওয়ে লজিক
    const userChoice = confirm("For Bkash/Nagad click 'OK'. For International Card/PayPal click 'Cancel'.");
    if(userChoice) {
        window.open("https://wa.me/8801989150941?text=I+want+to+buy+premium", "_blank");
    } else {
        window.open("https://www.buymeacoffee.com/shakil", "_blank");
    }
}
