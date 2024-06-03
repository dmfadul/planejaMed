from app import db
from sqlalchemy import ForeignKey


class Center(db.Model):
    __tablename__ = 'centers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    abbreviation = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    appointments = db.relationship('Appointment', back_populates='center', lazy=True)   
    base_appointments = db.relationship('BaseAppointment', back_populates='center', lazy=True)

    def __repr__(self):
        return self.name