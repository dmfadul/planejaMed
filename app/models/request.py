import re
from app import db
from sqlalchemy import ForeignKey, desc
from sqlalchemy.orm import relationship
from datetime import datetime
from .associations import request_appointment_association
from app.models.appointment import Appointment
from app.hours_conversion import convert_hours_to_line


class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    requester_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    receivers_code = db.Column(db.Text, nullable=False)
    # requestee_code = db.Column(db.Text, nullable=False)
    responder_id = db.Column(db.Integer, ForeignKey('users.id'))
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
        return self.message 
 
    @property
    def appointment_date(self):
        if self.action in ['include_user', 'approve_vacation']:
            return None
        
        if self.action == 'exchange':
            text = self.info.split("para")[0].strip()
        else:
            text = self.info
        
        date_pattern = r"\b\d{2}/\d{2}/\d{2}\b"
        date = re.search(date_pattern, text)

        if date:
            return datetime.strptime(date.group(), "%d/%m/%y")

        return None

    @property
    def appointment_date_two(self):
        if not self.action == 'exchange':
            return None
        
        second_part = self.info.split("para")[1].strip()
        date_pattern = r"\b\d{2}/\d{2}/\d{2}\b"
        date = re.search(date_pattern, second_part)

        if date:
            return datetime.strptime(date.group(), "%d/%m/%y")

        return None

    @property
    def appointment_center(self):
        if self.action in ['include_user', 'approve_vacation']:
            return None
        
        if self.action == 'exchange':
            text = self.info.split("para")[0].strip()
        else:
            text = self.info

        center = text.split("no centro")[1].strip()
        center = center.split("no dia")[0].strip()
        return center

    @property
    def appointment_center_two(self):
        if not self.action == 'exchange':
            return None
        
        second_part = self.info.split("para")[1].strip()
        center = second_part.split("no centro")[1].strip()
        center = center.split("no dia")[0].strip()

        return center

    @property
    def appointment_hour_range(self):
        from ..hours_conversion import gen_hour_range

        if self.action in ['include_user', 'approve_vacation']:
            return None
        
        if self.action == 'exchange':
            text = self.info.split("para")[0].strip()
        else:
            text = self.info

        hours = text.split("horários:")[1].strip()
        hours = hours.split("no")[0].strip()
        str_hour, end_hour = hours.split("-") 

        str_hour = str_hour.split(":")[0].strip()
        end_hour = end_hour.split(":")[0].strip()

        hour_range = gen_hour_range((int(str_hour), int(end_hour)-1))

        return hour_range

    @property
    def appointment_hour_range_two(self):
        from ..hours_conversion import gen_hour_range

        if not self.action == 'exchange':
            return None
        
        second_part = self.info.split("para")[1].strip()
        hours = second_part.split("no")[0].strip()

        str_hour, end_hour = hours.split("-") 

        str_hour = str_hour.split(":")[0].strip()
        end_hour = end_hour.split(":")[0].strip()

        hour_range = gen_hour_range((int(str_hour), int(end_hour)-1))


        return hour_range
    
    @property
    def message(self):
        try:
            unedit_message = self.info
            message = unedit_message.replace('*', "")
            message = message.replace('+', "")

        except Exception as e:
            message = f"""Uma requisição apresentou erro.
            Por favor, informe ao administrador o código r-{self.id},
            para que este erro seja corrijido."""

        return message

    @property
    def receivers(self):
        from app.models.user import User

        user_ids = [user.id for user in User.query.all() if user.is_sudo]

        if self.receivers_code == "*":
        # if self.requestee_code == "*":
            user_ids += [user.id for user in User.query.all() if user.is_admin]
        else:
            user_ids += [user.id for user in User.query.all() if user.id == int(self.receivers_code)]
            # user_ids += [user.id for user in User.query.all() if user.id == int(self.requestee_code)]

        return user_ids

    def signal(self, requester_crm):
        if self.action in ['include_user', 'approve_vacation']:
            return None
    
        if self.action == 'include_appointments':
            return 1
        
        if self.action == 'exclude_appointments':
            return -1

        if self.action == 'donate':
            if self.requester.crm == requester_crm and "DE" in self.info:
                return 1
            if not self.requester.crm == requester_crm and "PARA" in self.info:
                return 1
            if self.requester.crm == requester_crm and "PARA" in self.info:
                return -1
            if not self.requester.crm == requester_crm and "DE" in self.info:
                return -1
        
        if self.action == 'exchange':
            return 0        

    @property
    def working_month(self):
        from app.global_vars import STR_DAY

        if not 31 >= self.appointment_date.day >= STR_DAY:
            return self.appointment_date.month

        if self.appointment_date.month == 12:
            return 1
        
        return self.appointment_date.month + 1

    @property
    def working_year(self):
        from app.global_vars import STR_DAY

        if not 31 >= self.appointment_date.day >= STR_DAY:
            return self.appointment_date.year
        
        if self.appointment_date.month == 12:
            return self.appointment_date.year + 1
        
        return self.appointment_date.year

    @classmethod
    def new_user(cls, doctor_to_include_id):
        new_request = cls(
            requester_id=doctor_to_include_id,
            receivers_code="*",
            # requestee_code="*",
            action="include_user",
        )

        db.session.add(new_request)
        db.session.commit()

        new_request.info=f"""O Médico {new_request.requester.full_name} solicitou inclusão no sistema."""
        
        db.session.commit()

        return new_request
    
    @classmethod
    def vacation(cls, doctor, start_date, end_date, is_sick_leave=False):
        new_request = cls(
            requester_id=doctor.id,
            receivers_code="*",
            # requestee_code="*",
            action="approve_vacation",
        )

        db.session.add(new_request)
        db.session.commit()

        privilege_type = "licença médica" if is_sick_leave else "férias"
        new_request.info=f"""*{doctor.full_name}* +solicitou+ {privilege_type} de
                            {start_date.strftime("%d/%m/%y")} a {end_date.strftime("%d/%m/%y")}"""
        
        db.session.commit()

        return new_request


    @classmethod
    def exclusion(cls, doctor, center, day, hours, requester):
        new_request = cls(
            requester_id=requester.id,
            receivers_code="*",
            # requestee_code="*",
            action="exclude_appointments",
            info = ""
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

            if app.has_open_requests:
                db.session.rollback()
                return f"Horário (ou parte dele) tem requisição pendente"
            
            new_request.appointments.append(app)
        
        db.session.commit()

        if requester.id == doctor.id:
            new_request.info = f"""*{doctor.full_name}* +solicitou+ EXCLUSÃO dos horários:
                               {convert_hours_to_line(hours)} no centro {center.abbreviation}
                               no dia {day.date.strftime("%d/%m/%y")}"""
        else:
            new_request.info = f"""*{requester.full_name}* +solicitou+ EXCLUSÃO para {doctor.full_name}
                               nos horários:{convert_hours_to_line(hours)} no centro {center.abbreviation}
                               no dia {day.date.strftime("%d/%m/%y")}"""
        return new_request

    @classmethod
    def inclusion(cls, doctor, center, day, hours, requester):
        new_request = cls(
            requester_id=requester.id,
            receivers_code="*",
            # requestee_code="*",
            action="include_appointments",
            info=""
        )

        db.session.add(new_request)

        for hour in hours:
            app = Appointment.query.filter_by(
                day_id=day.id,
                user_id=doctor.id,
                hour=hour
            ).first()

            if app is None:
                continue
            
            if app.is_confirmed:
                db.session.rollback()
                return f"""Conflito - {doctor.full_name} já tem esse horário
                        (ou parte dele) no centro {app.center.abbreviation}"""
            
            if app.has_open_requests:
                db.session.rollback()
                return f"""O Médico {doctor.full_name} já tem
                            Requisição Pendente para o Horário Requisitado ou para Parte dele."""
        
            if not app.is_confirmed:
                db.session.rollback()
                return f"""Conflito - Já há Requisição pendente para {doctor.full_name}
                            em {center.abbreviation} no dia {day.date}
                            para o horário pedido (ou parte dele)."""
        
        for hour in hours:
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

        db.session.commit()

        if requester.id == doctor.id:
            new_request.info = f"""*{doctor.full_name}* +solicitou+ INCLUSÃO dos horários:
                               {convert_hours_to_line(hours)} no centro {center.abbreviation}
                               no dia {day.date.strftime("%d/%m/%y")}"""
        else:
            new_request.info = f"""*{requester.full_name}* +solicitou+ INCLUSÃO para {doctor.full_name}
                               nos horários:{convert_hours_to_line(hours)} no centro {center.abbreviation}
                               no dia {day.date.strftime("%d/%m/%y")}"""
        return new_request
    
    @classmethod
    def donation(cls, donor, donee, center, day, hours, requester):
        if requester.id == donor.id:
            # hours go from current_user to other_users
            receiver_code = str(donee.id)
            # requestee_code = str(donee.id)
        else:
            # hours go from other_users to current_user
            receiver_code = str(donor.id)
            # requestee_code = str(donor.id)

        new_request = cls(
            requester_id=requester.id,
            receivers_code=receiver_code,
            # requestee_code=requestee_code,
            action="donate"
        )

        db.session.add(new_request)

        if requester.id == donee.id:
            new_request.info=f"""*{requester.full_name}* +solicitou+ DOAÇÃO dos horários:
                                {convert_hours_to_line(hours)} no centro {center.abbreviation}
                                no dia {day.date.strftime("%d/%m/%y")} (DE {donor.full_name})"""
        elif requester.id == donor.id:
            new_request.info=f"""*{requester.full_name}* +solicitou+ DOAÇÃO dos horários:
                                {convert_hours_to_line(hours)} no centro {center.abbreviation}
                                no dia {day.date.strftime("%d/%m/%y")} (PARA {donee.full_name})"""

        for hour in hours:
            app_donor = Appointment.query.filter_by(
                day_id=day.id,
                user_id=donor.id,
                center_id=center.id,
                hour=hour,
                is_confirmed=True
            ).first()

            if not app_donor:
                db.session.rollback()
                return f"Horário de {donor.full_name} (ou parte dele) não foi encontrado"

            if app_donor.has_open_requests:
                db.session.rollback()
                return f"Horário de {donor.full_name} (ou parte dele) tem requisições pendentes"
            
            app_donee = Appointment.query.filter_by(
                day_id=day.id,
                user_id=donee.id,
                hour=hour,
                is_confirmed=True
            ).first()
            
            if app_donee:
                db.session.rollback()
                return f"""Horário de {donee.full_name} (ou parte dele) já está ocupado
                        no centro {app_donee.center.abbreviation}."""

            new_request.appointments.append(app_donor)
        
        db.session.commit()
        return new_request
    
    @classmethod
    def exchange(cls, doctor_1, center_1, day_1, hours_1,
                 doctor_2, center_2, day_2, hours_2, requester):
                
        if len(hours_1) != len(hours_2):
            return "Conflito - Horários de tamanhos diferentes"
        
        new_request = cls(
            requester_id=doctor_1.id,
            receivers_code=str(doctor_2.id),
            # requestee_code=str(doctor_2.id),
            action="exchange",
        )

        db.session.add(new_request)

        if requester.id == doctor_1.id:
            new_request.info = f"""*{requester.full_name}* +solicitou+ TROCA dos horários:
                                {convert_hours_to_line(hours_1)} no centro {center_1.abbreviation}
                                no dia {day_1.date.strftime("%d/%m/%y")} para
                                {convert_hours_to_line(hours_2)} no centro {center_2.abbreviation}
                                no dia {day_2.date.strftime("%d/%m/%y")} com {doctor_2.full_name}"""
        elif requester.id == doctor_2.id:
            new_request.info = f"""*{requester.full_name}* +solicitou+ TROCA dos horários:
                                {convert_hours_to_line(hours_2)} no centro {center_2.abbreviation}
                                no dia {day_2.date.strftime("%d/%m/%y")} para
                                {convert_hours_to_line(hours_1)} no centro {center_1.abbreviation}
                                no dia {day_1.date.strftime("%d/%m/%y")} com {doctor_1.full_name}"""
        
        for i in range(len(hours_1)):
            out_app_doc_1 = Appointment.query.filter_by(
                day_id=day_1.id,
                user_id=doctor_1.id,
                center_id=center_1.id,
                hour=hours_1[i],
                is_confirmed=True
            ).first()

            if not out_app_doc_1:
                db.session.rollback()
                return f"Horário de {doctor_1.full_name} (ou parte dele) não foi encontrado"

            if out_app_doc_1.has_open_requests:
                db.session.rollback()
                return f"Horário de {doctor_1.full_name} (ou parte dele) tem requisições pendentes"

            out_app_doc_2 = Appointment.query.filter_by(
                day_id=day_2.id,
                user_id=doctor_2.id,
                hour=hours_2[i],
                is_confirmed=True
            ).first()

            if not out_app_doc_2:
                db.session.rollback()
                return f"Horário de {doctor_2.full_name} (ou parte dele) não foi encontrado"

            if out_app_doc_2.has_open_requests:
                db.session.rollback()
                return f"Horário de {doctor_2.full_name} (ou parte dele) tem requisições pendentes"
            
            in_app_doc_1 = Appointment.query.filter_by(
                day_id=day_2.id,
                user_id=doctor_1.id,
                hour=hours_2[i],
                is_confirmed=True
            ).first()

            if in_app_doc_1 and not in_app_doc_1 == out_app_doc_1:
                db.session.rollback()             
                return f"""Conflito - {doctor_1.full_name} já tem esse horário
                        (ou parte dele) no centro {in_app_doc_1.center.abbreviation}"""
            
            in_app_doc_2 = Appointment.query.filter_by(
                day_id=day_1.id,
                user_id=doctor_2.id,
                hour=hours_1[i],
                is_confirmed=True
            ).first()

            if in_app_doc_2 and not in_app_doc_2 == out_app_doc_2:
                db.session.rollback()
                return f"""Conflito - {doctor_2.full_name} já tem esse horário
                        (ou parte dele) no centro {in_app_doc_2.center.abbreviation}"""

            new_request.appointments.append(out_app_doc_1)         
            new_request.appointments.append(out_app_doc_2)
        
        db.session.commit()
        return new_request
    
    def delete(self):
        for app in self.appointments:
            if not app.is_confirmed:
                app.delete_entry(del_requests=False)
            else:
                app.requests.remove(self)

        for message in self.messages:
            message.delete()

        db.session.delete(self)
        db.session.commit()

    @classmethod
    def filter_by_user(cls, user_id):
        return [req for req in cls.query.filter_by(is_open=True).all() if user_id in req.receivers]

    @classmethod
    def report(cls):
        from app.models.user import User
        requests = cls.query.order_by(desc(cls.id)).all()

        output = []
        for req in requests:
            output.append({
                "id": req.id,
                "requester": req.requester.full_name,
                "receivers": [User.query.get(user_id).full_name for user_id in req.receivers],
                "action": req.action,
                "creation_date": req.creation_date,
                "is_open": req.is_open,
                "response_date": req.response_date,
                "response": req.response,
                "info": req.info
            })

        return output

    def add_appointment(self, appointment):
        self.appointments.append(appointment)
        db.session.commit()

    def respond(self, responder_id, response, send_confirmation=True):
        from app.models.message import Message
        for message in self.messages:
            message.delete()
            
        self.responder_id = responder_id
        self.response = response
        self.response_date = datetime.now()
        self.is_open = False

        db.session.commit()
        if send_confirmation:
            Message.new_confirmation_message(
                sender_id=responder_id,
                request_id=self.id,
                receivers_code=str(self.requester_id),
                # requestee_code=str(self.requester_id),
                )
        return 0

    # def close(self, closer_id, response):           
    #     self.responder_id = closer_id
    #     self.response = response
    #     self.response_date = datetime.now()
    #     self.is_open = False

    #     db.session.commit()
    #     return 0
    
    def resolve(self, responder_id, authorized, send_confirmation=True):
        from app.models import User

        if not authorized:
            for app in self.appointments:
                if not app.is_confirmed:
                    app.delete_entry(del_requests=False)

            if self.action == 'approve_vacation':
                denied_vacation = self.requester.vacations[-1]
                denied_vacation.deny()

            self.respond(responder_id=responder_id, response="denied")
            return "A solicitação foi Negada", 'success'
        
        if self.action == 'include_user':
            new_user = User.query.get(self.requester_id)
            new_user.activate()
            new_user.make_visible()

            self.respond(responder_id=responder_id, response='authorized')
            return f"O usuário {new_user.full_name} foi incluído com sucesso", 'success'

        if self.action == 'approve_vacation':
            vacations = [v for v in self.requester.vacations if v.status == 'pending_approval']
            vacations = [v for v in vacations if v.start_date.strftime("%d/%m/%y") in self.message]
            
            if not len(vacations) == 1:
                return "Erro ao localizar Férias.", 'danger'

            vacation = vacations[0]
            vacation.approve()

            self.respond(responder_id=responder_id, response='authorized')
            return "Férias aprovadas", 'success'

        if self.action == "include_appointments":
            for app in self.appointments:
                app.confirm()

            self.respond(responder_id=responder_id,
                         response='authorized',
                         send_confirmation=send_confirmation)

            return "Os horários foram incluídos com sucesso", 'success'
        
        if self.action == "exclude_appointments":
            for app in self.appointments:   
                app.delete_entry(del_requests=False)

            self.respond(responder_id=responder_id,
                         response='authorized',
                         send_confirmation=send_confirmation)
                         
            return "Os horários foram excluídos com sucesso", 'success'
        
        if self.action == "donate":
            
            for app in self.appointments:
                if app.user_id == self.requester_id:
                    doctor_that_receives = int(self.receivers_code)
                else:
                    doctor_that_receives = self.requester_id

                test_app = Appointment.query.filter_by(
                    user_id=doctor_that_receives,
                    day_id=app.day_id,
                    hour=app.hour,
                    is_confirmed=True
                ).first()

                if test_app:
                    self.delete()
                    return f"""Conflito - {User.query.get(doctor_that_receives).full_name} já tem esse horário
                            (ou parte dele) no centro {test_app.center.abbreviation}""", 'danger'

            for app in self.appointments:
                if app.user_id == self.requester_id:
                    app.change_doctor(int(self.receivers_code))
                    # app.change_doctor(int(self.requestee_code))
                else:
                    app.change_doctor(self.requester_id)

            self.respond(responder_id=responder_id, response='authorized')
            return "Os horários foram doados com sucesso", 'success'

        if self.action == "exchange":
            # the requester is doctor_1, the one who initiated the exchange
            # the responder is doctor_2, the one who accepts the exchange

            for app in self.appointments:
                if app.user_id == self.requester_id:
                    test_app = Appointment.query.filter_by(
                        user_id=int(self.receivers_code),
                        day_id=app.day_id,
                        hour=app.hour,
                        is_confirmed=True
                    ).first()

                    test_user = User.query.filter_by(id=int(self.receivers_code)).first()
                else:
                    test_app = Appointment.query.filter_by(
                        user_id=self.requester_id,
                        day_id=app.day_id,
                        hour=app.hour,
                        is_confirmed=True
                    ).first()
                    test_user = User.query.filter_by(id=self.requester_id).first()

                if test_app:
                    self.delete()
                    return f"""Conflito - {test_user.full_name} já tem esse horário (ou parte dele)
                             no centro {test_app.center.abbreviation}""", 'danger'

            for app in self.appointments:
                if app.user_id == self.requester_id:
                    app.change_doctor(int(self.receivers_code))
                    # app.change_doctor(int(self.requestee_code))
                elif app.user_id == int(self.receivers_code): 
                # elif app.user_id == int(self.requestee_code): 
                    app.change_doctor(self.requester_id)
                else:
                    db.session.rollback()
                    return "Erro ao trocar horários", 'danger'
            
            self.respond(responder_id=responder_id, response='authorized')
            return "Os horários foram trocados com sucesso", 'success'

        return "ação não reconhecida", 'danger'
        