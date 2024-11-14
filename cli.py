# import migration_funcs
from app.models import User, Center, Month, Appointment, Day, Request, Message, BaseAppointment, Vacation
from app import create_app, db
from app.routes.dataview.resolve_data import convert_hours
from app.hours_conversion import appointments_letters_key, gen_redudant_hour_list
from app.hours_conversion import convert_letter_to_hours
from app.routes.calendar.gen_data import gen_days_dict
from app.config import Config
import app.hours_conversion as hc
from datetime import datetime
import tests
import json


# app = create_app()
# with app.app_context():
#     rs = [374, 373, 359, 355]
    
#     for n in rs:
#         r = Request.query.filter_by(id=n).first()
#         print(r, r.response)


tests.test_originals(11, 2024)

