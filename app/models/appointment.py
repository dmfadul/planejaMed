from app import db
from sqlalchemy import ForeignKey


class Appointment(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    center_id = db.Column(db.Integer, ForeignKey('centers.id'), nullable=False)
    day_id = db.Column(db.Integer, ForeignKey('days.id'), nullable=False)

    hour = db.Column(db.Integer, nullable=False)

    user = db.relationship('User', back_populates='appointments', lazy=True)
    center = db.relationship('Center', back_populates='appointments', lazy=True)
    day = db.relationship('Day', back_populates='appointments', lazy=True)
    general_requests = db.relationship('Request', foreign_keys='Request.existing_appointment_id', back_populates='existing_appointment', lazy=True)
    requests_to_exchange = db.relationship('Request', foreign_keys='Request.appointment_to_exchange_id', back_populates='appointment_to_exchange', lazy=True)

    @classmethod
    def add_entry(cls, user_id, center_id, day_id, hour):       
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
    
    @classmethod
    def remove_entry(cls, user_id, center_id, day_id, hour):
        appointment = cls.query.filter_by(user_id=user_id,
                                          center_id=center_id,
                                          day_id=day_id,
                                          hour=hour).first()

        if appointment:
            db.session.delete(appointment)
            db.session.commit()
            return 0
        else:
            return -1
