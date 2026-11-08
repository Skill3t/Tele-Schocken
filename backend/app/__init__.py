import secrets

from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_bootstrap import Bootstrap
from flask_mail import Mail

app = Flask(__name__, static_folder='static', static_url_path='')
app.config.from_object(Config)
mail = Mail(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

from app import routes, models, errors
bootstrap = Bootstrap(app)


def csp_nonce():
    """Per-request nonce for the Content-Security-Policy, used in templates as {{ csp_nonce() }}."""
    if 'csp_nonce' not in g:
        g.csp_nonce = secrets.token_urlsafe(16)
    return g.csp_nonce


app.jinja_env.globals['csp_nonce'] = csp_nonce


@app.after_request
def set_csp_header(response):
    # only <script> tags carrying the nonce are executed, inline scripts and onclick handlers are blocked
    if response.mimetype == 'text/html':
        response.headers['Content-Security-Policy'] = (
            "script-src 'nonce-{}'; object-src 'none'; base-uri 'self'".format(csp_nonce()))
    return response



def create_app():
    app = Flask(__name__, static_folder='static')
    app.config.from_object(Config)
    mail = Mail(app)
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    from app import routes, models, errors
    bootstrap = Bootstrap(app)
    return app
