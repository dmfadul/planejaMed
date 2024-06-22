from datetime import datetime
from calendar import monthcalendar
from app.models import Center, Day, Month, Appointment, User
from app.hours_conversion import split_hours, convert_hours_to_line, gen_redudant_hour_list


def gen_days_dict(center_abbr):
    month = Month.get_current()

    days_dict = {}
    for day in month.days:
        if day.date.day not in days_dict:
            days_dict[day.date.day] = gen_day_hours(center_abbr, day.date.day)

    return days_dict


def gen_day_hours(center_abbr, day_num):
    center = Center.query.filter_by(abbreviation=center_abbr).first()
    month = Month.get_current()

    day = month.get_day(day_num)
    appointments = Appointment.query.filter_by(center_id=center.id, day_id=day.id).all()

    appointments_dict = {}
    for app in appointments:
        doctor_name = app.user.full_name
        doctor_crm = app.user.crm
        if (doctor_name, doctor_crm) not in appointments_dict:
            appointments_dict[(doctor_name, doctor_crm)] = []
        appointments_dict[(doctor_name, doctor_crm)].append(app.hour)
    
    appointments_list = ['-']
    for doctor_name_crm, hour_range in appointments_dict.items():
        hour_list = split_hours(hour_range)
        
        all_hours = ""
        for hour in hour_list:
            all_hours += convert_hours_to_line(hour)
        
        appointments_list.append((f"{doctor_name_crm[0]}*{all_hours}", doctor_name_crm[1]))

    return appointments_list


def gen_doctors_dict(center_abbr):
    center = Center.query.filter_by(abbreviation=center_abbr).first()
    month = Month.get_current()
    month_dates = [day.date for day in month.days]
    doctors = User.query.all()

    doctors_dict = {}
    for doctor in doctors:
        if doctor.crm not in doctors_dict:
            doctors_dict[doctor.crm] = {}

        center_schedule = doctor.app_dict.get(center.abbreviation, [])
        for date in center_schedule:
            if date not in month_dates:
                continue
            if date.day not in doctors_dict[doctor.crm]:
                doctors_dict[doctor.crm][date.day] = gen_redudant_hour_list(center_schedule[date],
                                                                            include_line=True)

    return doctors_dict
