from app import db
from datetime import datetime


class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    creation_date = db.Column(db.Date, nullable=False, default=datetime.now())

    user = db.relationship('User', back_populates='logs', lazy=True)

    def __repr__(self):
        return f'{self.user} - {self.action} - {self.creation_date}'
    
    @classmethod
    def new_log(cls, user_id, action):
        new_log = cls(user_id=user_id,
                      action=action)
        db.session.add(new_log)
        db.session.commit()
        return new_log