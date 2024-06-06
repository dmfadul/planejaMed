from flask import Blueprint, render_template

dataview_bp = Blueprint(
                        "dataview",
                        __name__,
                        template_folder="templates",
                        static_folder="static",
                        static_url_path="/static/dataview"
                        )


@dataview_bp.route("/dataview")
def monthview():

    return render_template("monthview.html",
                           data=[],
                           hdays=[],
                           center="CCQ",
                           month="January",
                           year="2020",
                           is_admin=True)