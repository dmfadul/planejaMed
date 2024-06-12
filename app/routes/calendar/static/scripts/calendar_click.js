document.addEventListener('DOMContentLoaded', function() {
    function handleDayClick(event) {
        const clickedDay = event.target;
        const center = document.querySelector('.calendar-header th').textContent.split(' ').slice(-1)[0];
        // Check if clicked element is a day (a TD element with a number)
        if (clickedDay.tagName === "TD" && !isNaN(clickedDay.innerText) && clickedDay.innerText !== '') {
            document.querySelectorAll('.calendar td').forEach(td => {
                td.classList.remove('day-clicked');
            });

            clickedDay.classList.add('day-clicked');

            fetch(`/calendar/${center}/${clickedDay.innerText}`)
                .then(response => response.json())
                .then(data => {
                    let output = '<ul>';

                    let dayList = data.data;

                    let index = 0;
                    for (let item of dayList) {
                        output += `
                            <li id="item-${index}">
                                ${item.split("*").join("<br>")}
                                <div class="kebab-menu">
                                    <button class="kebab-button">&#8942;</button>
                                    <div class="kebab-content">
                                        <a href="#" onclick="processRequest('${item.split("*").join("<br>")}', 'exchange')" data-action="exchange">Trocar</a>
                                        <a href="#" onclick="processRequest('${item.split("*").join("<br>")}', 'exclude')" data-action="exclude">Excluir</a>
                                        <a href="#" onclick="processRequest('${item.split("*").join("<br>")}', 'donation')" data-action="donation">Doação</a>
                                    </div>
                                </div>
                            </li>`;
                        index++;
                    }
                    output += '</ul>';  // Close the unordered list

                    document.getElementById('dictData').innerHTML = output;
                })
        }
    }

    // Add the click event listener to the table
    const calendarTable = document.querySelector('.calendar');
    calendarTable.addEventListener('click', handleDayClick);
});