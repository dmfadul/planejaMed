from app import db
from sqlalchemy import ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship as relationship
from .associations import request_appointment_association


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    center_id = db.Column(db.Integer, ForeignKey('centers.id'), nullable=False)
    day_id = db.Column(db.Integer, ForeignKey('days.id'), nullable=False)
    request_id = db.Column(db.Integer, ForeignKey('requests.id'), nullable=True)
    hour = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', back_populates='appointments', lazy=True)
    center = db.relationship('Center', back_populates='appointments', lazy=True)
    day = db.relationship('Day', back_populates='appointments', lazy=True)

    requests = relationship(
        'Request',
        secondary=request_appointment_association,
        back_populates='appointments'
    )


    is_confirmed = db.Column(db.Boolean, default=True)
    
    __table_args__ = (UniqueConstraint('user_id', 'day_id', 'hour', name='unique_appointment'),)
    __table_args__ = (CheckConstraint('hour >= 0 AND hour < 24', name='valid_hour_range'),)
    
    @classmethod
    def add_entry(cls, user_id, center_id, day_id, hour):
        existing_apps = cls.query.filter_by(user_id=user_id, day_id=day_id, hour=hour).all()

        # existing_apps = [app for app in existing_apps if app.user_id == user_id]
        # existing_apps = [app for app in existing_apps if app.day_id == day_id]
        # existing_apps = [app for app in existing_apps if app.hour == hour]
        existing_apps_other_centers = [app for app in existing_apps if app.center_id != center_id]
        existing_apps_same_center = [app for app in existing_apps if app.center_id == center_id]

        if existing_apps_other_centers:
            app = existing_apps_other_centers[0]
            return f"""Conflito - {app.user.full_name} já tem esse horário
                        (ou parte dele) no centro {app.center.abbreviation}"""
        
        if existing_apps_same_center:
            app = existing_apps_same_center[0]
            return 0

        appointment = cls(user_id=user_id,
                          center_id=center_id,
                          day_id=day_id,
                          hour=hour)
        
        db.session.add(appointment)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e
        
        return appointment
    
    def delete_entry(self):
        db.session.delete(self)
        db.session.commit()

    @property
    def is_night(self):
        from app.global_vars import NIGHT_HOURS
        return self.hour in NIGHT_HOURS
    
    def change_doctor(self, new_doctor_id):
        self.user_id = new_doctor_id
        db.session.commit()
    
    def confirm(self):
        self.is_confirmed = True
        db.session.commit()

    def unconfirm(self):
        self.is_confirmed = False
        db.session.commit()

    @staticmethod
    def add_entries(entries):
        """gets a list of entries and adds them to the database"""
        from app import db
        db.session.bulk_save_objects(entries)
        db.session.commit()

        return 0
