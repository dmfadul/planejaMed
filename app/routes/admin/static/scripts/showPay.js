function showPay(button) {
    const vacationID = button.getAttribute('data-id');
    
    fetch('/admin/calculate-vacation-pay', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ vacationID: vacationID }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        document.getElementById('payModal').innerText = data;
        document.getElementById('payModal').style.display = 'block';
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function closeModal() {
    document.getElementById('payModal').style.display = 'none';
}

window.onclick = function() {
    closeModal();
};
