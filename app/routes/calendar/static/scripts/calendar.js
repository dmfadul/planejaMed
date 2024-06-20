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
                        const itemContent = item.split("*").join("<br>");
                        if (item === '-') {
                            output += `
                                <li id="item-${index}">
                                    ${itemContent}
                                    <div class="kebab-menu">
                                        <button class="kebab-button">&#8942;</button>
                                        <div class="kebab-content">
                                            <a href="#" onclick="processRequest('${itemContent}', 'include')" data-action="include">Inclusão</a>
                                        </div>
                                    </div>
                                </li>`;
                        } else {
                            output += `
                                <li id="item-${index}">
                                    ${itemContent}
                                    <div class="kebab-menu">
                                        <button class="kebab-button">&#8942;</button>
                                        <div class="kebab-content">
                                            <a href="#" onclick="processRequest('${itemContent}', 'exchange')" data-action="exchange">Troca</a>
                                            <a href="#" onclick="processRequest('${itemContent}', 'exclude')" data-action="exclude">Exclusão</a>
                                            <a href="#" onclick="processRequest('${itemContent}', 'donation')" data-action="donation">Doação</a>
                                        </div>
                                    </div>
                                </li>`;
                        }
                        index++;
                    }
                    output += '</ul>';  // Close the unordered list

                    document.getElementById('dictData').innerHTML = output;
                });
        }
    }

    // Add the click event listener to the table
    const calendarTable = document.querySelector('.calendar');
    calendarTable.addEventListener('click', handleDayClick);
});
