from flask import Blueprint, render_template, request, jsonify
from app.models import BaseAppointment, Center
from .gen_data import gen_base

dataview_bp = Blueprint(
                        "dataview",
                        __name__,
                        template_folder="templates",
                        static_folder="static",
                        static_url_path="/static/dataview"
                        )


@dataview_bp.route("/baseview/", methods=["GET", "POST"])
def baseview():
    center = request.form.get("center")
    center_id = Center.query.filter_by(abbreviation=center).first().id


    data = gen_base(center_id)

    return render_template("baseview.html",
                           data=data,
                           center=center,
                           is_admin=True)

@dataview_bp.route("/monthview/")
def monthview():
    return render_template("monthview.html",
                           data=[],
                           hdays=[],
                           center="CCG",
                           month="JUL",
                           year=2024,
                           is_admin=True)


@dataview_bp.route("/overview/")
def overview():
    return "Overview"


@dataview_bp.route("/update-appointments", methods=["POST"])
def update_appointments():
    data = request.get_json()
    print("data: ", data)
    return jsonify({"status": "success", 'message': 'Database updated successfully'})
