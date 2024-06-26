document.getElementById("print-table").addEventListener("click", function() {
    // Collect the data
    var center = centerValue;
    var month = monthValue;
    var year = yearValue;

    // Redirect to the new page with the data
    window.location.href = `/print-table/${center}/${month}/${year}`;
});

if (isAdmin) {
    document.getElementById("sum-hours-button").addEventListener("click", function() {
        // Collect the data
        var center = centerValue;
        var month = monthValue;
        var year = yearValue;

        // Redirect to the new page with the data
        window.location.href = `/sum-days/${center}/${month}/${year}`;
    });


    document.getElementById("gen-report").addEventListener("click", function() {
        // Collect the data
        var center = centerValue;
        var month = monthValue;
        var year = yearValue;

        // Redirect to the new page with the data
        window.location.href = `/report/${center}/${month}/${year}`;
    });

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
}