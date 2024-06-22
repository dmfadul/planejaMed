from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from .gen_data import gen_day_hours, gen_days_dict, gen_doctors_dict
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
    days_dict = gen_days_dict(center)
    doctors_dict = gen_doctors_dict(center)

    kwargs = {
    'month_name': month.name,
    'month_year': month.year,
    'center': center,
    'calendar_days': month.calendar,
    'days_dict': days_dict,
    'doctors_dict': doctors_dict,
    'curr_user_schedule': current_user_schedule
    }
    return render_template("calendar.html", **kwargs)


@calendar_bp.route("/schedule/", methods=["GET"])
@login_required
def schedule():
    return render_template("schedule.html", schedule=current_user.schedule)


@calendar_bp.route("/update_hours/", methods=["POST"])
def update_hours():
    data = request.json
    print(data)
    return jsonify({"status": "success"})