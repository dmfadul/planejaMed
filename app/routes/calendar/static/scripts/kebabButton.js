document.addEventListener('click', function(event) {
    if (event.target.classList.contains('kebab-button')) {
        event.target.nextElementSibling.style.display = 'block';
    } else {
        var openMenus = document.querySelectorAll('.kebab-content');
        for (var menu of openMenus) {
            if (menu.style.display === 'block') {
                menu.style.display = 'none';
            }
        }
    }
});
