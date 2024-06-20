document.addEventListener('click', function(event) {
    if (event.target.classList.contains('kebab-button')) {
        event.target.nextElementSibling.style.display = 'block';
    } else {
        var openMenus = document.querySelectorAll('.kebab-content');
        for (var menu of openMenus) {
            if (menu.style.display === 'block') {
                menu.style.display = 'none';
            }
        }
    }
});


function processRequest(itemInfo, action){
    console.log(itemInfo);
    let counter = 0;
    let hours = [];
    let extraInfo = '';
    let label = '';

    if((action=="exclude" || action=="donation") && itemInfo.includes('--')) {
        hours = itemInfo.split('--').slice(2);
        extraInfo = itemInfo.split('--');
        extraInfo[2] = 0;
        label = 'Horários: '
    }else if(action == "include") {
        hours = ["CCG", "CCO", "CCQ"];  // TODO: mudar para pegar do banco
        label = 'Centros: '
    }else{
        hours = itemInfo.split('<br>').slice(1);
        extraInfo = itemInfo.split('<br>')[0];
        label = 'Horários: '
    }

    openModal(hours, label, action, counter, extraInfo); // open hourModal
}

function openModal(inputList, ddLabel, action, counter, extraInfo) {
    if((inputList.includes("M: 07:00 - 13:00") && inputList.includes("T: 13:00 - 19:00") && !inputList.includes("D: 07:00 - 19:00"))){
        inputList.unshift("D: 07:00 - 19:00");
    }
    if ((inputList.includes("D: 07:00 - 19:00") && inputList.includes("N: 19:00 - 07:00") && !inputList.includes("DN: 07:00 - 07:00"))){
        inputList.push("DN: 07:00 - 07:00");
    }
    if(!inputList.some(string => string.includes("M: 07:00 - 13:00")) && inputList.some(string => string.includes("D: 07:00 - 19:00"))){
        inputList.push("M: 07:00 - 13:00");
        inputList.push("T: 13:00 - 19:00");
    }
    let modal = document.getElementById('hourModal');
    let hourOptionsDiv = document.getElementById('hourOptions');

    hourOptionsDiv.innerHTML = ''; // Clear previous options

    let flexContainer = document.createElement('div');
    flexContainer.className = 'flex-container';

    let dropdownLabel = document.createElement('label');
    dropdownLabel.innerHTML = ddLabel ;
    dropdownLabel.htmlFor = 'scheduleDropdown';

    let dropdown = document.createElement('select');
    dropdown.id = 'scheduleDropdown';

    inputList.forEach(item => {
        let option = document.createElement('option');
        option.value = item;
        option.text = item;
        dropdown.appendChild(option);
    });

    flexContainer.appendChild(dropdownLabel);
    flexContainer.appendChild(dropdown);

    hourOptionsDiv.appendChild(flexContainer);
    hourOptionsDiv.appendChild(document.createElement('br'));

    modal.style.display = "block";

    document.getElementById('submitHours').onclick = function() {
        let dropdown = document.getElementById('scheduleDropdown');
        let selection = dropdown.options[dropdown.selectedIndex].value;

        if((action=="exclude" || action=="donation") && extraInfo[2]==0) {
            extraInfo[2] = selection;
        }

        sendHoursToServer(selection, action, counter, extraInfo);
        modal.style.display = "none";
    };

    let closeButton = document.querySelector('.close');
    closeButton.onclick = function() {
        modal.style.display = "none";
    };

    document.addEventListener('keydown', function(event) {
        if (event.key === "Escape") { // Checks if the pressed key is 'Escape'
            modal.style.display = "none";
        }
    });
}

// Function to send selected hours to the server
function sendHoursToServer(selection, action, counter, extraInfo) {
    fetch('/update_hours/', {
        method: 'POST',
        body: JSON.stringify({ action: action,
                               mainInfo: selection,
                               extraInfo: extraInfo,
                               counter: counter
                             }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if(data.status == "success") {
            alert("Requisição Realizada com Sucesso");
            console.log('The request was successful and returned:', data.message);
        } else if(data.status == "failure") {
            alert("Requisição Não Realizada:\nVerifique os dados e tente novamente");
            console.log('The request failed and returned:', data.message);
        } else {
            let counter = +data.counter;
            counter++;
            openModal(data.info, data.newLabel, data.action, counter, extraInfo);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
