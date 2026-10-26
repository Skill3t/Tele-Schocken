# Backend Tests 🧪

Pytest suite for the Flask backend and its JSON API (`/api/...`).

## Setup

From the `backend/` directory:

```bash
python3 -m venv .venv-test
source .venv-test/bin/activate
pip install -r requirements-test.txt
```

`requirements-test.txt` contains versions that install on current Python
(tested with 3.12). The original pins in `requirements.txt` are too old to build there.

No `config.py`, MySQL server or mail server is needed: the tests register their own
config with an in-memory SQLite database (see `tests/conftest.py`).

## Run

From the `backend/` directory:

```bash
python -m pytest                                     # all tests
python -m pytest -q -p no:warnings                   # short output, without deprecation warnings
python -m pytest tests/test_game_endpoints.py        # one file
python -m pytest -k transfer                         # tests whose name contains "transfer"
python -m pytest tests/test_admin_endpoints.py::test_play_final -v   # a single test
```

## Test files

| File | Covers |
| --- | --- |
| `test_admin_endpoints.py` | create / start game, chip transfers, losing a half, final, remove player, change admin, back to waiting |
| `test_game_endpoints.py` | game state, join, roll dice, finish turn, passive players, reveal dice, turn sixes, sort dice |
| `test_routes.py` | HTML pages (`/`, `/game_waiting/<gid>`, `/game/<gid>`) render |

## Fixtures (`conftest.py`)

| Fixture | What it does |
| --- | --- |
| `app` | app context with freshly created tables, dropped after each test |
| `client` | Flask test client |
| `create_game(name)` | creates a game via the API, returns `(uuid, admin_id)` |
| `add_user(gid, name)` | joins a player via the API, returns the user id |
| `started_game` | started game with the players `admin`, `bob`, `carl`; `admin` moves first. Returns `(uuid, [admin_id, bob_id, carl_id])` |
| `emitted` | *(autouse)* replaces socket.io `emit` and records the events, e.g. `emitted[-1]['event'] == 'reload_game'` |
| `no_falling_dice` | *(autouse)* dice never fall from the table; patch `game_endpoints.decision` in a test to change that |

The helpers `get_game(gid)` and `get_user(uid)` in `conftest.py` reload objects from the
database, so assertions see the state written by the request.

## Writing a new test

```python
from tests.conftest import get_game


def test_finish_throwing(client, started_game):
    gid, (admin_id, bob_id, carl_id) = started_game
    client.post('/api/game/{}/user/{}/dice'.format(gid, admin_id),
                json={'dice1': True, 'dice2': True, 'dice3': True})
    response = client.post('/api/game/{}/user/{}/finisch'.format(gid, admin_id))
    assert response.status_code == 200
    assert get_game(gid).move_user_id == bob_id
```

Randomness can be controlled with `monkeypatch`, e.g.
`monkeypatch.setattr(game_endpoints, 'randint', lambda a, b: 1)` for a schockout.
