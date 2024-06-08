function executeEdit(action){
    if (state.mode == null || state.selectedCells.length == 0) {
        return
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
            fetch('/update-database', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(state)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Success:', data);
                sessionStorage.setItem("clickButton", true)
                window.location.reload();
            })
        })
        .catch((error) => {
            console.error('Error:', error);
        })
        .finally(() => {
            // Remove 'selected' class from all cells
            document.querySelectorAll('.selected').forEach(cell => {
                cell.classList.remove('selected');
                cell.style.backgroundColor = ""; // Reset background color if needed
                state.selectedCells = [];
                state.action = null;
            });
        });
}


function confirmData() {
    return new Promise((resolve, reject) => {
        if (state.action == "delete") {
            setTimeout(resolve, 500);
            return;
        }

        // Show the modal
        const modal = document.getElementById('confirmationModal');
        const modalBody = document.getElementById('modalBody');
        modal.style.display = 'block';

        // Clear previous content
        modalBody.innerHTML = '';

        const numberOfElements = state.selectedCells.length;
        for (let i = 0; i < numberOfElements; i++) {
            let message = `${state.selectedCells[i]['doctorName']}: ${state.selectedCells[i]['monthDay']}, ${state.selectedCells[i]['weekDay']}`;
            let div = document.createElement('div');
            div.className = 'message-container';
            div.innerHTML = `<span class="message">${message} ${i + 1}</span>`;

            // Create and append the first dropdown for hour letter
            let firstDropdown = document.createElement('select');
            firstDropdown.id = `firstDropdown${i}`;
            firstDropdown.className = 'dropdown';
            let options = ['-', 'd', 'm', 't', 'n', 'c', 'dn'];
            options.forEach(option => {
                let optionElement = document.createElement('option');
                optionElement.value = option;
                optionElement.textContent = option;
                firstDropdown.appendChild(optionElement);
            });
            div.appendChild(firstDropdown);

            // Create and append the second and third dropdowns for start and end times
            for (let dropdown = 2; dropdown <= 3; dropdown++) {
                let timeDropdown = document.createElement('select');
                timeDropdown.id = `dropdown${dropdown}_${i}`;
                timeDropdown.className = 'dropdown';
                for (let hour = 0; hour <= 23; hour++) { // Assuming hours from 07:00 to 18:00
                    let hourString = `${hour < 10 ? '0' : ''}${hour}:00`;
                    let optionElement = document.createElement('option');
                    optionElement.value = hourString;
                    optionElement.textContent = hourString;
                    timeDropdown.appendChild(optionElement);
                }
                div.appendChild(timeDropdown);
            }

            modalBody.appendChild(div);
        }

        // Close modal events
        document.querySelector('.close').onclick = function() {
            modal.style.display = 'none';
            reject('User cancelled the operation');
        };
        document.getElementById('cancelButton').onclick = function() {
            modal.style.display = 'none';
            reject('User cancelled the operation');
        };
        document.getElementById('saveButton').onclick = function() {
            // Collect data from dropdowns and resolve promise
            for (let i = 0; i < numberOfElements; i++) {
                let hour_letter = document.getElementById(`firstDropdown${i}`).value;
                let hour_init = document.getElementById(`dropdown2_${i}`).value;
                let hour_end = document.getElementById(`dropdown3_${i}`).value;
                state.selectedCells[i]["hourValue"] = [hour_letter, hour_init, hour_end];
            }
            modal.style.display = 'none';
            resolve();
        };

        // Handle clicking outside the modal
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = 'none';
                reject('User cancelled the operation');
            }
        };
    });
}
