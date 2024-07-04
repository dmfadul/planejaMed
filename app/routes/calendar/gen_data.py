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
        
        all_hours = ""
        for hour in hour_list:
            all_hours += convert_hours_to_line(hour)
        
        redudant_list = gen_redudant_hour_list(hour_range, include_line=True)
        doctor_name = User.query.filter_by(crm=doctor_crm).first().full_name

        appointments_dict[doctor_crm] = {'hours': (all_hours, redudant_list),
                                         'name': doctor_name}

    return appointments_dict


def gen_doctors_dict():
    doctors = User.query.all()

    doctors_dict = {}
    doctors_list = []
    for doctor in doctors:
        if doctor.crm not in doctors_dict:
            doctors_list.append((doctor.crm, doctor.full_name))
            doctors_dict[doctor.crm] = []
        
        month = Month.get_current()
        month_dates = [day.date for day in month.days]

        schedule = doctor.redundant_schedule
    
        for app in schedule:
            date = datetime.strptime(app.split(" -- ")[1], "%d/%m/%y").date()
            if date in month_dates:
                doctors_dict[doctor.crm ].append(app)
    
    return doctors_dict, doctors_list
