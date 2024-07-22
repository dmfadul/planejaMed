from datetime import datetime
from calendar import monthcalendar
from app.models import Center, Day, Month, Appointment, User
from app.hours_conversion import split_hours, convert_hours_to_line, gen_redudant_hour_list


def gen_days_dict(center_abbr):
    month = Month.get_current()

    if month is None:
        return {}

    days_dict = {}
    for day in month.days:
        if day.date.day not in days_dict:
            days_dict[day.date.day] = gen_day_hours(center_abbr, day.date.day)

    return days_dict


def gen_day_hours(center_abbr, day_num):
    center = Center.query.filter_by(abbreviation=center_abbr).first()
    month = Month.get_current()

    day = month.get_day(day_num)
    appointments = Appointment.query.filter_by(center_id=center.id,
                                               day_id=day.id,
                                               is_confirmed=True).all()

    appointments_dict = {}
    for app in appointments:
        doctor_name, doctor_crm = app.user.full_name, app.user.crm

        if doctor_crm not in appointments_dict:
            appointments_dict[doctor_crm] = []
        appointments_dict[doctor_crm].append(app.hour)
    
    for doctor_crm, hour_range in appointments_dict.items():
        hour_list = split_hours(hour_range)
        
        all_hours = []
        for hour in hour_list:
            all_hours.append(convert_hours_to_line(hour))
        
        all_hours = '*'.join(all_hours)
        
        redudant_list = gen_redudant_hour_list(hour_range, include_line=True)
        doctor_name = User.query.filter_by(crm=doctor_crm).first().full_name

        appointments_dict[doctor_crm] = {'hours': (all_hours, redudant_list),
                                         'name': doctor_name}

    return appointments_dict


def gen_doctors_dict():
    doctors = User.query.filter_by(is_active=True).all()

    doctors_dict = {}
    doctors_list = []
    for doctor in doctors:
        if doctor.crm not in doctors_dict:
            doctors_list.append((doctor.crm, doctor.full_name))
            doctors_dict[doctor.crm] = {}

        schedule = doctor.app_dict
        for center, date_hours in schedule.items():
            if center not in doctors_dict:
                doctors_dict[doctor.crm][center] = {}
            
            for date, hours in date_hours.items():
                if date.day not in doctors_dict[doctor.crm][center]:
                    doctors_dict[doctor.crm][center][date.day] = []

                redudant_hours = gen_redudant_hour_list(hours, include_line=True)
                doctors_dict[doctor.crm][center][date.day].append(redudant_hours)

    doctors_list = sorted(doctors_list, key=lambda x: x[1])       

    return doctors_dict, doctors_list
