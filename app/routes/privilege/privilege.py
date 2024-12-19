from flask import Blueprint, jsonify, request, flash, redirect, url_for, render_template
from flask_login import login_required, current_user

from app.models import Month, Vacation, User
from datetime import datetime

privilege_bp = Blueprint('privilege',
                         __name__,
                         template_folder='templates',
                         static_folder='static',
                         static_url_path='/static/privilege'
                         )


@privilege_bp.route('/get-privilege-report', methods=['POST'])
@login_required
def get_vacation_report():
    if not current_user.is_admin:
        return "Unauthorized", 401

    output = "output\noutput"
    return jsonify(output)


@privilege_bp.route('/admin/calculate-vacation-pay', methods=['POST', 'GET'])
@login_required
def calculate_vacation_pay():
    """calculate hypothetical payment for a vacation period.
    Should be deleted after mode is implemented"""
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


@privilege_bp.route('/get-vacation-pay', methods=['POST'])
@login_required
def get_vacation_pay():
    """Provide payment information to be displayed on the privilege report"""
    if not current_user.is_admin:
        return "Unauthorized", 401

    vacation_id = request.json['vacationID']
    vacation = Vacation.query.filter_by(id=vacation_id).first()

    start_date = vacation.start_date
    end_date = vacation.end_date
    doctor = vacation.user   
    
    output = vacation.calculate_payment()

    return jsonify(output)


@privilege_bp.route('/vacations-report', methods=['GET'])
@login_required
def vacations_report():
    if not current_user.is_admin:
        return "Unauthorized", 401

    Vacation.update_status()
    vacations = Vacation.get_report()
    return render_template('vacations-report.html', vacations=vacations)


@privilege_bp.route('/register-privilege', methods=['POST'])
@login_required
def register_privilege():
    """For admin to register privilege directly and bypass the request system"""
    if not current_user.is_admin:
        return "Unauthorized", 401

    Vacation.update_status()
    
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


@privilege_bp.route('/get-privilege-rights', methods=['GET'])
@login_required
def check_vacation_rights():
    if not current_user.is_admin:
        return "Unauthorized", 401

    current_month = Month.get_current()

    vac_dict = Month.check_for_vacation_entitlement_loss(current_month.number, current_month.year)
    no_base = vac_dict['no_base_rights']
    losing_base = vac_dict['losing_base_rights']
    no_realized = vac_dict['no_realized_rights']
    losing_realized = vac_dict['losing_realized_rights']

    vac_report = ""
    if losing_base:
        vac_report = "Os seguintes Médicos PERDERÃO direito (base) a férias:</br></br>"
        for user in losing_base:
            report = Month.get_vacation_entitlement_report(user.id, current_month.number, current_month.year)
            vac_report += f"{user} - {user.crm} - {report}.</br>"
            # send message to user

    if losing_realized:
        vac_report += "</br></br>"
        vac_report = "Os seguintes Médicos PERDERÃO direito (realizado) a férias:</br></br>"
        for user in losing_realized:
            routine, plaintemps = Month.get_vacation_entitlement_balance(user.id,
                                                                        current_month.number,
                                                                        current_month.year)    

            if routine < 0:
                vac_report += f"""O médico {user.full_name} - {user.crm} cumpriu {abs(routine)}
                                    horas de rotina A MENOS que o necessário.</br>"""
            elif plaintemps < 0:
                vac_report += f"""O médico {user.full_name} - {user.crm} cumpriu {abs(plaintemps)}
                                    horas de plantão A MENOS que o necessário.</br>"""
            else:
                vac_report += ""

            # send message to user

    if no_base:
        vac_report += "</br></br>"
        vac_report += "Os seguintes Médicos CONTINUARÃO SEM direito (base) a férias:</br></br>"
        for user in no_base:
            vac_report += f"{user.full_name} - {user.crm}</br>"
    else:
        vac_report += ""

    if no_realized:
        vac_report += "</br></br>"
        vac_report += "Os seguintes Médicos CONTINUARÃO SEM direito (realizado) a férias:</br></br>"
        for user in no_realized:
            vac_report += f"{user.full_name} - {user.crm}</br>"
    else:
        vac_report += ""
    
    vac_report += "</br></br>"
    return jsonify(vac_report)


@privilege_bp.route('/change-privilege-status', methods=['POST'])
@login_required
def change_privilege_status():
    if not current_user.is_admin:
        return "Unauthorized", 401

    vacation_id = request.json['vacationID']
    new_status = request.json['newStatus']
    vacation = Vacation.query.filter_by(id=vacation_id).first()
    if not vacation:
        return "Vacation not found", 404

    if new_status == 'paid':
        flag = vacation.pay()
        if isinstance(flag, str):
            flash(flag, "danger")
            return jsonify(flag)
    elif new_status == 'defered':
        vacation.approve()
    elif new_status == 'deleted':
        vacation.delete()
    else:
        return "Invalid status", 400

    return jsonify("success")

@privilege_bp.route('/privilege-rights', methods=['GET'])
@login_required
def check_privilege_rights():
    """direct access route. Only for admin to check privilege rights"""
    if not current_user.is_admin:
        return "Unauthorized", 401

    users = User.query.filter_by(is_active=True, is_visible=True).all()
    users = sorted(users, key=lambda x: x.full_name)

    output = ""
    for user in users:
        response = Vacation.check_vacation_entitlement(user.id, datetime.now())
        if response == 0:
            continue
        output += f"{user} - {user.crm} - {response}</br>"

    return output