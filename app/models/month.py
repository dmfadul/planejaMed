from app import db
from sqlalchemy import ForeignKey, UniqueConstraint
from datetime import datetime, timedelta
import instance.global_vars as global_vars


class Month(db.Model):
    __tablename__ = 'months'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    center_id = db.Column(db.Integer, db.ForeignKey('centers.id'), nullable=False)
    number = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    is_populated = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    is_current = db.Column(db.Boolean, default=False)

    center = db.relationship('Center', back_populates='months', lazy=True)
    days = db.relationship('Day', back_populates='month', lazy=True)

    __table_args__ = (
        UniqueConstraint('center_id', 'number', 'year', name='uq_center_month_year'),
    )

    def __repr__(self):
        return f"{self.number}/{self.year}"  

    @classmethod
    def gen_new_month(cls, center_id, number, year):
        month = cls(center_id=center_id, number=number, year=year)
        db.session.add(month)
        db.session.commit()
        return month

    @property
    def holidays(self):
        return []

    @property
    def previous_month(self):
        if self.number == 1:
            return f"12/{self.year - 1}"
        return f"{self.number - 1}/{self.year}"

    @property
    def next_month(self):
        if self.number == 12:
            return f"1/{self.year + 1}"
        return f"{self.number + 1}/{self.year}"

    @property
    def dates_row():
        return []