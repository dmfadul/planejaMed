from app import db
from datetime import datetime, timedelta


class Month(db.Model):
    __tablename__ = 'months'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    number = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    is_current = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)

    days = db.relationship('Day', back_populates='month', lazy=True)

    def __repr__(self):
        return f"{self.number}/{self.year}"  

    @classmethod
    def gen_new_month(cls, number, year):
        month = cls(number=number, year=year)
        db.session.add(month)
        db.session.commit()
        return month

    @property
    def holidays(self):
        return []

    # @property
    # def previous_month(self):
    #     self.number -= 1

    # @property
    # def next_month(self):
    #     pass

    @property
    def dates_row():
        return []