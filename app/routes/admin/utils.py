import app.global_vars as global_vars


def get_months(start_date, end_date):
    months = []

    curr_year, curr_month = start_date.year, start_date.month

    while (curr_year, curr_month) <= (end_date.year, end_date.month):
        months.append((curr_year, curr_month))

        curr_month += 1
        if curr_month > 12:
            curr_month = 1
            curr_year += 1

    if global_vars.STR_DAY <= start_date.day <= 31:
        months.pop(0)

    if global_vars.STR_DAY <= end_date.day <= 31:
        extra_month = end_date.month + 1
        if extra_month == 13:
            extra_month = 1
            extra_year = end_date.year + 1
        else:
            extra_year = end_date.year
        months.append((extra_year, extra_month))

    return months
