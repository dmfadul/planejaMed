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
    if flag == 0:
        return jsonify({"status": "success", 'message': 'Appointments updated'})

    if flag == 1:
        flash("Horários Inválidos - A hora de Início e de Fim são iguais", "danger")
        return jsonify({"status": "error", 'message': 'Invalid hours - Start and End time are the same'})
    if flag == 2:
        return jsonify({"status": "error", 'message': 'Invalid hours - End time goes to the next day'})
    if flag == -1:
        flash("O Médico Selecionado Tem Horários conflitantes em Outro Centro", "danger")
        return jsonify({"status": "error", 'message': 'Conflicting hours'})
    
    return jsonify({"status": "error", 'message': 'An unexpected error occurred'})    


@dataview_bp.route("/sum-doctors", methods=["POST"])
@login_required
def sum_by_doctor():
    if not current_user.is_admin:
        return jsonify({"status": "error", 'message': 'You are not an admin'})
    
    month_name = request.form.get("month")
    year = request.form.get("year")
    month = Month.query.filter_by(number=global_vars.MESES.index(month_name)+1, year=year).first()

    # return jsonify({"status": "success", 'doctors': doctors})
    return render_template("sumview.html", data=[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]])