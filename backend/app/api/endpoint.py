from app.api import bp
from app import db

from flask import jsonify
from flask import request
from app.models import User, Game, Status
from random import seed, randint, random


from app.api.errors import bad_request

'''
* GET   /api/game/<gid>                     Return the State of the Game (Polling)
* POST  /api/game                           Add a new Game.
* POST  /api/game/<gid>/user/               Add a new User to a Game.
* GET   /api/game/<gid>/user/<uid>/dice     Roll a given number of dice
'''


# get Game Data
@bp.route('/game/<gid>', methods=['GET'])
def get_game(gid):
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify()
        response.status_code = 404
        return response
    return jsonify(game.to_dict())


# Create new Game
@bp.route('/game', methods=['POST'])
def create_Game():
    seed(1)
    data = request.get_json() or {}
    if 'name' not in data:
        return bad_request('must include name field')
    game = Game()
    user = User()
    user.name = data['name']
    game.users.append(user)
    db.session.add(game)
    db.session.commit()
    game.admin_user_id = user.id
    db.session.add(game)
    db.session.commit()
    response = jsonify(Link='tele-schocken.de/{}'.format(game.UUID), UUID=game.UUID)
    response.status_code = 201
    return response


# set User to Game
@bp.route('/game/<gid>/user', methods=['POST'])
def set_game_user(gid):
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify()
        response.status_code = 404
        return response
    data = request.get_json() or {}
    if 'name' not in data:
        return bad_request('must include name field')
    user = User()
    user.name = data['name']
    game.users.append(user)
    db.session.add(game)
    db.session.commit()
    return jsonify(game.to_dict())


# Start the Game
@bp.route('/game/<gid>/start', methods=['POST'])
def start_game(gid):
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify()
        response.status_code = 404
        return response
    game.status = Status.STARTED
    db.session.add(game)
    db.session.commit()
    response = jsonify()
    response.status_code = 201
    return response

# roll dice
@bp.route('/game/<gid>/user/<uid>/dice', methods=['POST'])
def roll_dice(gid, uid):
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
            game.status = Status.FINISCH
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
            db.session.add(userA)
            db.session.add(userB)
            db.session.commit()
    # transfer from stack to user B
    if 'count' in data and 'stack' in data and 'target' in data:
        userB = User.query.get_or_404(data['target'])
        if game.stack >= data['count']:
            game.stack = game.stack - data['count']
            userB.chips = userB.chips + data['count']
            db.session.add(game)
            db.session.add(userB)
            db.session.commit()
    response = jsonify()
    response.status_code = 201
    return response


def decision(probability):
    return random() < probability
