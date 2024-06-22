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


function processCalRequest(itemInfo, crm, action){
    if(action=="exclude") {
        hours = doctorsDict[crm][day];
        
        openModal(hours, "Escolha Horas para Excluir:", function(selectedValue) {
            let hoursToExclude = selectedValue;
            sendHoursToServer(action, itemInfo, crm, hoursToExclude);
        });
            
    }else if(action == "include") {
    }else if(action == "exchange") {
    }else if(action == "donate") {
    }else{
        console.log("Invalid action");
    }
}

function processSchRequest(itemInfo, crm, action){
    if(action=="exclude") {
    }else if(action == "include") {
    }else if(action == "exchange") {
    }else if(action == "donate") {
    }else{
        console.log("Invalid action");
    }
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
