document.addEventListener('DOMContentLoaded', function() {
    // Access the data from the data-container
     let dataContainer = document.getElementById('data-container');
     let schedule = JSON.parse(dataContainer.getAttribute('data-items'));
 
     createScheduleCards(schedule);
 });
 
 
 function createScheduleCards(schedule) {
     let output = '<ul>';
 
     let index = 0;
     for (let item of schedule) {
     let action = (index === 0) ? 'include' : 'exclude';
     let label = (index === 0) ? 'Inclusão' : 'Exclusão';
 
         output += `
             <li id="item-${index}">
                 ${item.split("*").join("<br>")}
                 <div class="kebab-menu">
                     <button class="kebab-button">&#8942;</button>
                     <div class="kebab-content">
                         <a href="#" onclick="processRequest('${item}', '${action}')" data-action="${action}">${label}</a>
                         ${index !== 0 ? `<a href="#" onclick="processRequest('${item}', 'donation')" data-action="donation">Doação</a>` : ''}
                         ${index !== 0 ? `<a href="#" onclick="processRequest('${item}', 'exchange')" data-action="exchange">Troca</a>` : ''}
                     </div>
                 </div>
             </li>`;
         index++;
     }
     output += '</ul>';
 
     document.getElementById('dictData').innerHTML = output;
 }
 