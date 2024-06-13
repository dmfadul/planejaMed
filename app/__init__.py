from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_filename=None):
    config_filename = config_filename or '../instance/config.py'

    app = Flask(__name__)
    
    app.config.from_pyfile(config_filename)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

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

    return app

create_app()    