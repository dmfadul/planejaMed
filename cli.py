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
    # req = Request.query.filter_by(id=359).first()
    # print(req.signal(26704))

    # user = User.query.filter_by(crm=26704).first()
    # reqs = user.get_month_requests(11, 2024)

    # for req in reqs:
    #     r = Request.query.filter_by(id=req[0]).first()
    #     print(r)


tests.test_originals(11, 2024, single_user=[26704])
