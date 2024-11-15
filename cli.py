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
    # user = User.query.filter_by(crm=26704).first()
    # month = Month.get_current()
    # day = month.get_day(25)
    # center = Center.query.filter_by(abbreviation="CCG").first()

    # apps = Appointment.query.filter_by(user_id=user.id,
    #                                    day_id=day.id,
    #                                    center_id=center.id).all()
    
    # for a in apps:
    #     print(a.user, a.day, a.center.abbreviation, a.hour, a.is_confirmed)
    #     a.delete_entry()

    # r = Request.query.all()[-1]
    # print(r, r.id, r.response, r.is_open)

    # r.delete()

    # req = Request.query.filter_by(id=359).first()
    # print(req.signal(26704))

    # user = User.query.filter_by(crm=26704).first()
    # reqs = user.get_month_requests(11, 2024)

    # for req in reqs:
    #     r = Request.query.filter_by(id=req[0]).first()
    #     print(r)


tests.test_originals(11, 2024, single_user=[34085])
