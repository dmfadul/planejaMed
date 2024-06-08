import instance.global_vars as global_vars


def resolve_data(data):
    hours_map = global_vars.HOURS_MAP
    center = data.get("center")
    month = data.get("month")
    year = data.get("year")
    action = data.get("action")
    selected_cells = data.get("selectedCells")

    print(hours_map, center, month, year, action, selected_cells)

    return 0