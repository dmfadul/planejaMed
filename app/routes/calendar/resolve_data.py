from app.models import Appointment, Request, User, Center, Day, Month
from app.hours_conversion import gen_hour_range, convert_hours
from flask_login import current_user
from datetime import datetime


def resolve_data(action, info_dict):
    if action == "cal_include":
        return cal_include(info_dict)
    elif action == "cal_exchange":
        return cal_exchange(info_dict)
    elif action == "cal_exclude":
        return cal_exclude(info_dict)
    elif action == "cal_donate":
        return cal_donate(info_dict)



def cal_include(info_dict):
    day = info_dict.get('day')
    center = info_dict.get('center')
    crm = info_dict.get('crmToInclude')

    hours = convert_hours(info_dict.get('hoursToInclude'))

    print(day, center, crm)


def cal_exclude(info_dict):
    day = info_dict.get('day')
    crm = info_dict.get('crmToExclude')
    hours_to_exclude_line = info_dict.get('hoursToExclude')


def cal_exchange(info_dict):
    other_user_day = info_dict.get('day')
    other_user_center = info_dict.get('other_user_center')
    other_user_crm = info_dict.get('other_user_crm')
    other_user_hours = info_dict.get('other_user_hours').split(': ')[1].strip()
    str_hour, end_hour = other_user_hours.split('-')

    str_hour = int(str_hour.split(':')[0])
    end_hour = int(end_hour.split(':')[0])
    hours = gen_hour_range((str_hour, end_hour))

    current_month = Month.get_current()
    date = datetime(current_month.year, current_month.number, int(other_user_day))
    center = Center.query.filter_by(abbreviation=other_user_center).first()
    day = Day.query.filter_by(date=date).first()

    curent_user_crm = info_dict.get('current_user_crm')
    current_user_center = info_dict.get('current_user_center_date_hours').split('--')[0].strip()
    current_user_date = info_dict.get('current_user_center_date_hours').split('--')[1].strip()
    current_user_hours = info_dict.get('current_user_center_date_hours').split('--')[2].strip()
    
    current_user_day = int(current_user_date.split('/')[0])

    pending_appointments = []
    for hour in hours:
        pending_appointments.append(Appointment(user_id=current_user.id,
                                                center_id=center.id,
                                                day_id=day.id,
                                                hour=hour))
        
    # if pending_appointments:
    #     Appointment.add_entries(pending_appointments)
    

def cal_donate(info_dict):
    pass
