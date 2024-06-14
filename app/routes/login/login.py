from flask import Blueprint, redirect, url_for, render_template, flash
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app import db, bcrypt

login_bp = Blueprint('login',
                     __name__,
                     template_folder='templates',
                     static_folder='static',
                     static_url_path='/static/login')


@login_bp.route('/')
def index():
    return redirect(url_for('dashboard.dashboard'))


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    return 'Login page'


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
