from app import app
from app import mail
from flask_mail import Message


def sendMail(body):
    with app.app_context():
        msg = Message('New Teleschocken Game', sender='lars@tele-schocken.de', recipients=['lars@tele-schocken.de'])
        msg.body = body
        mail.send(msg)
    return


def sendFeedbackMail(browser, body, email):
    with app.app_context():
        msg = Message('Feedback Teleschocken', sender='lars@tele-schocken.de', recipients=['lars@tele-schocken.de'])
        msg.body = '{} /n {} {}'.format(browser, body, email)
        mail.send(msg)
    return
