from app import db
from datetime import datetime
from sqlalchemy import ForeignKey


class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    sender_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    request_id = db.Column(db.Integer, ForeignKey('requests.id'), nullable=True)
    receivers_code = db.Column(db.Text, nullable=False)
    action = db.Column(db.Text, nullable=False, default="info")
    content = db.Column(db.Text, nullable=False)

    creation_date = db.Column(db.Date, nullable=False, default=datetime.now())
    is_archived = db.Column(db.Boolean, default=False)

    sender = db.relationship('User', foreign_keys=[sender_id], back_populates='messages_sent', lazy=True)
    request = db.relationship('Request', back_populates='messages', lazy=True) 

    def __repr__(self):
        return self.payload
    
    @classmethod
    def new_message(cls, sender_id, receivers_code, content):
        new_message = cls(sender_id=sender_id,
                          receivers_code=receivers_code,
                          content=content)
        
        db.session.add(new_message)
        db.session.commit()
        return new_message
    
    @classmethod
    def new_cancel_message(cls, sender_id, request_id, receivers_code):
        new_message = cls(sender_id=sender_id,
                          request_id=request_id,
                          receivers_code=receivers_code,
                          action="cancel",
                          content=""
                          )
        
        db.session.add(new_message)
        db.session.commit()

        return "new_message"
    
    def delete(self):
        self.request_id = None
        db.session.delete(self)
        db.session.commit()
        return 0
    
    @classmethod
    def filter_by_user(cls, user_id):
        return [m for m in cls.query.filter_by(is_archived=False).all() if user_id in m.receivers]
    
    @property
    def receivers(self):
        from app.models.user import User

        if self.receivers_code == "*":
            user_ids = [user.id for user in User.query.all() if user.is_admin]
        else:
            user_ids = [user.id for user in User.query.all() if user.id == int(self.receivers_code)]
    
        return user_ids
    
    @property
    def payload(self):
        from app.hours_conversion import convert_hours_to_line

        if self.action == "info":
            return self.content
        
        noun = self.request.noun
        date = self.request.date.strftime("%d/%m/%Y")
        hours = convert_hours_to_line(self.request.hours)
        center = self.request.center.abbreviation

        message = f"""Você tem uma solicitação de {noun} para {date}
        de {hours} no centro {center}. Aperte Cancelar para cancelar a solicitação."""

        return message

    def dismiss(self):
        self.is_archived = True
        db.session.commit()
        return "A mensagem foi arquivada com sucesso."
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return "A mensagem foi deletada com sucesso."

    def cancel(self):
        self.request.delete()
        self.request_id = None
        db.session.delete(self)
        db.session.commit()

        return "A requisição foi cancelada com sucesso."