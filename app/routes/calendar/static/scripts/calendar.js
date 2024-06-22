let day;

document.addEventListener('DOMContentLoaded', function() {
    function handleDayClick(event) {
        const clickedDay = event.target;
        // Check if clicked element is a day (a TD element with a number)
        if (clickedDay.tagName === "TD" && !isNaN(clickedDay.innerText) && clickedDay.innerText !== '') {
            document.querySelectorAll('.calendar td').forEach(td => {
                td.classList.remove('day-clicked');
            });

            clickedDay.classList.add('day-clicked');
            let output = '<ul>';

            day = clickedDay.innerText;
            let dayList = daysDict[day];

            let index = 0;
            for (let name_crm of dayList) {
                let item = name_crm[0];
                const itemContent = item.split("*").join("<br>");
                if (item === '-') {
                    output += `
                        <li id="item-${index}">
                            ${itemContent}
                            <div class="kebab-menu">
                                <button class="kebab-button">&#8942;</button>
                                <div class="kebab-content">
                                    <a href="#" onclick="processCalRequest('${itemContent}', '${name_crm[1]}', 'include')" data-action="include">Inclusão</a>
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
                                    <a href="#" onclick="processCalRequest('${itemContent}', '${name_crm[1]}', 'exchange')" data-action="exchange">Troca</a>
                                    <a href="#" onclick="processCalRequest('${itemContent}', '${name_crm[1]}', 'exclude')" data-action="exclude">Exclusão</a>
                                    <a href="#" onclick="processCalRequest('${itemContent}', '${name_crm[1]}', 'donate')" data-action="donation">Doação</a>
                                </div>
                            </div>
                        </li>`;
                }
                index++;
            }
            output += '</ul>';  // Close the unordered list

            document.getElementById('dictData').innerHTML = output;
        }
    }

    // Add the click event listener to the table
    const calendarTable = document.querySelector('.calendar');
    calendarTable.addEventListener('click', handleDayClick);
});
