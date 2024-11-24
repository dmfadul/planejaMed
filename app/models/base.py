import math
from app import db
from sqlalchemy import ForeignKey


class BaseAppointment(db.Model):
    __tablename__ = 'base_appointments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    center_id = db.Column(db.Integer, ForeignKey('centers.id'), nullable=False)
    week_day = db.Column(db.Integer, nullable=False)
    week_index = db.Column(db.Integer, nullable=False)
    hour = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', back_populates='base_appointments')
    center = db.relationship('Center', back_populates='base_appointments')
    
    def __repr__(self):
        return f'{self.week_day} - {self.week_index} - {self.hour}'
    
    @classmethod
    def check_conflicts(cls, user_id, center_id, week_day, week_index, hour):
        existing_apps = cls.query.filter_by(user_id=user_id,
                                            week_day=week_day,
                                            week_index=week_index,
                                            hour=hour).all()

        # existing_apps = [app for app in existing_apps if app.user_id == user_id]
        # existing_apps = [app for app in existing_apps if app.week_day == week_day]
        # existing_apps = [app for app in existing_apps if app.week_index == week_index]
        # existing_apps = [app for app in existing_apps if app.hour == hour]
        existing_apps_other_centers = [app for app in existing_apps if app.center_id != center_id]
        existing_apps_same_center = [app for app in existing_apps if app.center_id == center_id]

        if existing_apps_other_centers:
            app = existing_apps_other_centers[0]
            return f"Conflito - {app.user.full_name} já tem esse horário na base {app.center.abbreviation}"
        
        if existing_apps_same_center:
            app = existing_apps_same_center[0]
            return 0

    @classmethod
    def add_entry(cls, user_id, center_id, week_day, week_index, hour):
        flag = cls.check_conflicts(user_id, center_id, week_day, week_index, hour)

        if flag:
            return flag
        
        new_base_appointment = cls(
            user_id = user_id,
            center_id = center_id,
            week_day = week_day,
            week_index = week_index,
            hour = hour
        )

        db.session.add(new_base_appointment)
        db.session.commit()

        return new_base_appointment
    
    def delete_entry(self):
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def appointments_dict(cls, center_id):
        appointments = cls.query.filter_by(center_id=center_id).all()
        return {}
    
    @classmethod
    def day_night_hours_dict(cls, center_id):
        appointments = cls.query.filter_by(center_id=center_id).all()

        app_dict = {}
        for app in appointments:
            if (app.week_day, app.week_index) not in app_dict:
                app_dict[(app.week_day, app.week_index)] = [0, 0]

            if app.is_night:
                app_dict[(app.week_day, app.week_index)][1] += 1
            else:
                app_dict[(app.week_day, app.week_index)][0] += 1
                
        return app_dict

    @classmethod
    def get_users_delta(cls, user_id, split_the_fifth=True):
        from app.models import User

        user = User.query.filter_by(id=user_id).first()
        if not user:
            return -1

        user_total = cls.get_users_total(user_id, split_the_fifth)
        user_rules = user.get_vacation_rules()
        delta = {key: user_total[key] - user_rules[key] for key in user_total}

        return delta


    @classmethod
    def get_users_total(cls, user_id, split_the_fifth=False):
        apps = cls.query.filter_by(user_id=user_id).all()

        output = {"routine": 0, "plaintemps": 0}
        for app in apps:
            count = 1
            if split_the_fifth and app.week_index == 5:
                count /= 3

            if app.week_day in [5, 6] or app.is_night:
                output["plaintemps"] += count
            else:
                output["routine"] += count    

        output["plaintemps"] = math.ceil(round(output["plaintemps"], 5))
        output["routine"] = math.ceil(round(output["routine"], 5))

        return output
    
    @classmethod
    def get_user_by_center(cls, user_id, center_id, split_the_fifth=False):
        apps = cls.query.filter_by(user_id=user_id, center_id=center_id).all()

        output = {"routine": 0, "plaintemps": 0}
        for app in apps:
            count = 1
            if split_the_fifth and app.week_index == 5:
                count /= 3

            if app.week_day in [5, 6] or app.is_night:
                output["plaintemps"] += count
            else:
                output["routine"] += count

        output["plaintemps"] = math.ceil(output["plaintemps"])
        output["routine"] = math.ceil(output["routine"])

        return output

    @property
    def is_night(self):
        from app.global_vars import NIGHT_HOURS
        return self.hour in NIGHT_HOURS
    
    @staticmethod
    def add_entries(entries):
        """gets a list of entries and adds them to the database"""
        from app import db
        db.session.bulk_save_objects(entries)
        db.session.commit()

        return 0
