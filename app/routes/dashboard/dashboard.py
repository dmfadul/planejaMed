from flask import Blueprint, render_template, redirect, request, jsonify, flash, url_for
from flask_login import login_required, current_user
import app.global_vars as global_vars
from app.models import Center, Month, Request, Message, Vacation, User
from datetime import datetime

dashboard_bp = Blueprint(
                        'dashboard',
                        __name__,
                        template_folder='templates',
                        static_folder='static',
                        static_url_path='/static/dashboard'
                        )


@dashboard_bp.route('/dashboard/')
@login_required
def dashboard():
    months = global_vars.MESES
    month = Month.get_current()
    if month is None:
        current_year = 2024
        current_month = "Janeiro"
    else:
        current_year = month.year
        current_month = month.name
    
    pending_requests = Request.filter_by_user(current_user.id) + Message.filter_by_user(current_user.id)
    centers = [center.abbreviation for center in Center.query.filter_by(is_active=True).all()]

    return render_template(
                            "dashboard.html",
                            title="Dashboard",
                            user_is_admin=current_user.is_admin,
                            centers=centers,
                            months=months,
                            current_month=current_month,
                            current_year=current_year,
                            pending_requests=pending_requests
                            )


@dashboard_bp.route('/resolve-vacations', methods=['POST'])
@login_required
def resolve_vacations():
    start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d")
    end_date = datetime.strptime(request.form['end_date'], "%Y-%m-%d")

    if start_date >= end_date:
        flash("Data de início não pode ser posterior a data final", "danger")
        return redirect(url_for('dashboard.dashboard'))

    Vacation.has_base_rights(current_user.id)


    flash("Férias Solicitadas", "success")

    return redirect(url_for('dashboard.dashboard'))


@dashboard_bp.route('/requests')
@login_required
def requests():
    reqs = Request.filter_by_user(current_user.id) + Message.filter_by_user(current_user.id)
    
    return render_template("requests.html", title="Requests", requests=reqs)


@dashboard_bp.route('/resolve-request', methods=['POST'])
@login_required
def resolve_request():
    response = request.json['response']
    req_id = request.json['request']

    if response in ['yes', 'no']:
        req = Request.query.get(req_id)
        authorized = response == 'yes'
        flag, status = req.resolve(current_user.id, authorized)
    elif response == 'dismiss':
        message = Message.query.get(req_id)
        flag = message.dismiss()
        status = 'success'
    elif response == 'cancel':
        message = Message.query.get(req_id)
        flag = message.cancel()
        status = 'success'
    else:
        flag, status = "error", 'danger'

    flash(flag, status)

    return jsonify({"status": "success", 'message': 'Requests updated'})
    