import math
from instance import global_vars
from app.models import BaseAppointment, User


def gen_base(center_id):
    weekdays = [day[:3] for day in global_vars.DIAS_SEMANA] * 5
    weekindexes = [math.ceil(int(x)/7) for x in range(1, 36)]
    table_header = [['']+weekdays, ['']+weekindexes]

    table = table_header
    users = sorted(User.query.filter_by(is_active=True).all(), key=lambda x: x.full_name)
    for user in users:
        data = user.base_row(center_id)
        row = [(user.abbreviated_name, user.crm)] + ['']*(len(weekdays))
        table.append(row)

    return table