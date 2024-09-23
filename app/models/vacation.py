from app import db
from app.models import User, BaseAppointment


class Vacation(db.Model):
    __tablename__ = "vacations"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(100), nullable=False, default='pending')

    user = db.relationship('User', back_populates='vacations', lazy=True)
    
    
    @classmethod
    def check(cls, user_id):
        routine_plaintemps = BaseAppointment.get_users_total(user_id, split_the_fifth=True)

        print(routine_plaintemps)

