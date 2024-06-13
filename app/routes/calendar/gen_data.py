from datetime import datetime
from calendar import monthcalendar
from app.models import Center, Day, Month, Appointment
from app.hours_conversion import split_hours, convert_hours_to_line


def gen_day_hours(center_abbr, day_num):
    center = Center.query.filter_by(abbreviation=center_abbr).first()
    month = Month.get_current()
    date = datetime(day=int(day_num), month=month.number, year=month.year)
    day = Day.query.filter_by(month_id=month.id, date=date).first()
    
    appointments = Appointment.query.filter_by(center_id=center.id, day_id=day.id).all()

    appointments_dict = {}
    for app in appointments:
        doctor_name = app.user.full_name
        if doctor_name not in appointments_dict:
            appointments_dict[doctor_name] = []
        appointments_dict[doctor_name].append(app.hour)
    
    appointments_list = []
    for doctor_name, hour_range in appointments_dict.items():
        hour_list = split_hours(hour_range)
        all_hours = ""
        for hour in hour_list:
            all_hours += "*" + convert_hours_to_line(hour)
        
        appointments_list.append(f"{doctor_name}*{all_hours}")

    return appointments_list
