from flask import Blueprint, redirect, url_for, render_template
import instance.global_vars as global_vars
from app.models import Center

dashboard_bp = Blueprint(
                        'dashboard',
                        __name__,
                        template_folder='templates',
                        static_folder='static',
                        static_url_path='/static/dashboard'
                        )



@dashboard_bp.route('/')
def index():
    return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/dashboard/')
def dashboard():
    months = [m[:3] for m in global_vars.MESES]
    current_month_number, current_year = 7, 2024
    current_month = "JUL"
    next_month = "AGOSTO"
    pending_requests = None
    centers = [center.abbreviation for center in Center.query.all()]

    return render_template(
                            "dashboard.html",
                            title="Dashboard",
                            user=15893, # current_user.crm,
                            user_is_admin=True, # current_user.is_admin,
                            centers=centers,
                            months=months,
                            current_month=current_month,
                            current_year=current_year,
                            next_month=next_month,
                            pending_requests=pending_requests
                            )


@dashboard_bp.route('/create-month/')
def create_month():
    return "Create Month"