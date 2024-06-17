from app import db
from sqlalchemy import ForeignKey
from datetime import datetime

class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    requester_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    responder_id = db.Column(db.Integer, ForeignKey('users.id'))
    receivers_code = db.Column(db.Text, nullable=False)
    action = db.Column(db.Text, nullable=False)

    is_open = db.Column(db.Boolean, default=True)
    creation_date = db.Column(db.Date, nullable=False, default=datetime.now())

    existing_appointment_id = db.Column(db.Integer, ForeignKey('appointments.id'))
    appointment_to_exchange_id = db.Column(db.Integer, ForeignKey('appointments.id'))
    doctor_who_will_cover_id = db.Column(db.Integer, ForeignKey('users.id'))
    doctor_to_include_id = db.Column(db.Integer, ForeignKey('users.id'))

    authorized = db.Column(db.Boolean, nullable=True)
    response_date = db.Column(db.Date, nullable=True)

    requester = db.relationship('User', foreign_keys=[requester_id], back_populates='requests_sent', lazy=True)
    responder = db.relationship('User', foreign_keys=[responder_id], back_populates='requests_received', lazy=True)
    existing_appointment = db.relationship('Appointment', foreign_keys=[existing_appointment_id], back_populates='general_requests', lazy=True)
    appointment_to_exchange = db.relationship('Appointment', foreign_keys=[appointment_to_exchange_id], back_populates='requests_to_exchange', lazy=True)
    doctor_who_will_cover = db.relationship('User', foreign_keys=[doctor_who_will_cover_id], lazy=True)
    doctor_to_include = db.relationship('User', foreign_keys=[doctor_to_include_id], lazy=True)
    
    def __repr__(self):
        return f'{self.requester} - {self.action} - {self.is_open}'
    
    @classmethod
    def new_user(cls, doctor_to_include_id):
        new_request = cls(requester_id=doctor_to_include_id,
                          receivers_code="*",
                          action="include_user",
                          existing_appointment_id=None,
                          appointment_to_exchange_id=None,
                          doctor_who_will_cover_id=None,
                          doctor_to_include_id=doctor_to_include_id)
        db.session.add(new_request)
        db.session.commit()
        return new_request
    
    @classmethod
    def filter_by_user(cls, user_id):
        return [req for req in cls.query.filter_by(is_open=True).all() if user_id in req.responders]

    @property
    def responders(self):
        from app.models.user import User

        user_ids = [user.id for user in User.query.all() if user.is_sudo]

        if self.receivers_code == "*":
            user_ids += [user.id for user in User.query.all() if user.is_admin]
        else:
            user_ids += [user.id for user in User.query.all() if user.id == int(self.receivers_code)]
    
        return user_ids
    

    def respond(self, responder_id, is_authorized):
        self.responder_id = responder_id
        self.authorized = is_authorized
        self.response_date = datetime.now()
        self.is_open = False

        db.session.commit()
        return 0
            