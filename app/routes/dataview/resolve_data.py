from app import create_app
from app.models import User, BaseAppointment, Center
import instance.global_vars as global_vars


def convert_hours(hour_list):
    hours_map = global_vars.HOURS_MAP

    if hour_list[0] == "-":
        start_hour, end_hour = int(hour_list[1].split(":")[0]), int(hour_list[2].split(":")[0])
        if start_hour == end_hour:
            return 1
        if start_hour > end_hour and end_hour > 6:
            return 2 
        
        if start_hour > end_hour:
            hours = list(range(start_hour, 24)) + list(range(0, end_hour))
        else:
            hours = list(range(start_hour, end_hour))
    else:
        start_hour, end_hour = hours_map[hour_list[0]]
        hours = list(range(start_hour, end_hour + 1))

    return hours


def resolve_data(data):


    if data.get("year") is None:
        resolve_base_appointments(data)

    else:
        resolve_month_appointments(data)
        

    return 0


def resolve_base_appointments(data):
    action = data.get("action")
    center = Center.query.filter_by(abbreviation=data.get("center")).first()

    selected_cells = data.get("selectedCells")
    for cell in selected_cells:
        weekday = [day[:3] for day in global_vars.DIAS_SEMANA].index(cell.get("weekDay"))
        weekindex = int(cell.get("monthDay"))
        doctor = User.query.filter_by(crm=cell.get("doctorCRM")).first()

        if action == "delete":
            app = create_app()
            with app.app_context():
                base_appointments = BaseAppointment.query.filter_by(
                    user_id=doctor.id,
                    center_id=center.id,
                    week_day=weekday,
                    week_index=weekindex,
                ).all()

                for base_appointment in base_appointments:
                    print("base_appointment: ", base_appointment)
                    base_appointment.delete_entry()

        elif action == "add":
            hour_list = cell.get("hourValue") # Hour_list has the format ["-", "00:00", "00:00"]
            hours = convert_hours(hour_list)
            if hours == 1:
                print("A hora inicial e final são iguais")
            if hours == 2:
                print("Horário final passa para o dia seguinte")
            app = create_app()
            with app.app_context():
                for hour in hours:
                    print("hour: ", hour)
                    BaseAppointment.add_entry(doctor.id, center.id, weekday, weekindex, hour)

        else:
            print("Erro")


def resolve_month_appointments(data):
    action = data.get("action")
    center = data.get("center")
    month = data.get("month")
    year = data.get("year")
    selected_cells = data.get("selectedCells")