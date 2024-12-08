import re
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

        new_message.content = new_message.request.info
        db.session.commit()

        return new_message
    
    @classmethod
    def new_confirmation_message(cls, sender_id, request_id, receivers_code):
        new_message = cls(sender_id=sender_id,
                          request_id=request_id,
                          receivers_code=receivers_code,
                          action="info",
                          content=""
                          )
        
        db.session.add(new_message)
        db.session.commit()
        
        if new_message.request.action == "include_user":
            new_message.content = "Sua solicitação de entrada no aplicativo"
        elif new_message.request.action == "approve_vacation":
            new_message.content = f"""{new_message.request.info} foi autorizada. No entanto,
                                    você precisa continuar seguindo as regras do grupo
                                    até a data de início para receber o benefício."""
        else:
            new_message.content = new_message.request.info
        db.session.commit()

        return new_message
    
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
        try:
            if self.action == "cancel":
                message = re.sub(r'\*.*?\*', 'Você tem uma SOLICITAÇÃO PENDENTE de ', self.content)
                message = re.sub(r'\+[^+]*\+', '', message)
                message = message + ". Aperte Cancelar para cancelar a solicitação."
            elif self.action == "info" and self.request:
                answer = "autorizada" if self.request.response == 'authorized' else "negada"
                message = re.sub(r'\*.*?\*', 'Sua SOLICITAÇÃO DE ', self.content)
                message = re.sub(r'\+[^+]*\+', '', message) + f" foi {answer}."
            else:
                return self.content
        except Exception as e:
            message = f"""Uma mensagem apresentou erro.
            Por favor, informe ao administrador o código m-{self.id},
            para que este erro seja corrijido.{e}"""
        return message

    @property
    def is_open(self):
        return not self.is_archived
    
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