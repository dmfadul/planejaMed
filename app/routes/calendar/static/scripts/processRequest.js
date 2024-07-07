let redudantHoursList = [];


function processCalRequest(itemInfo, crm, action) {
    if (parseInt(crm) !== 0) {
        redudantHoursList = daysDict[day][crm]["hours"][1];
        redudantHoursList = redudantHoursList.map(h => [h, h]);
    }

    infoDict = {};
    infoDict["day"] = day;
    infoDict["month_name"] = monthName;
    infoDict["year"] = monthYear;
    infoDict["center"] = openCenter;
    infoDict["crm"] = crm;


    if (action === "include") {
        handleInclude(infoDict);
    } else if (action === "exclude") {
        handleExclude(infoDict);
    } else if (action === "donate") {
        handleDonate(infoDict);
    } else if (action === "exchange") {
        handleExchange(infoDict);
    } else {
        console.log("Invalid action");
    }
}

// include functions
function handleInclude(infoDict) {
    let doctors = doctorsList;
    let title = "Escolha quem Incluir:"
    let label = "Médicos: "

    openModal("modal1", doctors, title, label, function(selectedDoc) {
        infoDict["crm"] = selectedDoc;
        openHourModal(function(selectedValue){
            infoDict["hours"] = selectedValue;
            sendHoursToServer("cal_include", infoDict);
        });
    });
}

// exchange functions
function handleExchange(infoDict) {
    if (currUserData[0] === parseInt(infoDict["crm"])) {
        handleExchangeFromCurrentUser(infoDict);
    } else {
        handleExchangeFromOtherUser(infoDict);
    }
}

function handleExchangeFromCurrentUser(infoDict) {
    getOtherUserCRM(infoDict);
}

function handleExchangeFromOtherUser(infoDict) {
    getOtherUserHour(infoDict, true);
}

function getOtherUserCRM(infoDict) {
    let doctors = doctorsList.filter(d => d[0] !== currUserData[0]);
    let title = "Escolha com quem Trocar:"
    let label = "Médicos: "

    openModal("modal1", doctors, title, label, function(selectedDoc) {
        infoDict["other_user_crm"] = selectedDoc;
        getOtherUserHour("cal_exchange", selectedDoc);
    });
}

function getOtherUserHour(infoDict, dayOnly=false) {
    let availableHours = null;
    if (dayOnly) {
        availableHours = daysDict[day][infoDict["crm"]]["hours"][1];
    } else {
        availableHours = doctorsDict[infoDict["other_user_crm"]];
    }
    availableHours = availableHours.map(h => [h, h]);
    let title = "Escolha Horas para Receber:"
    let label = "Horários: "

    openModal("modal2", availableHours, title, label, function(selectedHrs) {
        infoDict["hours"] = selectedHrs;
        getCurrentUserHour();
    });
}

function getCurrentUserHour() {
    let availableHours = doctorsDict[currUserData[0]];
    availableHours = availableHours.map(h => [h, h]);
    let title = "Escolha Horários para Trocar:"
    let label = "Seus Horários: "

    openModal("modal1", availableHours, title, label, function(selectedInfo) {
        infoDict["current_user_center_date_hours"] = selectedInfo;
        sendHoursToServer("cal_exchange", infoDict);
    });
}

// exclude functions
function handleExclude(infoDict) {
    let availableHours = redudantHoursList;
    let title = "Escolha Horas para Excluir:"
    let label = "Horários: "
    
    openModal('modal1', availableHours, title, label, function(selectedValue) {
        infoDict["hours"] = selectedValue;
        sendHoursToServer("cal_exclude", infoDict);
    });
}

// donation functions
function handleDonate(infoDict) {
    if (currUserData[0] === parseInt(infoDict["crm"])) {
        handleOfferDonation(infoDict);
    }else{
        handleRequestDonation(infoDict);
    }
}

function handleOfferDonation(infoDict) {
    let availableHours = redudantHoursList;
    let title = "Escolha Horas para Doar:"
    let label = "Horários: "
    
    openModal("modal1", availableHours, title, label, function(selectedHrs) {
        infoDict["hours"] = selectedHrs;
        action = "cal_donate";

        let doctors = doctorsList.filter(d => d[0] !== parseInt(currentUserCRM));
        let title = "Escolha para quem Doar:"
        let label = "Médicos: "

        openModal("modal2", doctors, title, label, function(selectedDoc) {
            infoDict["receiverCRM"] = selectedDoc;
            sendHoursToServer("cal_donate", infoDict);
        });
    });
}

function handleRequestDonation(infoDict) {
    let availableHours = redudantHoursList;
    let title = "Escolha Horas para Receber:"
    let label = "Horários: "
    
    openModal("modal1", availableHours, title, label, function(selectedHrs) {
        infoDict["hours"] = selectedHrs;  
        sendHoursToServer("cal_donate", infoDict);
    });
}


// Function to send selected hours to the server
function sendHoursToServer(action, infoDict) {
    fetch('/update_hours/', {
        method: 'POST',
        body: JSON.stringify({ action: action, infoDict: infoDict }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert("Requisição Realizada com Sucesso");
            console.log('The request was successful and returned:', data.message);
        } else {
            alert("Requisição Não Realizada:\nVerifique os dados e tente novamente");
            console.log('The request failed and returned:', data.message);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    })
    .finally(() => {
        window.location.reload();
    });
}
