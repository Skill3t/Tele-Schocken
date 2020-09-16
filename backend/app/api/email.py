from app import app
from app import mail
from flask_mail import Message


def sendMial(body):
    with app.app_context():
        msg = Message('New Teleschocken Game', sender='lars@tele-schocken.de', recipients=['lars@tele-schocken.de'])
        msg.body = body
        mail.send(msg)
    return
