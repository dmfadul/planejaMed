from flask import Blueprint
from app.forms import LoginForm, RegistrationForm


login_bp = Blueprint('login',
                     __name__,
                     template_folder='templates',
                     static_folder='static',
                     static_url_path='/static/login')


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    return 'Login page'