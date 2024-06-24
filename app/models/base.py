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
        existing_apps = cls.query.all()

        existing_apps = [app for app in existing_apps if app.user_id == user_id]
        existing_apps = [app for app in existing_apps if app.week_day == week_day]
        existing_apps = [app for app in existing_apps if app.week_index == week_index]
        existing_apps = [app for app in existing_apps if app.hour == hour]
        existing_apps_other_centers = [app for app in existing_apps if app.center_id != center_id]
        existing_apps_same_center = [app for app in existing_apps if app.center_id == center_id]

        if existing_apps_other_centers:
            app = existing_apps_other_centers[0]
            return f"Conflito - {app.user.full_name} já tem esse horário na base {app.center.abbreviation}"
        
        if existing_apps_same_center:
            app = existing_apps_same_center[0]
            return 0


    @classmethod
    def add_entries(cls, entries):
        for entry in entries:
            flag = cls.check_conflicts(**entry)

            flags = []
            if flag:
                flags.append(flag)
                continue

            new_base_appointment = cls(**entry)
            db.session.add(new_base_appointment)
        db.session.commit()
        return flags or 0


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
    
    @property
    def is_night(self):
        from app.global_vars import NIGHT_HOURS
        return self.hour in NIGHT_HOURS