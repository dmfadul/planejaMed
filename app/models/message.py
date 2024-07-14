from app import db
from datetime import datetime
from sqlalchemy import ForeignKey


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    sender_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    request_id = db.Column(db.Integer, ForeignKey('requests.id'), nullable=False)
    receivers_code = db.Column(db.Text, nullable=False)
    action = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)

    creation_date = db.Column(db.Date, nullable=False, default=datetime.now())
    is_archived = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='messages_sent', lazy=True)
    request = db.relationship('Request', back_populates='messages', lazy=True) 

    def __repr__(self):
        return f'{self.sender} - {self.receiver} - {self.creation_date}'
    
    @classmethod
    def new_message(cls, sender_id, receiver_id, content):
        new_message = cls(sender_id=sender_id,
                          receiver_id=receiver_id,
                          content=content)
        db.session.add(new_message)
        db.session.commit()
        return new_message
    
    @property
    def receivers(self):
        from app.models.user import User

        user_ids = [user.id for user in User.query.all() if user.is_sudo]

        if self.receivers_code == "*":
            user_ids += [user.id for user in User.query.all() if user.is_admin]
        else:
            user_ids += [user.id for user in User.query.all() if user.id == int(self.receivers_code)]
    
        return user_ids