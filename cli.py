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
import json


app = create_app()
with app.app_context():
    user = User.query.filter_by(crm="26704").first()
    Vacation.check_concomitant_vacations("2024-11-20", "2024-11-26", user.id)
    
    # datetime_object = datetime.strptime("2024-11-20", "%Y-%m-%d")
    # Vacation.check(datetime_object, 26)
