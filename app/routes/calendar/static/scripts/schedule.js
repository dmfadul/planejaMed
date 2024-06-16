document.addEventListener('DOMContentLoaded', function() {
    // Access the data from the data-container
     let dataContainer = document.getElementById('data-container');
     let schedule = JSON.parse(dataContainer.getAttribute('data-items'));
 
     createContent(schedule);
 });
 
 
 function createContent(schedule) {
     let output = '<ul>';
 
     let index = 0;
     for (let item of schedule) {
     let action = (index === 0) ? 'include' : 'exclude';
     let label = (index === 0) ? 'Incluir' : 'Excluir';
 
         output += `
             <li id="item-${index}">
                 ${item.split("*").join("<br>")}
                 <div class="kebab-menu">
                     <button class="kebab-button">&#8942;</button>
                     <div class="kebab-content">
                         <a href="#" onclick="processRequest('${item.split("*").join("<br>")}', '${action}')" data-action="${action}">${label}</a>
                         ${index !== 0 ? `<a href="#" onclick="processRequest('${item.split("*").join("<br>")}', 'donation')" data-action="donation">Doar</a>` : ''}
                     </div>
                 </div>
             </li>`;
         index++;
     }
     output += '</ul>';
 
     document.getElementById('dictData').innerHTML = output;
 }
 