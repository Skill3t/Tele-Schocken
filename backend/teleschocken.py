"""
teleschocken.py
====================================
The core module of teleschocken project

Local development server (gevent + Socket.IO, like production)::

    python teleschocken.py

``flask run`` does not work: its threaded dev server can not serve the
gevent based Socket.IO connection, so the game never starts.
"""
if __name__ == '__main__':
    # must happen before anything else is imported
    from gevent import monkey
    monkey.patch_all()

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


if __name__ == '__main__':
    import os
    from app.api.game_endpoints import socketio
    from app.scheduler import start_scheduler

    start_scheduler()
    port = int(os.environ.get('PORT', 8000))
    print('Tele-Schocken running on http://127.0.0.1:{}'.format(port), flush=True)
    socketio.run(app, host='127.0.0.1', port=port)
