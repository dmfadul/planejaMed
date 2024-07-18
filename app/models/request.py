from app import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .associations import request_appointment_association
from app.models.appointment import Appointment
from app.hours_conversion import convert_hours_to_line

# TODO: TRANSLATION - fill info

# ADD MESSAGES
# TODO: front-end - fix requests order/create different buttons for messages

# REPLACE DATABASE
# TODO: make dashboard work without current month
# TODO: create edit_user function in migrations
# TODO: add __init__ to month

# TODO: ADD LOGS

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

    info = db.Column(db.Text, nullable=True)

    requester = db.relationship('User', foreign_keys=[requester_id], back_populates='requests_sent', lazy=True)
    responder = db.relationship('User', foreign_keys=[responder_id], back_populates='requests_received', lazy=True)
    messages = relationship('Message', back_populates='request', lazy=True)

    appointments = relationship(
        'Appointment',
        secondary=request_appointment_association,
        back_populates='requests'
    )
    
    def __repr__(self):
        return self.info
    
    @classmethod
    def new_user(cls, doctor_to_include_id):
        new_request = cls(
            requester_id=doctor_to_include_id,
            receivers_code="*",
            action="include_user"
        )

        db.session.add(new_request)
        new_request.info=f"""O Médico {new_request.requester.full_name} solicitou inclusão no sistema."""
        
        db.session.commit()

        return new_request
    
    @classmethod
    def exclusion(cls, doctor, center, day, hours):
        new_request = cls(
            requester_id=doctor.id,
            receivers_code="*",
            action="exclude_appointments",
            info = f"""{doctor.full_name} solicitou EXCLUSÃO dos horários:
                    {convert_hours_to_line(hours)} no centro {center.abbreviation}
                    no dia {day.date}."""
        )

        db.session.add(new_request)
        
        for hour in hours:
            app = Appointment.query.filter_by(
                day_id=day.id,
                user_id=doctor.id,
                center_id=center.id,
                hour=hour,
                is_confirmed=True
            ).first()

            if not app:
                db.session.rollback()
                return f"Horário (ou parte dele) não foi encontrado"

            if any([(r.is_open and r.action=='exclude_appointments') for r in app.requests]):
                db.session.rollback()
                return f"Horário (ou parte dele) tem requisição pendente"
            
            new_request.appointments.append(app)
        
        db.session.commit()
        return new_request

    @classmethod
    def inclusion(cls, doctor, center, day, hours):
        new_request = cls(
            requester_id=doctor.id,
            receivers_code="*",
            action="include_appointments",
            info=f"""{doctor.full_name} solicitou INCLUSÃO dos horários:
                    {convert_hours_to_line(hours)} no centro {center.abbreviation}
                    no dia {day.date}."""
        )

        db.session.add(new_request)

        for hour in hours:
            app = Appointment.query.filter_by(
                day_id=day.id,
                user_id=doctor.id,
                center_id=center.id,
                hour=hour
            ).first()

            if not app:
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
                continue

            if app.is_confirmed:
                db.session.rollback()
                return f"O Médico {doctor.full_name} está Ocupado no Horário Requisitado ou em Parte dele."
            
            if app.has_open_requests:
                db.session.rollback()
                return f"""O Médico {doctor.full_name} já tem
                            Requisição Pendente para o Horário Requisitado ou para Parte dele."""
        
            if not app.is_confirmed:
                db.session.rollback()
                return f"""Conflito - Já há Requisição pendente para {doctor.full_name}
                            em {center.abbreviation} no dia {day.date}
                            para o horário pedido (ou parte dele)."""
        
        db.session.commit()
        return new_request
    
    @classmethod
    def donation(cls, donor, center, day, hours, receiver, requester):
        new_request = cls(
            requester_id=donor.id,
            receivers_code=str(receiver.id),
            action="donate"
        )

        db.session.add(new_request)

        if requester.id == receiver.id:
            new_request.info=f"""{requester.full_name} solicitou DOAÇÃO dos horários:
                                {convert_hours_to_line(hours)} no centro {center.abbreviation}
                                no dia {day.date} de {donor.full_name}."""
        elif requester.id == donor.id:
            new_request.info=f"""{requester.full_name} solicitou DOAÇÃO dos horários:
                                {convert_hours_to_line(hours)} no centro {center.abbreviation}
                                no dia {day.date} (para {receiver.full_name})."""

        for hour in hours:
            app = Appointment.query.filter_by(
                day_id=day.id,
                user_id=donor.id,
                center_id=center.id,
                hour=hour,
                is_confirmed=True
            ).first()

            if not app:
                db.session.rollback()
                return f"Horário (ou parte dele) não foi encontrado"

            if app.has_open_requests:
                db.session.rollback()
                return f"Horário (ou parte dele) tem requisição pendente"
            
            new_request.appointments.append(app)
        
        db.session.commit()
        return new_request
    
    @classmethod
    def exchange(cls, doctor_1, center_1_id, day_1_id, hours_1,
                 doctor_2, center_2_id, day_2_id, hours_2, requester):
        
        new_request = cls(
            requester_id=doctor_1.id,
            receivers_code=str(doctor_2.id),
            action="exchange",
        )

        db.session.add(new_request)

        if requester.id == doctor_1.id:
            new_request.info = f"""{requester.full_name} solicitou TROCA dos horários:
                                {convert_hours_to_line(hours_1)} no centro {center_1_id}
                                no dia {day_1_id} com {doctor_2.full_name}."""
        elif requester.id == doctor_2.id:
            new_request.info = f"""{requester.full_name} solicitou TROCA dos horários:
                                {convert_hours_to_line(hours_2)} no centro {center_2_id}
                                no dia {day_2_id} com {doctor_1.full_name}."""
        
        for hour in hours_1:
            app = Appointment.query.filter_by(
                day_id=day_1_id,
                user_id=doctor_1.id,
                center_id=center_1_id,
                hour=hour,
                is_confirmed=True
            ).first()

            if not app:
                db.session.rollback()
                return f"Horário de {doctor_1.full_name} (ou parte dele) não foi encontrado"

            if app.has_open_requests:
                db.session.rollback()
                return f"Horário de {doctor_1.full_name} (ou parte dele) tem requisições pendentes"
            
            new_request.appointments.append(app)

        for hour in hours_2:
            app = Appointment.query.filter_by(
                day_id=day_2_id,
                user_id=doctor_2.id,
                center_id=center_2_id,
                hour=hour,
                is_confirmed=True
            ).first()

            if not app:
                db.session.rollback()
                return f"Horário de {doctor_2.full_name} (ou parte dele) não foi encontrado"

            if app.has_open_requests:
                db.session.rollback()
                return f"Horário de {doctor_2.full_name} (ou parte dele) tem requisições pendentes"
            
            new_request.appointments.append(app)
        
        db.session.commit()
        return new_request
    
    def delete(self):
        for app in self.appointments:
            if not app.is_confirmed:
                app.delete_entry()
            else:
                app.requests.remove(self)

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
        
        if self.action == "donate":
            for app in self.appointments:
                app.change_doctor(int(self.receivers_code))

            self.respond(responder_id=responder_id, response='authorized')
            return "Os horários foram doados com sucesso"

        if self.action == "exchange":
            # the requester is doctor_1, the one who initiated the exchange
            # the responder is doctor_2, the one who accepts the exchange
            for app in [app for app in self.appointments if app.user_id == self.requester_id]:
                app.change_doctor(int(self.receivers_code))

            for app in [app for app in self.appointments if app.user_id == int(self.receivers_code)]: 
                app.change_doctor(self.requester_id)
            
            self.respond(responder_id=responder_id, response='authorized')
            return "Os horários foram trocados com sucesso"

        return "ação não reconhecida"
        