from flask import Blueprint, request, session, render_template, jsonify, flash, redirect, url_for
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
    if not current_user.is_admin:
        return "Unauthorized", 401
    
    if request.method == "POST":
        center_abbr = request.form.get("center")
        session["center_abbr"] = center_abbr
    else:
        center_abbr = session.get("center_abbr")

    if not center_abbr:
        return "Centro não encontrado", 404
    
    data = gen_base_table(center_abbr)

    return render_template("baseview.html",
                           data=data,
                           center=center_abbr,
                           is_admin=current_user.is_admin)


@dataview_bp.route("/monthview/", methods=["GET", "POST"])
@login_required
def monthview():
    if request.method == "POST":
        center_abbr = request.form.get("center")
        year = request.form.get("year")
        month_name = request.form.get("month")
        session["center_abbr"] = center_abbr
        session["year"] = year
        session["month_name"] = month_name
    else:
        center_abbr = session.get("center_abbr")
        year = session.get("year")
        month_name = session.get("month_name")

    if month_name is None or year is None or center_abbr is None:
        month = Month.get_current()
        center_abbr = "CCG"
    else:
        month = Month.query.filter_by(number=global_vars.MESES.index(month_name)+1, year=year).first()

    if month is None:
        flash(f"O mês {month_name} de {year} ainda não foi criado", "danger")
        return redirect(url_for("dashboard.dashboard"))

    data = gen_month_table(center_abbr, month.name, month.year)

    return render_template("monthview.html",
                           data=data,
                           hdays=month.holidays,
                           center=center_abbr,
                           month=month.name,
                           year=month.year,
                           is_admin=current_user.is_admin)


@dataview_bp.route("/update-appointments", methods=["POST"])
@login_required
def update_appointments():
    if not current_user.is_admin:
        return jsonify({"status": "error", 'message': 'You are not an admin'})
    
    flag = resolve_data(request.get_json())
    if flag == 0:
        return jsonify({"status": "success", 'message': 'Appointments updated'})
    
    flash(flag, "danger")
    return jsonify({"status": "error", 'message': 'Appointments not updated'})


@dataview_bp.route("/resolve-holidays", methods=["POST"])
@login_required
def resolve_holidays():
    if not current_user.is_admin:
        return jsonify({"status": "error", 'message': 'You are not an admin'})
    
    action = request.get_json().get("action")

    day_num = request.get_json().get("day")
    month_name = request.get_json().get("monthName")
    year = request.get_json().get("year")

    month = Month.query.filter_by(number=global_vars.MESES.index(month_name)+1, year=year).first()
    day = month.get_day(day_num)

    if not day:
        return jsonify({"status": "error", 'message': 'Day not found'})

    if action == "add":
        day.add_holiday()

    elif action == "remove":
        day.remove_holiday()

    return jsonify({"status": "success", 'message': 'Holidays updated'})


@dataview_bp.route("/sum-doctors-base", methods=["POST"])
@login_required
def sum_doctor_by_base():
    if not current_user.is_admin:
        return jsonify({"status": "error", 'message': 'You are not an admin'})

    centers = [center.abbreviation for center in Center.query.filter_by(is_active=True).all()]
    doctors = sorted(User.query.filter_by(is_active=True, is_visible=True).all(), key=lambda x: x.full_name)

    header_1 = ["", ""] + [x for tup in list(zip(centers, centers)) for x in tup] + ["Total", "Total"]
    header_2 = ['Nº', 'Anestesiologista'] + ['Rotina', 'Plantão'] * (len(centers) + 1)
    data = [header_1, header_2]

    for i, doctor in enumerate(doctors):
        row = [i+1, doctor.full_name]
        for center in Center.query.filter_by(is_active=True).all():
            center_hours = BaseAppointment.get_user_by_center(doctor.id, center.id, split_the_fifth=True)
            row += [round(center_hours.get('routine')), round(center_hours.get('plaintemps'))]

        total = BaseAppointment.get_users_total(doctor.id, split_the_fifth=True)
        row += [round(total.get('routine')), round(total.get('plaintemps'))]
        data.append(row)

    return render_template("doctor-sumview.html", data=data)
    


@dataview_bp.route("/sum-doctors-month", methods=["POST"])
@login_required
def sum_doctor_by_month():
    if not current_user.is_admin:
        return jsonify({"status": "error", 'message': 'You are not an admin'})
    
    month_name = request.form.get("month")
    year = request.form.get("year")

    month = Month.query.filter_by(number=global_vars.MESES.index(month_name)+1, year=year).first()
    centers = [center.abbreviation for center in Center.query.filter_by(is_active=True).all()]
    doctors = sorted(month.users, key=lambda x: x.full_name)
    # doctors = sorted(User.query.filter_by(is_active=True, is_visible=True).all(), key=lambda x: x.full_name)

    header_1 = ["", month] + [x for tup in list(zip(centers, centers)) for x in tup]
    header_2 = ['Nº', 'Anestesiologista'] + ['Rotina', 'Plantão'] * len(centers)
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
