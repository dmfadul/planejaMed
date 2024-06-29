function processCalRequest(itemInfo, crm, action){
    if(action=="exclude") {
        let redudantHoursList = daysDict[day][crm]["hours"][1];
        
        openModal();
            
    }else if(action == "include") {
    }else if(action == "exchange") {
        populateIdDropdown();

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
function sendHoursToServer(action, infoDict) {
    fetch('/update_hours/', {
        method: 'POST',
        body: JSON.stringify({ action: action, infoDict: infoDict}),
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
