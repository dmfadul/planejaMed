from flask import Blueprint, request, render_template, jsonify, flash
from app.models import BaseAppointment, Center
from .resolve_data import resolve_data
from .gen_data import gen_base
import instance.global_vars as global_vars

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
    center_id = Center.query.filter_by(abbreviation=center_abbr).first().id

    data = gen_base(center_id)

    return render_template("baseview.html",
                           data=data,
                           center=center_abbr,
                           is_admin=True)


@dataview_bp.route("/monthview/", methods=["GET", "POST"])
def monthview():
    center_abbr = request.form.get("center")
    center_id = Center.query.filter_by(abbreviation=center_abbr).first().id
    data = gen_base(center_id)

    month = [m for m in global_vars.MESES if request.form.get("month") in m][0]
    year = request.form.get("year")

    return render_template("monthview.html",
                           data=data,
                           hdays=[1],
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
