from app import app
from app import mail
from flask_mail import Message
from flask import render_template
from threading import Semaphore


def sendMail(body):
    lock = Semaphore()
    with lock:
        with app.app_context():
            msg = Message('New Teleschocken Game', sender='lars@tele-schocken.de', recipients=['lars@tele-schocken.de'])
            msg.body = body
            mail.send(msg)
        return


def sendFeedbackMail(browser, body, email):
    lock = Semaphore()
    with lock:
        with app.app_context():
            msg = Message('Feedback Teleschocken', sender='lars@tele-schocken.de', recipients=['lars@tele-schocken.de'])
            msg.body = '{} /n {} {}'.format(browser, body, email)
            msg.html = render_template('mail.html', message=body, email=email, browser=browser)
            mail.send(msg)
        return