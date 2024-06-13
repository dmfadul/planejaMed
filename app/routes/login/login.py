from flask import Blueprint, redirect, url_for, render_template
from app.forms import LoginForm, RegistrationForm


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