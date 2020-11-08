from app.api import bp
from app import db

from flask import jsonify
from flask import request
from app.models import User, Game, Status
from random import randint, random
import time
from datetime import datetime
from jinja2 import utils

from app.api.errors import bad_request


# testforpolling
# the roud is not used is can be used to improve server performance if needed
@bp.route('/game/<gid>/poll', methods=['GET'])
def get_refreshed_game(gid):
    game = Game.query.filter_by(UUID=gid).first()
    old_game = game.to_dict()
    # db.session.expire_all()
    if game is None:
        response = jsonify(Message='Game id not in Database')
        response.status_code = 404
        return response
    # Check if the Game os not modified
    modified = False
    counter = 0
    while counter < 20:
        counter = counter + 1
        db.session.commit()
        game2 = Game.query.filter_by(UUID=gid).first()
        new_game = game2.to_dict()
        modified = not sorted(old_game.items()) == sorted(new_game.items())
        time.sleep(0.5)
        if modified:
            response = jsonify(game.to_dict())
            response.status_code = 200
            return response
    response = jsonify(Message='Game data not changed')
    response.status_code = 200
    return response

# get Game Data
@bp.route('/game/<gid>', methods=['GET'])
def get_game(gid):
    """**GET   /api/game/<gid>**

    Return a hole game as json

    :reqheader Accept: application/json
    :statuscode 200: Game Data
    :statuscode 404: Game id not in Database

    Parameters
    ----------
    gid : 'Integer'
        A Game UUID

    Examples
    --------
    .. sourcecode:: http

         HTTP/1.1 200 OK
         Content-Type: text/json

            {
               "Stack":10,
               "State":"String",
               "Game_Half_Count":0,
               "Move":"Userid",
               "Message":"Hallo",
               "First":"Userid",
               "Admin":"Userid",
               "Users":[
                  {
                     "id":11,
                     "Name":"Hans",
                     "Chips":2,
                     "passive":false,
                     "Halfcount":0,
                     "Number_Dice":0,
                  },
                  {
                     "id":11,
                     "Name":"Hans",
                     "Chips":2,
                     "passive":false,
                     "Halfcount":0,
                     "Number_Dice":0,
                     "Dices":[
                        {
                           "Dice1":2
                        },
                        {
                           "Dice2":6
                        },
                        {
                           "Dice3":6
                        }
                     ]
                  }
               ]
            }

    .. sourcecode:: http

      HTTP/1.1 404
      Content-Type: text/json
          {
            "Message": "Game id not in Database"
          }
    """
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify(Message='Game id not in Database')
        response.status_code = 404
        return response
    response = jsonify(game.to_dict())
    response.status_code = 200
    return response





# set User to Game
@bp.route('/game/<gid>/user', methods=['POST'])
def set_game_user(gid):
    """Add a User to a game with the STATUS WAITING

    Parameters
    ----------
    gid : 'int'
        A Game UUID
    name : 'str'
        Username

    Examples
    --------

    .. code-block:: json

        {"name": "jimbo10"}

    Examples
    --------
    .. sourcecode:: http

         HTTP/1.1 200 OK
         Content-Type: text/json

            {
               "Stack":10,
               "State":"String",
               "First_Halfe":true,
               "Move":"Userid",
               "First":"Userid",
               "Admin":"Userid",
               "Users":[
                  {
                     "id":11,
                     "Name":"Hans",
                     "Chips":2,
                     "passive":false,
                     "visible":false
                  },
                  {
                     "id":11,
                     "Name":"Hans",
                     "Chips":2,
                     "passive":false,
                     "visible":true,
                     "Dices":[
                        {
                           "Dice1":2
                        },
                        {
                           "Dice2":6
                        },
                        {
                           "Dice3":6
                        }
                     ]
                  }
               ]
            }

    .. sourcecode:: http

      HTTP/1.1 400
      Content-Type: text/json
          {
            "Status": "Game already Startet create new Game",
          }

    """
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify()
        response.status_code = 404
        return response
    if game.status != Status.WAITING:
        response = jsonify(Message='Game already started create new Game')
        response.status_code = 400
        return response
    data = request.get_json() or {}
    if 'name' not in data:
        return bad_request('must include name field')
    escapedusername = str(utils.escape(data['name']))
    inuse = User.query.filter_by(name=escapedusername).first()
    if inuse is not None:
        response = jsonify(Message='username in use!')
        response.status_code = 400
        return response
    user = User()
    user.name = escapedusername
    game.users.append(user)
    db.session.add(game)
    db.session.commit()
    return jsonify(game.to_dict())


# pull up the dice cup
@bp.route('game/<gid>/user/<uid>/visible', methods=['POST'])
def pull_up_dice_cup(gid, uid):
    """
    Pull the Dice cup up so that every user can see the dice's

    Parameters
    ----------
    gid : 'int'
        A Game UUID
    uid : 'int'
        A User ID
    value : 'bool'
        True = Visible False = invisible. So change the visibility of your dices
    Examples
    --------
    .. code-block:: json

        {
            "value": true
        }

    Examples
    --------
    .. sourcecode:: http

        HTTP/1.1 400
        Content-Type: text/json
            {
                "Message": "Request must include visible",
            }

    .. sourcecode:: http

        HTTP/1.1 201
        Content-Type: text/json
            {
                "Message": "suscess",
            }
    """
    game = Game.query.filter_by(UUID=gid).first()
    user = User.query.get_or_404(uid)
    if game is None:
        response = jsonify(Message='Game not found')
        response.status_code = 404
        return response
    data = request.get_json() or {}
    if 'visible' in data:
        escapedvisible = str(utils.escape(data['visible']))
        val = escapedvisible.lower() in ['true', '1']
        user.dice1_visible = val
        user.dice2_visible = val
        user.dice3_visible = val
        db.session.add(user)
        db.session.commit()
        allvisible = True
        for user in game.users:
            if not (user.dice1_visible and user.dice2_visible and user.dice3_visible):
                allvisible = False
        if allvisible:
            game.message = "Warten auf Vergabe der Chips!"
            db.session.add(game)
            db.session.commit()
        response = jsonify(Message='suscess')
        response.status_code = 201
        return response
    else:
        response = jsonify(Message="Request must include visible")
        response.status_code = 400
        return response


# user finisch bevor 3 rolls
@bp.route('/game/<gid>/user/<uid>/finisch', methods=['POST'])
def finish_throwing(gid, uid):
    game = Game.query.filter_by(UUID=gid).first()
    user = User.query.get_or_404(uid)
    if game is None:
        response = jsonify(Message='Game not found')
        response.status_code = 404
        return response
    if user.game_id != game.id:
        response = jsonify(Message='Player not in Game')
        response.status_code = 404
        return response
    # no chips on the stack but user has chips so you need to dice onece
    if game.stack == 0 and user.chips != 0 and user.number_dice == 0:
        response = jsonify(Message='Dice at least once')
        response.status_code = 400
        return response
    # chips on the stack need to dice onece
    if game.stack != 0 and user.number_dice == 0:
        response = jsonify(Message='Dice at least once')
        response.status_code = 400
        return response
    if user.dice1 is None or user.dice2 is None or user.dice3 is None:
        response = jsonify(Message='Dice again after turning 6er')
        response.status_code = 400
        return response
    waitinguser = User.query.get_or_404(game.move_user_id)
    if waitinguser.id == user.id:
        # https://stackoverflow.com/questions/364621/how-to-get-items-position-in-a-list
        aktualuserid = [i for i, x in enumerate(game.users) if x == user]
        if len(game.users) > aktualuserid[0]+1:
            game.move_user_id = game.users[aktualuserid[0]+1].id
        else:
            game.move_user_id = game.users[0].id
        next_user = User.query.get_or_404(game.move_user_id)
        if next_user.number_dice != 0:
            game.message = "Aufdecken!"
        db.session.add(game)
        db.session.commit()
        response = jsonify(Message='suscess')
        response.status_code = 200
        return response
    else:
        response = jsonify(Message='Its not your turn')
        response.status_code = 400
        return response
    response = jsonify(Message='Error')
    response.status_code = 400
    return response


# roll dice
@bp.route('/game/<gid>/user/<uid>/dice', methods=['POST'])
def roll_dice(gid, uid):
    """A user can roll up to 3 dice. dice1, dice2, dice3 are optional attributes depending on witch one you will roll again

    Parameters
    ----------
    gid : 'int'
        A Game UUID
    uid : 'int'
        A User ID
    dice1 : 'bool', optional
        Roll dice 1 again
    dice2 : 'bool', optional
        Roll dice 2 again
    dice3 : 'bool', optional
        Roll dice 3 again

    Examples
    --------

    .. code-block:: json

        {
            "dice1" : 2,
            "dice2" : 3,
            "dice3" : 6,
        }

    Returns
    -------
    fallen : 'bool'
        one dice is rollen from the table (shot round)
    dice1 : 'int'
        value of the first dice
    dice2 : 'int'
        value of the second dice
    dice3 : 'int'
        value of the third dice

    Examples
    --------

    .. sourcecode:: http

        HTTP/1.1 201
        Content-Type: text/json
            {
                "fallen": true,
                "dice1": 3,
                "dice2": 4,
                "dice3": 6
            }
    """
    game = Game.query.filter_by(UUID=gid).first()
    user = User.query.filter_by(id=uid).first()
    if game is None:
        response = jsonify()
        response.status_code = 404
        return response
    if user.game_id != game.id:
        response = jsonify()
        response.status_code = 404
        return response
    data = request.get_json() or {}
    # Cloud be improved to game.first_user_id first user.number_dice
    first_user = User.query.get_or_404(game.first_user_id)
    waitinguser = User.query.get_or_404(game.move_user_id)
    game.refreshed = datetime.now()
    if waitinguser.id == user.id or user.passive:
        if game.status == Status.GAMEFINISCH:
            game.status = Status.STARTED
            response = jsonify(Message='New Game Startet')
        if user.passive:
            user.passive = False
        if first_user.number_dice == 0 or user.number_dice < first_user.number_dice or first_user.id == user.id:
            if user.number_dice >= 3:
                response = jsonify(Message='User hase alread dice 3 times')
                response.status_code = 404
                return response
            user.number_dice = user.number_dice + 1
            if user.number_dice == first_user.number_dice and user.id != first_user.id or user.number_dice == 3:
                # https://stackoverflow.com/questions/364621/how-to-get-items-position-in-a-list
                aktualuserid = [i for i, x in enumerate(game.users) if x == user]
                if len(game.users) > aktualuserid[0]+1:
                    game.move_user_id = game.users[aktualuserid[0]+1].id
                else:
                    game.move_user_id = game.users[0].id
                next_user = User.query.get_or_404(game.move_user_id)
                # Back to first user
                if next_user.number_dice != 0:
                    game.message = "Aufdecken!"
                    db.session.add(game)
                    db.session.commit()
            if 'dice1' in data:
                escapeddice1 = str(utils.escape(data['dice1']))
                if escapeddice1.lower() in ['true', '1']:
                    user.dice1 = randint(1, 6)
                else:
                    user.dice1_visible = True
            else:
                user.dice1_visible = True
            if 'dice2' in data:
                escapeddice2 = str(utils.escape(data['dice2']))
                if escapeddice2.lower() in ['true', '1']:
                    user.dice2 = randint(1, 6)
                else:
                    user.dice2_visible = True
            else:
                user.dice2_visible = True

            if 'dice3' in data:
                escapeddice3 = str(utils.escape(data['dice3']))
                if escapeddice3.lower() in ['true', '1']:
                    user.dice3 = randint(1, 6)
                else:
                    user.dice3_visible = True
            else:
                user.dice3_visible = True
        else:
            response = jsonify(Message='Its not your turn')
            response.status_code = 400
            return response
        fallen = decision(game.changs_of_fallling_dice)
        if fallen:
            user.number_dice = user.number_dice - 1
            game.message = "Hoppla, {} ist ein Würfel vom Tisch gefallen!".format(user.name)
            game.fallling_dice_count = game.fallling_dice_count + 1
            db.session.add(game)
            db.session.commit()
        if user.dice1 == 1 and user.dice2 == 1 and user.dice3 == 1:
            game.schockoutcount = game.schockoutcount + 1
            db.session.add(game)
            db.session.commit()
        game.throw_dice_count = game.throw_dice_count + 1
        db.session.add(game)
        db.session.commit()
        response = jsonify(fallen=fallen, dice1=user.dice1, dice2=user.dice2, dice3=user.dice3)
        response.status_code = 201
        db.session.add(user)
        db.session.commit()
        return response
    else:
        response = jsonify(Message='Its not your turn')
        response.status_code = 400
    return response

# turn dice (2 or 3 6er to 1 or 2 1er)
@bp.route('/game/<gid>/user/<uid>/diceturn', methods=['POST'])
def turn_dice(gid, uid):
    """If a User Throws tow or three 6er in Throw 1 or 2 he/ she ist allowed
    to turn 1 dice (tow 6er) or 2 dice (three 6er) to dice with the numer 1

    Parameters
    ----------
    gid : 'int'
        A Game UUID
    uid : 'int'
        A User ID
    count : 'int'
        allowed values 1 or 2. To change 1 or 2 6er dice to 1er dice

    Examples
    --------

    .. code-block:: json

        {
            "count" : 1
        }

    Returns
    -------
    dice1 : 'int'
        value of the first dice
    dice2 : 'int'
        value of the second dice
    dice3 : 'int'
        value of the third dice

    Examples
    --------
    .. sourcecode:: http

        HTTP/1.1 201
        Content-Type: text/json
            {
                "dice1": 1,
                "dice2": 2,
                "dice3": None
            }
    """
    game = Game.query.filter_by(UUID=gid).first()
    user = User.query.get_or_404(uid)
    if game is None:
        response = jsonify(Message='Game not found')
        response.status_code = 404
        return response
    if user.game_id != game.id:
        response = jsonify(Message='User not in game')
        response.status_code = 404
        return response
    data = request.get_json() or {}
    first_user = User.query.get_or_404(game.first_user_id)
    waitinguser = User.query.get_or_404(game.move_user_id)
    if waitinguser.id == user.id:
        if first_user.number_dice == 0 or user.number_dice < first_user.number_dice or first_user.number_dice < 3:
            if 'count' in data:
                escapedcount = str(utils.escape(data['count']))
                if int(escapedcount) == 1:
                    if user.dice1 == 6 and user.dice2 == 6:
                        user.dice1 = 1
                        user.dice2 = None
                    elif user.dice2 == 6 and user.dice3 == 6:
                        user.dice2 = 1
                        user.dice3 = None
                    elif user.dice1 == 6 and user.dice3 == 6:
                        user.dice1 = 1
                        user.dice3 = None
                    else:
                        response = jsonify(Message='Could not finde tow dices with value 6')
                        response.status_code = 400
                        return response
                elif int(escapedcount) == 2:
                    if user.dice1 == 6 and user.dice2 == 6 and user.dice3 == 6:
                        user.dice1 = 1
                        user.dice2 = 1
                        user.dice3 = None
                    else:
                        response = jsonify(Message='Could not finde three dices with value 6')
                        response.status_code = 400
                        return response
                else:
                    response = jsonify(Message='count value not 1 or 2')
                    response.status_code = 400
                    return response
            else:
                response = jsonify(Message='count not in data')
                response.status_code = 400
                return response
        else:
            response = jsonify(Message='less then 1 throw left')
            response.status_code = 400
            return response
    else:
        response = jsonify(Message='Its not your turn')
        response.status_code = 400
        return response
    response = jsonify(dice1=user.dice1, dice2=user.dice2, dice3=user.dice3)
    response.status_code = 201
    db.session.add(user)
    db.session.commit()
    return response


def decision(probability) -> bool:
    """
    Return a Boolen that reprenet a fallen dice
    Parameters
    ----------
    probability : 'flaot'
        A Float that represent a changs that a dice will fall
    Returns
    -------
    random : 'bool'
        True = Dice fallen, False = Dice not fallen
    """
    return random() < probability
