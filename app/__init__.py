from flask import Flask, redirect, url_for, flash, session
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app(config_filename=None):
    config_filename = config_filename or '../instance/config.py'

    app = Flask(__name__)
    
    app.config.from_pyfile(config_filename)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = app.config['SECRET_KEY']

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = 'login.login'
    login_manager.login_message_category = 'danger'
    login_manager.login_message = 'Você precisa estar logado para acessar esta página.'

    from app.routes.dashboard.dashboard import dashboard_bp
    from app.routes.dataview.dataview import dataview_bp
    from app.routes.calendar.calendar import calendar_bp
    from app.routes.admin.admin import admin_bp
    from app.routes.login.login import login_bp
    from app.routes.privilege.privilege import privilege_bp
    from app.routes.report.report import report_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(dataview_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(privilege_bp)
    app.register_blueprint(report_bp)

    @app.context_processor
    def inject_user():
        from flask_login import current_user
        user_name = current_user.abbreviated_name if current_user.is_authenticated else ''
        
        return dict(user_name=user_name)
    
    @app.before_request
    def check_for_maintenence():
        from flask_login import current_user
        from app.config import Config

        config = Config()
        MAINTENANCE_MODE = config.get('maintenance_mode')
        
        if MAINTENANCE_MODE and current_user.is_authenticated and not current_user.is_root:
            session.clear()
            flash("O Aplicativo está em manutenção e voltará a funcionar em algumas horas", "danger")
            return redirect(url_for('login.login'))

    return app

create_app()


# TODO: CSS
# TODO: fix aesthetics/simplify css and js

# TODO: Replace popup by modal
# TODO: CLEAN UP MODALS.JS

# TODO: change (example) mt4 to d4
# TODO: https - do nginx course

# TODO: fix lists for add/remove doctor to month
# TODO: add flash messages to doctor add to month

# TODO: move setting to settings file.


# FOR LATER

# TODO: fill reports
# TODO: add logic to user add a new center

# TODO: list of months in db (only show months with data in lists)

# TODO: add home button/return button to all pages



# POSSIBILITIES:
# TODO: ADD LOGS
# TODO: start using crm instead of id for users

# TODO: improve variables names on messages and requests
# add check for users id on requests

# TODO: reset password function
# TODO: change admin table interaction and clean up its js
