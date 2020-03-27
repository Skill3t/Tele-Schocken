"""
endpoint.py
====================================

.. code-block:: none

    JSON REST API
    * GET   /api/game/<gid>                     Return the State of the Game (Polling)
    * POST  /api/game                           Add a new Game.
    * POST  /api/game/<gid>/user/               Add a new User to a Game.
    * GET   /api/game/<gid>/user/<uid>/dice     Roll a given number of dice

"""
from app.api import bp
from app import db

from flask import jsonify
from flask import request
from app.models import User, Game, Status2
from random import seed, randint, random


from app.api.errors import bad_request


# get Game Data
@bp.route('/game/<gid>', methods=['GET'])
def get_game(gid):
    """
    Return a hole game as json
    JSON example:

    .. code-block:: json

        {
        "Stack" : 10,
        "State" : "String",
        "First_Halfe" : true,
        "Move" : "Userid",
        "First" : "Userid",
        "Admin" : "Userid",
        "Users": [{
            "id" : 11,
            "Name"  : "Hans",
            "Chips" : 2,
            "passive" : false,
            "visible" : false
            },
            {
            "id" : 11,
            "Name"  : "Hans",
            "Chips" : 2,
            "passive" : false,
            "visible" : false
            }
        ]
        }

    or a 404 if the given game ID ist not in the Database
    """
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify()
        response.status_code = 404
        return response
    response = jsonify(game.to_dict())
    response.status_code = 200
    return response


# Create new Game
@bp.route('/game', methods=['POST'])
def create_Game():
    """
    Create a new Game the creater is the Admin send the folowing json
    JSON example:

    .. code-block:: json

        {"name":"jimbo10"}

    return 201 if the game is sucesccfully reated

    or a 400 if the username is aready in use

    return

    .. code-block:: json

        {"Link":"tele-schocken.de/a8a5fbc2-706e-11ea-825e-fa00a8584800","UUID":"a8a5fbc2-706e-11ea-825e-fa00a8584800", "Admin_Id":11}

    """
    seed(1)
    data = request.get_json() or {}
    if 'name' not in data:
        return bad_request('must include name field')
    game = Game()
    inuse = User.query.filter_by(name=data['name']).first()
    if inuse is not None:
        response = jsonify(Message='username in use!')
        response.status_code = 400
        return response
    user = User()
    user.name = data['name']
    game.users.append(user)
    db.session.add(game)
    db.session.commit()
    game.admin_user_id = user.id
    db.session.add(game)
    db.session.commit()
    response = jsonify(Link='tele-schocken.de/{}'.format(game.UUID), UUID=game.UUID, Admin_Id=user.id)
    response.status_code = 201
    return response


# set User to Game
@bp.route('/game/<gid>/user', methods=['POST'])
def set_game_user(gid):
    """
    Add a User to a game with the STATUS WAITING

    Parameters
    ----------
    gid
        A Game UUID

        .. code-block:: json

            {"name":"jimbo10"}

    """
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify()
        response.status_code = 404
        return response
    if game.status2 != Status2.WAITING:
        response = jsonify(Status='Game already Startet create new Game')
        response.status_code = 404
        return response
    data = request.get_json() or {}
    if 'name' not in data:
        return bad_request('must include name field')
    inuse = User.query.filter_by(name=data['name']).first()
    if inuse is not None:
        response = jsonify(Message='username in use!')
        response.status_code = 400
        return response
    user = User()
    user.name = data['name']
    game.users.append(user)
    db.session.add(game)
    db.session.commit()
    return jsonify(game.to_dict())


# Start the Game
@bp.route('/game/<gid>/start', methods=['POST'])
def start_game(gid):
    """
    The Admin can use This rout to Start the game and set the STATUS started

    Parameters
    ----------
    gid
        A Game UUID
    """
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify()
        response.status_code = 404
        return response
    game.status2 = Status2.STARTED
    db.session.add(game)
    db.session.commit()
    response = jsonify()
    response.status_code = 201
    return response


#
@bp.route('game/<gid>/user/<uid>/visible', methods=['POST'])
def pull_up_dice_cup(gid, uid):
    """
    The Admin can use This rout to Start the game and set the STATUS started

    Parameters
    ----------
    gid
        A Game UUID
    uid
        A User ID

    .. code-block:: json

        {"value": true}

    """
    game = Game.query.filter_by(UUID=gid).first()
    user = User.query.get_or_404(uid)
    if game is None:
        response = jsonify()
        response.status_code = 404
        return response
    game.status2 = Status2.STARTED
    db.session.add(game)
    db.session.commit()
    response = jsonify()
    response.status_code = 201
    return response

# user finisch bevor 3 rolls
@bp.route('/game/<gid>/user/<uid>/finisch', methods=['POST'])
def finish_throwing(gid, uid):
    """
    The Admin can use This rout to Start the game and set the STATUS started

    Parameters
    ----------
    gid
        A Game UUID
    uid
        A User ID
    """
    game = Game.query.filter_by(UUID=gid).first()
    user = User.query.get_or_404(uid)
    if game is None:
        response = jsonify()
        response.status_code = 404
        return response
    if user.game_id != game.id:
        response = jsonify()
        response.status_code = 404
        return response
    # https://stackoverflow.com/questions/364621/how-to-get-items-position-in-a-list
    aktualuserid = [i for i, x in enumerate(game.users) if x == user]
    if len(game.users) > aktualuserid[0]+1:
        game.move_user_id = game.users[aktualuserid[0]+1].id
    else:
        game.move_user_id = game.users[0].id
    db.session.add(game)
    db.session.commit()
    response = jsonify()
    response.status_code = 201
    return response


# roll dice
@bp.route('/game/<gid>/user/<uid>/dice', methods=['POST'])
def roll_dice(gid, uid):
    """
    A user can roll up to 3 dice

    Parameters
    ----------
    gid
        A Game UUID
    uid
        A User ID

    json
        dice1, dice2, dice3 are optional attributes depending on witch one you will roll again

        .. code-block:: json

            {
            "dice1" : 2,
            "dice2" : 3,
            "dice3" : 6,
            }

    Returns:

        .. code-block:: json

            {
            fallen=fallen, dice1=user.dice1, dice2=user.dice2, dice3=user.dice3
            }
        bool: The return value. True for success, False otherwise.


    """
    game = Game.query.filter_by(UUID=gid).first()
    user = User.query.get_or_404(uid)
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
    if first_user.number_dice == 0 or user.number_dice < first_user.number_dice:
        if user.number_dice >= 3:
            response = jsonify(Message='User hase alread dice 3 times')
            response.status_code = 404
            return response
        user.number_dice = user.number_dice + 1
        if user.number_dice == 3:
            # https://stackoverflow.com/questions/364621/how-to-get-items-position-in-a-list
            aktualuserid = [i for i, x in enumerate(game.users) if x == user]
            if len(game.users) > aktualuserid[0]+1:
                game.move_user_id = game.users[aktualuserid[0]+1].id
            else:
                game.move_user_id = game.users[0].id
        if 'dice1' in data:
            if data['dice1']:
                user.dice1 = randint(1, 6)
        if 'dice2' in data:
            if data['dice2']:
                user.dice2 = randint(1, 6)
        if 'dice3' in data:
            if data['dice3']:
                user.dice3 = randint(1, 6)
        if user.dice1 == 1 and user.dice2 == 1 and user.dice3 == 1:
            if game.firsthalf:
                game.status2 = Status2.FINISCH
            else:
                game.firsthalf = True
            db.session.add(game)
            db.session.commit()
        fallen = decision(game.changs_of_fallling_dice)
        response = jsonify(fallen=fallen, dice1=user.dice1, dice2=user.dice2, dice3=user.dice3)
        response.status_code = 201
        db.session.add(user)
        db.session.commit()
        return response
    else:
        response = jsonify(Message='User not correct initialted')
        response.status_code = 400
    return response

# turn dice (2 or 3 6er to 1 or 2 1er)
@bp.route('/game/<gid>/user/<uid>/diceturn', methods=['POST'])
def turn_dice(gid, uid):
    game = Game.query.filter_by(UUID=gid).first()
    user = User.query.get_or_404(uid)
    if game is None:
        response = jsonify()
        response.status_code = 404
        return response
    if user.game_id != game.id:
        response = jsonify()
        response.status_code = 404
        return response
    data = request.get_json() or {}
    if 'count' in data:
        if data['count'] == 1:
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
                response = jsonify()
                response.status_code = 400
                return response
        elif data['count'] == 2:
            if user.dice1 == 6 and user.dice2 == 6 and user.dice3 == 6:
                user.dice1 = 1
                user.dice2 = 1
                user.dice3 = None
            else:
                response = jsonify()
                response.status_code = 400
                return response
        else:
            response = jsonify()
            response.status_code = 400
            return response
    else:
        response = jsonify()
        response.status_code = 400
        return response
    response = jsonify(dice1=user.dice1, dice2=user.dice2, dice3=user.dice3)
    response.status_code = 201
    db.session.add(user)
    db.session.commit()
    return response


# transfer chips
@bp.route('/game/<gid>/user/chips', methods=['POST'])
def transfer_chips(gid):
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify()
        response.status_code = 404
        return response
    data = request.get_json() or {}
    # requierd attribute not included
    if 'count' not in data or 'target' not in data:
        response = jsonify()
        response.status_code = 400
        return response
    # transfer from user a to B
    if 'count' in data and 'source' in data and 'target' in data:
        userA = User.query.get_or_404(data['source'])
        userB = User.query.get_or_404(data['target'])
        if userA.chips >= data['count']:
            userA.chips = userA.chips - data['count']
            userB.chips = userB.chips + data['count']
            game.first_user_id = userB.id
            db.session.add(game)
            db.session.add(userA)
            db.session.add(userB)
            db.session.commit()
    # transfer from stack to user B
    if 'count' in data and 'stack' in data and 'target' in data:
        userB = User.query.get_or_404(data['target'])
        if game.stack >= data['count']:
            game.stack = game.stack - data['count']
            userB.chips = userB.chips + data['count']
            game.first_user_id = userB.id
            db.session.add(game)
            db.session.add(userB)
            db.session.commit()
    for user in game.users:
        user.dice1 = None
        user.dice2 = None
        user.dice3 = None
        user.number_dice = 0
    db.session.add(game)
    db.session.commit()
    response = jsonify()
    response.status_code = 201
    return response


def decision(probability) -> bool:
    """
    Return a Boolen that reprenet a fallen dice
    Parameters
    ----------
    probability
        A Float that represent a changs that a dice will fall
    """
    return random() < probability
