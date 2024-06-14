from flask import Flask
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
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(dataview_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(login_bp)

    # @app.context_processor
    # def inject_user():
    #     from flask_login import current_user
    #     user_first_name = current_user.first_name if current_user.is_authenticated else None

    #     if user_first_name is None:
    #         return dict(user_name='')
        
    #     user_middle_name = current_user.middle_name
    #     user_last_name = current_user.last_name
    #     user_name = f"{user_first_name} {user_middle_name} {user_last_name}"
    #     user_name = user_name.strip().replace("  ", " ")

    #     return dict(user_name=user_name)

    return app

create_app()    