# import migration_funcs
from app.models import User, Center, Month, Appointment, Day, Request, Message
from app import create_app, db
from app.routes.dataview.resolve_data import convert_hours
from app.hours_conversion import appointments_letters_key, gen_redudant_hour_list
from app.hours_conversion import convert_letter_to_hours
from app.routes.calendar.gen_data import gen_days_dict
from app.config import Config
import app.hours_conversion as hc
from datetime import datetime
import json


vacs_crm = [
    26704,
    34085,
    28107,
    10880,
    15812,
    11967,
    24250,
    31051,
    23301,
    35636,
    28327,
    7804,
    33198,
    5078
]

app = create_app()
with app.app_context():
    with open("/home/david/Downloads/dicionario.json", "r") as f:
        data = json.load(f)

    for key in data.keys():
        user = User.query.filter_by(crm=key).first()
        date = datetime.strptime(data[key], "%Y-%m-%d")

        if user is None:
            print(key)
            continue

        print(user, date)
        user.date_joined = date
        db.session.commit()

        if key in vacs_crm:
            pre_approved_vacation = True
            db.session.commit()

  

# migration_funcs.drop_all_tables()
# migration_funcs.add_centers()
# migration_funcs.migrate_users()
# migration_funcs.adjust_users()

# migration_funcs.migrate_base("CCG--BASE")

# migration_funcs.migrate_months()
