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
        try:
            message = self.payload
        except Exception as e:
            message = f"""Uma mensagem apresentou erro.
            Por favor, informe ao administrador o código m-{self.id},
            para que este erro seja corrijido."""
        return message
    
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
        if not self.content == "":
            return self.content
        
        if self.action == "cancel":
            message = "Você tem " + self.core + " Aperte Cancelar para cancelar a solicitação."
        elif self.action == "info":
            answer = "autorizada" if self.request.response == 'authorized' else "negada"
            message = "Sua " + self.core + f" foi {answer}."

        return message

    @property
    def core(self):
        from app.hours_conversion import convert_hours_to_line
        
        if self.request.action == "include_user":
            return "solicitação de inclusão de usuário"
        
        if self.request.action == "include_appointments" and self.request.response == "denied":
            return "solicitação de inclusão"
        
        if self.request.action == "exclude_appointments" and self.request.response is not None:
            return "solicitação de inclusão"
        
        if self.request.action == "donate" and self.request.response is not None:
            return "solicitação de doação"
        
        noun = self.request.noun
        date = self.request.date.strftime("%d/%m/%Y")
        hours = convert_hours_to_line(self.request.hours)
        center = self.request.center.abbreviation

        if self.request.action in ["include_appointments", "exclude_appointments"]:
            core = f"""solicitação de {noun} para {date} de {hours} no centro {center}."""
        
        if self.request.action == "donate":
            other_doctor = [d for d in self.request.doctors if d != self.sender][0].full_name
            core = f"""solicitação de {noun} para {other_doctor}."""

        if self.request.action == "exchange":
            other_doctor = [d for d in self.request.doctors if d != self.sender][0].full_name
            core = f"""solicitação de {noun} com {other_doctor}"""

        return core

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