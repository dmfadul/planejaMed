from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required

import app.global_vars as global_vars
from app.models import Center, Month, User, Vacation, Request
from app.routes.calendar.gen_data import gen_doctors_dict
from app.config import Config
from datetime import datetime
import json
import os

admin_bp = Blueprint(
                    'admin',
                    __name__,
                    template_folder='templates',
                    static_folder='static',
                    static_url_path='/static/admin'
                    )


@admin_bp.route('/admin/', methods=['GET', 'POST'])
def admin():
    if not current_user.is_admin:
        return "Unauthorized", 401
    config = Config()
    maintenance_is_on = config.get('maintenance_mode')
    months = global_vars.MESES
    current_month = Month.get_current()
    current_year = current_month.year
    current_month_name = current_month.name
    next_month_name = current_month.next_month_name
    _, doctors_list = gen_doctors_dict(exclude_invisible=True)
    open_months = [current_month_name] if current_month.is_latest else [current_month_name, next_month_name]
    open_doctors_list = [d for d in doctors_list if d[0] not in [d.crm for d in current_month.users]]

    return render_template(
                           "admin.html",
                           title="Admin",
                           months=months,
                           current_month_name=current_month_name,
                           current_year=current_year,
                           next_month_name=next_month_name,
                           next_month_year=current_month.next_month[1],
                           curr_is_latest=current_month.is_latest,
                           doctors_list=doctors_list,
                           open_months=open_months,
                           open_doctors_list=open_doctors_list,
                           user_is_root=current_user.is_root,
                           maintenance_is_on=maintenance_is_on
                           )


@admin_bp.route('/admin/create-month', methods=['GET', 'POST'])
@login_required
def create_month():
    if not current_user.is_admin:
        return "Unauthorized", 401
    
    current_month = Month.get_current()
    next_month_number, next_month_year = current_month.next_month

    new_month = Month.create_new_month(next_month_number, next_month_year)
    if new_month == -1:
        flash(f"O mês {next_month_number}/{next_month_year} já existe", 'warning')
        return redirect(url_for('admin.admin'))
    flash(f"Foi criado o mês {next_month_number}/{next_month_year}", 'success')
    
    flag = new_month.populate()
    if flag:
        flash(f"O mês {next_month_number}/{next_month_year} não foi populado", 'danger')
        return redirect(url_for('admin.admin'))
    flash(f"O mês {next_month_number}/{next_month_year} foi populado", 'success')

    flag = new_month.gen_appointments()
    if flag:
        flash(f"Os plantões de {next_month_number}/{next_month_year} não foram gerados", 'danger')
        return redirect(url_for('admin.admin'))
    flash(f"Os plantões de {next_month_number}/{next_month_year} foram gerados", 'success')

    flag = new_month.fix_users()
    if flag:
        flash(f"Os usuários do mês {next_month_number}/{next_month_year} não foram corrigidos", 'danger')
        return redirect(url_for('admin.admin'))
    
    flag = new_month.save_original()
    if flag:
        flash(f"O original do mês {next_month_number}/{next_month_year} não foi salvo", 'danger')
        return redirect(url_for('admin.admin'))
    flash(f"O original do mês {next_month_number}/{next_month_year} foi salvo", 'success')

    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/next-month', methods=['GET', 'POST'])
@login_required
def next_month():
    if not current_user.is_admin:
        return "Unauthorized", 401

    current_month = Month.get_current()
    next_month_number, next_month_year = current_month.next_month
    next_month = Month.query.filter_by(number=next_month_number, year=next_month_year).first()

    if not next_month:
        raise Exception("Next month does not exist")
    
    flag = next_month.set_current()
    if not flag:
        flash(f"O mês corrente foi avançado para {next_month.name}/{next_month.year} ", 'success')

    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/delete-month', methods=['POST'])
@login_required
def delete_month():
    if not current_user.is_admin:
        return "Unauthorized", 401

    year = int(request.form['year'])
    month = request.form['month']

    for center in Center.query.all():
        # flag = Month.delete(center, month, year)
        flash(f"Foi deletado o mês {month} de {year} para o centro {center.abbreviation}")

    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/exclude-doctor', methods=['GET', 'POST'])
@login_required
def exclude_doctor():
    if not current_user.is_admin:
        return "Unauthorized", 401
    
    doctor_crm = request.form.get('crm')
    doctor = User.query.filter_by(crm=doctor_crm).first()
    
    if not doctor:
        return "Doctor not found", 404
    
    doctor.deactivate()
    doctor.make_invisible()

    flash(f"Foi excluído o médico {doctor.full_name} - {doctor.crm}", 'success')
    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/include-doctor-month', methods=['POST'])
@login_required
def include_doctor_month():
    if not current_user.is_admin:
        return "Unauthorized", 401

    crm = request.form.get('crm')
    doctor = User.query.filter_by(crm=crm).first()
    if not doctor:
        return "Doctor not found", 404

    month_name = request.form.get('month')
    current_month = Month.get_current()

    if month_name == current_month.name:
        month = current_month
    elif month_name == current_month.next_month_name:
        month = Month.get_next()
    else:
        return "Month not found", 404

    month.add_user(doctor)
    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/exclude-doctor-month', methods=['POST'])
@login_required
def exclude_doctor_month():
    if not current_user.is_admin:
        return "Unauthorized", 401

    crm = request.form.get('crm')
    doctor = User.query.filter_by(crm=crm).first()
    if not doctor:
        return "Doctor not found", 404

    month_name = request.form.get('month')
    current_month = Month.get_current()

    if month_name == current_month.name:
        month = current_month
    elif month_name == current_month.next_month_name:
        month = Month.get_next()
    else:
        return "Month not found", 404

    flag = month.remove_user(doctor)
    if flag:
        flash(f"O médico {doctor.full_name} - {doctor.crm} não foi excluído do mês {month.name}/{month.year}", 'danger')
        return redirect(url_for('admin.admin'))
    flash(f"O médico {doctor.full_name} - {doctor.crm} foi excluído do mês {month.name}/{month.year}", 'success')
    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/create-center', methods=['POST'])
@login_required
def create_center():
    if not current_user.is_admin:
        return "Unauthorized", 401

    abbreviation = request.form['abbreviation']
    name = request.form['name']

    # flag = Center.create(abbreviation, name)
    flash(f"Foi criado o centro {abbreviation} - {name}")

    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/request-report', methods=['GET'])
@login_required
def request_report():
    if not current_user.is_admin:
        return "Unauthorized", 401

    reqs = Request.report()
    return render_template('request-report.html', reqs=reqs)


@admin_bp.route('/admin/register_privilege', methods=['POST'])
@login_required
def register_privilege():
    if not current_user.is_admin:
        return "Unauthorized", 401

    crm = request.form['crm']
    user = User.query.filter_by(crm=crm).first()
    if not user:
        return "User not found", 404

    start_date = datetime.strptime(request.form['start_date'], "%Y-%m-%d")
    end_date = datetime.strptime(request.form['end_date'], "%Y-%m-%d")
    is_sick_leave = bool(int(request.form['privilege_type']))

    existing_vacations = Vacation.query.filter(Vacation.user_id==user.id,
                                               Vacation.status.in_(['approved', 'ongoing'])).all()
    for vac in existing_vacations:
        existing_start_date_check = start_date.date() <= vac.start_date <= end_date.date()
        new_start_date_check = vac.start_date <= start_date.date() <= vac.end_date
        existing_end_date_check = start_date.date() <= vac.end_date <= end_date.date()
        new_end_date_check = vac.start_date <= end_date.date() <= vac.end_date

        start_date_check = existing_start_date_check or new_start_date_check
        end_date_check = existing_end_date_check or new_end_date_check
        
        if start_date_check or end_date_check:
            flash("Férias conflitantes", "danger")
            return redirect(url_for('admin.admin'))

    new_vacation = Vacation.add_entry(start_date=start_date,
                                      end_date=end_date,
                                      user_id=user.id,
                                      is_sick_leave=is_sick_leave)    

    if isinstance(new_vacation, str):
        flash(new_vacation, "danger")
        return redirect(url_for('admin.admin'))

    new_vacation.approve()

    flash("Férias criadas", "success")
    return redirect(url_for('admin.admin'))
      


@admin_bp.route('/admin/vacations-report', methods=['GET'])
@login_required
def vacations_report():
    if not current_user.is_admin:
        return "Unauthorized", 401

    Vacation.update_status()
    vacations = Vacation.get_report()
    return render_template('vacations-report.html', vacations=vacations)


@admin_bp.route('/admin/get-vacation-pay', methods=['POST'])
@login_required
def get_vacation_pay():
    if not current_user.is_admin:
        return "Unauthorized", 401

    vacation_id = request.json['vacationID']
    vacation = Vacation.query.get(vacation_id)

    start_date = vacation.start_date
    end_date = vacation.end_date
    doctor = vacation.user   
    
    output = vacation.calculate_payment()

    return jsonify(output)


@admin_bp.route('/admin/calculate-vacation-pay', methods=['POST', 'GET'])
@login_required
def calculate_vacation_pay():
    if not current_user.is_admin:
        return "Unauthorized", 401

    data = request.form.to_dict()
    
    user = User.query.filter_by(crm=data['crm']).first()
    start_date = datetime.strptime(data['start_date'], "%Y-%m-%d")
    end_date = datetime.strptime(data['end_date'], "%Y-%m-%d")

    vacation = Vacation.add_entry(start_date=start_date,
                                  end_date=end_date,
                                  user_id=user.id)

    if isinstance(vacation, str):
        flash(vacation, "danger")
        return vacation
                                
    output = vacation.calculate_payment()
    vacation.remove_entry()

    return output


@admin_bp.route('/admin/pay-vacation', methods=['POST'])
@login_required
def pay_vacation():
    if not current_user.is_admin:
        return "Unauthorized", 401

    vacation_id = request.json['vacationID']
    vacation = Vacation.query.get(vacation_id)

    flag = vacation.pay()
    if isinstance(flag, str):
        flash(flag, "danger")
        return jsonify(flag)

    flash("Pagamento efetuado", "success")
    return jsonify("success")


@admin_bp.route('/admin/toggle-maintenance', methods=['POST', 'GET'])
@login_required
def toggle_maintenance():
    if not current_user.is_root:
        return "Unauthorized", 401

    config = Config()
    maintenance_is_on = config.get('maintenance_mode')
    config.set('maintenance_mode', not maintenance_is_on)

    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/get-vacation-report', methods=['POST'])
@login_required
def get_vacation_report():
    if not current_user.is_admin:
        return "Unauthorized", 401

    output = "output\noutput"
    return jsonify(output)


@admin_bp.route('/admin/force-aprove', methods=['POST'])
@login_required
def force_aprove():
    if not current_user.is_admin:
        return "Unauthorized", 401

    vacation_id = request.json['vacationID']
    vacation = Vacation.query.get(vacation_id)
    vacation.approve()

    return jsonify("success")