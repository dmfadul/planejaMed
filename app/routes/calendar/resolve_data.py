from app.models import Appointment, Request, User, Center, Day, Month
from app.hours_conversion import convert_hours, convert_line_to_hour
from flask_login import current_user

from datetime import datetime
import app.global_vars as global_vars


def resolve_data(action, info_dict):
    month = Month.get_current()
    
    day_number = int(info_dict.get('day'))
    day = month.get_day(day_number)
    if not day:
        return "Dia não encontrado"

    center_abbr = info_dict.get('center')
    center = Center.query.filter_by(abbreviation=center_abbr).first()
    if not center:
        return "Centro não encontrado"

    crm = info_dict.get('crm')
    doctor = User.query.filter_by(crm=crm).first()
    if not doctor:
        return "Médico não encontrado"
    
    selected_hours = info_dict.get('hours')
    if isinstance(selected_hours, str):
        hours = convert_line_to_hour()
    elif isinstance(selected_hours, list):
        hours = convert_hours(selected_hours)

    if action == "include":
        return include(doctor, center, day, hours)
    
    elif action == "exclude":
        return exclude(doctor, center, day, hours)
    
    elif action == "cal_donate":
        receiver_crm = info_dict.get('receiverCRM')
        receiver = User.query.filter_by(crm=receiver_crm).first() or current_user

        return cal_donate(doctor, center, day, hours, receiver)
    
    elif action == "cal_exchange":
        day2_number = int(info_dict.get('day2'))
        day_2 = month.get_day(day2_number)
        if not day:
            return "Dia não encontrado"
        center2_abbr = info_dict.get('center2')
        center_2 = Center.query.filter_by(abbreviation=center2_abbr).first()
        if not center:
            return "Centro não encontrado"
        crm2 = info_dict.get('crm2')
        doctor_2 = User.query.filter_by(crm=crm2).first()
        if not doctor:
            return "Médico não encontrado"
    
        hours_2 = convert_hours(info_dict.get('hours2'))
    
        return cal_exchange(doctor, center, day, hours,
                            doctor_2, center_2, day_2, hours_2)


def include(doctor, center, day, hours):
    flag = Request.inclusion(doctor, center, day, hours)
    if isinstance(flag, str):
        return flag   
    return 0


def exclude(doctor, center, day, hours):
    flag = Request.exclusion(doctor.id, center.id, day.id, hours)
    if isinstance(flag, str):
        return flag 
    return 0


def cal_exchange(doctor_1, center_1, day_1, hours_1, doctor_2, center_2, day_2, hours_2):
    flag = cal_donate(doctor_1, center_1, day_1, hours_1, doctor_2)
    if flag:
        return flag
    
    flag = cal_donate(doctor_2, center_2, day_2, hours_2, doctor_1)
    if flag:
        return flag
    
    return 0
 

def cal_donate(donor, center, day, hours, receiver):
    apps = []
    for hour in hours:
        app = Appointment.query.filter_by(day_id=day.id,
                                          user_id=donor.id,
                                          center_id=center.id,
                                          hour=hour).first()
        if app:
            apps.append(app)
        else:
            return f"Horário {hour} não encontrado"
    
    for app in apps:
        app.change_doctor(receiver.id)
        
    return 0
