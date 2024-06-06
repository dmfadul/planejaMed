from flask import Blueprint, render_template
from app.models import BaseAppointment, Center

dataview_bp = Blueprint(
                        "dataview",
                        __name__,
                        template_folder="templates",
                        static_folder="static",
                        static_url_path="/static/dataview"
                        )


@dataview_bp.route("/baseview")
def baseview():
    center = "CCG"
    center_id = Center.query.filter_by(abbreviation=center).first().id
    data = BaseAppointment.gen_grid(center_id)

    return render_template("monthview.html",
                           data=data,
                           hdays=[],
                           center="CCQ",
                           month="January",
                           year="2020",
                           is_admin=True)