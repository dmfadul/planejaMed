from app import create_app, db
from app.models import User, Center
from datetime import datetime
import sqlite3
import json

DATABASE = 'old_db.db'


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
    user_dict["password"] = user[1]
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


def add_centers():
    centers = [
               {"name": "CENTRO CIRÚRGICO GERAL", "abbreviation": "CCG"},
               {"name": "CENTRO CIRÚRGICO OBSTÉTRICO", "abbreviation": "CCO"},
               {"name": "CENTRO CIRÚGICO DE QUEIMADOS", "abbreviation": "CCQ"},
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
    center = base[1]
    data = json.loads(base[2])

    for i in range(len(data)):
        if i in [0, 1]:
            continue
        doctor_name = data[i][0]
        print(doctor_name)

        for j in range(len(data[i])):
            if j == 0:
                continue
            if data[i][j] == '' or data[i][j] is None:
                continue

            date = (data[0][j], data[1][j])
            print(date, data[i][j])
