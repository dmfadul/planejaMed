function openModal(options, text, callback) {
    // Get the modal element
    var modal = document.getElementById("hourModal");
    var modalBody = document.getElementById("modalBody");

    // Clear previous content
    modalBody.innerHTML = '';

    // Create text element
    var textElement = document.createElement("p");
    textElement.textContent = text;
    modalBody.appendChild(textElement);

    // Create dropdown
    var dropdown = document.createElement("select");
    dropdown.id = "dropdownMenu";

    // Populate dropdown with options
    options.forEach(function(option) {
        var optionElement = document.createElement("option");
        optionElement.value = option;
        optionElement.textContent = option;
        dropdown.appendChild(optionElement);
    });

    // Append dropdown to modal body
    modalBody.appendChild(dropdown);

    // Display the modal
    modal.style.display = "block";

    // Get the <span> element that closes the modal
    var span = document.getElementById("close");

    // When the user clicks on <span> (x), close the modal
    span.onclick = function() {
        modal.style.display = "none";
    };

    // When the user clicks on the cancel button, close the modal
    document.getElementById("cancelButton").onclick = function() {
        modal.style.display = "none";
    };

    // Add an event listener to the save button to get the selected value
    document.getElementById("saveButton").onclick = function() {
        var selectedValue = dropdown.value;
        callback(selectedValue);
        modal.style.display = "none";
    };

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    };
}
