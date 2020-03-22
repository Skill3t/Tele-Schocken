# from app import app, create_app, db
from app import app, db

from app.models import User, Game

'''
ADD USER
flask shell
u = User()
db.session.add(u)
db.session.commit()
'''

'''
DB Update
flask db migrate -m "Your Text"
flask db upgrade
'''


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Game': Game}
