from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required

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


@admin_bp.route('/admin/create-month', methods=['POST'])
@login_required
def create_month():
    if not current_user.is_admin:
        return "Unauthorized", 401
    
    year = int(request.form['year'])
    month = request.form['month']

    for center in Center.query.all():
        # flag = Month.create(center, month, year)
        flash(f"Foi Criado o mês {month} de {year} para o centro {center.abbreviation}")

    return redirect(url_for('admin.admin'))


@admin_bp.route('/admin/next-month', methods=['POST'])
@login_required
def next_month():
    if not current_user.is_admin:
        return "Unauthorized", 401

    for center in Center.query.all():
        # flag = Month.next(center)
        flash(f"O mês corrente foi avançado para o mês ")

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