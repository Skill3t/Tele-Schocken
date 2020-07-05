import atexit
from app import app, db

from apscheduler.schedulers.background import BackgroundScheduler
from app.models import Game, Statistic
from datetime import datetime
from dateutil.relativedelta import relativedelta


def schedulerdeletegame():
    todayDate = datetime.now()
    delta = relativedelta(days=-1)
    one_hour = todayDate + delta
    old_games = Game.query.filter(Game.refreshed <= one_hour).all() # noqa
    for old_game in old_games:
        # print('old_game.refreshed:{}'.format(old_game.refreshed))
        # print('delte: {}'.format(old_game))
        stat = Statistic()
        stat.usercount = len(old_game.users)
        stat.started = old_game.started
        stat.refreshed = old_game.refreshed
        stat.halfcount = old_game.halfcount
        stat.schockoutcount = old_game.schockoutcount
        stat.fallling_dice_count = old_game.fallling_dice_count
        stat.throw_dice_count = old_game.throw_dice_count
        db.session.add(stat)
        for user in old_game.users:
            db.session.delete(user)
        db.session.delete(old_game)
        db.session.commit()
    db.session.commit()


scheduler = BackgroundScheduler()
# 3.600 seconds are 1 houer
scheduler.add_job(func=schedulerdeletegame, trigger="interval", seconds=3.600)

scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())
