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


def test_originals(month, year, single_user=None):
    with open(f"instance/originals/original_{month}_{year}.json") as f:
        month_dict = json.load(f)
        data = month_dict["data"]
        to_search = single_user if single_user else data

    app = create_app()
    with app.app_context():    
        for user_crm in to_search:
            test_originals = data.get(str(user_crm))
            user = User.query.filter_by(crm=user_crm).first()
            o_apps = user.get_original_appointments_by_month(month, year)

            if single_user is None:
                print(f"User {user} - {user_crm}: {test_originals == o_apps}")

    #         # for center in o_apps:
    #         #     print(center)
    #         #     for day, hour in o_apps[center].items():
    #         #         print(day, hour)
    
    #         if isinstance(o_apps, str):
    #             print(f"User {user} - {user_crm}: {o_apps}")
    #         else:
    #             print(f"User {user} - {user_crm}: {test_originals == o_apps}")

    # #     if len(test_originals) != len(o_apps):
    # #         print("Lengths are different")

    # #     for center in test_originals:
    # #         if center not in o_apps:
    # #             print(f"Center {center} is not in original appointments")
           
    # #     for center in o_apps:
    # #         if center not in test_originals:
    # #             print(f"Center {center} is not in test originals")
        
    # #     for center in test_originals:
    # #         oa_center = o_apps.get(center)
    # #         test_center = test_originals.get(center)

    # #         if len(oa_center) != len(test_center):
    # #             print(f"Lengths are different for {center}")

    # #         for day in oa_center:
    # #             if day not in test_center:
    # #                 print(f"Day {day} is not in test originals for {center}")
                
    # #         for day in test_center:
    # #             if day not in oa_center:
    # #                 print(f"Day {day} is not in original appointments for {center}")

    # #         oa_day = oa_center.get(day)
    # #         test_day = test_center.get(day)

    # #         if oa_day != test_day:
    # #             print(f"Original appointment {oa_day} is not equal to test appointment {test_day}")

