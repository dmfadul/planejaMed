from flask import Blueprint, request, render_template, jsonify, flash
from flask_login import login_required, current_user
from app.models import BaseAppointment, Center, Month
from .resolve_data import resolve_data
from .gen_data import gen_base_table, gen_month_table
import app.global_vars as global_vars

dataview_bp = Blueprint(
                        "dataview",
                        __name__,
                        template_folder="templates",
                        static_folder="static",
                        static_url_path="/static/dataview"
                        )


@dataview_bp.route("/baseview/", methods=["GET", "POST"])
@login_required
def baseview():
    center_abbr = request.form.get("center")
    data = gen_base_table(center_abbr)

    return render_template("baseview.html",
                           data=data,
                           center=center_abbr,
                           is_admin=True)


@dataview_bp.route("/monthview/", methods=["GET", "POST"])
@login_required
def monthview():
    center_abbr = request.form.get("center")
    year = request.form.get("year")
    month_name = request.form.get("month")

    month = Month.query.filter_by(number=global_vars.MESES.index(month_name)+1, year=year).first()
    print(month.holidays)

    data = gen_month_table(center_abbr, month_name, year)

    return render_template("monthview.html",
                           data=data,
                           hdays=month.holidays,
                           center=center_abbr,
                           month=month_name,
                           year=year,
                           is_admin=True)



@dataview_bp.route("/update-appointments", methods=["POST"])
@login_required
def update_appointments():
    if not current_user.is_admin:
        return jsonify({"status": "error", 'message': 'You are not an admin'})
    
    flag = resolve_data(request.get_json())
    if flag == 1:
        return jsonify({"status": "error", 'message': 'An unexpected error occurred'})
    if flag == -1:
        flash("Horários conflitantes", "danger")
        return jsonify({"status": "error", 'message': 'Conflicting hours'})
    
    return jsonify({"status": "success", 'message': 'Database updated successfully'})
