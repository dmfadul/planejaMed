from app import db
from sqlalchemy import ForeignKey
from unidecode import unidecode
from datetime import datetime


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    first_name = db.Column(db.Text, nullable=False)
    middle_name = db.Column(db.Text, nullable=True)
    last_name = db.Column(db.Text, nullable=False)

    crm = db.Column(db.Integer, nullable=False, unique=True)
    rqe = db.Column(db.Integer, nullable=False, unique=True)

    phone = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)

    date_joined = db.Column(db.Date, default=datetime.now())
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    is_locked = db.Column(db.Boolean, default=True)
    
    password = db.Column(db.Text, nullable=False)

    appointments = db.relationship('Appointment', back_populates='user', lazy=True)
    base_appointments = db.relationship('BaseAppointment', back_populates='user', lazy=True)

    requests_sent = db.relationship('Request', foreign_keys='Request.requester_id', back_populates='requester', lazy=True)
    requests_received = db.relationship('Request', foreign_keys='Request.responder_id', back_populates='responder', lazy=True)

    def __repr__(self):
        return f'{self.first_name} {self.last_name}'
    
    @classmethod
    def add_entry(cls, first_name, middle_name, last_name, crm, rqe, phone, email, password):
        users = cls.query.all()
        crms = [user.crm for user in users]
        names = [user.full_name() for user in users]

        # Create a new instance of Appointments
        new_user = cls(
            first_name = first_name,
            middle_name = middle_name,
            last_name = last_name,
            crm = crm,
            rqe = rqe,
            phone = phone,
            email = email,
            password = password
        )

        # Add the new instance to the session and commit it
        db.session.add(new_user)
        if new_user.crm in crms:
            db.session.rollback()
            return -1
        if new_user.full_name in names:
            db.session.rollback()
            return -2
        # try:
        #     db.session.commit()
        # except Exception as e:
        #     db.session.rollback()
        #     raise e

        return new_user

    @classmethod
    def get_crm(cls, full_name):
        full_name_clean = unidecode(' '.join([part.strip().lower() for part in full_name.split()]))
        users = cls.query.all()
        names = [unidecode(user.full_name().lower()) for user in users]

        if names.count(full_name_clean) == 0:
            print(full_name_clean)
            return -1
        
        if names.count(full_name_clean) == 1:
            for user in users:
                if unidecode(user.full_name().lower()) == full_name_clean:
                    return user.crm
                
        return -2
    
    @property
    def full_name(self):
        return f'{self.first_name} {self.middle_name} {self.last_name}'
    
    def lock(self):
        self.is_locked = True
        db.session.commit()
    
    def unlock(self):
        self.is_locked = False
        db.session.commit()
    
    def activate(self):
        self.is_active = True
        db.session.commit()

    def deactivate(self):
        self.is_active = False
        db.session.commit()