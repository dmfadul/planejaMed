document.getElementById("sum-hours-button").addEventListener("click", function() {
    // Collect the data
    var center = centerValue;
    var month = monthValue;
    var year = yearValue;

    // Create the data object
    var data = {
        test: "test",
        center: center,
        month: month,
        year: year
    };

    // Send the data to the backend using an AJAX request
    fetch('/sum-days', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
        // Handle success (e.g., display a message or update the UI)
    })
    .catch((error) => {
        console.error('Error:', error);
        // Handle error (e.g., display an error message)
    });
});
