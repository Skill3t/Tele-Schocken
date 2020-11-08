from flask import Blueprint

bp = Blueprint('api', __name__)

from app.api import game_endpoints, admin_endpoints, errors, statistic
