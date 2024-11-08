function showPay(button) {
    fetch('/admin/calculate-vacation-pay')
    .then(response => response.json())
    .then(data => {
        document.getElementById('payModal').innerText = data.message;
        document.getElementById('payModal').style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function closeModal() {
    document.getElementById('payModal').style.display = 'none';
}