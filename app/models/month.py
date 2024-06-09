from app import db
from sqlalchemy import ForeignKey, UniqueConstraint
from .associations import month_day_association
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
    days = db.relationship('Day', secondary=month_day_association, back_populates='months', lazy=True)


    __table_args__ = (
        UniqueConstraint('center_id', 'number', 'year', name='uq_center_month_year'),
    )

    def __repr__(self):
        return f"{self.number}/{self.year}"  

    @classmethod
    def create_new_month(cls, center_id, number, year):
        month = cls(center_id=center_id, number=number, year=year)
        month.is_locked = True

        db.session.add(month)
        db.session.commit()
        return month

    @property
    def holidays(self):
        return []

    @property
    def previous_month(self):
        if self.number == 1:
            return 12, self.year - 1
        return self.number - 1, self.year

    @property
    def next_month(self):
        if self.number == 12:
            return 1, self.year + 1
        return self.number + 1, self.year

    @property
    def dates_row(self):
        start_date = datetime(self.previous_month[1], self.previous_month[0], global_vars.STR_DAY)
        end_date = datetime(self.year, self.number, global_vars.STR_DAY-1)

        dates_row = []
        while start_date <= end_date:
            dates_row.append(start_date)
            start_date += timedelta(days=1)
        
        return dates_row
    
    def populate_month(self):
        from app.models.day import Day
        if self.is_populated:
            return -1

        for date in self.dates_row:
            flag = Day.add_entry(month_id=self.id, date=date)

            if flag == -1:
                print(f"Data {date} já existe.")
                continue

        self.is_populated = True
        return 0