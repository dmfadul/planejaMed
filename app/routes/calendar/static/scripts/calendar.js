let day;


function displayDayData(dayDict) {
    let output = '<ul>'
    output += `
    <li id="item-0" class="card">
        INCLUSÃO
        <div class="kebab-menu">
            <button class="kebab-button"></button>
            <div class="kebab-content">
                <a href="#" onclick="processCalRequest('0', 'include')" data-action="include">Inclusão</a>
            </div>
        </div>
    </li>`;
    
    let dayValues = Object.entries(dayDict).sort((a, b) => a[1].name.localeCompare(b[1].name))

    for (let [crm, infoDict] of dayValues) {
        let name = infoDict['name'];
        let hourLine = infoDict['hours'][0];
        hourLine = hourLine.replace(/\*/g, '<br>');

        const itemContent = [name, hourLine].join("<br>");

        output += `
        <li id="${crm}" class="card">
            ${itemContent}
            <div class="kebab-menu">
                <button class="kebab-button"></button>
                <div class="kebab-content">
                <a href="#" onclick="processCalRequest('${crm}', 'exclude')" data-action="exclude">Exclusão</a>
                <a href="#" onclick="processCalRequest('${crm}', 'donate')" data-action="donation">Doação</a>
                <a href="#" onclick="processCalRequest('${crm}', 'exchange')" data-action="exchange">Troca</a>
                </div>
            </div>
        </li>`;

    }
    output += '</ul>';  // Close the unordered list
    
    document.getElementById('dictData').innerHTML = output;
}


document.addEventListener('DOMContentLoaded', function() {
    function handleDayClick(event) {
        const clickedDay = event.target;
        // Check if clicked element is a day (a TD element with a number)
        if (clickedDay.tagName === "TD" && !isNaN(clickedDay.innerText) && clickedDay.innerText !== '') {
            document.querySelectorAll('.calendar td').forEach(td => {
                td.classList.remove('day-clicked');
            });

            clickedDay.classList.add('day-clicked');   
            day = clickedDay.innerText;

            const xhr = new XMLHttpRequest();
            xhr.open('GET', `/get-day-data?day=${encodeURIComponent(day)}&center=${encodeURIComponent(openCenter)}`, true);

            xhr.onload = function() {
                if (this.status === 200) {
                    const response = JSON.parse(this.responseText);
                    // console.log(response);
                    displayDayData(response);
                } else {
                    console.error('Error fetching day data');
                }
                xhr.onerror = function() {
                    console.error('Error fetching day data');
                }
            }
            xhr.send();
        }
    }

    // Add the click event listener to the table
    const calendarTable = document.querySelector('.calendar');
    calendarTable.addEventListener('click', handleDayClick);
});
