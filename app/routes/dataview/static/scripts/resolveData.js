function executeEdit(action) {
    if (!state.mode || state.selectedCells.length === 0) {
        return;
    }
    state.action = action;

    document.querySelectorAll('.selected').forEach(cell => {
        cell.style.backgroundColor = state.action === 'delete' ? 'red' : 'green';
    });
    sendData();
}

function sendData() {
    confirmData()
        .then(() => {
            return fetch('/update-appointments', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(state)
            });
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            sessionStorage.setItem("clickButton", true);
            window.location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
        })
        .finally(() => {
            clearSelection();
        });
}

function clearSelection() {
    document.querySelectorAll('.selected').forEach(cell => {
        cell.classList.remove('selected');
        cell.style.backgroundColor = ""; // Reset background color if needed
    });
    state.selectedCells = [];
    state.action = null;
}

function confirmData() {
    return new Promise((resolve, reject) => {
        if (state.action === "delete") {
            setTimeout(resolve, 500);
            return;
        }

        const modal = document.getElementById('confirmationModal');
        const modalBody = document.getElementById('modalBody');
        modal.style.display = 'block';
        modalBody.innerHTML = '';

        state.selectedCells.forEach((cell, index) => {
            let message = `${cell.doctorName}: ${cell.monthDay}, ${cell.weekDay}`;
            let div = document.createElement('div');
            div.className = 'message-container';
            div.innerHTML = `<span class="message">${message} ${index + 1}</span>`;

            let firstDropdown = createDropdown(`firstDropdown${index}`, ['-', 'd', 'm', 't', 'n', 'c', 'dn']);
            let dropdown2 = createTimeDropdown(`dropdown2_${index}`);
            let dropdown3 = createTimeDropdown(`dropdown3_${index}`);

            firstDropdown.addEventListener('change', () => {
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
            });

            div.appendChild(firstDropdown);
            div.appendChild(dropdown2);
            div.appendChild(dropdown3);

            modalBody.appendChild(div);
        });

        setupModalEvents(resolve, reject);
    });
}

function createDropdown(id, options) {
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

function createTimeDropdown(id) {
    let dropdown = document.createElement('select');
    dropdown.id = id;
    dropdown.className = 'dropdown';
    for (let hour = 0; hour <= 23; hour++) {
        let hourString = `${hour < 10 ? '0' : ''}${hour}:00`;
        let optionElement = document.createElement('option');
        optionElement.value = hourString;
        optionElement.textContent = hourString;
        dropdown.appendChild(optionElement);
    }
    return dropdown;
}

function setupModalEvents(resolve, reject) {
    const modal = document.getElementById('confirmationModal');

    function closeModal() {
        modal.style.display = 'none';
        reject('User cancelled the operation');
    }

    document.getElementById('close').onclick = closeModal;
    document.getElementById('cancelButton').onclick = closeModal;

    document.getElementById('saveButton').onclick = () => {
        state.selectedCells.forEach((cell, index) => {
            let hour_letter = document.getElementById(`firstDropdown${index}`).value;
            let hour_init = document.getElementById(`dropdown2_${index}`).value;
            let hour_end = document.getElementById(`dropdown3_${index}`).value;
            cell.hourValue = [hour_letter, hour_init, hour_end];
        });
        modal.style.display = 'none';
        resolve();
    };

    window.onclick = event => {
        if (event.target == modal) {
            closeModal();
        }
    };

    window.onkeydown = event => {
        if (event.key === 'Escape') {
            closeModal();
        }
    };
}
