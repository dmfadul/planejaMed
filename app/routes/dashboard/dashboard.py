from flask import Blueprint, render_template, redirect, request, jsonify, flash, url_for
from flask_login import login_required, current_user
import app.global_vars as global_vars
from app.models import Center, Month, Request, Message, Vacation, User
from datetime import datetime, timedelta

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
                            user_is_root=current_user.is_root,
                            centers=centers,
                            months=months,
                            current_month=current_month,
                            current_year=current_year,
                            pending_requests=pending_requests
                            )


@dashboard_bp.route('/resolve-privilege', methods=['POST'])
@login_required
def resolve_privilege():
    from app.global_vars import MAX_VACATION_SPLIT, TOTAL_VACATION_DAYS
    Vacation.update_status()
   
    start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d")
    end_date = datetime.strptime(request.form['end_date'], "%Y-%m-%d")
    is_sick_leave = bool(int(request.form['privilege_type']))

    if not current_user.is_visible or not current_user.is_active:
        flash("Usuário não está ativo", "danger")
        return redirect(url_for('dashboard.dashboard'))

    if start_date < datetime.now():
        flash("Não é possível pedir férias em datas passadas", "danger")
        return redirect(url_for('dashboard.dashboard'))
    
    if end_date - start_date > timedelta(days=TOTAL_VACATION_DAYS):
        flash(f"Férias não podem exceder {TOTAL_VACATION_DAYS} dias", "danger")
        return redirect(url_for('dashboard.dashboard'))

    # check if user has privileges rights
    if not current_user.pre_approved_vacation:
        flag = Vacation.check_vacation_entitlement(current_user.id, start_date)
        if isinstance(flag, str):
            flash(flag, "danger")
            return redirect(url_for('dashboard.dashboard'))

    if not is_sick_leave:
        flag = Vacation.check_vacations_availability(start_date, end_date, current_user.id)
        if isinstance(flag, str):
            flash(flag, "danger")
            return redirect(url_for('dashboard.dashboard'))
    
    # no need to exclude deleted, as query only looks for pending approvals
    unnaproved_vacations = Vacation.query.filter(
                           Vacation.user_id == current_user.id,
                           Vacation.status == "pending_approval"
                           ).all()
    
    unnaproved_vac_len = len(unnaproved_vacations) if isinstance(unnaproved_vacations, list) else 0 
    if unnaproved_vac_len >= MAX_VACATION_SPLIT:
        msg = f"""Usuário tem o número máximo de férias não aprovadas.
                    Aguarde aprovação ou contacte o Administrador"""
        flash(msg, "danger")
        return redirect(url_for('dashboard.dashboard'))

    # no need to exclude deleted, as query only looks for approved vacations      
    pending_vacations = Vacation.query.filter(
                        Vacation.user_id == current_user.id,
                        Vacation.status == "approved"
                        ).all()

    pending_vac_len = len(pending_vacations) if isinstance(pending_vacations, list) else 0
    if pending_vac_len >= MAX_VACATION_SPLIT:
        msg = f"""Usuário já tem o número máximo de férias programadas.
                    Aguarde a conclusão ou contacte o Administrador"""
        flash(msg, "danger")
        return redirect(url_for('dashboard.dashboard'))
    
    if pending_vac_len + unnaproved_vac_len >= MAX_VACATION_SPLIT:
        msg = f"""Usuário já tem o número máximo de férias programadas ou não aprovadas.
                    Aguarde a conclusão/aprovação ou contacte o Administrador"""
        flash(msg, "danger")
        return redirect(url_for('dashboard.dashboard'))
    
    new_vacation = Vacation.add_entry(start_date=start_date,
                                      end_date=end_date,
                                      user_id=current_user.id,
                                      is_sick_leave=is_sick_leave)

    if isinstance(new_vacation, str):
        flash(new_vacation, "danger")
        return redirect(url_for('dashboard.dashboard'))

    new_request = Request.vacation(current_user,
                                   new_vacation.start_date,
                                   new_vacation.end_date,
                                   is_sick_leave)

    if isinstance(new_request, str):
        new_vacation.remove_entry()
        flash(new_request, "danger")
        return redirect(url_for('dashboard.dashboard'))

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
    