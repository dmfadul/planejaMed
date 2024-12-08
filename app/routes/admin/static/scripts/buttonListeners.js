function handleCreateButtonClick() {
    // Show confirmation dialog
    const userConfirmed = confirm("Confirmar a criação de um Novo Mês. Tem a certeza que deseja continuar?");

    if (userConfirmed) {
        // Show the waiting message
        document.getElementById('waitingMessage').style.display = 'block';

        // Redirect to the URL (simulate form submission or AJAX request)
        window.location.href = '/admin/create-month';
    }
}


function getVacationRights() {
    xhr = new XMLHttpRequest();
    xhr.open('GET', `/admin/get-vacation-rights`, true);

    xhr.onload = function() {
        if (this.status === 200) {
            let vacationRights = JSON.parse(this.responseText);
            console.log(vacationRights);

            const modal = document.getElementById('Modal');
            const overlay = document.getElementById('overlay');

            // Set the modal position based on the current scroll position
            modal.style.top = `${window.scrollY + window.innerHeight / 2 - modal.offsetHeight / 2}px`;
            modal.style.left = `${window.innerWidth / 2 - modal.offsetWidth / 2}px`;

            modal.classList.remove('hidden');
            overlay.classList.remove('hidden');

        } else {
            console.log("Error: Could not get Vacations Rights");
        }
    }
    xhr.send();
}


function handleNextButtonClick() {
    // Show confirmation dialog
    const userConfirmed = confirm("Confirmar a Liberação de um Novo Mês. Tem a certeza que deseja continuar?");

    if (userConfirmed) {
        // Show the waiting message
        document.getElementById('waitingMessage').style.display = 'block';

        // Redirect to the URL (simulate form submission or AJAX request)
        window.location.href = '/admin/next-month';
    }
}

function toggleMaintenance() {
    // Show confirmation dialog
    const actionConfirmed = confirm("Tem a certeza que deseja mudar o estado de manutenção?");

    if (actionConfirmed) {
        // Show the waiting message
        document.getElementById('waitingMessage').style.display = 'block';

        // Redirect to the URL (simulate form submission or AJAX request)
        window.location.href = '/admin/toggle-maintenance';
    }
}
