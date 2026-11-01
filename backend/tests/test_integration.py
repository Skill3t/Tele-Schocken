import os
import subprocess
import sys
from datetime import datetime, timedelta

import flask_socketio
import pytest

from app import db, mail
from app.api import admin_endpoints, game_endpoints
from app.api.game_endpoints import socketio
from app.models import Game, Statistic
from tests.conftest import get_game
from tests.test_game_endpoints import set_dice


@pytest.fixture
def real_emit(monkeypatch):
    """Undo the ``emitted`` fixture so events go through Flask-SocketIO."""
    monkeypatch.setattr(game_endpoints, 'emit', flask_socketio.emit)
    monkeypatch.setattr(admin_endpoints, 'emit', flask_socketio.emit)


def received(socket_client, event):
    return [e for e in socket_client.get_received('/game') if e['name'] == event]


# socket.io (Flask-SocketIO / python-socketio)
def test_socket_connect(app, client, real_emit):
    socket_client = socketio.test_client(app, namespace='/game', flask_test_client=client)
    assert socket_client.is_connected('/game')
    assert received(socket_client, 'my_response')[0]['args'][0] == {'data': 'Connected', 'count': 0}


def test_socket_join_room_receives_game_updates(app, client, create_game, real_emit):
    gid, admin_id = create_game()
    socket_client = socketio.test_client(app, namespace='/game', flask_test_client=client)
    socket_client.emit('join', {'room': gid}, namespace='/game')
    assert received(socket_client, 'reload_game')[0]['args'][0]['Admin'] == admin_id

    client.post('/api/game/{}/user'.format(gid), json={'name': 'bob'})
    update = received(socket_client, 'reload_game')
    assert [u['Name'] for u in update[0]['args'][0]['User']] == ['admin', 'bob']


def test_socket_other_room_gets_no_updates(app, client, create_game, real_emit):
    gid, _ = create_game('admin')
    other_gid, _ = create_game('other')
    socket_client = socketio.test_client(app, namespace='/game', flask_test_client=client)
    socket_client.emit('join', {'room': other_gid}, namespace='/game')
    socket_client.get_received('/game')

    client.post('/api/game/{}/user'.format(gid), json={'name': 'bob'})
    assert received(socket_client, 'reload_game') == []


# CLI commands (cronjobs)
def test_cli_create_statistics_archives_old_games(app, create_game, add_user):
    old_gid, _ = create_game('old')
    add_user(old_gid, 'old2')
    new_gid, _ = create_game('new')
    get_game(old_gid).refreshed = datetime.now() - timedelta(days=2)
    db.session.commit()

    result = app.test_cli_runner().invoke(args=['create-statistics'])
    assert result.exit_code == 0
    assert get_game(old_gid) is None
    assert get_game(new_gid) is not None
    statistic = Statistic.query.one()
    assert statistic.usercount == 2
    assert statistic.stack_max == 13


def test_cli_send_new_game_mail(app, create_game):
    gid, _ = create_game()
    with mail.record_messages() as outbox:
        result = app.test_cli_runner().invoke(args=['send_new_game_mail'])
        assert result.exit_code == 0
        assert [m.subject for m in outbox] == ['New Teleschocken Game']
        app.test_cli_runner().invoke(args=['send_new_game_mail'])
        assert len(outbox) == 1
    assert get_game(gid).is_mail_send is True


# HTML forms (Flask-WTF / WTForms / Flask-Bootstrap / Flask-Mail)
def test_feedback_form_sends_mail(client, create_game):
    gid, _ = create_game()
    page = client.get('/game/{}'.format(gid))
    assert b'name="message"' in page.data
    with mail.record_messages() as outbox:
        response = client.post('/game/{}'.format(gid), data={
            'browser': 'Firefox', 'message': 'Hallo <b>Welt</b>', 'mail': 'a@b.de'})
    assert response.status_code == 302
    assert len(outbox) == 1
    assert outbox[0].subject == 'Feedback Teleschocken'
    assert 'Hallo &lt;b&gt;Welt&lt;/b&gt;' in outbox[0].html


def test_feedback_form_requires_message(client, create_game):
    gid, _ = create_game()
    with mail.record_messages() as outbox:
        response = client.post('/game/{}'.format(gid), data={'browser': 'Firefox', 'message': ''})
    assert response.status_code == 200
    assert outbox == []


def test_feedback_form_requires_csrf_token(app, client, create_game, monkeypatch):
    gid, _ = create_game()
    monkeypatch.setitem(app.config, 'WTF_CSRF_ENABLED', True)
    with mail.record_messages() as outbox:
        response = client.post('/game/{}'.format(gid), data={'browser': 'Firefox', 'message': 'x'})
    assert response.status_code == 200
    assert outbox == []


def test_unknown_page_renders_404_template(client, app):
    response = client.get('/does-not-exist')
    assert response.status_code == 404
    assert response.mimetype == 'text/html'


def test_static_files_are_served(client, app):
    assert client.get('/scripts/socket.io.js').status_code == 200


# behaviour kept stable across the Flask 1 -> 3 upgrade
def test_request_without_json_body_is_a_normal_bad_request(client, app):
    response = client.post('/api/game', data='name=x', content_type='application/x-www-form-urlencoded')
    assert response.status_code == 400
    assert response.get_json()['message'] == 'must include name field'


def test_empty_response_is_an_empty_object(client, started_game):
    gid, users = started_game
    for uid in users:
        set_dice(uid, 5, 1, 3)
        client.post('/api/game/{}/user/{}/visible'.format(gid, uid), json={'visible': True})
    response = client.put('/api/game/{}/sort'.format(gid), json={'admin_id': users[0]})
    assert response.status_code == 200
    assert response.get_json() == {}


def test_unknown_user_id_returns_404(client, started_game):
    gid, _ = started_game
    response = client.post('/api/game/{}/user/99999/finisch'.format(gid))
    assert response.status_code == 404


def test_status_enum_round_trip(app, create_game):
    gid, _ = create_game()
    game = get_game(gid)
    game.status = game.status.PLAYFINAL
    db.session.commit()
    assert Game.query.filter_by(UUID=gid).one().status.value == 'playfinal'


# "flask run" can not serve gevent Socket.IO and is blocked (see game_endpoints.py)
def _flask(tmp_path, *args):
    (tmp_path / 'config.py').write_text(
        "class Config(object):\n"
        "    SECRET_KEY = 'test'\n"
        "    SQLALCHEMY_DATABASE_URI = 'sqlite://'\n")
    backend = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env = dict(os.environ, PYTHONPATH=str(tmp_path), FLASK_APP='teleschocken.py')
    return subprocess.run([sys.executable, '-m', 'flask', *args], cwd=backend, env=env,
                          capture_output=True, text=True, timeout=60)


def test_flask_run_is_blocked(tmp_path):
    result = _flask(tmp_path, 'run', '-p', '5999')
    assert result.returncode != 0
    assert 'python teleschocken.py' in result.stderr


def test_other_flask_commands_still_work(tmp_path):
    result = _flask(tmp_path, 'db', '--help')
    assert result.returncode == 0
    assert 'upgrade' in result.stdout
