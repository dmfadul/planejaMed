from flask import Blueprint, request, render_template, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models import Center, Month, User, BaseAppointment
from .resolve_data import resolve_data
from .gen_data import gen_base_table, gen_month_table
import app.global_vars as global_vars

dataview_bp = Blueprint(
                        "dataview",
                        __name__,
                        template_folder="templates",
                        static_folder="static",
                        static_url_path="/static/dataview"
                        )


@dataview_bp.route("/baseview/", methods=["GET", "POST"])
@login_required
def baseview():
    center_abbr = request.form.get("center")
    data = gen_base_table(center_abbr)

    return render_template("baseview.html",
                           data=data,
                           center=center_abbr,
                           is_admin=True)


@dataview_bp.route("/monthview/", methods=["GET", "POST"])
@login_required
def monthview():
    center_abbr = request.form.get("center")
    year = request.form.get("year")
    month_name = request.form.get("month")

    month = Month.query.filter_by(number=global_vars.MESES.index(month_name)+1, year=year).first()
    if month is None:
        flash(f"O mês {month_name} de {year} ainda não foi criado", "danger")
        return redirect(url_for("dashboard.dashboard"))


    data = gen_month_table(center_abbr, month_name, year)

    return render_template("monthview.html",
                           data=data,
                           hdays=month.holidays,
                           center=center_abbr,
                           month=month_name,
                           year=year,
                           is_admin=True)



@dataview_bp.route("/update-appointments", methods=["POST"])
@login_required
def update_appointments():
    if not current_user.is_admin:
        return jsonify({"status": "error", 'message': 'You are not an admin'})
    
    flag = resolve_data(request.get_json())
    if flag == 0:
        return jsonify({"status": "success", 'message': 'Appointments updated'})

    if flag == 1:
        flash("Horários Inválidos - A hora de Início e de Fim são iguais", "danger")
        return jsonify({"status": "error", 'message': 'Invalid hours - Start and End time are the same'})
    if flag == 2:
        return jsonify({"status": "error", 'message': 'Invalid hours - End time goes to the next day'})
    if flag == -1:
        flash("O Médico Selecionado Tem Horários conflitantes em Outro Centro", "danger")
        return jsonify({"status": "error", 'message': 'Conflicting hours'})
    
    return jsonify({"status": "error", 'message': 'An unexpected error occurred'})    


@dataview_bp.route("/sum-doctors", methods=["POST"])
@login_required
def sum_by_doctor():
    if not current_user.is_admin:
        return jsonify({"status": "error", 'message': 'You are not an admin'})
    
    month_name = request.form.get("month")
    year = request.form.get("year")

    month = Month.query.filter_by(number=global_vars.MESES.index(month_name)+1, year=year).first()
    centers = [center.abbreviation for center in Center.query.all()]
    doctors = sorted(User.query.all(), key=lambda x: x.full_name)

    header_1 = ["", month] + [x for tup in list(zip(centers, centers)) for x in tup]
    header_2 = ['Nº', 'Anestesiologista'] + ['Rotina', 'Plantões'] * 3
    data = [header_1, header_2]

    for i, doctor in enumerate(doctors):
        row = [i+1, doctor.full_name]
        for center in centers:
            center_hours = doctor.hours(month.id).get(center) or [0, 0]
            row += [center_hours[0], center_hours[1]]

        data.append(row)

    return render_template("doctor-sumview.html", data=data)


@dataview_bp.route("/sum-days/<center>/<month>/<year>", methods=["GET"])
@login_required
def sum_by_days(center, month, year):
    dias_semana = global_vars.DIAS_SEMANA
    if not current_user.is_admin:
        return jsonify({"status": "error", 'message': 'You are not an admin'})
    
    center = Center.query.filter_by(abbreviation=center).first()
    if year == 'null':
        base_dict = BaseAppointment.day_night_hours_dict(center.id)
        
        week_days = ['']
        week_indexes = ['']
        daytime_values = ['DIA:']
        night_values = ['NOITE:']

        for key in sorted(base_dict.keys(), key=lambda x: (x[1], x[0])):
            week_days.append(dias_semana[key[0]][0])
            week_indexes.append(key[1])
            daytime_values.append(base_dict[key][0])
            night_values.append(base_dict[key][1])

        data = [week_days, week_indexes, daytime_values, night_values]
    
    else:
        month = Month.query.filter_by(number=global_vars.MESES.index(month)+1, year=year).first()

        month_days = [''] + [f"{int(day.date.day):02d}" for day in month.days]
        week_days = [''] + [dias_semana[day.date.weekday()][0] for day in month.days]
        
        daytime_values = ['DIA: '] + [day.hours(center.id)[0] for day in month.days]
        night_values = ['NOITE: '] + [day.hours(center.id)[1] for day in month.days]

        data = [month_days, week_days, daytime_values, night_values]

    return render_template("day-sumview.html", data=data)
