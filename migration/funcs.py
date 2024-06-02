import sqlite3
import json

DATABASE = 'migration/old_db.db'


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

            