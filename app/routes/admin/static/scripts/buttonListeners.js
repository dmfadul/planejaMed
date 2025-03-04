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
