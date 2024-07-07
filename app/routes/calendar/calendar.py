from flask import Blueprint, render_template, jsonify, request, flash
from flask_login import login_required, current_user
from .gen_data import gen_days_dict, gen_doctors_dict
from .resolve_data import resolve_data
from app.models import Month, Center


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

    days_dict = gen_days_dict(center)
    doctors_dict, doctors_list = gen_doctors_dict()

    kwargs = {
    'month_name': month.name,
    'month_year': month.year,
    'open_center': center,
    'calendar_days': month.calendar,
    'curr_user_data': (current_user.crm, current_user.full_name),
    'days_dict': days_dict,
    'doctors_dict': doctors_dict,
    'doctors_list': doctors_list
    }
    return render_template("calendar.html", **kwargs)


@calendar_bp.route("/schedule/", methods=["GET"])
@login_required
def schedule():
    return render_template("schedule.html", schedule=current_user.schedule)


@calendar_bp.route("/update_hours/", methods=["POST"])
def update_hours():
    data = request.json
    action = data.get('action')
    info_dict = data.get('infoDict')

    flag = resolve_data(action, info_dict)
    if flag == 0:
        flash("Pedido feito com sucesso", "success")
        return jsonify({"status": "success", 'message': "Horários excluídos com sucesso"})
    
    flash(flag, "danger")
    return jsonify({"status": "error", 'message': 'Appointments not updated'})
