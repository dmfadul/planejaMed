let selectedDoctor = null;
let selectedHours = null;


function processCalRequest(itemInfo, crm, action) {
    if (action === "exclude") {
        handleExclude(crm);
    } else if (action === "include") {
        handleInclude();
    } else if (action === "donate") {
        let infoDict = {};
        handleDonate(crm);
    } else if (action === "exchange") {
        handleExchange(crm);
    } else {
        console.log("Invalid action");
    }
}

function handleExclude(crm) {
    infoDict = {};

    infoDict["day"] = day;
    infoDict["crmToExclude"] = crm;

    let redudantHoursList = daysDict[day][crm]["hours"][1];
    let title = "Escolha Horas para Excluir:"
    let label = "Horários: "
    
    openModal('modal1', redudantHoursList, title, label, function(selectedValue) {
        infoDict["hoursToExclude"] = selectedValue;
        sendHoursToServer("cal_exclude", infoDict);
    });
}

function handleDonate(crm) {
    infoDict = {};

    infoDict["donorDay"] = day;
    infoDict["donorCenter"] = openCenter;
    infoDict["donorCRM"] = crm;

    if (currUserData[0] === parseInt(crm)) {
        handleOfferDonation(crm);
    }else{
        handleRequestDonation(crm);
    }
}

function handleRequestDonation(donorCRM) {
    let availableHours = daysDict[day][donorCRM]["hours"][1];
    let title = "Escolha Horas para Receber:"
    let label = "Horários: "
    
    openModal("modal1", availableHours, title, label, function(selectedHrs) {
        infoDict["donorHours"] = selectedHrs;
        action = "cal_donate";
        
        sendHoursToServer(action, infoDict);
    });
}

function handleOfferDonation(currentUserCRM) {
    let availableHours = daysDict[day][currentUserCRM]["hours"][1];
    let title = "Escolha Horas para Doar:"
    let label = "Horários: "
    
    openModal("modal1", availableHours, title, label, function(selectedHrs) {
        infoDict["donorHours"] = selectedHrs;
        action = "cal_donate";

        let doctorList = Object.keys(daysDict[day]);
        let title = "Escolha para quem Doar:"
        let label = "Médicos: "

        openModal("modal2", doctorList, title, label, function(selectedDoc) {
            infoDict["receiverCRM"] = selectedDoc;
        
            sendHoursToServer(action, infoDict);
        });
    });
}

function handleExchange(crm) {
    infoDict = {};

    infoDict["day"] = day;
    infoDict["other_user_center"] = openCenter;
    infoDict["current_user_crm"] = currUserData[0];
    infoDict["other_user_crm"] = crm;
    

    if (currUserData[0] === parseInt(crm)) {
        getExchangerCRM();
    } else {
        getExchangerHour(crm);
    }
}

function getExchangerCRM() {
    console.log("getExchangerCRM");
    let doctorList = Object.keys(daysDict[day]);
    let title = "Escolha com quem Trocar:"
    let label = "Médicos: "

    openModal("modal1", doctorList, title, label, function(selectedDoc) {
        infoDict["other_user_crm"] = selectedDoc;
        getExchangerHour(selectedDoc);
    });
}

function getExchangerHour(crm) {
    let availableHours = daysDict[day][crm]["hours"][1];
    let title = "Escolha Horas para Receber:"
    let label = "Horários: "

    openModal("modal2", availableHours, title, label, function(selectedHrs) {
        infoDict["other_user_hours"] = selectedHrs;
        getCurrentUserHour();
    });
}

function getCurrentUserHour() {
    let availableHours = doctorsDict[currUserData[0]];
    let title = "Escolha Horários para Trocar:"
    let label = "Seus Horários: "

    openModal("modal1", availableHours, title, label, function(selectedInfo) {
        infoDict["current_user_center_date_hours"] = selectedInfo;
        sendHoursToServer("cal_exchange", infoDict);
    });
}

function handleInclude() {
    // Your code for handling include
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
    });
}
