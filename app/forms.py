from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class LoginForm(FlaskForm):
    crm_number = StringField('CRM', validators=[DataRequired(), Length(4, 8)])
    password = PasswordField('Senha', validators=[DataRequired(), Length(3, 20)])
    remember = BooleanField('Lembre-se de Mim')

    submit = SubmitField('Entrar')


class RegistrationForm(FlaskForm):
    first_name = StringField('Primeiro Nome', validators=[DataRequired(), Length(2, 15)])
    middle_name = StringField('Nome do Meio', validators=[Length(0, 15)])
    last_name = StringField('Sobrenome', validators=[DataRequired(), Length(2, 15)])
    cellphone = StringField('Celular', validators=[DataRequired(), Length(8, 16)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    crm_number = StringField('CRM', validators=[DataRequired(), Length(4, 8)])
    rqe_number = StringField('RQE', validators=[DataRequired()])

    password = PasswordField('Senha', validators=[DataRequired(), Length(3, 20)])
    confirm_password = PasswordField('Confirme a Senha', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Confirmar')
