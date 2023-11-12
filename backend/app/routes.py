from flask import render_template, redirect, url_for

from app import app, db
from app.forms import CreateGameFrom
from app.models import Game


@app.route('/index2')
def index2():
    return render_template('index2.html')


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
    return render_template('game.html', title='Spiel', game=game)


@app.route('/game/<gid>', methods=['GET', 'POST'])
def game_play(gid):
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        return render_template('404.html')
    return render_template('gameplay.html', title='Spiel', game=game)
