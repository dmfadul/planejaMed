let selectedDoctor = null;
let selectedHours = null;
let globalCrm = null;
let globalDay = null;


function processCalRequest(itemInfo, crm, action) {
    globalCrm = crm; // Store globally
    globalDay = day; // Store globally

    if (action === "exclude") {
        handleExclude(crm);
    } else if (action === "include") {
        handleInclude();
    } else if (action === "exchange") {
        handleExchangeStep1(crm);
    } else if (action === "donate") {
        handleDonate();
    } else {
        console.log("Invalid action");
    }
}

function handleExclude(crm) {
    let redudantHoursList = daysDict[globalDay][crm]["hours"][1];
    
    openModal('modal1', redudantHoursList, "Escolha Horas para Excluir:", "Horários: ", function(selectedValue) {
        let infoDict = {
            "day": globalDay,
            "crmToExclude": crm,
            "hoursToExclude": selectedValue
        };

        sendHoursToServer("cal_exclude", infoDict);
    });
}

function handleInclude() {
    // Your code for handling include
}

function handleExchangeStep1(crm) {
    let doctorList = Object.keys(daysDict[globalDay]);

    openModal("modal1", doctorList, "Com quem deseja trocar?", "Médicos: ", function(selectedDoc) {
        selectedDoctor = selectedDoc;
        if (selectedDoctor === null) {
            // User cancelled on the first modal
            return;
        }
        
        handleExchangeStep2();
    });
}

function handleExchangeStep2() {
    let availableHours = ["08:00 - 12:00", "12:00 - 16:00", "16:00 - 20:00"];

    openModal("modal2", availableHours, "Escolha Horas para Trocar:", "Horários: ", function(selectedHrs) {
        selectedHours = selectedHrs;
        if (selectedHours === null) {
            // User cancelled on the second modal
            return;
        }

        let infoDict = {
            "day": globalDay,
            "crmToExchange": globalCrm,
            "hoursToExchange": selectedHours,
            "crmToReceive": selectedDoctor
        };

        sendHoursToServer("cal_exchange", infoDict);
    });
}

function handleDonate() {
    // Your code for handling donate
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