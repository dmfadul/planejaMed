from flask import Blueprint, request, render_template, jsonify, flash
from app.models import BaseAppointment, Center, Month
from .resolve_data import resolve_data
from .gen_data import gen_base, gen_month
import app.global_vars as global_vars

dataview_bp = Blueprint(
                        "dataview",
                        __name__,
                        template_folder="templates",
                        static_folder="static",
                        static_url_path="/static/dataview"
                        )


@dataview_bp.route("/baseview/", methods=["GET", "POST"])
def baseview():
    center_abbr = request.form.get("center")
    data = gen_base(center_abbr)

    return render_template("baseview.html",
                           data=data,
                           center=center_abbr,
                           is_admin=True)


@dataview_bp.route("/monthview/", methods=["GET", "POST"])
def monthview():
    center_abbr = request.form.get("center")
    month = request.form.get("month")
    year = request.form.get("year")

    data = gen_month(center_abbr, month, year)

    return render_template("monthview.html",
                           data=data,
                           hdays=[],
                           center=center_abbr,
                           month=month,
                           year=year,
                           is_admin=True)


@dataview_bp.route("/overview/")
def overview():
    return "Overview"


@dataview_bp.route("/update-appointments", methods=["POST"])
def update_appointments():
    flag = resolve_data(request.get_json())
    if flag == 1:
        return jsonify({"status": "error", 'message': 'An unexpected error occurred'})
    if flag == -1:
        flash("Horários conflitantes", "danger")
        return jsonify({"status": "error", 'message': 'Conflicting hours'})
    
    return jsonify({"status": "success", 'message': 'Database updated successfully'})
