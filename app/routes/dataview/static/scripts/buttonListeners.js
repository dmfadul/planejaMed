document.getElementById("print-table").addEventListener("click", function() {
    // Collect the data
    var center = centerValue;
    var month = monthValue;
    var year = yearValue;

    // Redirect to the new page with the data
    // window.location.href = `/print-table/${center}/${month}/${year}`;
    window.open(`/print-table/${center}/${month}/${year}`, '_blank');
});

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
