from flask import Blueprint, jsonify
from flask_login import login_required, current_user

from app.models import Month

privilege_bp = Blueprint('privilege',
                         __name__,
                         template_folder='templates',
                         static_folder='static',
                         static_url_path='/static/privilege'
                         )


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
