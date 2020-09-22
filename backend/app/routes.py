from flask import render_template, redirect, url_for

from app import app, db
from app.forms import CreateGameFrom, FeedbackFrom
from app.models import Game
from app.api.email import sendFeedbackMail


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = CreateGameFrom()
    if form.validate_on_submit():
        game = Game()
        db.session.add(game)
        db.session.commit()
        next_page = url_for('game')
        next_page = url_for('game', variable=game.UUID)
        return redirect(next_page)
    return render_template('index.html', title='Home', form=form)


@app.route('/game_waiting/<gid>', methods=['GET'])
def game(gid):
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        return render_template('404.html')
    return render_template('game.html', title='Edit Profile', game=game)


@app.route('/game/<gid>', methods=['GET', 'POST'])
def game_play(gid):
    game = Game.query.filter_by(UUID=gid).first()
    form = FeedbackFrom()
    if form.validate_on_submit():
        browser = str(form.browser.data)
        body = str(form.message.data)
        email = str(form.mail.data)
        sendFeedbackMail(browser=browser, body=body, email=email)
        return redirect(url_for('game_play', gid=game.UUID))
    return render_template('gameplay.html', title='Edit Profile', game=game, form=form)
