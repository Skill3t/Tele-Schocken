from app import app
from app import mail
from flask_mail import Message
from flask import render_template
from multiprocessing import Lock


lock = Lock()
lock2 = Lock()


def sendMail(body):
    send = False
    try:
        lock.acquire()
        if not send:
            # critical section
            with app.app_context():
                msg = Message('New Teleschocken Game', sender='lars@tele-schocken.de', recipients=['lars@tele-schocken.de'])
                msg.body = body
                mail.send(msg)
    except:
        print("An exception occurred")
    finally:
        send = True
        lock.release()
        return


def sendFeedbackMail(browser, body, email):
    try:
        lock2.acquire()
        # critical section
        with app.app_context():
            msg = Message('Feedback Teleschocken', sender='lars@tele-schocken.de', recipients=['lars@tele-schocken.de'])
            msg.body = '{} /n {} {}'.format(browser, body, email)
            msg.html = render_template('mail.html', message=body, email=email, browser=browser)
            mail.send(msg)
    except:
        print("An exception occurred")
    finally:
        lock2.release()
        return
