function getPrivilegeRights() {
    xhr = new XMLHttpRequest();
    xhr.open('GET', `/get-privilege-rights`, true);

    xhr.onload = function() {
        if (this.status === 200) {
            let vacationRights = JSON.parse(this.responseText);

            const modal = document.getElementById('mainModal');
            const modalContent = document.getElementById('mainModalContent');
            const overlay = document.getElementById('mainoverlay');

            const modalTitle = document.createElement('h2');
            modalTitle.innerHTML = 'Checagem Férias';

            const modalBody = document.createElement('div');
            modalBody.id = 'mainModalBody';
            modalBody.innerHTML = vacationRights;

            const buttonGroup = document.createElement('div');
            buttonGroup.classList.add('button-group');

            const closeButton = document.createElement('button');
            closeButton.textContent = 'Fechar';
            closeButton.classList.add('submit-button', 'cancel-button');
            closeButton.onclick = () => {
                closeMainModal();
            };

            const actionButton = document.createElement('button');
            actionButton.textContent = 'Mandar Mensagens';
            actionButton.classList.add('submit-button', 'save-button', 'disabled-button');
            actionButton.onclick = () => {
            };

            buttonGroup.appendChild(closeButton);
            buttonGroup.appendChild(actionButton);

            modalContent.appendChild(modalTitle);
            modalContent.appendChild(modalBody);
            modalContent.appendChild(buttonGroup);

            // Set the modal position based on the current scroll position
            modal.style.top = `${window.scrollY + window.innerHeight / 2 - modal.offsetHeight / 2}px`;
            modal.style.left = `${window.innerWidth / 2 - modal.offsetWidth / 2}px`;
            // document.getElementById('mainModalBody').innerHTML = vacationRights;

            modal.classList.remove('hidden');
            overlay.classList.remove('hidden');

        } else {
            console.log("Error: Could not get Vacations Rights");
        }
    }
    xhr.send();
}


function closeMainModal() {
    const modal = document.getElementById('mainModal');
    const overlay = document.getElementById('mainOverlay');

    modal.classList.add('hidden');
    overlay.classList.add('hidden');
}