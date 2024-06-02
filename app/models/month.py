from app import db


class Month(db.Model):
    __tablename__ = 'months'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    year = db.Column(db.Text, nullable=False)
    month_name = db.Column(db.Text, nullable=False)

    appointments = db.relationship('Appointment', backref='month', lazy=True)