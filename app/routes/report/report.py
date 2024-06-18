from flask import Blueprint
from flask_login import login_required

report_bp = Blueprint(
                      'report',
                      __name__,
                      template_folder='templates',
                      static_folder='static',
                      static_url_path='/static/report'
                      )


@report_bp.route('/report/')
@login_required
def gen_report():
    return "Report"


@report_bp.route('/print-table/')
@login_required
def print_table():
    return "Table"
