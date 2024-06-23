from app.models import Appointment, Request, User


def resolve_data(action, info_dict):
    if action == "cal_exclude":
        return cal_exclude(info_dict)
    

def cal_exclude(info_dict):
    day = info_dict.get('day')
    crm = info_dict.get('crmToExclude')
    hours_to_exclude_line = info_dict.get('hoursToExclude')

    
        