from app import create_app
from app.models import User, Center, Day, Month, BaseAppointment, Appointment
from datetime import datetime
from app.hours_conversion import convert_hours
import app.global_vars as global_vars


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

        elif action in ["add", "add-direct"]:
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
    from app.models import Request

    system_user = User.query.filter_by(crm=0).first()
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
            return -1
        else:
            day = day[0]
        
        if action == "delete":
            app = create_app()
            with app.app_context():
                appointments = Appointment.query.filter_by(
                    user_id=doctor.id,
                    center_id=center.id,
                    day_id = day.id,
                    is_confirmed=True
                ).all()

                appointments.delete_requests()

                hours = [appointment.hour for appointment in appointments]
                req = Request.exclusion(doctor=doctor,
                                        center=center,
                                        day=day,
                                        hours=hours,
                                        requester=system_user)

                if not isinstance(req, str):
                    req.close(system_user.id, "authorized")

                for appointment in appointments:
                    appointment.delete_entry(del_requests=False)
                   
            return 0

        elif action in ["add", "add-direct"]:
            hour_list = cell.get("hourValue") # Hour_list has the format ["-", "00:00", "00:00"]
            hours = convert_hours(hour_list)
            if isinstance(hours, str):
                return hours

            app = create_app()
            with app.app_context():
                req = Request.inclusion(doctor=doctor,
                                        center=center,
                                        day=day,
                                        hours=hours,
                                        requester=system_user)

                if not isinstance(req, str):
                    req.close(system_user.id, "authorized")

                flags = []
                for hour in hours:
                    flag = Appointment.add_entry(doctor.id, center.id, day.id, hour)
                    if isinstance(flag, str):
                        flags.append(flag)

            return 0 if not flags else '\n'.join(list(set(flags)))       
        else:
            print("Erro")
