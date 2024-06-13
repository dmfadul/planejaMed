from flask import Blueprint, render_template, jsonify
from .gen_data import gen_day_hours
from app.models import Month



calendar_bp = Blueprint(
                        'calendar',
                        __name__,
                        template_folder='templates',
                        static_folder='static',
                        static_url_path='/static/calendar'
                        )


@calendar_bp.route('/calendar/<center>', methods=['GET'])
def calendar(center):
    month = Month.get_current()
    current_user_schedule = []

    kwargs = {
    'month_name': month.name,
    'month_year': month.year,
    'center': center,
    'calendar_days': month.calendar,
    'curr_user_schedule': current_user_schedule
    }
    return render_template("calendar.html", **kwargs)


@calendar_bp.route("/calendar/<center>/<day>", methods=["GET"])
def calendar_day(center, day):
    day_data = gen_day_hours(center, day)

    return jsonify({"data": day_data})
