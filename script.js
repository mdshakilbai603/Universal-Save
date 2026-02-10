// ইউজার যখন অর্ডার বাটনে ক্লিক করবে
async function placeOrder(productName) {
    const phone = prompt(`${productName} কিনতে আপনার মোবাইল নম্বর দিন:`);
    if (phone) {
        const res = await fetch('/api/place-order', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ item: productName, phone: phone })
        });
        const result = await res.json();
        if (result.success) {
            alert("অর্ডার সফল! শাকিল আপনাকে ফোন করবে।");
        }
    }
}
