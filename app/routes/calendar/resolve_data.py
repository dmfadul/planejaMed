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
        hours = convert_line_to_hour(selected_hours)
    elif isinstance(selected_hours, list):
        hours = convert_hours(selected_hours)

    # Check request's action
    if action == "include":
        flag = Request.inclusion(doctor, center, day, hours)
        if isinstance(flag, str):
            return flag   
        return 0

    elif action == "exclude":
        flag = Request.exclusion(doctor.id, center.id, day.id, hours)
        if isinstance(flag, str):
            return flag 
        return 0
    
    elif action == "donate":
        receiver_crm = info_dict.get('receiverCRM')
        receiver = User.query.filter_by(crm=receiver_crm).first() or current_user

        flag = Request.donation(doctor.id, center.id, day.id, hours, receiver.id)
        if isinstance(flag, str):
            return flag 
        return 0
    
    elif "exchange" in action:
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

        if action == "exchange_from_other_user":
            doctor, doctor_2 = doctor_2, doctor
            center, center_2 = center_2, center
            day, day_2 = day_2, day
            hours, hours_2 = hours_2, hours
    
        flag = Request.exchange(doctor, center.id, day.id, hours,
                                doctor_2, center_2.id, day_2.id, hours_2)
        
        if isinstance(flag, str):
            return flag
                
        return 0
