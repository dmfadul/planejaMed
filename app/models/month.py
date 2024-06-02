from app import db


class Month(db.Model):
    __tablename__ = 'months'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)

    appointments = db.relationship('Appointment', backref='month', lazy=True)