from app.api import bp
from app import db

from flask import jsonify
from flask import request
from app.models import User, Game, Status
from random import seed, randrange
from jinja2 import utils

from app.api.errors import bad_request


# Create new Game
@bp.route('/game', methods=['POST'])
def create_Game():
    """Create a new Game the creater is the Admin send the folowing json

    Parameters
    ----------
    name : 'str'
        Admin user name

    Examples
    --------

    .. code-block:: json

        {"name":"jimbo10"}

    Returns
    -------
    Link : 'str'
        Link to Share  and join new users
    UUID : 'str'
        UUID to identify the new Game
    Admin_Id : 'int'
        ID of the new Admin

    Examples
    --------

    .. sourcecode:: http

      HTTP/1.1 201
      Content-Type: text/json
          {
            "Link": "tele-schocken.de/a8a5fbc2-706e-11ea-825e-fa00a8584800",
            "UUID": "a8a5fbc2-706e-11ea-825e-fa00a8584800",
            "Admin_Id": 11
          }

    .. sourcecode:: http

      HTTP/1.1 400
      Content-Type: text/json
          {
            "Message": "username in use!",
          }
    """
    seed(1)
    data = request.get_json() or {}
    response = jsonify()
    if 'name' not in data:
        return bad_request('must include name field')
    else:
        escapedusername = str(utils.escape(data['name']))
        game = Game()
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
        game.admin_user_id = user.id
        db.session.add(game)
        db.session.commit()
        response = jsonify(Link='tele-schocken.de/{}'.format(game.UUID), UUID=game.UUID, Admin_Id=user.id)
        response.status_code = 201
    return response


# Start the Game
@bp.route('/game/<gid>/start', methods=['POST'])
def start_game(gid):
    """
    The Admin can use This rout to Start the game and set the STATUS started

    Parameters
    ----------
    gid : 'int'
        A Game UUID

    Examples
    --------
    .. sourcecode:: http

        HTTP/1.1 404
        Content-Type: text/json
            {
                "Message": "Game already Startet create new Game",
            }

    .. sourcecode:: http

        HTTP/1.1 201
        Content-Type: text/json
            {
                "Message": "suscess",
            }
    """
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify(Message='Game not found')
        response.status_code = 404
        return response
    game.status = Status.STARTED
    game.first_user_id = game.users[randrange(len(game.users))].id
    game.move_user_id = game.first_user_id
    db.session.add(game)
    db.session.commit()
    response = jsonify(Message='suscess')
    response.status_code = 201
    return response


# transfer chips
@bp.route('/game/<gid>/user/chips', methods=['POST'])
def transfer_chips(gid):
    """At the end of a round the Admin Transers chips from the Stack to a User or
    Form User A to User B

    Parameters
    ----------
    gid : 'int'
        A Game UUID
    count : 'int'
    source : 'int', optional
    stack : 'int', optional
    target : 'int'


    Examples
    --------
    **Example 1**
    Transfere 5 Chip from User A (User ID 12) to User with UserB (User ID 13)

    .. code-block:: json

        {
            "count" : 5,
            "source": 12,
            "target": 13
        }

    **Example 2**
    Transfere 3 Chip from Stack to User with User ID 13

    .. code-block:: json

        {
            "count" : 3,
            "stack": true,
            "target": 13
        }

    Returns
    -------
    Message : 'str'
        Return Message with reson

    Examples
    --------
    .. sourcecode:: http

        HTTP/1.1 400
        Content-Type: text/json
            {
                "Message": "Request must include value",
            }
    """
    response = jsonify(Message='sucess')
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify(Message='Game not found')
        response.status_code = 404
        return response
    data = request.get_json() or {}
    # requierd attribute not included
    if 'target' not in data:
        response = jsonify(Message='request must include target')
        response.status_code = 400
        return response
    # transfer from user A to B
    if 'count' in data and 'source' in data and 'target' in data:
        escapedsource = str(utils.escape(data['source']))
        userA = User.query.get_or_404(escapedsource)
        escapedtarget = str(utils.escape(data['target']))
        userB = User.query.get_or_404(escapedtarget)
        escapedcount = int(utils.escape(data['count']))

        if userA.chips >= escapedcount:
            userA.chips = userA.chips - escapedcount
            userB.chips = userB.chips + escapedcount
            game.first_user_id = userB.id
            game.move_user_id = userB.id
            game.message = "{} Chip(s) von: {} an: {} verteilt!".format(escapedcount, userA.name, userB.name)

            db.session.add(game)
            db.session.add(userA)
            db.session.add(userB)
            db.session.commit()
        else:
            response = jsonify(Message='source has not enough chips on his stack. try again')
            response.status_code = 400
            return response
    # transfer from stack to user B
    if 'count' in data and 'stack' in data and 'target' in data:
        escapedtarget = str(utils.escape(data['target']))
        userB = User.query.get_or_404(escapedtarget)
        escapedcount = int(utils.escape(data['count']))
        if game.stack >= escapedcount:
            game.stack = game.stack - escapedcount
            userB.chips = userB.chips + escapedcount
            game.first_user_id = userB.id
            game.move_user_id = userB.id
            game.message = "{} Chip(s) vom Stapel an: {} verteilt!".format(escapedcount, userB.name)

            db.session.add(game)
            db.session.add(userB)
            db.session.commit()
        else:
            response = jsonify(Message='Not enough chips on the stack. try again')
            response.status_code = 400
            return response
    # transfer all to B Schockaus
    if 'schockaus' in data and 'target' in data:
        escapedtarget = str(utils.escape(data['target']))
        userB = User.query.get_or_404(escapedtarget)
        escapedschockaus = utils.escape(data['schockaus'])
        if escapedschockaus:
            game.stack = 0
            userB.chips = 13
            game.first_user_id = userB.id
            game.move_user_id = userB.id
            game.message = "Schockaus alle Chips an: {} verteilt!".format(userB.name)

            db.session.add(game)
            db.session.add(userB)
            db.session.commit()
        else:
            response = jsonify(Message='wrong transfere check transfere and try again')
            response.status_code = 400
            return response
    if game.status == Status.ROUNDFINISCH:
        game.status = Status.STARTED
    # Game GAMEFINISCH or ROUNDFINISCH
    escapedtarget = str(utils.escape(data['target']))
    userB = User.query.get_or_404(escapedtarget)
    if userB.chips == 13:
        userB.halfcount = userB.halfcount + 1
        game.status = Status.ROUNDFINISCH
        game.stack = 13
        game.halfcount = game.halfcount + 1
        game.changs_of_fallling_dice = game.changs_of_fallling_dice + 0.001
        response = jsonify(Message='Player {} lose a half'.format(userB.name))
    for user in game.users:
        if game.status == Status.ROUNDFINISCH:
            user.chips = 0
        user.dice1 = 0
        user.dice2 = 0
        user.dice3 = 0
        user.number_dice = 0
        # user.visible = False
        user.dice1_visible = False
        user.dice2_visible = False
        user.dice3_visible = False
    db.session.add(game)
    db.session.commit()
    response.status_code = 200
    return response

# XHR Delete User from Game
@bp.route('/game/<gid>/user/<uid>', methods=['DELETE'])
def delete_player(gid, uid):
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

    if game.admin_user_id == user.id:
        response = jsonify(Message='Admin can not be removed!')
        response.status_code = 404
        return response
    if user.id == game.first_user_id:
        aktualuserid = [i for i, x in enumerate(game.users) if x == user]
        if len(game.users) > aktualuserid[0]+1:
            game.first_user_id = game.users[aktualuserid[0]+1].id
        else:
            game.first_user_id = game.users[0].id
    if user.id == game.move_user_id:
        aktualuserid = [i for i, x in enumerate(game.users) if x == user]
        if len(game.users) > aktualuserid[0]+1:
            game.move_user_id = game.users[aktualuserid[0]+1].id
        else:
            game.move_user_id = game.users[0].id
    game.message = "Spieler: {} vom Admin entfernt".format(user.name)
    db.session.add(game)
    db.session.commit()
    db.session.delete(user)
    db.session.commit()
    response = jsonify(Message='suscess')
    response.status_code = 200
    return response


# XHR choose  new admin
@bp.route('/game/<gid>/user/<uid>', methods=['POST'])
def choose_admin(gid, uid):
    game = Game.query.filter_by(UUID=gid).first()
    user = User.query.get_or_404(uid)
    data = request.get_json() or {}
    # requierd attribute not included
    if 'new_admin_id' not in data:
        response = jsonify(Message='request must include new_admin_id')
        response.status_code = 400
        return response
    else:
        new_admin_id = str(utils.escape(data['new_admin_id']))
        new_admin = User.query.get_or_404(new_admin_id)

    if game is None:
        response = jsonify(Message='Game not found')
        response.status_code = 404
        return response
    if user.game_id != game.id:
        response = jsonify(Message='Player not in Game')
        response.status_code = 404
        return response
    if game.admin_user_id == user.id:
        print(new_admin)
        game.admin_user_id = new_admin.id
        game.message = "Admin gewechselt neuer Admin: {}! Neuer Admin muss die Seite einmal neu laden".format(new_admin.name)
        db.session.add(game)
        db.session.commit()
        response = jsonify(Message='suscess')
        response.status_code = 200
        return response
    response = jsonify(Message='Unknown Error')
    response.status_code = 404
    return response


# back to waiting
@bp.route('/game/<gid>/back', methods=['POST'])
def wait_game(gid):
    """
    The Admin can use This rout to put the game back to the waitung area

    Parameters
    ----------
    gid : 'int'
        A Game UUID

    Examples
    --------
    .. sourcecode:: http

        HTTP/1.1 404
        Content-Type: text/json
            {
                "Message": "error",
            }

    .. sourcecode:: http

        HTTP/1.1 201
        Content-Type: text/json
            {
                "Message": "suscess",
            }
    """
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify(Message='Game not found')
        response.status_code = 404
        return response
    game.status = Status.WAITING
    db.session.add(game)
    db.session.commit()
    response = jsonify(Message='suscess')
    response.status_code = 201
    return response
