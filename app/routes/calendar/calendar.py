from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
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
@login_required
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
@login_required
def calendar_day(center, day):
    day_data = gen_day_hours(center, day)
    
    day_dict = {
        "day": day,
        "data": day_data
    }

    return jsonify({"data": day_data, "day_dict": day_dict})


@calendar_bp.route("/schedule/", methods=["GET"])
@login_required
def schedule():
    return render_template("schedule.html", schedule=current_user.schedule)