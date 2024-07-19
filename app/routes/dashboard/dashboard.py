from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required, current_user
import app.global_vars as global_vars
from app.models import Center, Month, Request, Message

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
    current_year = Month.get_current().year
    current_month = Month.get_current().name
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
        flag = req.resolve(current_user.id, authorized)
    elif response == 'dismiss':
        message = Message.query.get(req_id)
        flag = message.dismiss()
    elif response == 'cancel':
        message = Message.query.get(req_id)
        flag = message.cancel()
    else:
        flag = "error"

    flash(flag, 'success')

    return jsonify({"status": "success", 'message': 'Requests updated'})
    