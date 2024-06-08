function cellClicked(cell) {
    if (!state.mode) return; // Do nothing if no mode is selected

    var isSelected = cell.classList.contains('selected');
    if (isSelected) {
        //FIXed UNSELECT BUG ?
        cell.classList.remove('selected');
        cell.style.backgroundColor = ""; // Reset background color

        //Remove cell from state.selectedCells
        state.selectedCells = state.selectedCells.filter(info => info.cell !== cell);
    } else {
        cell.classList.add('selected');
        cell.style.backgroundColor = 'gray';

        // Collect cell info
        var weekDay = cell.closest("table").querySelectorAll("tr")[0].cells[cell.cellIndex].textContent;
        var monthDay = cell.closest("table").querySelectorAll("tr")[1].cells[cell.cellIndex].textContent;
        var doctorName = cell.closest("tr").querySelector("td").textContent;
        var doctorCRM = cell.closest("tr").querySelector("td").getAttribute("id");
        var hourValue = cell.textContent;

        // Add to state
        state.selectedCells.push({
            weekDay: weekDay,
            monthDay: monthDay,
            doctorName: doctorName,
            doctorCRM: doctorCRM,
            hourValue: hourValue,
            cell: cell
        });
    }
  }
