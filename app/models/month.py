from app import db


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
    