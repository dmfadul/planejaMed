from datetime import datetime
from calendar import monthcalendar
from app.models import Center, Day, Month, Appointment
from app.hours_conversion import split_hours, convert_hours_to_line


def gen_day_hours(center_abbr, day_num):
    center = Center.query.filter_by(abbreviation=center_abbr).first()
    month = Month.get_current()

    day = [day for day in month.days if day.date.day == int(day_num)][0]   
    appointments = Appointment.query.filter_by(center_id=center.id, day_id=day.id).all()

    appointments_dict = {}
    for app in appointments:
        doctor_name = app.user.full_name
        if doctor_name not in appointments_dict:
            appointments_dict[doctor_name] = []
        appointments_dict[doctor_name].append(app.hour)
    
    appointments_list = ['-']
    for doctor_name, hour_range in appointments_dict.items():
        hour_list = split_hours(hour_range)
        all_hours = ""
        for hour in hour_list:
            all_hours += "*" + convert_hours_to_line(hour)
        
        appointments_list.append(f"{doctor_name}*{all_hours}")

    return appointments_list


def gen_days_dict(center_abbr):
    month = Month.get_current()

    days_dict = {}
    for day in month.days:
        if day.date.day not in days_dict:
            days_dict[day.date.day] = gen_day_hours(center_abbr, day.date.day)

    return days_dict
