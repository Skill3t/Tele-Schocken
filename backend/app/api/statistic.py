from app import app, db
from app.models import Game, Statistic
from datetime import datetime
from dateutil.relativedelta import relativedelta


# Runs every 24 hours via APScheduler (app/scheduler.py), needs an app context
def create_statistics():
    todayDate = datetime.now()
    delta = relativedelta(days=-1)
    one_day = todayDate + delta
    print('Schedular runs')
    try:
        old_games = db.session.query(Game).filter(Game.refreshed <= one_day).with_for_update().all()
        if len(old_games) > 0:
            for old_game in old_games:
                stat = Statistic()
                stat.usercount = len(old_game.users)
                stat.started = old_game.started
                stat.refreshed = old_game.refreshed
                stat.halfcount = old_game.halfcount
                stat.schockoutcount = old_game.schockoutcount
                stat.fallling_dice_count = old_game.fallling_dice_count
                stat.changs_of_fallling_dice = old_game.changs_of_fallling_dice
                stat.throw_dice_count = old_game.throw_dice_count
                stat.stack_max = old_game.stack_max
                stat.play_final = old_game.play_final
                stat.finalcount = old_game.finalcount
                db.session.add(stat)
                for user in old_game.users:
                    db.session.delete(user)
                db.session.delete(old_game)
                db.session.commit()
    finally:
        db.session.commit()


# Manual run: flask create-statistics
@app.cli.command("create-statistics")
def create_statistics_command():
    create_statistics()
