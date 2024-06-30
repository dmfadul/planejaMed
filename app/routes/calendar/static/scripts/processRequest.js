let infoDict = {};

let selectedDoctor = null;
let selectedHours = null;


function processCalRequest(itemInfo, crm, action) {
    if (action === "exclude") {
        handleExclude(crm);
    } else if (action === "include") {
        handleInclude();
    } else if (action === "exchange") {
        handleExchange(crm);

    } else if (action === "donate") {
        handleDonate();
    } else {
        console.log("Invalid action");
    }
}

function handleExclude(crm) {
    infoDict = {};
    let redudantHoursList = daysDict[day][crm]["hours"][1];
    
    openModal('modal1', redudantHoursList, "Escolha Horas para Excluir:", "Horários: ", function(selectedValue) {
        if (selectedValue === null) {
            // User cancelled on the first modal
            return;
        }
        infoDict["day"] = day;
        infoDict["crmToExclude"] = crm;
        infoDict["hoursToExclude"] = selectedValue;

        sendHoursToServer("cal_exclude", infoDict);
    });
}

function handleInclude() {
    // Your code for handling include
}

function handleDonate() {
    // Your code for handling donate
}

function handleExchange(crm) {
    infoDict = {};
    if (currUserCRM === parseInt(crm)) {
        // handleExchangeStep1(crm);
        alert("Você não pode trocar horários consigo mesmo");
        return;
    }
    infoDict["day"] = day;
    infoDict["other_user_center"] = openCenter;
    infoDict["current_user_crm"] = currUserCRM;
    infoDict["other_user_crm"] = crm;

    handleExchangeStep2(crm);
}

function handleExchangeStep1(crm) {
    let doctorList = Object.keys(daysDict[day]);

    openModal("modal1", doctorList, "Com quem deseja trocar?", "Médicos: ", function(selectedDoc) {
        selectedDoctor = selectedDoc;
        if (selectedDoctor === null) {
            // User cancelled on the first modal
            return;
        }
        
        handleExchangeStep2(crm);
    });
}

function handleExchangeStep2(crm) {
    let availableHours = daysDict[day][crm]["hours"][1];

    openModal("modal2", availableHours, "Escolha Horas para Trocar:", "Horários: ", function(selectedHrs) {
        selectedHours = selectedHrs;
        if (selectedHours === null) {
            console.log("selectedHours");
            return;
        }
        
        console.log("Sending hours to server");

        infoDict["other_user_hours"] = selectedHours;
        handleExchangeStep3(crm);
    });
}

function handleExchangeStep3(crm) {
    let availableHours = currUserSchedule;

    openModal("modal1", availableHours, "Escolha Horas para Trocar:", "Seus Horários: ", function(selectedInfo) {
        selectedHours = selectedInfo;
        if (selectedInfo === null) {
            // User cancelled on the second modal
            return;
        }

        infoDict["current_user_center_date_hours"] = selectedInfo;
        sendHoursToServer("cal_exchange", infoDict);
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
    });
}