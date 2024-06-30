function openModal(modalID, options, title, label, callback) {
    // const modal = document.querySelector(".modal");
    const modal = document.getElementById(modalID);
    const overlay = document.querySelector(".overlay");
    const modalTitle = modal.querySelector(".modal-title");
    const modalLabel = modal.querySelector(".modal-label");
    const dropdown = modal.querySelector(".dropdown");

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

    const saveButton = modal.querySelector(".save-button");
    saveButton.addEventListener("click", function() {
        const selectedValue = dropdown.value;
        callback(selectedValue);
        closeModal(modalID);
    }, { once: true }); // Ensure the event listener is added only once

    const cancelButton = modal.querySelector(".cancel-button");
    cancelButton.addEventListener("click", function() {
        callback(null);
        closeModal(modalID);
    }, { once: true }); // Ensure the event listener is added only once

    const closeButton = modal.querySelector(".close-button");
    closeButton.addEventListener("click", function() {
        callback(null);
        closeModal(modalID);
    }, { once: true }); // Ensure the event listener is added only once
}

function closeModal(modalID) {
    // const modal = document.querySelector(".modal");
    const modal = document.getElementById(modalID);
    const overlay = document.querySelector(".overlay");

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
