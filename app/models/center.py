from app import db
from sqlalchemy import ForeignKey


class Center(db.Model):
    __tablename__ = 'centers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    abbreviation = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    months = db.relationship('Month', back_populates='center', lazy=True)   
    base_appointments = db.relationship('BaseAppointment', back_populates='center', lazy=True)

    def __repr__(self):
        return self.name
    
    @classmethod
    def add_entry(cls, name, abbreviation):
        centers = cls.query.all()
        names = [center.name for center in centers]
        abbreviations = [center.abbreviation for center in centers]

        new_center = cls(
            name = name,
            abbreviation = abbreviation
        )

        db.session.add(new_center)
        if new_center.name in names:
            db.session.rollback()
            return -1
        if new_center.abbreviation in abbreviations:
            db.session.rollback()
            return -2
        
        db.session.commit()

        return new_center
    