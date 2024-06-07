var state = {
    mode: null, // 'edit', or null
    action: null, //'add', 'delete' or null
    center: null,
    month: null,
    year: null,
    selectedCells: [] // Array of objects with cell info
};

function startEditing() {
    document.getElementById('default-buttons').style.display = 'none';
    document.getElementById('edit-buttons').style.display = 'block';

    //document.getElementById('myButton').classList.add('disabled-button');

    state.mode = 'edit';
    state.center = centerValue;
    state.month = monthValue;
    state.year = yearValue;
    state.selectedCells = []; // Clear previous selections
}


function finishEditing() {
    document.getElementById('edit-buttons').style.display = 'none';
    document.getElementById('default-buttons').style.display = 'block';
    // Remove 'selected' class from all cells
    document.querySelectorAll('.selected').forEach(cell => {
        cell.classList.remove('selected');
        cell.style.backgroundColor = ""; // Reset background color if needed
        state.selectedCells = [];
    });
    state.mode = null;
    state.action = null;

}
