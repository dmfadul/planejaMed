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

            let dayList = daysDict[clickedDay.innerText];

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
                                    <a href="#" onclick="processRequest('${itemContent}', 'cal_include')" data-action="include">Inclusão</a>
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
                                    <a href="#" onclick="processRequest('${itemContent}', 'cal_exchange')" data-action="exchange">Troca</a>
                                    <a href="#" onclick="processRequest('${itemContent}', 'cal_exclude')" data-action="exclude">Exclusão</a>
                                    <a href="#" onclick="processRequest('${itemContent}', 'cal_donate')" data-action="donation">Doação</a>
                                </div>
                            </div>
                        </li>`;
                }
                index++;
            }
            output += '</ul>';  // Close the unordered list

            document.getElementById('dictData').innerHTML = output;
            console.log(daysDict[clickedDay.innerText]);
        }
    }

    // Add the click event listener to the table
    const calendarTable = document.querySelector('.calendar');
    calendarTable.addEventListener('click', handleDayClick);
});
