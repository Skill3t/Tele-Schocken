from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_bootstrap import Bootstrap


app = Flask(__name__, static_folder='static')
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')


def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    return app
