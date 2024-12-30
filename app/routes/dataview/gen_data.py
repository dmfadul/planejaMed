import math
import app.global_vars as global_vars
from app.models import Center, User, Month


def gen_base_table(center_abbr, names_only=False, include_crm=False, abbr_names=False):
    center_id = Center.query.filter_by(abbreviation=center_abbr).first().id

    weekdays = [day[:3] for day in global_vars.DIAS_SEMANA] * 5
    weekindexes = [math.ceil(int(x)/7) for x in range(1, 36)]
    table_header = [['']+weekdays, ['']+weekindexes]

    table = table_header
    users = sorted(User.query.filter_by(is_visible=True).all(), key=lambda x: x.full_name)
    for user in users:
        name = user.abbreviated_name if abbr_names else user.full_name
        if names_only:
            row = [name] + user.base_row(center_id)
        elif include_crm:
            row = [name, user.crm] + user.base_row(center_id)
        else:
            row = [(name, user.crm)] + user.base_row(center_id)
        table.append(row)

    return table


def gen_month_table(center_abbr, month, year, names_only=False, include_crm=False, abbr_names=False):
    month_num = global_vars.MESES.index(month)+1
    
    center = Center.query.filter_by(abbreviation=center_abbr).first()
    month = Month.query.filter_by(number=month_num, year=year).first()

    weekdays = [global_vars.DIAS_SEMANA[day.date.weekday()][:3] for day in month.days]
    monthdays = [day.date.day for day in month.days]
    table_header = [['']+weekdays, ['']+monthdays]

    table = table_header
    users = sorted(month.users, key=lambda x: x.full_name)

    for user in users:
        name = user.abbreviated_name if abbr_names else user.full_name
        if names_only:
            row = [name]
        elif include_crm:
            row = [f"{name} - {user.crm}"]
        else:
            row = [(name, user.crm)]
        
        for day in month.days:
            appointments = user.filtered_appointments(center.id, day.id, unified=True)
            row.append(appointments)
        table.append(row)

    return table
