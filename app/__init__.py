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
    from app.routes.report.report import report_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(dataview_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(report_bp)

    @app.context_processor
    def inject_user():
        from flask_login import current_user
        user_name = current_user.full_name if current_user.is_authenticated else ''
        
        return dict(user_name=user_name)

    return app

create_app()


# TODO: FINISH ADMIN FUNCTIONS
# TODO: list of months in db
# TODO: Create exclude user function
# TODO: add logic to user add a new center

# TODO: ADD REQUESTS
# TODO: !!stop doctor from offering same hour to two people

# TODO: Include: delete holidays
# TODO: add replies to answered requests
# TODO: change admin table interaction
# TODO: add an actual settings file.
# TODO: Replace popup by modal

# TODO: FOR LATER
# TODO: add home button
# TODO: use profile name to gen abbreviated names (recreate user table)/finish reports
# TODO: fix aesthetics/simplify css and js
# TODO: add visible password button




