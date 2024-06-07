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
        return f'{self.user.full_name} - {self.center.name} - {self.week_day} - {self.hour}'
    
    @classmethod
    def add_entry(cls, user_id, center_id, week_day, week_index, hour):
        base_appointments = cls.query.all()
        user_ids = [appointment.user_id for appointment in base_appointments]
        center_ids = [appointment.center_id for appointment in base_appointments]
        week_days = [appointment.week_day for appointment in base_appointments]
        week_indexes = [appointment.week_index for appointment in base_appointments]
        hours = [appointment.hour for appointment in base_appointments]

        new_base_appointment = cls(
            user_id = user_id,
            center_id = center_id,
            week_day = week_day,
            week_index = week_index,
            hour = hour
        )

        db.session.add(new_base_appointment)
        same_user = new_base_appointment.user_id in user_ids
        same_center = new_base_appointment.center_id in center_ids
        same_day = new_base_appointment.week_day in week_days
        same_index = new_base_appointment.week_index in week_indexes
        same_hour = new_base_appointment.hour in hours

        if same_user and same_day and same_index and same_hour:
            db.session.rollback()
            return -1
        db.session.commit()
        return new_base_appointment
    
    def delete_entry(self):
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def appointments_dict(cls, center_id):
        appointments = cls.query.filter_by(center_id=center_id).all()
        return {}