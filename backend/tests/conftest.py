"""
conftest.py
====================================
Shared pytest fixtures for the backend API tests.

The app imports ``Config`` from a local (gitignored) ``config`` module that
points to MySQL. For the tests a stand-in module with an in-memory SQLite
database is registered before ``app`` is imported.
"""
import sys
import types
from typing import Any, Callable, Dict, Iterator, List, Optional, Tuple

import pytest
from flask import Flask
from flask.testing import FlaskClient


class TestConfig(object):
    SECRET_KEY = 'test'
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SUPPRESS_SEND = True


config_module = types.ModuleType('config')
config_module.Config = TestConfig
sys.modules['config'] = config_module

from app import app as flask_app, db  # noqa: E402
from app.api import admin_endpoints, game_endpoints  # noqa: E402
from app.models import Game, User  # noqa: E402

CreateGame = Callable[..., Tuple[str, int]]
AddUser = Callable[[str, str], int]
StartedGame = Tuple[str, List[int]]


@pytest.fixture
def app() -> Iterator[Flask]:
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture(autouse=True)
def emitted(monkeypatch: pytest.MonkeyPatch) -> List[Dict[str, Any]]:
    """Replace the socket.io ``emit`` and record the emitted events instead."""
    events: List[Dict[str, Any]] = []

    def fake_emit(event: str, data: Any = None, **kwargs: Any) -> None:
        events.append({'event': event, 'data': data, **kwargs})

    monkeypatch.setattr(game_endpoints, 'emit', fake_emit)
    monkeypatch.setattr(admin_endpoints, 'emit', fake_emit)
    return events


@pytest.fixture(autouse=True)
def no_falling_dice(monkeypatch: pytest.MonkeyPatch) -> None:
    """Dice never fall from the table unless a test says otherwise."""
    monkeypatch.setattr(game_endpoints, 'decision', lambda probability: False)


@pytest.fixture
def create_game(client: FlaskClient) -> CreateGame:
    """Create a game via the API and return (uuid, admin_id)."""
    def _create_game(name: str = 'admin') -> Tuple[str, int]:
        response = client.post('/api/game', json={'name': name})
        assert response.status_code == 201
        data = response.get_json()
        return data['UUID'], data['Admin_Id']
    return _create_game


@pytest.fixture
def add_user(client: FlaskClient) -> AddUser:
    """Add a user to a game via the API and return the new user id."""
    def _add_user(gid: str, name: str) -> int:
        response = client.post('/api/game/{}/user'.format(gid), json={'name': name})
        assert response.status_code == 200
        return next(u['Id'] for u in response.get_json()['User'] if u['Name'] == name)
    return _add_user


@pytest.fixture
def started_game(client: FlaskClient, create_game: CreateGame, add_user: AddUser) -> StartedGame:
    """A started game with the players admin, bob and carl.

    The admin moves first so the tests do not depend on the random start player.
    Returns (uuid, [admin_id, bob_id, carl_id]).
    """
    gid, admin_id = create_game('admin')
    bob_id = add_user(gid, 'bob')
    carl_id = add_user(gid, 'carl')
    response = client.post('/api/game/{}/start'.format(gid), json={'stack_max': 13, 'play_final': False})
    assert response.status_code == 201
    game = get_game(gid)
    game.first_user_id = admin_id
    game.move_user_id = admin_id
    db.session.commit()
    return gid, [admin_id, bob_id, carl_id]


def get_game(gid: str) -> Optional[Game]:
    db.session.expire_all()
    return Game.query.filter_by(UUID=gid).first()


def get_user(uid: int) -> Optional[User]:
    db.session.expire_all()
    return User.query.get(uid)
