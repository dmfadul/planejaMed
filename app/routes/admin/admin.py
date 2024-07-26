from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required

import app.global_vars as global_vars
from app.models import Center, Month, User
from app.routes.calendar.gen_data import gen_doctors_dict


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
    
    months = global_vars.MESES
    current_month = Month.get_current()
    current_year = current_month.year
    current_month_name = current_month.name
    next_month_name = current_month.next_month_name
    _, doctors_list = gen_doctors_dict()
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

    month.remove_user(doctor)
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