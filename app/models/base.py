import instance.global_vars as global_vars
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
    def add_entry(cls, user_id, center_id, week_day, week_index, hour):
        existing_apps = cls.query.all()

        existing_apps = [app for app in existing_apps if app.user_id == user_id]
        existing_apps = [app for app in existing_apps if app.week_day == week_day]
        existing_apps = [app for app in existing_apps if app.week_index == week_index]
        existing_apps = [app for app in existing_apps if app.hour == hour]

        if existing_apps:
            print("Conflicting hours")
            return -1

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