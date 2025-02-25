function processSchRequest(item, action) {
    let infoDict = {};
    crm = currUserData[0];
    infoDict["crm"] = crm;

    if (action === "include") {
        handleSchInclude(infoDict);
    } else {
        let center = item.split("--")[0].trim();
        let date = item.split("--")[1].trim();
        let hours = item.split("--")[2].trim();

        let day = parseInt(date.split("/")[0].trim());

        infoDict["day"] = parseInt(date.split("/")[0]);
        infoDict["center"] = center;
        infoDict["hours"] = hours;

        console.log(crm, day, center, hours);
        xhr = new XMLHttpRequest();
        xhr.open('GET', `/get-redundant-hours?crm=${crm}&center=${center}&day=${day}`, true);

        xhr.onload = function() {
            if (this.status === 200) {
                let redudantHoursList = JSON.parse(this.responseText);
                redudantHoursList = redudantHoursList.map(h => [h, h]);
                
                if (action === "exclude") {
                    handleSchExclude(infoDict, redudantHoursList);
                } else if (action === "donate") {
                    handleOfferDonation(infoDict);
                } else if (action === "exchange") {
                    handleExchangeFromCurrentUser(infoDict);
                } else {
                    console.log("Invalid action");
                }
            } else {
                console.log("Error: Could not get redundant hours list");
            }
        }
        xhr.send();
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

function handleSchExclude(infoDict, availableHours) {
    console.log(availableHours);
    let title = "Especifique Horas para Excluir";
    let label = "Horários: ";
    
    openModal('modal1', availableHours, title, label, function(selectedValue) {
        infoDict["hours"] = selectedValue;
        sendHoursToServer("exclude", infoDict);
    });
}


// Calendar functions
function processCalRequest(crm, action) {
    infoDict = {};
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
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/get-doctors', true);
    xhr.onload = function() {
        if (this.status === 200) {
            let doctors = JSON.parse(this.responseText);
            doctors = doctors.map(d => [d[0], d[1]]);

            let title = "Escolha quem Incluir";
            let label = "Médicos: ";
        
            openModal("modal1", doctors, title, label, function(selectedDoc) {
                infoDict["crm"] = selectedDoc;
                openHourModal(function(selectedValue){
                    infoDict["hours"] = selectedValue;
                    sendHoursToServer("include", infoDict);
                });
            });
        } else {
            console.log("Error: Could not get doctors list");
        }
    }
    xhr.send();
}

// exchange functions
function handleExchange(infoDict) {
    if (parseInt(infoDict["crm"]) === currUserData[0]) {
        console.log("Exchange from current user");
        handleExchangeFromCurrentUser(infoDict);
    } else {
        console.log("Exchange from other user");
        handleExchangeFromOtherUser(infoDict);
    }
}

function handleExchangeFromCurrentUser(infoDict) {
    let crm = infoDict["crm"];
    let center = infoDict["center"];
    let day = infoDict["day"];

    xhr = new XMLHttpRequest();
    xhr.open('GET', `/get-redundant-hours?crm=${crm}&center=${center}&day=${day}`, true);

    xhr.onload = function() {
        if (this.status === 200) {
            let availableHours = JSON.parse(this.responseText);
            availableHours = availableHours.map(h => [h, h]);

            let title = "Especifique as Horas das quais Você quer Sair";
            let label = "Horários: ";
    
            openModal('modal1', availableHours, title, label, function(selectedValue) {
                infoDict["hours"] = selectedValue;
                
                xhr = new XMLHttpRequest();
                xhr.open('GET', '/get-doctors', true);

                xhr.onload = function() {
                    if (this.status === 200) {
                        let doctorsList = JSON.parse(this.responseText);
                        doctors = doctorsList.filter(d => d[0] !== currUserData[0]);
                        doctors = doctors.map(d => [d[0], d[1]]);

                        let title = "Escolha com quem Trocar";
                        let label = "Médicos: ";
            
                        openModal("modal2", doctors, title, label, function(selectedDoc) {
                            infoDict["crm2"] = selectedDoc;
                            
                            xhr = new XMLHttpRequest();
                            xhr.open('GET', `/get-doctor-centers?crm=${selectedDoc}`, true);
                            
                            xhr.onload = function() {
                                if (this.status === 200) {
                                    let centers = JSON.parse(this.responseText);
                                    centers = centers.map(h => [h, h]);
                
                                    let title = "Escolha o Centro que você quer entrar";
                                    let label = "Centros: ";
                        
                                    openModal("modal1", centers, title, label, function(selectedCenter) {
                                        infoDict["center2"] = selectedCenter;
                                        xhr = new XMLHttpRequest();
                                        xhr.open('GET', `/get-doctor-days?crm=${selectedDoc}&center=${selectedCenter}`, true);

                                        xhr.onload = function() {
                                            if(this.status === 200) {
                                                let days = JSON.parse(this.responseText);
                                                days = days.map(h => [h, h])
                                                let title = "Escolha o dia que você quer entrar";
                                                let label = "Dias: ";
                                 
                                                openModal("modal2", days, title, label, function(selectedDay) {
                                                    infoDict["day2"] = selectedDay;

                                                    xhr = new XMLHttpRequest();
                                                    xhr.open('GET', `/get-redundant-hours?crm=${selectedDoc}&center=${selectedCenter}&day=${selectedDay}`, true);

                                                    xhr.onload = function() {
                                                        if (this.status === 200) {
                                                            let hours = JSON.parse(this.responseText);
                                                            hours = hours.map(h => [h, h]);
                                                            let title = "Escolha as Horas que você quer entrar";
                                                            let label = "Horas: ";
                                                    
                                                            openModal("modal1", hours, title, label, function(selectedHour){
                                                                infoDict["hours2"] = selectedHour;
                                                                
                                                                sendHoursToServer("exchange", infoDict)
                                                            });
                                                        } else {
                                                            console.log("Error: Could not get redundant hours list");
                                                        }
                                                    }
                                                    xhr.send();
                                                });
                                            } else {
                                                console.log("Error: Could not get doctors list");
                                            }
                                        }
                                        xhr.send();
                                    });
                                } else {
                                    console.log("Error: Could not get doctors list");
                                }
                            }
                            xhr.send();
                        });
                    } else {
                        console.log("Error: Could not get doctors list");
                    }
                }
                xhr.send();
            });
        } else {
            console.log("Error: Could not get redundant hours list");
        }
    }
    xhr.send();
}

function handleExchangeFromOtherUser(infoDict) {
    let selectedDoc = currUserData[0];

    let crm = infoDict["crm"];
    let center = infoDict["center"];
    let day = infoDict["day"];
    
    let xhr = new XMLHttpRequest();
    xhr.open('GET', `/get-redundant-hours?crm=${crm}&center=${center}&day=${day}`, true);

    xhr.onload = function() {
        if (this.status === 200) {
            let availableHours = JSON.parse(this.responseText);
            availableHours = availableHours.map(h => [h, h]);

            let title = "Especifique as Horas nas quais Você quer Entrar";
            let label = "Horários: ";

            openModal('modal1', availableHours, title, label, function(selectedValue) {
                if (selectedValue === null) return; // User cancelled
                infoDict["hours"] = selectedValue;
                infoDict["crm2"] = currUserData[0];
                
                let xhr = new XMLHttpRequest();
                xhr.open('GET', `/get-doctor-centers?crm=${selectedDoc}`, true);

                xhr.onload = function() {
                    if (this.status === 200) {
                        let centers = JSON.parse(this.responseText);
                        centers = centers.map(h => [h, h]);
                
                        let title = "Escolha o Centro do qual você quer sair";
                        let label = "Centros: ";

                        openModal("modal1", centers, title, label, function(selectedCenter) {
                            if (selectedCenter === null) return; // User cancelled
                            infoDict["center2"] = selectedCenter;
                            
                            let xhr = new XMLHttpRequest();
                            xhr.open('GET', `/get-doctor-days?crm=${selectedDoc}&center=${selectedCenter}`, true);

                            xhr.onload = function() {
                                if(this.status === 200) {
                                    let days = JSON.parse(this.responseText);
                                    days = days.map(h => [h, h]);

                                    let title = "Escolha o dia que você do qual você quer sair";
                                    let label = "Dias: ";

                                    openModal("modal2", days, title, label, function(selectedDay) {
                                        if (selectedDay === null) return; // User cancelled
                                        infoDict["day2"] = selectedDay;

                                        let xhr = new XMLHttpRequest();
                                        xhr.open('GET', `/get-redundant-hours?crm=${selectedDoc}&center=${selectedCenter}&day=${selectedDay}`, true);

                                        xhr.onload = function() {
                                            if (this.status === 200) {
                                                let hours = JSON.parse(this.responseText);
                                                hours = hours.map(h => [h, h]);
                                                let title = "Escolha as Horas das quais você quer sair";
                                                let label = "Horas: ";

                                                openModal("modal1", hours, title, label, function(selectedHour){
                                                    if (selectedHour === null) return; // User cancelled
                                                    infoDict["hours2"] = selectedHour;
                                                    sendHoursToServer("exchange_from_other_user", infoDict);
                                                });
                                            }
                                        }
                                        xhr.send();
                                    });
                                }
                            }
                            xhr.send();
                        });
                    }
                }
                xhr.send();
            });
        }
    }
    xhr.send();
}


// exclude function
function handleExclude(infoDict) {
    let crm = infoDict["crm"];
    let center = infoDict["center"];
    let day = infoDict["day"];
    
    xhr = new XMLHttpRequest();
    xhr.open('GET', `/get-redundant-hours?crm=${crm}&center=${center}&day=${day}`, true);

    xhr.onload = function() {
        if (this.status === 200) {
            let availableHours = JSON.parse(this.responseText);
            availableHours = availableHours.map(h => [h, h]);

            let title = "Especifique Horas para Excluir";
            let label = "Horários: "
 
            openModal('modal1', availableHours, title, label, function(selectedValue) {
                infoDict["hours"] = selectedValue;
                sendHoursToServer("exclude", infoDict);
            });
        } else {
            console.log("Error: Could not get redundant hours list");
        }
    }
    xhr.send();
}

// donation functions
function handleDonate(infoDict) {
    if (currUserData[0] === parseInt(infoDict["crm"])) {
        console.log("Donation from current user");
        handleOfferDonation(infoDict);
    }else{
        console.log("Donation from other user");
        handleRequestDonation(infoDict);
    }
}

function handleOfferDonation(infoDict) {
    let crm = infoDict["crm"];
    let center = infoDict["center"];
    let day = infoDict["day"];

    xhr = new XMLHttpRequest();
    xhr.open('GET', `/get-redundant-hours?crm=${crm}&center=${center}&day=${day}`, true);
    
    xhr.onload = function() {
        if (this.status == 200) {
            let availableHours = JSON.parse(this.responseText);
            availableHours = availableHours.map(h => [h, h]);

            let title = "Escolha Horas para Doar";
            let label = "Horários: ";
            
            openModal("modal1", availableHours, title, label, function(selectedHrs) {
                infoDict["hours"] = selectedHrs;

                xhr = new XMLHttpRequest();
                xhr.open('GET', '/get-doctors', true);

                xhr.onload = function() {
                    if (this.status === 200) {
                        let doctors = JSON.parse(this.responseText);
                        doctors = doctors.filter(d => d[0] !== parseInt(currUserData[0]));
                        doctors = doctors.map(d => [d[0], d[1]]);

                        let title = "Escolha para quem Doar";
                        let label = "Médicos: ";
        
                        openModal("modal2", doctors, title, label, function(selectedDoc) {
                            infoDict["receiverCRM"] = selectedDoc;
                            sendHoursToServer("donate", infoDict);
                        });
                    } else {
                        console.log("Error: Could not get doctors list");
                    }
                }
                xhr.send();
            });            
        } else {
            console.log("Error: Could not get redundant hours list");
        }
    }
    xhr.send();
}

function handleRequestDonation(infoDict) {
    let crm = infoDict["crm"];
    let center = infoDict["center"];
    let day = infoDict["day"];

    xhr = new XMLHttpRequest();
    xhr.open('GET', `/get-redundant-hours?crm=${crm}&center=${center}&day=${day}`, true);

    xhr.onload = function() {
        if (this.status === 200) {
            let availableHours = JSON.parse(this.responseText);
            availableHours = availableHours.map(h => [h, h]);

            let title = "Escolha Horas para Receber";
            let label = "Horários: ";
    
            openModal("modal1", availableHours, title, label, function(selectedHrs) {
                infoDict["hours"] = selectedHrs;
                sendHoursToServer("donate", infoDict);
            });
        } else {
            console.log("Error: Could not get redundant hours list");
        }
    }
    xhr.send();
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
