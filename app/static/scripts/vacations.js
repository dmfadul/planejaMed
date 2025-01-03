function getPrivilegeRights() {
    xhr = new XMLHttpRequest();
    xhr.open('GET', `/get-privilege-rights`, true);

    xhr.onload = function() {
        if (this.status === 200) {
            let vacationRights = JSON.parse(this.responseText);

            const modal = document.getElementById('mainModal');
            const overlay = document.getElementById('mainoverlay');

            // Set the modal position based on the current scroll position
            modal.style.top = `${window.scrollY + window.innerHeight / 2 - modal.offsetHeight / 2}px`;
            modal.style.left = `${window.innerWidth / 2 - modal.offsetWidth / 2}px`;
            document.getElementById('mainModalBody').innerHTML = vacationRights;

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