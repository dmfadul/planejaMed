from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required

import app.global_vars as global_vars
from app.models import Center, Month, User, Request
from app.routes.calendar.gen_data import gen_doctors_dict
from app.config import Config
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
    
    current_month = Month.get_current()
    doctors_list = sorted([(d.crm, d.full_name) for d in current_month.users], key=lambda x: x[1])
    documents = ["-", 'COPAN', 'MACKENZIE']

    return render_template('admin.html',
                           title='Admin',
                           curr_is_latest=current_month.is_latest,
                           months= global_vars.MESES,
                           current_month_name=current_month.name,
                           current_year=current_month.year,
                           doctors_list=doctors_list,
                           next_month_name=current_month.next_month_name,
                           next_month_year=current_month.next_month[1],
                           user_is_root=current_user.is_root,
                           documents=documents)

@admin_bp.route('/admin/root', methods=['GET', 'POST'])
@login_required
def root_dashboard():
    if not current_user.is_admin or not current_user.is_root:
        return "Unauthorized", 401
    
    current_month = Month.get_current()
    next_month = Month.get_next()
    
    doctors_list = sorted([(d.crm, d.full_name) for d in current_month.users], key=lambda x: x[1])
    all_doctors = User.query.filter_by(is_active=True, is_visible=True).all()

    if not next_month:
        open_doctors_list = [d for d in all_doctors if d not in current_month.users]
    else:
        open_doctors_list = [d for d in all_doctors if d not in current_month.users or d not in next_month.users]

    open_doctors_list = sorted([(d.crm, d.full_name) for d in open_doctors_list], key=lambda x: x[1])
    open_doctors_list = open_doctors_list if open_doctors_list else [(0, "Nenhum médico disponível")]

    open_months = [current_month.name] if current_month.is_latest else [current_month.name, current_month.next_month_name]

    config = Config()
    maintenance_is_on = config.get('maintenance_mode')

    return render_template('root-dashboard.html',
                           title='Root',
                           doctors_list=doctors_list,
                           open_months=open_months,
                           open_doctors_list=open_doctors_list,
                           maintenance_is_on=maintenance_is_on,
                           months= global_vars.MESES,
                           current_month_name=current_month.name,
                           current_year=current_month.year)


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
    new_month.remove_base_entitlements()

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

    next_month.update_month_entitlements()
    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/delete-month', methods=['POST'])
@login_required
def delete_month():
    if not current_user.is_admin:
        return "Unauthorized", 401

    year = int(request.form['year'])
    month = request.form['month']

    next_month = Month.get_next()
    if not next_month.name == month or not next_month.year == year:
        flash(f"O mês {month} de {year} não pode ser apagado. Contacte o sysAdmin.", 'danger')
        return redirect(url_for('admin.root_dashboard'))

    month_number = global_vars.MESES.index(month) + 1
    flag = Month.delete(month_number, year)
    if flag:
        flash(f"O mês {month} de {year} não foi apagado", 'danger')
        return redirect(url_for('admin.root_dashboard'))
    
    for center in Center.query.all():
        flash(f"Foi deletado o mês {month} de {year} para o centro {center.abbreviation}")

    return redirect(url_for('admin.root_dashboard'))


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
    return redirect(url_for('admin.root_dashboard'))


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

    if doctor in month.users:
        flash(f"O médico {doctor.full_name} - {doctor.crm} já está no mês {month.name}/{month.year}", 'danger')
        return redirect(url_for('admin.root_dashboard'))
    
    month.add_user(doctor)
    flash(f"O médico {doctor.full_name} - {doctor.crm} foi incluído no mês {month.name}/{month.year}", 'success')
    return redirect(url_for('admin.root_dashboard'))


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
    return redirect(url_for('admin.root_dashboard'))


@admin_bp.route('/admin/create-center', methods=['POST'])
@login_required
def create_center():
    if not current_user.is_admin:
        return "Unauthorized", 401

    name = request.form['center_name']
    abbreviation = request.form['center_abbr']

    flag = Center.add_entry(name=name, abbreviation=abbreviation)
    if flag == -1:
        flash(f"O centro {name} já existe", 'danger')
        return redirect(url_for('admin.root_dashboard'))
    if flag == -2:
        flash(f"A abreviação {abbreviation} já existe", 'danger')
        return redirect(url_for('admin.root_dashboard'))
    
    if isinstance(flag, Center):
        flash(f"Foi criado o centro {abbreviation} - {name}", 'success')

    return redirect(url_for('admin.root_dashboard'))


@admin_bp.route('/admin/request-report', methods=['GET'])
@login_required
def request_report():
    if not current_user.is_admin:
        return "Unauthorized", 401

    reqs = Request.report()
    return render_template('request-report.html', reqs=reqs)


@admin_bp.route('/admin/rights-report', methods=['GET'])
@login_required
def rights_report():
    if not current_user.is_admin:
        return "Unauthorized", 401

    users = sorted([u for u in User.query.all() if (u.is_active and u.is_visible)], key=lambda x: x.full_name)
    rights = [{'user': u.full_name,
               'since': u.compliant_since,
               'history': u.compliance_history} for u in users ]
    return render_template('rights-report.html', rights=rights)


@admin_bp.route('/admin/toggle-maintenance', methods=['POST', 'GET'])
@login_required
def toggle_maintenance():
    if not current_user.is_root:
        return "Unauthorized", 401

    config = Config()
    maintenance_is_on = config.get('maintenance_mode')
    config.set('maintenance_mode', not maintenance_is_on)

    return redirect(url_for('admin.root_dashboard'))


@admin_bp.route('/upload', methods=['POST'])
def upload_file():
    from instance.config import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
    if not current_user.is_admin:
        return "Unauthorized", 401
    
    if 'file' not in request.files:
        flash("Erro no Upload", 'danger')
        return redirect(url_for('admin.admin'))
    
    file = request.files['file']
    if file.filename == '':
        flash("Nenhum arquivo selecionado", 'danger')
        return redirect(url_for('admin.admin'))
    
    if '.' not in file.filename:
        flash("Extensão de arquivo inválida", 'danger')
        return redirect(url_for('admin.admin'))
    
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        flash("Extensão de arquivo inválida", 'danger')
        return redirect(url_for('admin.admin'))

    month_name = request.form.get('month')
    year = request.form.get('year')
    document = request.form.get('document')
    
    if document == '-':
        flash("Escolha um tipo de documento", 'danger')
        return redirect(url_for('admin.admin'))
    
    new_filename = f"{document}_{year}-{month_name}.{file_ext}"

    filepath = os.path.join(UPLOAD_FOLDER, new_filename)
    # add check for existing file
    file.save(filepath)
    
    flash(f"Arquivo {file.filename} foi salvo", 'success')
    return redirect(url_for('admin.admin'))