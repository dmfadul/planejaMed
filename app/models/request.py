from app import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .associations import request_appointment_association


class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    requester_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    responder_id = db.Column(db.Integer, ForeignKey('users.id'))
    receivers_code = db.Column(db.Text, nullable=False)
    action = db.Column(db.Text, nullable=False)

    creation_date = db.Column(db.Date, nullable=False, default=datetime.now())
    is_open = db.Column(db.Boolean, default=True)
    response_date = db.Column(db.Date, nullable=True)
    response = db.Column(db.Text, nullable=True)

    requester = db.relationship('User', foreign_keys=[requester_id], back_populates='requests_sent', lazy=True)
    responder = db.relationship('User', foreign_keys=[responder_id], back_populates='requests_received', lazy=True)

    appointments = relationship(
        'Appointment',
        secondary=request_appointment_association,
        back_populates='requests'
    )
    
    def __repr__(self):
        return self.translate()
    
    @classmethod
    def new_user(cls, doctor_to_include_id):
        new_request = cls(
            requester_id=doctor_to_include_id,
            receivers_code="*",
            action="include_user",
        )

        db.session.add(new_request)
        db.session.commit()
        return new_request
    
    @classmethod
    def exclusion(cls, doctor_id, center_id, day_id, hours):
        from app.models.appointment import Appointment

        new_request = cls(
            requester_id=doctor_id,
            receivers_code="*",
            action="exclude_appointments",
        )

        db.session.add(new_request)
        
        apps_not_found = []
        for hour in hours:
            app = Appointment.query.filter_by(
                day_id=day_id,
                user_id=doctor_id,
                center_id=center_id,
                hour=hour
            ).first()

            if not app:
                apps_not_found.append(hour)
                continue

            apps_with_del_req = []
            if app.requests and any(r.is_open and r.action == "exclude_appointments" for r in app.requests):
                apps_with_del_req.append(app)
                continue 

            new_request.appointments.append(app)

        if apps_not_found:
            db.session.rollback()
            return f"Horário (ou parte dele) não foi encontrado"
        
        if apps_with_del_req:
            db.session.rollback()
            return f"Horário (ou parte dele) já está marcado para exclusão"    
        
        db.session.commit()
        return new_request

    @classmethod
    def inclusion(cls, doctor, center, day, hours):
        from app.models.appointment import Appointment
        
        new_request = cls(
            requester_id=doctor.id,
            receivers_code="*",
            action="include_appointments",
        )

        db.session.add(new_request)

        unconfirmed_apps = []
        confirmed_apps = []
        for hour in hours:
            app = Appointment.query.filter_by(
                day_id=day.id,
                user_id=doctor.id,
                center_id=center.id,
                hour=hour
            ).first()

            if app and not app.is_confirmed:
                unconfirmed_apps.append(app)
            elif app and app.is_confirmed:
                confirmed_apps.append(app)
            elif not app:
                app = Appointment.add_entry(
                    user_id=doctor.id,
                    center_id=center.id,
                    day_id=day.id,
                    hour=hour,
                )

                if isinstance(app, str):
                    return app
                
                app.unconfirm()
            
            new_request.appointments.append(app)
        
        if confirmed_apps:
            db.session.rollback()
            return f"O Médico {doctor.full_name} está Ocupado no Horário Requisitado ou em Parte dele."
         
        if unconfirmed_apps:
            db.session.rollback()
            return f"""Conflito - Já há Requisição pendente para {doctor.full_name} em {center.abbreviation}
                        no dia {day.date} para o horário pedido (ou parte dele)."""
        
        db.session.commit()
        return new_request
    
    def delete(self):
        self.appointments = []

        db.session.delete(self)
        db.session.commit()

    @classmethod
    def filter_by_user(cls, user_id):
        return [req for req in cls.query.filter_by(is_open=True).all() if user_id in req.receivers]

    @property
    def receivers(self):
        from app.models.user import User

        user_ids = [user.id for user in User.query.all() if user.is_sudo]

        if self.receivers_code == "*":
            user_ids += [user.id for user in User.query.all() if user.is_admin]
        else:
            user_ids += [user.id for user in User.query.all() if user.id == int(self.receivers_code)]
    
        return user_ids
    
    def add_appointment(self, appointment):
        self.appointments.append(appointment)
        db.session.commit()

    def respond(self, responder_id, response):
        self.responder_id = responder_id
        self.response = response
        self.response_date = datetime.now()
        self.is_open = False

        db.session.commit()
        return 0
    
    def resolve(self, responder_id, authorized):
        from app.models import User

        if not authorized:
            for app in self.appointments:
                if not app.is_confirmed:
                    app.delete_entry()

            self.respond(responder_id=responder_id, response="denied")
            return "A solicitação foi Negada"
        
        if self.action == 'include_user':
            new_user = User.query.get(self.requester_id)
            new_user.activate()
            new_user.make_visible()

            self.respond(responder_id=responder_id, response='authorized')
            return f"O usuário {new_user.full_name} foi incluído com sucesso"

        if self.action == "include_appointments":
            for app in self.appointments:
                app.confirm()

            self.respond(responder_id=responder_id, response='authorized')
            return "Os horários foram incluídos com sucesso"
        
        if self.action == "exclude_appointments":
            for app in self.appointments:
                app.delete_entry()

            self.respond(responder_id=responder_id, response='authorized')
            return "Os horários foram excluídos com sucesso"

        return "ação não reconhecida"
    
    def translate(self):
        if self.action == "include_user":
            return f"Inclusão de Usuário - {self.requester.full_name}"
        
        apps_date = [app.day.date for app in self.appointments][0]
        apps_center = [app.center.abbreviation for app in self.appointments][0]
        apps_hours = [app.hour for app in self.appointments]
        translation = f"{self.requester.full_name} - {self.action} - {apps_center} - {apps_date} - {apps_hours}"

        return translation
    