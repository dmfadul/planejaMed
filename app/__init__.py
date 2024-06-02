from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(config_filename=None):
    config_filename = config_filename or '../instance/config.py'

    app = Flask(__name__)
    
    app.config.from_pyfile(config_filename)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://david:741852@localhost/planejamed'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    from app.routes.dashboard.dashboard import dashboard_bp
    app.register_blueprint(dashboard_bp)

    return app

create_app()    