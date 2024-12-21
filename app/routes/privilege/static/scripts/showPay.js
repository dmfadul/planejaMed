function changeStatus(button, newStatus) {
    const vacationID = button.getAttribute('data-id');

    // Add a confirmation dialog
    if(newStatus === 'deleted') {
        const userConfirmed = confirm('Tem a certeza que deseja apagar este pedido? Esta ação é irreversível.');
        if (!userConfirmed) {
            return; // Stop execution if the user cancels
        }
    }

    fetch('/change-privilege-status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ vacationID: vacationID, newStatus: newStatus }),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        location.reload();
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function showReport(button) {
    const vacationID = button.getAttribute('data-id');
    
    fetch('/get-privilege-report', {
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


function showPay(button) {
    const vacationID = button.getAttribute('data-id');
    const vacationMonth = button.getAttribute('data-month');
    
    fetch('/get-vacation-pay', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ vacationID: vacationID, vacationMonth: vacationMonth}),
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

window.onkeydown = function(event) {
    if (event.key === 'Escape') {
        closeModal();
    }
};
