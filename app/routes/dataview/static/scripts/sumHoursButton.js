document.getElementById("sum-hours-button").addEventListener("click", function() {
    // Collect the data
    var center = centerValue;
    var month = monthValue;
    var year = yearValue;

    // Redirect to the new page with the data
    window.location.href = `/sum-days/${center}/${month}/${year}`;
});