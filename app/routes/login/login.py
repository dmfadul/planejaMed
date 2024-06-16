from flask import Blueprint, redirect, url_for, render_template, flash, request
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import LoginForm, RegistrationForm, UpdateProfileForm
from app.models import User
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
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(crm=form.crm_number.data).first()
        # if not user or not bcrypt.check_password_hash(user.password, form.password.data):
        if not user or not user.password == form.password.data:
            flash("Login Inválido. Verifique CRM e Senha", "danger")
            return redirect(url_for('login.login'))
        if not user.is_active:
            flash("Usuário Não Está Ativo. Entre em Contato com Admin", "danger")
            return redirect(url_for('login.login'))
        if user.is_locked:
            flash("Aguarde Liberação do Admin", "danger")
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
        flag = User.add_entry(form.first_name.data,
                              form.middle_name.data,
                              form.last_name.data,
                              form.crm_number.data,
                              form.rqe_number.data,
                              form.cellphone.data,
                              form.email.data,
                              hashed_password)
        if flag == -1:
            flash("CRM já cadastrado", "danger")
            return redirect(url_for('login.register'))
        if flag == -2:
            flash("Nome já cadastrado", "danger")
            return redirect(url_for('login.register'))

        if flag.isinstance(User):
            flash("Conta Criada Com Sucesso!", "success")
            return redirect(url_for('login.login'))
    else:
        print("not ok")

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
        flash('Erro ao Atualizar Informações', 'danger')
    return render_template('profile.html', title='Profile', form=form)