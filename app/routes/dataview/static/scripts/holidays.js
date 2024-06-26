function addHoliday() {
    askForHoliday().then(holiday => {
        if (holiday) {
            showHoliday(holiday);
            sendHoliday(holiday, action='add');
        }
    }).catch(error => {
        console.log(error);
    });
}

function removeHoliday() {
    askForHoliday().then(holiday => {
        if (holiday) {
            eraseHoliday(holiday);
            sendHoliday(holiday, action='remove');
        }
    }).catch(error => {
        console.log(error);
    });
}

function askForHoliday() {
    return new Promise((resolve, reject) => {
        const width = 400;
        const height = 200;
        const left = (window.screen.width / 2) + (9 * width);
        const top = (window.screen.height / 2) - height;

        const newWindow = window.open('', '', `width=${width},height=${height},left=${left},top=${top}`);

        newWindow.document.write('<html><head><title>Enter Number</title>');
        newWindow.document.write('<link rel="stylesheet" type="text/css" href="/static/css/tableaux/popup.css">');
        newWindow.document.write('</head><body>');
        newWindow.document.write('<input type="number" id="numberInput" placeholder="Enter a number"/>');
        newWindow.document.write('<button id="cancelButton">Cancel</button>');
        newWindow.document.write('<button id="okButton">OK</button>');
        newWindow.document.write('</body></html>');

        newWindow.document.close();

        const numberInput = newWindow.document.getElementById('numberInput');
        numberInput.focus();
        const okButton = newWindow.document.getElementById('okButton');

        numberInput.addEventListener('keypress', function(event) {
            if (event.keyCode === 13) { // 13 is the Enter key
                okButton.click();
            }
        });

        newWindow.document.getElementById('okButton').onclick = () => {
            const number = parseFloat(newWindow.document.getElementById('numberInput').value);
            if (!isNaN(number)) {
                newWindow.close();
                resolve(number);
            } else {
                alert("Please enter a valid number.");
            }
        };

        newWindow.document.getElementById('cancelButton').onclick = () => {
            reject('User cancelled the operation');
            newWindow.close();
        };
    });
}

function sendHoliday(holiday, action) {
    fetch('/resolve_holiday', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({'holiday': holiday, 'action': action}),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function showHoliday(holiday) {
    let targetClass = "col_" + holiday
    const elements = document.querySelectorAll('.' + targetClass);
    elements.forEach(element => {
        element.classList.add('holiday');
    });
}

function eraseHoliday(holiday) {
    let targetClass = "col_" + holiday
    const elements = document.querySelectorAll('.' + targetClass);
    elements.forEach(element => {
        element.classList.remove('holiday');
    });
}

function showAllHolidays(holidayVector) {
    for (let i=0; i < holidayVector.length; i++) {
        showHoliday(holidayVector[i]);
    }
}
