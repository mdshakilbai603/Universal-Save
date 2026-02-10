// ১. ভিডিও ডাউনলোড জেনারেটর ফাংশন
async function startDownload() {
    const urlInput = document.getElementById('videoUrl');
    const btn = document.querySelector('.btn-pro') || document.querySelector('button');
    const resultCard = document.getElementById('resultCard');

    if (!urlInput.value) {
        alert("দয়া করে একটি ভিডিও লিঙ্ক পেস্ট করুন!");
        return;
    }

    // বাটন লোডিং এনিমেশন
    const originalText = btn.innerText;
    btn.innerText = "Processing...";
    btn.disabled = true;

    try {
        const response = await fetch('/api/fetch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: urlInput.value })
        });

        const data = await response.json();

        if (data.success) {
            // প্রিভিউ কার্ডে ডাটা বসানো
            document.getElementById('vTitle').innerText = data.title;
            document.getElementById('vThumb').src = data.thumb;
            document.getElementById('vDl').href = data.url;
            
            // রেজাল্ট দেখানো
            resultCard.style.display = 'block';
            resultCard.scrollIntoView({ behavior: 'smooth' });
        } else {
            alert("দুঃখিত! ভিডিওটি পাওয়া যায়নি। লিঙ্কটি পুনরায় চেক করুন।");
        }
    } catch (error) {
        console.error("Error:", error);
        alert("সার্ভার সমস্যা! কিছুক্ষণ পর চেষ্টা করুন।");
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}

// ২. মার্কেটিং পণ্য অটোমেটিক লোড করা
async function loadMarketingProducts() {
    const shopGrid = document.getElementById('productGrid');
    if (!shopGrid) return;

    try {
        const res = await fetch('/api/config');
        const data = await res.json();
        
        shopGrid.innerHTML = ''; // আগের ডামি ডাটা পরিষ্কার করা
        
        data.products.forEach(p => {
            shopGrid.innerHTML += `
                <div class="p-card">
                    <img src="${p.img}" class="p-img" alt="${p.name}">
                    <h3>${p.name}</h3>
                    <p style="color:#0070f3; font-weight:bold; font-size:20px;">${p.price} BDT</p>
                    <button class="btn-pro" style="width:100%;" onclick="placeOrder('${p.name}')">অর্ডার করুন</button>
                </div>`;
        });
    } catch (err) {
        console.log("মার্কেটিং আইটেম লোড করা যায়নি।");
    }
}

// ৩. রিয়েল অর্ডার ফাংশন
async function placeOrder(productName) {
    const phone = prompt(`${productName} অর্ডার করতে আপনার ফোন নম্বর দিন:`);
    
    if (phone) {
        try {
            const res = await fetch('/api/place-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item: productName, phone: phone })
            });
            const result = await res.json();
            if (result.success) {
                alert("আপনার অর্ডারটি সফল হয়েছে! শাকিল শীঘ্রই আপনার সাথে যোগাযোগ করবে।");
            }
        } catch (err) {
            alert("অর্ডার নেওয়া সম্ভব হয়নি।");
        }
    }
}

// ৪. ওপেন পেমেন্ট গেটওয়ে (Premium)
function openPayment() {
    const confirmPay = confirm("আনলিমিটেড ভিডিও এবং বিজ্ঞাপন মুক্ত প্রিমিয়াম মেম্বারশিপ নিতে চান?\n\nফি: ৯৯ টাকা।");
    
    if (confirmPay) {
        // তোমার পার্সোনাল পেমেন্ট মেসেজ বা লিঙ্ক
        alert("বিকাশ/নগদ (পার্সোনাল): ০১৭XXXXXXXX\nটাকা পাঠানোর পর ট্রানজিশন আইডি দিয়ে শাকিলকে মেসেজ দিন।");
    }
}

// ৫. ভাষা পরিবর্তন (অটো-সেভ)
function changeLanguage(lang) {
    localStorage.setItem('prefLang', lang);
    // এখানে তোমার ট্রান্সলেশন লজিক কাজ করবে
    location.reload(); 
}

// পেজ লোড হওয়ার পর শপিং আইটেম দেখানো
window.onload = loadMarketingProducts;
