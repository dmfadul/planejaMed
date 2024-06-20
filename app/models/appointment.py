from app import db
from sqlalchemy import ForeignKey, UniqueConstraint


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    center_id = db.Column(db.Integer, ForeignKey('centers.id'), nullable=False)
    day_id = db.Column(db.Integer, ForeignKey('days.id'), nullable=False)
    hour = db.Column(db.Integer, nullable=False)
    # THE LINE ABOVE MUST BE COMMENTED OUT AND THE LINE BELOW UNCOMMENTED
    # hour = db.Column(db.Integer, nullable=False, checkConstraint='hour >= 0 AND hour < 24')

    user = db.relationship('User', back_populates='appointments', lazy=True)
    center = db.relationship('Center', back_populates='appointments', lazy=True)
    day = db.relationship('Day', back_populates='appointments', lazy=True)
    
    general_requests = db.relationship('Request', foreign_keys='Request.existing_appointment_id', back_populates='existing_appointment', lazy=True)
    requests_to_exchange = db.relationship('Request', foreign_keys='Request.appointment_to_exchange_id', back_populates='appointment_to_exchange', lazy=True)

    __table_args__ = (UniqueConstraint('user_id', 'day_id', 'hour', name='unique_appointment'),)
    
    @classmethod
    def add_entry(cls, user_id, center_id, day_id, hour):
        existing_apps = cls.query.all()

        existing_apps = [app for app in existing_apps if app.user_id == user_id]
        existing_apps = [app for app in existing_apps if app.day_id == day_id]
        existing_apps = [app for app in existing_apps if app.hour == hour]
        existing_apps_other_centers = [app for app in existing_apps if app.center_id != center_id]
        existing_apps_same_center = [app for app in existing_apps if app.center_id == center_id]

        if existing_apps_other_centers:
            app = existing_apps_other_centers[0]
            return f"Conflito - {app.user.full_name} já tem esse horário no centro {app.center.abbreviation}"
        
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
    