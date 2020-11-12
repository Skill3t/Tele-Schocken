from app import app
from app import mail
from app.models import Game
from app import db

from flask_mail import Message
from flask import render_template
from multiprocessing import Lock
# from sqlalchemy import is_


lock2 = Lock()


@app.cli.command("send_new_game_mail")
def sendMail():
    try:
        not_notified_games = db.session.query(Game).filter(Game.is_mail_send.is_(False)).with_for_update().all()
        if len(not_notified_games) > 0:
            for game in not_notified_games:
                with app.app_context():
                    msg = Message('New Teleschocken Game', sender='lars@tele-schocken.de', recipients=['lars@tele-schocken.de'])
                    msg.body = "New Game Created"
                    mail.send(msg)
                game.is_mail_send = True
                db.session.add(game)
                db.session.commit()
    finally:
        db.session.commit()
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
    finally:
        lock2.release()
        return
