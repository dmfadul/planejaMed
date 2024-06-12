from calendar import monthcalendar


def get_calendar_days(month_num, year):
    return [[day if day != 0 else "" for day in week] for week in monthcalendar(year, month_num)]