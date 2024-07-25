let redudantHoursList = [];


function processSchRequest(item, action) {
    let infoDict = {};
    infoDict["crm"] = currUserData[0];

    if (action !=="include") {
        let center = item.split("--")[0].trim();
        let date = item.split("--")[1].trim();
        let hours = item.split("--")[2].trim();

        let day = parseInt(date.split("/")[0].trim());

        infoDict["day"] = parseInt(date.split("/")[0]);
        infoDict["center"] = center;
        infoDict["hours"] = hours;

        redudantHoursList = doctorsDict[currUserData[0]][center][day][0];
        redudantHoursList = redudantHoursList.map(h => [h, h]);
    }

    if (action === "include") {
        handleSchInclude(infoDict);
    } else if (action === "exclude") {
        handleSchExclude(infoDict);
    } else if (action === "donate") {
        handleOfferDonation(infoDict);
    } else if (action === "exchange") {
        handleExchangeFromCurrentUser(infoDict);
    } else {
        console.log("Invalid action");
    }
}

function handleSchInclude(infoDict) {
    let availableCenters = centers;
    availableCenters = availableCenters.map(h => [h, h]);
    let title = "Escolha em que Centro Entrar";
    let label = "Centros: ";

    openModal("modal1", availableCenters, title, label, function(selectedCenter) {
        infoDict["center"] = selectedCenter;

        let availableDays = days;
        availableDays = availableDays.map(h => [h, h]);
        let title = "Escolha em que Dia Entrar";
        let label = "Centros: ";
        
        openModal("modal2", availableDays, title, label, function(selectedDay) {
            infoDict["day"] = selectedDay;
            
            openHourModal(function(selectedValue){
                infoDict["hours"] = selectedValue;
                sendHoursToServer("include", infoDict);
            });
        });
    });
}

function handleSchExclude(infoDict) {
    let availableHours = redudantHoursList;
    let title = "Especifique Horas para Excluir";
    let label = "Horários: ";
    
    openModal('modal1', availableHours, title, label, function(selectedValue) {
        infoDict["hours"] = selectedValue;
        sendHoursToServer("exclude", infoDict);
    });
}


// Calendar functions
function processCalRequest(crm, action) {
    if (parseInt(crm) !== 0) {
        redudantHoursList = daysDict[day][crm]["hours"][1];
        redudantHoursList = redudantHoursList.map(h => [h, h]);
    }

    infoDict = {};
    // infoDict["year"] = monthYear;
    // infoDict["month_name"] = monthName;
    infoDict["day"] = day;
    infoDict["center"] = openCenter;
    infoDict["crm"] = parseInt(crm);

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

// include function
function handleInclude(infoDict) {
    let doctors = doctorsList;
    let title = "Escolha quem Incluir";
    let label = "Médicos: ";

    openModal("modal1", doctors, title, label, function(selectedDoc) {
        infoDict["crm"] = selectedDoc;
        openHourModal(function(selectedValue){
            infoDict["hours"] = selectedValue;
            sendHoursToServer("include", infoDict);
        });
    });
}

// exchange functions
function handleExchange(infoDict) {
    if (parseInt(infoDict["crm"]) === currUserData[0]) {
        handleExchangeFromCurrentUser(infoDict);
    } else {
        handleExchangeFromOtherUser(infoDict);
    }
}

function handleExchangeFromCurrentUser(infoDict) {
    let availableHours = redudantHoursList;
    let title = "Especifique as Horas das quais Você quer Sair";
    let label = "Horários: ";
    
    openModal('modal1', availableHours, title, label, function(selectedValue) {
        infoDict["hours"] = selectedValue;

        let doctors = doctorsList.filter(d => d[0] !== currUserData[0]);
        let title = "Escolha com quem Trocar";
        let label = "Médicos: ";

        openModal("modal2", doctors, title, label, function(selectedDoc) {
            infoDict["crm2"] = selectedDoc;

            let centers = Object.keys(doctorsDict[selectedDoc]);
            centers = centers.map(h => [h, h]);
            let title = "Escolha o Centro que você quer entrar";
            let label = "Centros: ";

            openModal("modal1", centers, title, label, function(selectedCenter) {
                infoDict["center2"] = selectedCenter;

                let days = Object.keys(doctorsDict[selectedDoc][selectedCenter])
                days = days.map(h => [h, h])
                let title = "Escolha o dia que você quer entrar";
                let label = "Dias: ";

                openModal("modal2", days, title, label, function(selectedDay) {
                    infoDict["day2"] = selectedDay;

                    let hours = doctorsDict[selectedDoc][selectedCenter][selectedDay]
                    hours = hours[0].map(h => [h, h]);
                    let title = "Escolha as Horas que você quer entrar";
                    let label = "Horas: ";

                    openModal("modal1", hours, title, label, function(selectedHour){
                        infoDict["hours2"] = selectedHour;

                        sendHoursToServer("exchange", infoDict)
                    });
                });
            });
        });
    });
}

function handleExchangeFromOtherUser(infoDict) {
    let selectedDoc = currUserData[0];

    let availableHours = redudantHoursList;
    let title = "Especifique as Horas nas quais Você quer Entrar";
    let label = "Horários: ";
    
    openModal('modal2', availableHours, title, label, function(selectedValue) {
        infoDict["hours"] = selectedValue;
        infoDict["crm2"] = currUserData[0];

        let centers = Object.keys(doctorsDict[selectedDoc]);
        centers = centers.map(h => [h, h]);
        let title = "Escolha o Centro do qual você quer sair";
        let label = "Centros: ";

        openModal("modal1", centers, title, label, function(selectedCenter) {
            infoDict["center2"] = selectedCenter;

            let days = Object.keys(doctorsDict[selectedDoc][selectedCenter])
            days = days.map(h => [h, h])
            let title = "Escolha o dia que você do qual você quer sair";
            let label = "Dias: ";

            openModal("modal2", days, title, label, function(selectedDay) {
                infoDict["day2"] = selectedDay;

                let hours = doctorsDict[selectedDoc][selectedCenter][selectedDay]
                hours = hours[0].map(h => [h, h]);
                let title = "Escolha as Horas das quais você quer sair";
                let label = "Horas: ";
                
                openModal("modal1", hours, title, label, function(selectedHour){
                    infoDict["hours2"] = selectedHour;

                    sendHoursToServer("exchange_from_other_user", infoDict)
                });
            });
        });
    });
}


// exclude function
function handleExclude(infoDict) {
    let availableHours = redudantHoursList;
    let title = "Especifique Horas para Excluir";
    let label = "Horários: "
    
    openModal('modal1', availableHours, title, label, function(selectedValue) {
        infoDict["hours"] = selectedValue;
        sendHoursToServer("exclude", infoDict);
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
    let title = "Escolha Horas para Doar";
    let label = "Horários: ";
    
    openModal("modal1", availableHours, title, label, function(selectedHrs) {
        infoDict["hours"] = selectedHrs;

        let doctors = doctorsList.filter(d => d[0] !== parseInt(currUserData[0]));
        let title = "Escolha para quem Doar";
        let label = "Médicos: ";

        openModal("modal2", doctors, title, label, function(selectedDoc) {
            infoDict["receiverCRM"] = selectedDoc;
            sendHoursToServer("donate", infoDict);
        });
    });
}

function handleRequestDonation(infoDict) {
    let availableHours = redudantHoursList;
    let title = "Escolha Horas para Receber";
    let label = "Horários: ";
    
    openModal("modal1", availableHours, title, label, function(selectedHrs) {
        infoDict["hours"] = selectedHrs;  
        sendHoursToServer("donate", infoDict);
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
            // alert("Requisição Realizada com Sucesso");
            console.log('The request was successful and returned:', data.message);
        } else {
            // alert("Requisição Não Realizada:\nVerifique os dados e tente novamente");
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
