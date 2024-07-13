from app import create_app, db, bcrypt
from app.models import User, Center, BaseAppointment, Appointment, Month, Day
from datetime import datetime
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

def adjust_users():
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(crm=26704).first()
        user.make_admin()
        user.make_sudo()

        new_user = User.add_entry(first_name="David",
                                middle_name="Malheiro",
                                last_name="Fadul",
                                crm=10000,
                                rqe=10000,
                                phone="(41)99257-4321",
                                email="dmf030@gmail.com",
                                password="741852")
        new_user.make_admin()
        new_user.make_sudo()
        new_user.make_root()


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

    for i in range(len(data)):
        if i in [0, 1]:
            continue
        doctor_name = data[i][0]
        with app.app_context():
            doctor = User.get_by_name(doctor_name)
            center = Center.query.filter_by(abbreviation=base[1]).first()

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

            entries = []
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
        BaseAppointment.add_entries(entries)


def prepare_month(month_num, year):
    month = Month.create_new_month(month_num, year)
    month.populate()
    month.gen_appointments()
    
    return month


def migrate_month(center_abbr, month_num, year):
    month_id = f"{center_abbr}{month_num}{year}1"
    month_data = load_from_db('months', month_id)

    data_holidays = json.loads(month_data[5])

    data = data_holidays[:-1]
    holidays = [h for h in data_holidays[-1] if h]

    app = create_app()

    for i in range(len(data)):
        if i in [0, 1]:
            continue
        doctor_name = data[i][0]
        with app.app_context():
            center = Center.query.filter_by(abbreviation=center_abbr).first()
            doctor = User.get_by_name(doctor_name)
            if doctor == -1:
                continue
            month = Month.query.filter_by(number=month_num, year=year).first()
            if month.is_populated:
                continue
            if month is None:
                month = Month.add_entry(number=month_num, year=year, center_id=center.id)
                month.populate()

        for j in range(len(data[i])):
            if j == 0:
                continue
            if data[i][j] == '' or data[i][j] is None:
                continue

            month_day = int(data[1][j])
            actual_month = month_num -1 if 26 <= month_day <= 31 else month_num
            month_date = datetime(year, actual_month, month_day)       
                    
            hours_str = data[i][j].strip().lower()
            hours_str = hours_str.replace("n6", "c")
            hours_str = hours_str
            
            hours_str = sorted(list(hours_str), key=lambda x: ['dn', 'd', 'm', 't', 'n', 'c', 'v'].index(x))
            hours_str = ''.join(hours_str)

            hours = hours_map.get(hours_str)
            
            if hours is None:
                continue
            
            if hours_str == 'mn':
                hour_list = list(range(7, 13)) + list(range(19, 24)) + list(range(1, 7))
            elif hours[0] < hours[1]:
                hour_list = list(range(hours[0], hours[1]+1))
            else:
                hour_list = list(range(hours[0], 24)) + list(range(hours[1]+1))

            entries = []
            with app.app_context():
                for hour in hour_list:
                    print(doctor.id, center.id, day.id, hour)
                    day = Day.query.filter_by(month_id=month.id, date=month_date).first()
                    if month_day in holidays:
                        day.add_holiday()

                    entries.append(Appointment(
                                   user_id=doctor.id,
                                   center_id=center.id,
                                   day_id=day.id,
                                   hour=hour
                                  ))

    if entries and False:
        Appointment.add_entries(entries)
