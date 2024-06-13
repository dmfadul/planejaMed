from flask import Blueprint, render_template

import app.global_vars as global_vars
from app.models import Center, Month

admin_bp = Blueprint(
                    'admin',
                    __name__,
                    template_folder='templates',
                    static_folder='static',
                    static_url_path='/static/admin'
                    )


@admin_bp.route('/admin/')
def admin():
    # test if user is admin
    months = global_vars.MESES
    current_year = Month.get_current().year
    current_month = Month.get_current().name
    next_month = Month.get_current().next_month_name
    centers = [center.abbreviation for center in Center.query.all()]
    return render_template(
                           "admin.html",
                           title="Admin",
                           user_is_sudo=True, # current_user.is_sudo,
                           user_is_root=True, # current_user.is_root,
                           centers=centers,
                           months=months,
                           current_month=current_month,
                           current_year=current_year,
                           next_month=next_month,
                           )
