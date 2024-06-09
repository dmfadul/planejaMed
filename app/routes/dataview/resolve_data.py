import instance.global_vars as global_vars


def resolve_data(data):
    hours_map = global_vars.HOURS_MAP
    action = data.get("action")
    center = data.get("center")
    month = data.get("month")
    year = data.get("year")
    selected_cells = data.get("selectedCells")

    print("Action: ", action)
    print("Center: ", center)
    print("Month: ", month)
    print("Year: ", year)

    for cell in selected_cells:
        weekday = cell.get("weekDay")
        monthday = cell.get("monthDay")
        doctor_crm = cell.get("doctorCrm")
        hours = cell.get("hourValue")

        print("Weekday: ", weekday)
        print("Monthday: ", monthday)
        print("Doctor CRM: ", doctor_crm)
        print("Hours: ", hours) 
    return 0