from app import create_app
from app.models import User, Center, Day, Month, BaseAppointment, Appointment
from datetime import datetime
import app.global_vars as global_vars


def convert_hours(hour_list):
    # convert the string hour list from the frontend to a list of integers
    hours_map = global_vars.HOURS_MAP

    if hour_list[0] == "-":
        start_hour, end_hour = int(hour_list[1].split(":")[0]), int(hour_list[2].split(":")[0])
        if start_hour == end_hour and not start_hour == 7:
            return "Horários Inválidos - A hora de Início e de Fim são iguais"
        if start_hour > end_hour and end_hour > 6:
            return "Horários Inválidos - A hora de Fim Passa para o Dia Seguinte"
        
        if start_hour >= end_hour:
            hours = list(range(start_hour, 24)) + list(range(end_hour))
        else:
            hours = list(range(start_hour, end_hour))
    else:
        start_hour, end_hour = hours_map[hour_list[0]]
        
        if start_hour > end_hour:
            hours = list(range(start_hour, 24)) + list(range(end_hour + 1))
        else:
            hours = list(range(start_hour, end_hour + 1))

    return hours


def resolve_data(data):
    if data.get("year") is None:
        flag = resolve_base_appointments(data)
    else:
        flag = resolve_month_appointments(data)  

    return flag


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
                    base_appointment.delete_entry()
            
            return 0

        elif action == "add":
            hour_list = cell.get("hourValue") # Hour_list has the format ["-", "00:00", "00:00"]
            hours = convert_hours(hour_list)
            if isinstance(hours, str):
                return hours
            
            app = create_app()
            with app.app_context():
                flags = []
                for hour in hours:
                    flag = BaseAppointment.add_entry(doctor.id, center.id, weekday, weekindex, hour)
                    if isinstance(flag, str):
                        flags.append(flag)

            return 0 if not flags else '\n'.join(list(set(flags)))
        else:
            print("Erro")


def resolve_month_appointments(data):
    action = data.get("action")
    center = Center.query.filter_by(abbreviation=data.get("center")).first()
    year = int(data.get("year"))
    month = Month.query.filter_by(number=global_vars.MESES.index(data.get("month"))+1, year=year).first()

    selected_cells = data.get("selectedCells")
    for cell in selected_cells:
        doctor = User.query.filter_by(crm=cell.get("doctorCRM")).first()
        monthday = int(cell.get("monthDay"))
        day = [day for day in month.days if day.date.day == monthday]
            
        if not day:
            print("erro")
        else:
            day = day[0]
        
        if action == "delete":
            app = create_app()
            with app.app_context():
                appointments = Appointment.query.filter_by(
                    user_id=doctor.id,
                    center_id=center.id,
                    day_id = day.id,
                ).all()

                for appointment in appointments:
                    print("appointment: ", appointment.hour)
                    appointment.delete_entry()

        elif action == "add":
            hour_list = cell.get("hourValue") # Hour_list has the format ["-", "00:00", "00:00"]
            hours = convert_hours(hour_list)
            if hours == 1:
                return 1
            if hours == 2:
                return 2

            app = create_app()
            with app.app_context():
                flags = []
                for hour in hours:
                    flag = Appointment.add_entry(doctor.id, center.id, day.id, hour)
                    if flag == -1:
                        flags.append((doctor.id, center.id, day.id, hour))
            return 0 if not flags else -1
        else:
            print("Erro")
