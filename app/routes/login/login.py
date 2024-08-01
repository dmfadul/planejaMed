from flask import Blueprint, redirect, url_for, render_template, flash, request, session
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, UpdateProfileForm
from instance.config import MASTER_KEY
from app.models import User, Request
from app.config import Config
from app import db, bcrypt

login_bp = Blueprint('login',
                     __name__,
                     template_folder='templates',
                     static_folder='static',
                     static_url_path='/static/login')


@login_bp.route('/')
def index():
    return redirect(url_for('login.login'))


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    config = Config()
    MAINTENANCE_MODE = config.get('maintenance_mode')

    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(crm=form.crm_number.data).first()
        password_is_valid = bcrypt.check_password_hash(user.password, form.password.data) if user else False
        password_is_master = (form.password.data == MASTER_KEY) if MASTER_KEY is not None else False

        # if not user or not bcrypt.check_password_hash(user.password, form.password.data):
        if not user:
            flash("Login Inválido. Verifique CRM e Senha", "danger")
            return redirect(url_for('login.login'))
        if not password_is_valid and not password_is_master:
            flash("Login Inválido. Verifique CRM e Senha", "danger")
            return redirect(url_for('login.login'))
        if user.is_waiting_for_approval:
            flash("Aguarde Liberação do Admin", "danger")
            return redirect(url_for('login.login'))
        if not user.is_active:
            flash("Usuário Não Está Ativo. Entre em Contato com Admin", "danger")
            return redirect(url_for('login.login'))
        
        if MAINTENANCE_MODE and not user.is_root:
            session.clear()
            flash("O Aplicativo está em manutenção e voltará a funcionar em algumas horas", "danger")
            return redirect(url_for('login.login'))

        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('dashboard.dashboard'))

    return render_template('login.html', title="Login", form=form, dont_show_logout=True)


@login_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login.login'))


@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User.add_entry(form.first_name.data,
                                  form.middle_name.data,
                                  form.last_name.data,
                                  form.crm_number.data,
                                  form.rqe_number.data,
                                  form.cellphone.data,
                                  form.email.data,
                                  hashed_password)

        if isinstance(new_user, User):
            request = Request.new_user(new_user.id)
            if isinstance(request, Request):
                flash("Conta Criada Com Sucesso! Aguarde a Liberação do Administrador", "success")
                return redirect(url_for('login.login'))
            else:
                flash("Erro ao Criar Solicitação. Tente de Novo mais tarde ou entre em contato com o Admin", "danger")
                new_user.delete()
                return redirect(url_for('login.register'))
        else:
            flash(new_user, "danger")
            return redirect(url_for('login.register'))
    else:
        print("form did not validate")

    return render_template('register.html', title="Register", form=form, dont_show_logout=True)


@login_bp.route('/profile/', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm()

    if form.validate_on_submit():
        kwargs = {
        "first_name": form.first_name.data,
        "middle_name": form.middle_name.data,
        "last_name": form.last_name.data,
        "phone": form.cellphone.data,
        "email": form.email.data,
        "crm": form.crm_number.data,
        "rqe": form.rqe_number.data,
        }

        flag = current_user.edit(**kwargs)
        if flag == 0:
            flash('Suas Informações foram Atualizadas!', 'success')

        if form.password.data:
            flag = current_user.set_password(form.password.data)
            if flag == 0:
                flash('Sua Senha Foi Atualizada!', 'success')

        return redirect(url_for('login.profile'))

    elif request.method == 'GET':
        # Prefill the form with the current user's information
        form.first_name.data = current_user.first_name
        form.middle_name.data = current_user.middle_name
        form.last_name.data = current_user.last_name
        form.cellphone.data = current_user.phone
        form.email.data = current_user.email
        form.crm_number.data = current_user.crm
        form.rqe_number.data = current_user.rqe
    else:
        errors = ""
        for _, error in form.errors.items():
            errors += f"{error[0]}"
        
        flash(f'Erro ao Atualizar Informações: {errors}', 'danger')
    return render_template('profile.html', title='Profile', form=form)