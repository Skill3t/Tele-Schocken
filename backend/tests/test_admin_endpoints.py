from app import db
from app.models import Status, User
from tests.conftest import get_game, get_user


# POST /api/game
def test_create_game(client):
    response = client.post('/api/game', json={'name': 'jimbo10'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['UUID']
    assert data['Link'] == 'tele-schocken.de/{}'.format(data['UUID'])
    game = get_game(data['UUID'])
    assert game.status == Status.WAITING
    assert game.stack == 13
    assert game.admin_user_id == data['Admin_Id']
    assert [u.name for u in game.users] == ['jimbo10']


def test_create_game_without_name(client):
    response = client.post('/api/game', json={})
    assert response.status_code == 400
    assert response.get_json()['message'] == 'must include name field'


def test_create_game_username_in_use(client, create_game):
    create_game('jimbo10')
    response = client.post('/api/game', json={'name': 'jimbo10'})
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'Benutzername wird bereits verwendet!'


def test_create_game_escapes_username(client):
    response = client.post('/api/game', json={'name': '<b>bold</b>'})
    assert response.status_code == 201
    assert get_user(response.get_json()['Admin_Id']).name == '&lt;b&gt;bold&lt;/b&gt;'


# POST /api/game/<gid>/start
def test_start_game(client, create_game, add_user, emitted):
    gid, admin_id = create_game()
    bob_id = add_user(gid, 'bob')
    response = client.post('/api/game/{}/start'.format(gid), json={'stack_max': 10, 'play_final': 'true'})
    assert response.status_code == 201
    game = get_game(gid)
    assert game.status == Status.STARTED
    assert game.stack == 10
    assert game.stack_max == 10
    assert game.play_final is True
    assert game.first_user_id in (admin_id, bob_id)
    assert game.move_user_id == game.first_user_id
    assert emitted[-1]['event'] == 'reload_game'
    assert emitted[-1]['room'] == gid


def test_start_game_requires_stack_max(client, create_game):
    gid, _ = create_game()
    response = client.post('/api/game/{}/start'.format(gid), json={'play_final': False})
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'request must include stack_max'


def test_start_game_requires_play_final(client, create_game):
    gid, _ = create_game()
    response = client.post('/api/game/{}/start'.format(gid), json={'stack_max': 13})
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'request must include play_final'


def test_start_unknown_game(client, app):
    response = client.post('/api/game/fake/start', json={'stack_max': 13, 'play_final': False})
    assert response.status_code == 404


# POST /api/game/<gid>/user/chips
def test_transfer_chips_from_stack(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.post('/api/game/{}/user/chips'.format(gid), json={'count': 3, 'stack': True, 'target': bob_id})
    assert response.status_code == 200
    assert response.get_json()['Message'] == 'OK'
    game = get_game(gid)
    assert game.stack == 10
    assert get_user(bob_id).chips == 3
    assert game.first_user_id == bob_id
    assert game.move_user_id == bob_id
    assert game.message == '3 Chip(s) vom Stapel an: bob verteilt!'


def test_transfer_chips_between_users(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    client.post('/api/game/{}/user/chips'.format(gid), json={'count': 5, 'stack': True, 'target': bob_id})
    response = client.post('/api/game/{}/user/chips'.format(gid), json={'count': 2, 'source': bob_id, 'target': carl_id})
    assert response.status_code == 200
    assert get_user(bob_id).chips == 3
    assert get_user(carl_id).chips == 2
    assert get_game(gid).move_user_id == carl_id


def test_transfer_chips_resets_dice(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    client.post('/api/game/{}/user/{}/dice'.format(gid, admin_id), json={'dice1': True, 'dice2': True, 'dice3': True})
    client.post('/api/game/{}/user/chips'.format(gid), json={'count': 1, 'stack': True, 'target': admin_id})
    admin = get_user(admin_id)
    assert admin.number_dice == 0
    assert (admin.dice1, admin.dice2, admin.dice3) == (0, 0, 0)


def test_transfer_chips_requires_target(client, started_game):
    gid, _ = started_game
    response = client.post('/api/game/{}/user/chips'.format(gid), json={'count': 1, 'stack': True})
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'request must include target'


def test_transfer_chips_unknown_game(client, app):
    response = client.post('/api/game/fake/user/chips', json={'count': 1, 'stack': True, 'target': 1})
    assert response.status_code == 404


def test_transfer_more_chips_than_source_has(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.post('/api/game/{}/user/chips'.format(gid), json={'count': 1, 'source': bob_id, 'target': carl_id})
    assert response.status_code == 400
    assert get_user(carl_id).chips == 0


def test_transfer_more_chips_than_stack_has(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.post('/api/game/{}/user/chips'.format(gid), json={'count': 14, 'stack': True, 'target': bob_id})
    assert response.status_code == 400
    assert get_game(gid).stack == 13


def test_lose_half_without_final(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.post('/api/game/{}/user/chips'.format(gid), json={'count': 13, 'stack': True, 'target': bob_id})
    assert response.status_code == 200
    assert response.get_json()['Message'] == 'Spieler bob verliert eine Hälfte'
    game = get_game(gid)
    assert game.status == Status.ROUNDFINISCH
    assert game.halfcount == 1
    assert game.stack == 13
    assert get_user(bob_id).halfcount == 1
    assert all(u.chips == 0 for u in game.users)


def test_schockaus(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.post('/api/game/{}/user/chips'.format(gid), json={'schockaus': True, 'target': carl_id})
    assert response.status_code == 200
    assert response.get_json()['Message'] == 'Spieler carl verliert eine Hälfte'
    game = get_game(gid)
    assert game.status == Status.ROUNDFINISCH
    assert get_user(carl_id).halfcount == 1


def test_play_final(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    game = get_game(gid)
    game.play_final = True
    db.session.commit()
    url = '/api/game/{}/user/chips'.format(gid)

    # first half
    client.post(url, json={'schockaus': True, 'target': bob_id})
    assert get_game(gid).status == Status.ROUNDFINISCH
    # second half to another player -> final between bob and carl
    response = client.post(url, json={'schockaus': True, 'target': carl_id})
    assert response.get_json()['Message'] == 'Finale wird gespielt'
    game = get_game(gid)
    assert game.status == Status.PLAYFINAL
    assert get_user(admin_id).passive is True
    assert get_user(bob_id).passive is False

    # admin is not part of the final
    response = client.post(url, json={'count': 1, 'stack': True, 'target': admin_id})
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'Benutzer nicht im Finale'

    response = client.post(url, json={'schockaus': True, 'target': bob_id})
    assert response.get_json()['Message'] == 'Spieler bob hat das Finale verloren'
    game = get_game(gid)
    assert game.status == Status.GAMEFINISCH
    assert get_user(bob_id).finalcount == 1
    assert all(u.halfcount == 0 and not u.passive for u in game.users)


# DELETE /api/game/<gid>/user/<uid>
def test_delete_player(client, started_game, emitted):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.delete('/api/game/{}/user/{}'.format(gid, bob_id))
    assert response.status_code == 200
    assert get_user(bob_id) is None
    game = get_game(gid)
    assert [u.id for u in game.users] == [admin_id, carl_id]
    assert game.message.startswith('Spieler: bob vom Admin entfernt')
    assert emitted[-1]['event'] == 'reload_game'


def test_delete_player_who_moves_passes_turn(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    game = get_game(gid)
    game.first_user_id = bob_id
    game.move_user_id = bob_id
    db.session.commit()
    client.delete('/api/game/{}/user/{}'.format(gid, bob_id))
    game = get_game(gid)
    assert game.first_user_id == carl_id
    assert game.move_user_id == carl_id


def test_delete_admin_not_allowed(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.delete('/api/game/{}/user/{}'.format(gid, admin_id))
    assert response.status_code == 404
    assert response.get_json()['Message'] == 'Admin kann nicht entfernt werden'
    assert get_user(admin_id) is not None


def test_delete_player_from_other_game(client, started_game, create_game):
    gid, _ = started_game
    _, other_admin_id = create_game('other')
    response = client.delete('/api/game/{}/user/{}'.format(gid, other_admin_id))
    assert response.status_code == 404
    assert response.get_json()['Message'] == 'Spieler ist nicht in diesem Spiel'


# POST /api/game/<gid>/user/<uid>/change_admin
def test_change_admin(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.post('/api/game/{}/user/{}/change_admin'.format(gid, admin_id), json={'new_admin_id': bob_id})
    assert response.status_code == 200
    assert get_game(gid).admin_user_id == bob_id


def test_change_admin_by_non_admin(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.post('/api/game/{}/user/{}/change_admin'.format(gid, bob_id), json={'new_admin_id': carl_id})
    assert response.status_code == 404
    assert get_game(gid).admin_user_id == admin_id


def test_change_admin_requires_new_admin_id(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.post('/api/game/{}/user/{}/change_admin'.format(gid, admin_id), json={})
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'request must include new_admin_id'


# POST /api/game/<gid>/back
def test_back_to_waiting(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    client.post('/api/game/{}/user/chips'.format(gid), json={'count': 4, 'stack': True, 'target': bob_id})
    response = client.post('/api/game/{}/back'.format(gid))
    assert response.status_code == 201
    game = get_game(gid)
    assert game.status == Status.WAITING
    assert game.stack == game.stack_max
    assert all(u.chips == 0 for u in User.query.all())


def test_back_to_waiting_unknown_game(client, app):
    response = client.post('/api/game/fake/back')
    assert response.status_code == 404
