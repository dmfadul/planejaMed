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
            saveScrollPosition();  // Save scroll position before reloading
            window.location.reload();
        })
        .catch(error => {
            if (error !== 'User cancelled the operation') {
                console.error('Error:', error);
                alert('An error occurred while updating appointments. Please try again.');
            } else {
                console.log('Operation cancelled by the user.');
            }
        })
        .finally(() => {
            clearSelection();
        });
}

function saveScrollPosition() {
    sessionStorage.setItem('scrollPosition', window.scrollY);
}

function clearSelection() {
    document.querySelectorAll('.selected').forEach(cell => {
        cell.classList.remove('selected');
        cell.style.backgroundColor = ""; // Reset background color if needed
    });
    state.selectedCells = [];
    state.action = null;
}

function openModal() {
    const modal = document.getElementById('hourModal');
    const overlay = document.getElementById('overlay');

    modal.classList.remove('hidden');
    overlay.classList.remove('hidden');
}

function confirmData() {
    return new Promise((resolve, reject) => {
        if (state.action === "delete") {
            setTimeout(resolve, 500);
            return;
        }

        const modal = document.getElementById('hourModal');
        const modalBody = document.getElementById('modalBody');
        openModal();
        modalBody.innerHTML = '';

        state.selectedCells.forEach((cell, index) => {
            let message = `${cell.doctorName}: ${cell.weekDay}, ${cell.monthDay}`;
            let div = document.createElement('div');
            div.className = 'message-container';
            div.innerHTML = `<span class="message">${message}</span>`;

            let firstDropdown = createDropdown(`firstDropdown${index}`, ['-', 'd', 'm', 't', 'n', 'c', 'v', 'dn']);
            let dropdown2 = createTimeDropdown(`dropdown2_${index}`);
            let dropdown3 = createTimeDropdown(`dropdown3_${index}`);

            firstDropdown.addEventListener('change', () => handleDropdownChange(firstDropdown, dropdown2, dropdown3));

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

function setupModalEvents(resolve, reject) {
    const modal = document.getElementById('hourModal');

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

// Restore scroll position on page load
window.addEventListener('load', () => {
    const scrollPosition = sessionStorage.getItem('scrollPosition');
    if (scrollPosition) {
        window.scrollTo(0, parseInt(scrollPosition));
        sessionStorage.removeItem('scrollPosition');
    }
});
