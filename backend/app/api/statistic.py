from app import app, db
import sys
from app.models import Game, Statistic
from datetime import datetime
from dateutil.relativedelta import relativedelta


@app.cli.command("create-statistics")
def statistic():
    todayDate = datetime.now()
    delta = relativedelta(days=-1)
    one_day = todayDate + delta
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
                db.session.add(stat)
                for user in old_game.users:
                    db.session.delete(user)
                db.session.delete(old_game)
                db.session.commit()
    except:
        print("Unexpected error:{}".format(sys.exc_info()[0]))
    finally:
        db.session.commit()
