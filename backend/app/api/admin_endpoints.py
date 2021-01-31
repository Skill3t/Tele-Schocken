from app.api import bp
from app import db

from flask_socketio import emit


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
    stack_max : 'int'
        stack_max

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
                "Message": "success",
            }
    """
    data = request.get_json() or {}
    # requierd attribute not included
    if 'stack_max' not in data:
        response = jsonify(Message='request must include stack_max')
        response.status_code = 400
        return response
    if 'play_final' not in data:
        response = jsonify(Message='request must include play_final')
        response.status_code = 400
        return response
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify(Message='Game not found')
        response.status_code = 404
        return response
    game.status = Status.STARTED
    escaped_stack_max = int(utils.escape(data['stack_max']))

    game.stack_max = escaped_stack_max
    game.stack = escaped_stack_max

    escaped_play_final = str(utils.escape(data['play_final']))
    if escaped_play_final.lower() in ['true', '1', 't', 'y', 'yes']:
        game.play_final = True
    else:
        game.play_final = False

    game.first_user_id = game.users[randrange(len(game.users))].id
    game.move_user_id = game.first_user_id
    db.session.add(game)
    db.session.commit()
    emit('reload_game', game.to_dict(), room=gid, namespace='/game')
    response = jsonify(Message='success')
    response.status_code = 201
    return response


# transfer s
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
    response = jsonify(Message='success')
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
        if data['count'] is not None:
            escapedcount = int(utils.escape(data['count']))
        else:
            response = jsonify(Message='No chips in count. try again')
            response.status_code = 400
            return response

        if userA.chips >= escapedcount:
            if game.status == Status.PLAYFINAL:
                if userB.halfcount == 0 or userA.halfcount == 0:
                    response = jsonify(Message='Benutzer nicht im finale')
                    response.status_code = 400
                    return response
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
        if data['count'] is not None:
            escapedcount = int(utils.escape(data['count']))
        else:
            response = jsonify(Message='No chips in count. try again')
            response.status_code = 400
            return response
        if game.stack >= escapedcount:
            if game.status == Status.PLAYFINAL:
                if userB.halfcount == 0:
                    response = jsonify(Message='Benutzer nicht im finale')
                    response.status_code = 400
                    return response
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
            if game.status == Status.PLAYFINAL:
                if userB.halfcount == 0:
                    response = jsonify(Message='Benutzer nicht im finale')
                    response.status_code = 400
                    return response
            game.stack = 0
            userB.chips = game.stack_max
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
    if game.status == Status.ROUNDFINISCH or game.status == Status.GAMEFINISCH:
        game.status = Status.STARTED
    # Game GAMEFINISCH or ROUNDFINISCH
    escapedtarget = str(utils.escape(data['target']))
    userB = User.query.get_or_404(escapedtarget)
    # if userB.chips == game.stack_max:
    #    userB.halfcount = userB.halfcount + 1
    #    game.status = Status.ROUNDFINISCH
    #    game.stack = game.stack_max
    #    game.halfcount = game.halfcount + 1
    #    game.changs_of_fallling_dice = game.changs_of_fallling_dice + 0.0002
    #    response = jsonify(Message='Player {} lose a half'.format(userB.name))
    if userB.chips == game.stack_max:
        # someone lose a half increas the changse of fallen dice because they are more drunken
        game.changs_of_fallling_dice = game.changs_of_fallling_dice + 0.0002
        # play final
        if game.play_final:
            print('Hier')
            print('userB.halfcount {}'.format(userB.halfcount))
            print('game.halfcount {}'.format(game.halfcount))
            if game.status == Status.PLAYFINAL:
                message = 'Player {} lose the Game'.format(userB.name)
                game.message = 'Player {} lose the Game'.format(userB.name)
                game.status = Status.GAMEFINISCH
                userB.finalcount = userB.finalcount + 1
                game.halfcount = 0
                game.stack = game.stack_max
            else:
                # second half to the same user --> game finish
                if userB.halfcount == 1:
                    game.stack = game.stack_max
                    game.halfcount = game.halfcount + 1
                    if game.halfcount == 2:
                        game.stack = game.stack_max
                        game.status = Status.PLAYFINAL
                        print('play final')
                        game.halfcount = 0
                        for user in game.users:
                            user.passive = False
                            user.chips = 0
                        game.finalcount = game.finalcount + 1
                        message = 'Finale wird gespiel'
                        game.message = 'Finale wird gespielt grau hinterlegte Spieler müssen warten'
                    else:

                        message = 'Player {} lose the Game'.format(userB.name)
                # fist half round finish
                elif userB.halfcount == 0:
                    game.stack = game.stack_max
                    game.halfcount = game.halfcount + 1
                    userB.halfcount = userB.halfcount + 1
                    if game.halfcount == 2:
                        game.status = Status.PLAYFINAL
                        print('play final')
                        game.halfcount = 0
                        for user in game.users:
                            user.passive = False
                            user.chips = 0
                        message = 'Finale wird gespiel'
                        game.message = 'Finale wird gespielt grau hinterlegte Spieler müssen warten'
                    else:
                        game.status = Status.ROUNDFINISCH
                        message = 'Player {} lose a half'.format(userB.name)
                else:
                    message = 'Fehler'
                    print('log error final ')
        # no final only count halfs
        else:
            userB.halfcount = userB.halfcount + 1
            game.status = Status.ROUNDFINISCH
            game.stack = game.stack_max
            game.halfcount = game.halfcount + 1
            message = 'Player {} lose a half'.format(userB.name)
    else:
        message = 'OK'

    # message = round(userB, game)
    response = jsonify(Message=message)
    for user in game.users:
        if game.status == Status.ROUNDFINISCH:
            user.chips = 0
            user.passive = False

        if game.status == Status.GAMEFINISCH:
            user.chips = 0
            user.passive = False
            user.halfcount = 0
        if game.status == Status.PLAYFINAL:
            if user.halfcount == 0:
                user.passive = True
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
    emit('reload_game', game.to_dict(), room=gid, namespace='/game')
    return response


# XHR Delete User from Game
@bp.route('/game/<gid>/user/<uid>', methods=['DELETE'])
def delete_player(gid, uid):
    game = Game.query.filter_by(UUID=gid).first()
    delete_user = User.query.get_or_404(uid)
    if game is None:
        response = jsonify(Message='Game not found')
        response.status_code = 404
        return response
    if delete_user.game_id != game.id:
        response = jsonify(Message='Player not in Game')
        response.status_code = 404
        return response

    if game.admin_user_id == delete_user.id:
        response = jsonify(Message='Admin can not be removed!')
        response.status_code = 404
        return response
    if delete_user.id == game.first_user_id:
        aktualuserid = [i for i, x in enumerate(game.users) if x == delete_user]
        if len(game.users) > aktualuserid[0]+1:
            game.first_user_id = game.users[aktualuserid[0]+1].id
        else:
            game.first_user_id = game.users[0].id
    if delete_user.id == game.move_user_id:
        aktualuserid = [i for i, x in enumerate(game.users) if x == delete_user]
        if len(game.users) > aktualuserid[0]+1:
            game.move_user_id = game.users[aktualuserid[0]+1].id
        else:
            game.move_user_id = game.users[0].id
    for user in game.users:
        user.chips = 0
        user.dice1 = 0
        user.dice2 = 0
        user.dice3 = 0
        user.number_dice = 0
        user.passive = False
        # user.visible = False
        user.dice1_visible = False
        user.dice2_visible = False
        user.dice3_visible = False
    game.stack = game.stack_max
    game.message = "Spieler: {} vom Admin entfernt (ggf. Seite neu laden um Spielerliste zu aktualisieren)".format(delete_user.name)
    db.session.delete(delete_user)
    db.session.add(game)
    db.session.commit()
    emit('reload_game', game.to_dict(), room=gid, namespace='/game')
    response = jsonify(Message='success')
    response.status_code = 200
    return response


# XHR choose  new admin
@bp.route('/game/<gid>/user/<uid>/change_admin', methods=['POST'])
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
        game.admin_user_id = new_admin.id
        game.message = "Admin gewechselt neuer Admin: {}! Neuer Admin muss die Seite einmal neu laden".format(new_admin.name)
        db.session.add(game)
        db.session.commit()
        emit('reload_game', game.to_dict(), room=gid, namespace='/game')
        response = jsonify(Message='success')
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
                "Message": "success",
            }
    """
    game = Game.query.filter_by(UUID=gid).first()
    if game is None:
        response = jsonify(Message='Game not found')
        response.status_code = 404
        return response
    for user in game.users:
        if game.play_final:
            user.halfcount = 0
        user.chips = 0
        user.dice1 = 0
        user.dice2 = 0
        user.dice3 = 0
        user.number_dice = 0
        user.passive = False
        # user.visible = False
        user.dice1_visible = False
        user.dice2_visible = False
        user.dice3_visible = False
    if game.play_final:
        game.halfcount = 0
    game.message = ""
    game.stack = game.stack_max
    game.status = Status.WAITING
    db.session.add(game)
    db.session.commit()
    emit('reload_game', game.to_dict(), room=gid, namespace='/game')
    response = jsonify(Message='success')
    response.status_code = 201
    return response
