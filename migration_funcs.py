from app import create_app, db, bcrypt
from app.models import User, Center, BaseAppointment, Appointment, Month, Day
from datetime import datetime
from app.hours_conversion import convert_letter_to_hours

import app.global_vars as global_vars
import sqlite3
import json


DATABASE = 'old_db.db'

dias_semana = global_vars.DIAS_SEMANA
dias_semana_abbrev = [d[:3] for d in dias_semana]
hours_map = global_vars.HOURS_MAP.copy()
hours_map["tn"] = (13, 6)
hours_map["d10"] = (7, 17)
hours_map["d9"] = (7, 16)


def drop_all_tables():
    app = create_app()
    with app.app_context():
        db.drop_all()


def get_tables_names():
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    values = cursor.fetchall()

    if len(values) == 0:
        return None

    cursor.close()
    conn.close()

    return values


def load_from_db(table, id_num):
    conn = sqlite3.connect(DATABASE)
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table} WHERE id=?", (id_num,))
    values = cursor.fetchall()

    if len(values) == 0:
        return None

    values = values[0]

    cursor.close()
    conn.close()

    return values


def get_all_ids(table_name):
    conn = sqlite3.connect(DATABASE)  # Replace with your actual database
    cursor = conn.cursor()

    query = f"SELECT id FROM {table_name}"  # Adjust this query based on your table schema
    cursor.execute(query)

    all_ids = [row[0] for row in cursor.fetchall()]

    conn.close()
    return all_ids


def migrate_user(user_id):
    user = load_from_db('Users', user_id)

    user_dict = {}
    user_dict["first_name"] = user[2]
    user_dict["middle_name"] = user[3]
    user_dict["last_name"] = user[4]
    user_dict["crm"] = user[5]
    user_dict["rqe"] = user[6]
    user_dict["phone"] = user[7]
    user_dict["email"] = user[8]
    user_dict["password"] = bcrypt.generate_password_hash(user[1]).decode('utf-8')
    user_dict["date_joined"] = datetime.strptime(user[9], "%Y-%m-%d")

    return user_dict


def migrate_users():
    user_ids = get_all_ids("users")
    app = create_app()

    for user_id in user_ids:
        if int(user_id) < 5000:
            continue
        old_user = migrate_user(user_id=user_id)
        print('ou', old_user)
        date_joined = old_user.pop("date_joined")

        with app.app_context():
            new_user = User.add_entry(**old_user)

            if new_user == -1:
                print(f"{old_user.get("full_name")} crm already exists")
                continue
            if new_user == -2:
                print(f"{old_user.get("full_name")} name already exists")
                continue
            new_user.date_joined = date_joined
            new_user.activate()
            new_user.make_visible()


def edit_user(user_id):
    user = load_from_db('Users', user_id)

    user_dict = {}
    user_dict["crm"] = user[5]
    user_dict["phone"] = user[7]
    user_dict["email"] = user[8]
    user_dict["password"] = bcrypt.generate_password_hash(user[1]).decode('utf-8')

    return user_dict


def edit_users():
    user_ids = get_all_ids("users")
    app = create_app()

    for user_id in user_ids:
        if int(user_id) < 5000:
            continue
        old_user = migrate_user(user_id=user_id)
        print('ou', old_user)

        with app.app_context():
            new_user = User.query.filter_by(crm=old_user.get("crm")).first()

            if new_user is None:
                print(f"{old_user.get("full_name")} not found")
                continue

            new_user.edit(phone=old_user.get("phone"),
                          email=old_user.get("email"),
            )
            
            new_user.set_password(old_user.get("password"))


def adjust_users():
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(crm=26704).first()
        user.set_password("741852")
        user.make_admin()
        user.make_sudo()

        new_user = User.add_entry(first_name="David",
                                middle_name="Malheiro",
                                last_name="Fadul",
                                crm=10000,
                                rqe=10000,
                                phone="(41)99257-4321",
                                email="dmf030@gmail.com",
                                password="123456")
        new_user.set_password("741852")
        new_user.make_admin()
        new_user.make_sudo()
        new_user.make_root()
        
        new_user.activate()
        new_user.make_invisible()

        User.create_system_user()

def add_centers():
    centers = [
               {"name": "CENTRO CIRÚRGICO GERAL", "abbreviation": "CCG"},
               {"name": "CENTRO CIRÚRGICO OBSTÉTRICO", "abbreviation": "CCO"},
               {"name": "CENTRO CIRÚGICO DE QUEIMADOS", "abbreviation": "CCQ"},
               {"name": "SERVIÇO DE APOIO DE DIAGNÓSTICO E TRATAMENTO", "abbreviation": "SADT"},
              ]
    
    app = create_app()
    for center in centers:
        with app.app_context():
            new_center = Center.add_entry(**center)
            if new_center == -1:
                print(f"{new_center.name} name already exists")
                continue
            if new_center == -2:
                print(f"{new_center.abbreviation} abbreviation already exists")
                continue


def migrate_base(base_id):
    base = load_from_db('Bases', base_id)
    data = json.loads(base[2])

    app = create_app()

    entries = []
    for i in range(len(data)):
        if i in [0, 1]:
            continue
        doctor_name = data[i][0]
        with app.app_context():
            doctor = User.get_by_name(doctor_name)
            center = Center.query.filter_by(abbreviation=base[1]).first()

            if isinstance(doctor, int):
                print(f"{doctor_name} returned error {doctor}")
                continue

        for j in range(len(data[i])):
            if j == 0:
                continue
            if data[i][j] == '' or data[i][j] is None:
                continue

            week_day, week_index = dias_semana_abbrev.index(data[0][j]), data[1][j]
            
            hours_str = data[i][j].strip().lower()
            hours_str = hours_str.replace("n6", "c")
            hours = hours_map.get(hours_str)
            
            # if hours is None:
            #     print(hours_str)
            #     continue
            
            if hours_str == 'mn':
                hour_list = list(range(7, 13)) + list(range(19, 24)) + list(range(7))
            elif hours[0] < hours[1]:
                hour_list = list(range(hours[0], hours[1]+1))
            else:
                hour_list = list(range(hours[0], 24)) + list(range(hours[1]+1))

            with app.app_context():
                for hour in hour_list:
                    print(doctor.id, center.id, week_day, week_index, hour)
                    entries.append(BaseAppointment(
                        user_id=doctor.id,
                        center_id=center.id,
                        week_day=week_day,
                        week_index=week_index,
                        hour=hour
                    ))

    if entries:
        with app.app_context():
            BaseAppointment.add_entries(entries)


def prepare_month(month_num, year):
    month = Month.create_new_month(month_num, year)
    month.populate()
    month.gen_appointments()
    
    return month


def migrate_months():
    months_ids = get_all_ids("months")
    months = []
    for month_id in months_ids:
        center_abbr = month_id[:3]
        month_num = int(month_id[3:-5])
        month_type = month_id[-1]
        year = int(month_id[-5:-1])

        if month_num == 8:
            continue
        print(month_num, year)

        if month_type == '0':
            continue
        
        months.append((center_abbr, month_num, year))

    months = sorted(months, key=lambda x: (x[2], x[1]))

    for month in months:
        migrate_month(*month)


def migrate_month(center_abbr, month_num, year):
    month_id = f"{center_abbr}{month_num}{year}1"
    month_data = load_from_db('months', month_id)

    data_holidays = json.loads(month_data[5])

    data = data_holidays[:-1]
    holidays = [h for h in data_holidays[-1] if h]

    app = create_app()

    entries = []
    for i in range(len(data)):
        if i in [0, 1]:
            continue
        doctor_name = data[i][0]

        with app.app_context():
            doctor = User.get_by_name(doctor_name)
            if doctor == -1:
                continue

        for j in range(len(data[i])):
            if j == 0:
                continue
            if data[i][j] == '' or data[i][j] is None:
                continue
            
            with app.app_context():
                center = Center.query.filter_by(abbreviation=center_abbr).first()
                month = Month.query.filter_by(number=month_num, year=year).first()

                if month is None:
                    month = Month.create_new_month(number=month_num, year=year)
                    month.populate()
                
                day_num = int(data[1][j])
                day = month.get_day(day_num)
                  
                hours_str = data[i][j].strip().lower()
                hours_str = hours_str.replace("n6", "c")
            
                hour_list = convert_letter_to_hours(hours_str)
            
                if not hour_list:
                    continue

                if  hour_list == 1:
                    print("there was an X in the hours_str")
                    continue
        
                for hour in hour_list:
                    print(doctor.full_name, center.abbreviation, day.date, hour)
                    if day_num in holidays:
                        day.add_holiday()

                    entries.append(Appointment(
                                   user_id=doctor.id,
                                   center_id=center.id,
                                   day_id=day.id,
                                   hour=hour
                                  ))

    if entries:
        with app.app_context():
            Appointment.add_entries(entries)
