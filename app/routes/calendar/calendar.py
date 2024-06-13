from flask import Blueprint, render_template, jsonify
from .gen_data import get_calendar_days, gen_day_hours



calendar_bp = Blueprint(
                        'calendar',
                        __name__,
                        template_folder='templates',
                        static_folder='static',
                        static_url_path='/static/calendar'
                        )


@calendar_bp.route('/calendar/<center>', methods=['GET'])
def calendar(center):
    month_name = "Dezembro"
    month_num, year = 12, 2023
    calendar_days = get_calendar_days(month_num, year)
    current_user_schedule = []

    kwargs = {
    'month_name': month_name,
    'month_year': year,
    'center': center,
    'calendar_days': calendar_days,
    'curr_user_schedule': current_user_schedule
    }
    return render_template("calendar.html", **kwargs)


@calendar_bp.route("/calendar/<center>/<day>", methods=["GET"])
def calendar_day(center, day):
    day_data = gen_day_hours(center, day)

    return jsonify({"data": day_data})
