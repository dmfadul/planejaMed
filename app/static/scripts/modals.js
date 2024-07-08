function openHourModal(callback) {
    const modalID = "hourModal";
    const modal = document.getElementById(modalID);
    const overlay = document.querySelector(".overlay");
    const modalBody = modal.querySelector(".modalBody");
    const buttonDiv = modal.querySelector(".button-group");

    modal.classList.remove("hidden");
    overlay.classList.remove("hidden");

    modalBody.innerHTML = '';

    let message = "Escolha Horas: ";
    let div = document.createElement('div');
    div.className = 'message-container';
    div.innerHTML = `<span class="message">${message}</span>`;

    let letterDropdown = populateDropdown('letterDropdown', ['-', 'd', 'm', 't', 'n', 'c', 'v', 'dn']);
    let startHourDropdown = populateTimeDropdown('startHourDropdown');
    let endHourDropdown = populateTimeDropdown('endHourDropdown');

    letterDropdown.addEventListener('change', () => handleDropdownChange(letterDropdown, startHourDropdown, endHourDropdown));

    div.appendChild(letterDropdown);
    div.appendChild(startHourDropdown);
    div.appendChild(endHourDropdown);

    modalBody.appendChild(div);

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
        const selectedValue = [letterDropdown.value, startHourDropdown.value, endHourDropdown.value];
        callback(selectedValue);
        closeModal(modalID);
    }, { once: true }); // Ensure the event listener is added only once

    const closeButton = modal.querySelector(".close-button");
    closeButton.addEventListener("click", function() {
        closeModal(modalID);
    }, { once: true }); // Ensure the event listener is added only once
}

function populateDropdown(id, options) {
    let dropdown = document.createElement('select');
    dropdown.id = id;
    dropdown.className = 'dropdown';
    options.forEach(option => {
        let optionElement = document.createElement('option');
        optionElement.value = option;
        optionElement.textContent = option;
        dropdown.appendChild(optionElement);
    });
    return dropdown;
}

function populateTimeDropdown(id) {
    let dropdown = document.createElement('select');
    dropdown.id = id;
    dropdown.className = 'dropdown';

    // Add options from 07:00 to 23:00
    for (let hour = 7; hour <= 23; hour++) {
        let hourString = `${hour < 10 ? '0' : ''}${hour}:00`;
        let optionElement = document.createElement('option');
        optionElement.value = hourString;
        optionElement.textContent = hourString;
        dropdown.appendChild(optionElement);
    }

    // Add options from 00:00 to 06:00
    for (let hour = 0; hour < 7; hour++) {
        let hourString = `${hour < 10 ? '0' : ''}${hour}:00`;
        let optionElement = document.createElement('option');
        optionElement.value = hourString;
        optionElement.textContent = hourString;
        dropdown.appendChild(optionElement);
    }

    return dropdown;
}

function handleDropdownChange(firstDropdown, dropdown2, dropdown3) {
    if (firstDropdown.value !== '-') {
        dropdown2.disabled = true;
        dropdown3.disabled = true;
        dropdown2.style.backgroundColor = "#e9e9e9"; // Gray out the dropdown
        dropdown3.style.backgroundColor = "#e9e9e9"; // Gray out the dropdown
    } else {
        dropdown2.disabled = false;
        dropdown3.disabled = false;
        dropdown2.style.backgroundColor = ""; // Reset background color
        dropdown3.style.backgroundColor = ""; // Reset background color
    }
}


function openModal(modalID, options, title, label, callback) {
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
        optionElement.value = option[0];
        optionElement.textContent = option[1];
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

    const saveButton = modal.querySelector(".save-button");
    saveButton.remove();
    const cancelButton = modal.querySelector(".cancel-button");
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
