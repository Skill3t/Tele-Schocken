import pytest

from app import db
from app.api import game_endpoints
from app.models import Status
from tests.conftest import get_game, get_user

real_decision = game_endpoints.decision
ALL_DICE = {'dice1': True, 'dice2': True, 'dice3': True}


def roll(client, gid, uid, data=ALL_DICE):
    return client.post('/api/game/{}/user/{}/dice'.format(gid, uid), json=data)


def finish(client, gid, uid):
    return client.post('/api/game/{}/user/{}/finisch'.format(gid, uid))


def set_dice(uid, dice1, dice2, dice3, number_dice=1):
    user = get_user(uid)
    user.dice1, user.dice2, user.dice3 = dice1, dice2, dice3
    user.number_dice = number_dice
    db.session.commit()


# GET /api/game/<gid>
def test_get_game(client, create_game):
    gid, admin_id = create_game('jimbo10')
    response = client.get('/api/game/{}'.format(gid))
    assert response.status_code == 200
    data = response.get_json()
    assert data['Stack'] == 13
    assert data['State'] == 'waiting'
    assert data['Game_Half_Count'] == 0
    assert data['Game_Final_Count'] == 0
    assert data['Move'] is None
    assert data['First'] is None
    assert data['Message'] is None
    assert data['Admin'] == admin_id
    assert data['User'] == [{
        'Id': admin_id,
        'Name': 'jimbo10',
        'Chips': 0,
        'Passive': False,
        'Halfcount': 0,
        'Finalcount': 0,
        'Number_Dice': 0,
        'Dices': [],
    }]


def test_get_unknown_game(client, app):
    response = client.get('/api/game/fake')
    assert response.status_code == 404
    assert response.get_json()['Message'] == 'Spiel ist nicht in der Datenbank'


# POST /api/game/<gid>/user
def test_join_game(client, create_game, emitted):
    gid, _ = create_game()
    response = client.post('/api/game/{}/user'.format(gid), json={'name': 'bob'})
    assert response.status_code == 200
    assert [u['Name'] for u in response.get_json()['User']] == ['admin', 'bob']
    assert emitted[-1]['event'] == 'reload_game'
    assert emitted[-1]['room'] == gid


def test_join_unknown_game(client, app):
    response = client.post('/api/game/fake/user', json={'name': 'bob'})
    assert response.status_code == 404


def test_join_game_without_name(client, create_game):
    gid, _ = create_game()
    response = client.post('/api/game/{}/user'.format(gid), json={})
    assert response.status_code == 400
    assert response.get_json()['message'] == 'must include name field'


def test_join_game_username_in_use(client, create_game):
    gid, _ = create_game('admin')
    response = client.post('/api/game/{}/user'.format(gid), json={'name': 'admin'})
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'Benutzername schon vergeben!'


def test_join_started_game(client, started_game):
    gid, _ = started_game
    response = client.post('/api/game/{}/user'.format(gid), json={'name': 'late'})
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'Spiel ist bereits gestartet. Starte ein neues Spiel!'


# POST /api/game/<gid>/user/<uid>/dice
def test_roll_dice(client, started_game, emitted):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = roll(client, gid, admin_id)
    assert response.status_code == 201
    data = response.get_json()
    assert data['fallen'] is False
    assert data['number_dice'] == 1
    for key in ('dice1', 'dice2', 'dice3'):
        assert 1 <= data[key] <= 6
    game = get_game(gid)
    assert game.throw_dice_count == 1
    # the first player may roll up to three times
    assert game.move_user_id == admin_id
    assert emitted[-1]['event'] == 'reload_game'


def test_roll_only_selected_dice(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    set_dice(admin_id, 2, 3, 4)
    response = roll(client, gid, admin_id, {'dice1': True, 'dice2': False})
    assert response.get_json()['dice2'] == 3
    assert response.get_json()['dice3'] == 4
    admin = get_user(admin_id)
    assert admin.dice1_visible is False
    assert admin.dice2_visible is True
    assert admin.dice3_visible is True


def test_roll_dice_not_your_turn(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = roll(client, gid, bob_id)
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'Du bist nicht dran!'


def test_roll_dice_unknown_game(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = roll(client, 'fake', admin_id)
    assert response.status_code == 404


def test_first_player_turn_ends_after_three_rolls(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    for number in (1, 2, 3):
        assert roll(client, gid, admin_id).get_json()['number_dice'] == number
    assert get_game(gid).move_user_id == bob_id
    assert roll(client, gid, admin_id).status_code == 400


def test_following_players_roll_as_often_as_first_player(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    roll(client, gid, admin_id)
    roll(client, gid, admin_id)
    finish(client, gid, admin_id)
    roll(client, gid, bob_id)
    assert get_game(gid).move_user_id == bob_id
    roll(client, gid, bob_id)
    assert get_game(gid).move_user_id == carl_id
    roll(client, gid, carl_id)
    roll(client, gid, carl_id)
    # everybody has rolled -> reveal the dice
    game = get_game(gid)
    assert game.move_user_id == carl_id
    assert game.message == 'Aufdecken!'


def test_dice_fall_from_table(client, started_game, monkeypatch):
    gid, (admin_id, bob_id, carl_id) = started_game
    monkeypatch.setattr(game_endpoints, 'decision', lambda probability: True)
    response = roll(client, gid, admin_id)
    assert response.status_code == 201
    assert response.get_json()['fallen'] is True
    assert response.get_json()['number_dice'] == 0
    game = get_game(gid)
    assert game.fallling_dice_count == 1
    assert game.message == 'Hoppla, admin ist ein Würfel vom Tisch gefallen!'


def test_schockout_is_counted(client, started_game, monkeypatch):
    gid, (admin_id, bob_id, carl_id) = started_game
    monkeypatch.setattr(game_endpoints, 'randint', lambda a, b: 1)
    response = roll(client, gid, admin_id)
    assert [response.get_json()[k] for k in ('dice1', 'dice2', 'dice3')] == [1, 1, 1]
    assert get_game(gid).schockoutcount == 1


@pytest.mark.parametrize('probability, value, expected', [
    (0.5, 0.49, True),
    (0.5, 0.5, False),
])
def test_decision(monkeypatch, probability, value, expected):
    monkeypatch.setattr(game_endpoints, 'random', lambda: value)
    assert real_decision(probability) is expected


# POST /api/game/<gid>/user/<uid>/finisch
def test_finish_throwing(client, started_game, emitted):
    gid, (admin_id, bob_id, carl_id) = started_game
    roll(client, gid, admin_id)
    response = finish(client, gid, admin_id)
    assert response.status_code == 200
    assert get_game(gid).move_user_id == bob_id
    assert emitted[-1]['event'] == 'reload_game'


def test_finish_without_rolling(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = finish(client, gid, admin_id)
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'Du musst mindestens einmal würfeln!'


def test_finish_not_your_turn(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    set_dice(bob_id, 2, 3, 4)
    response = finish(client, gid, bob_id)
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'Du bist nicht dran!'


def test_finish_skips_passive_players(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    client.post('/api/game/{}/user/{}/passiv'.format(gid, bob_id), json={'userstate': True})
    roll(client, gid, admin_id)
    finish(client, gid, admin_id)
    assert get_game(gid).move_user_id == carl_id


# POST /api/game/<gid>/user/<uid>/passiv
def test_set_user_passive(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.post('/api/game/{}/user/{}/passiv'.format(gid, bob_id), json={'userstate': 'true'})
    assert response.status_code == 201
    assert get_user(bob_id).passive is True
    client.post('/api/game/{}/user/{}/passiv'.format(gid, bob_id), json={'userstate': False})
    assert get_user(bob_id).passive is False


def test_set_user_passive_requires_userstate(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.post('/api/game/{}/user/{}/passiv'.format(gid, bob_id), json={})
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'Request must include userstate'


# POST /api/game/<gid>/user/<uid>/visible
def test_pull_up_dice_cup(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.post('/api/game/{}/user/{}/visible'.format(gid, bob_id), json={'visible': True})
    assert response.status_code == 201
    bob = get_user(bob_id)
    assert bob.dice1_visible and bob.dice2_visible and bob.dice3_visible
    assert get_game(gid).message is None


def test_all_dice_cups_up_waits_for_chips(client, started_game):
    gid, users = started_game
    for uid in users:
        client.post('/api/game/{}/user/{}/visible'.format(gid, uid), json={'visible': True})
    assert get_game(gid).message == 'Warten auf Vergabe der Chips!'


def test_pull_up_dice_cup_requires_visible(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.post('/api/game/{}/user/{}/visible'.format(gid, bob_id), json={})
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'Request must include visible'


# POST /api/game/<gid>/user/<uid>/diceturn
def test_turn_two_sixes(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    set_dice(admin_id, 6, 3, 6)
    response = client.post('/api/game/{}/user/{}/diceturn'.format(gid, admin_id), json={'count': 1})
    assert response.status_code == 201
    assert response.get_json() == {'dice1': 1, 'dice2': 3, 'dice3': None}
    # a turned dice must be rolled again before finishing
    response = finish(client, gid, admin_id)
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'Nach dem Verwandeln von Sechsen in Einsen musst Du nochmal würfeln'


def test_turn_three_sixes(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    set_dice(admin_id, 6, 6, 6)
    response = client.post('/api/game/{}/user/{}/diceturn'.format(gid, admin_id), json={'count': 2})
    assert response.status_code == 201
    assert response.get_json() == {'dice1': 1, 'dice2': 1, 'dice3': None}


@pytest.mark.parametrize('dice, data, message', [
    ((6, 3, 4), {'count': 1}, 'Keine zwei Sechsen gefunden'),
    ((6, 6, 4), {'count': 2}, 'Keine drei Sechsen gefunden'),
    ((6, 6, 6), {'count': 3}, 'count value not 1 or 2'),
    ((6, 6, 6), {}, 'count not in data'),
])
def test_turn_dice_invalid(client, started_game, dice, data, message):
    gid, (admin_id, bob_id, carl_id) = started_game
    set_dice(admin_id, *dice)
    response = client.post('/api/game/{}/user/{}/diceturn'.format(gid, admin_id), json=data)
    assert response.status_code == 400
    assert response.get_json()['Message'] == message


def test_turn_dice_not_your_turn(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    set_dice(bob_id, 6, 6, 3)
    response = client.post('/api/game/{}/user/{}/diceturn'.format(gid, bob_id), json={'count': 1})
    assert response.status_code == 400
    assert response.get_json()['Message'] == 'Du bist nicht dran!'


# PUT /api/game/<gid>/sort
def test_sort_dice(client, started_game):
    gid, users = started_game
    for uid in users:
        set_dice(uid, 5, 1, 3)
        client.post('/api/game/{}/user/{}/visible'.format(gid, uid), json={'visible': True})
    response = client.put('/api/game/{}/sort'.format(gid), json={'admin_id': users[0]})
    assert response.status_code == 200
    for uid in users:
        user = get_user(uid)
        assert (user.dice1, user.dice2, user.dice3) == (1, 3, 5)


def test_sort_dice_before_all_revealed(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    response = client.put('/api/game/{}/sort'.format(gid), json={'admin_id': admin_id})
    assert response.status_code == 403


def test_sort_dice_requires_admin_id(client, started_game):
    gid, _ = started_game
    response = client.put('/api/game/{}/sort'.format(gid), json={})
    assert response.status_code == 400
    assert response.get_json()['message'] == 'must include admin_id'
