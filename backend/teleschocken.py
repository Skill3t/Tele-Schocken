"""
teleschocken.py
====================================
The core module of teleschocken project
"""
from app import app, db

from app.models import User, Game


'''
DB Update
flask db migrate -m "Your Text"
flask db upgrade
'''


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Game': Game}
