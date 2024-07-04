function openModal(modalID, options, title, label, callback) {
    // const modal = document.querySelector(".modal");
    const modal = document.getElementById(modalID);
    const overlay = document.querySelector(".overlay");
    const modalTitle = modal.querySelector(".modal-title");
    const modalLabel = modal.querySelector(".modal-label");
    const dropdown = modal.querySelector(".dropdown");
    const buttonDiv = modal.querySelector(".button-group");

    modal.classList.remove("hidden");
    overlay.classList.remove("hidden");

    modalTitle.textContent = title;
    modalLabel.textContent = label;

    // Clear existing options
    while (dropdown.firstChild) {
        dropdown.removeChild(dropdown.firstChild);
    }

    // Add new options
    options.forEach(option => {
        let optionElement = document.createElement('option');
        optionElement.value = option;
        optionElement.textContent = option;
        dropdown.appendChild(optionElement);
    });

    const cancelButton = document.createElement("button");
    cancelButton.textContent = "Cancelar";
    cancelButton.id = "cancelButton";
    cancelButton.className = "cancel-button";
    cancelButton.classList.add("submit-button");
    buttonDiv.appendChild(cancelButton);

    cancelButton.addEventListener("click", function() {
        closeModal(modalID);
    }, { once: true }); // Ensure the event listener is added only once

    const saveButton = document.createElement("button");
    saveButton.textContent = "Confirmar";
    saveButton.id = "saveButton";
    saveButton.className = "save-button";
    saveButton.classList.add("submit-button");
    buttonDiv.appendChild(saveButton);

    saveButton.addEventListener("click", function() {
        const selectedValue = dropdown.value;
        callback(selectedValue);
        closeModal(modalID);
    }, { once: true }); // Ensure the event listener is added only once

    const closeButton = modal.querySelector(".close-button");
    closeButton.addEventListener("click", function() {
        closeModal(modalID);
    }, { once: true }); // Ensure the event listener is added only once
}

function closeModal(modalID) {
    // const modal = document.querySelector(".modal");
    const modal = document.getElementById(modalID);
    const overlay = document.querySelector(".overlay");

    const saveButton = modal.querySelector("#saveButton");
    saveButton.remove();
    const cancelButton = modal.querySelector("#cancelButton");
    cancelButton.remove();

    modal.classList.add("hidden");
    overlay.classList.add("hidden");
}

document.addEventListener('keydown', function(e) {
    if(e.key === 'Escape' && !document.querySelector(".modal").classList.contains("hidden")){
        const modals = document.querySelectorAll(".modal");
        modals.forEach(modal => {
            if (!modal.classList.contains("hidden")) {
                closeModal(modal.id);
            }
        });        
    }
});

window.onclick = function(event) {
    if (event.target === document.querySelector(".overlay")) {
        const modals = document.querySelectorAll(".modal");
        modals.forEach(modal => {
            if (!modal.classList.contains("hidden")) {
                closeModal(modal.id);
            }
        });
    }
};
