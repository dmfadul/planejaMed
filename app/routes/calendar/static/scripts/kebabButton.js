document.addEventListener('click', function(event) {
    if (event.target.classList.contains('card')) {
        event.target.closest('.card').querySelector('.kebab-content').style.display = 'block';
    } else {
        let openMenus = document.querySelectorAll('.kebab-content');
        for (let menu of openMenus) {
            if (menu.style.display === 'block') {
                menu.style.display = 'none';
            }
        }
    }
});
