async function loadMarketing() {
    const response = await fetch('/api/data');
    const data = await response.json();
    const marketGrid = document.getElementById('marketGrid'); // তোমার HTML আইডি অনুযায়ী
    
    if (data.products.length > 0) {
        marketGrid.innerHTML = data.products.map(p => `
            <div class="product-card">
                <img src="${p.img}" alt="${p.name}" style="width:100%; border-radius:10px;">
                <h4>${p.name}</h4>
                <p>${p.price} BDT</p>
                <button onclick="placeOrder('${p.name}')">Buy Now</button>
            </div>
        `).join('');
    }
}
window.onload = loadMarketing;
