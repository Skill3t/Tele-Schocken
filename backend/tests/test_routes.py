import json
from app import app, db
from app.models import Game

gameid = ''
admin_id = None


def test_endpoint_route():
    client = app.test_client()
    url = '/'
    response = client.get(url)
    assert response.status_code == 200
    assert b'Tele-Schocken Beta' in response.data


def test_endpoint_game():
    # delete all data from db
    all_games = Game.query.all()
    for game in all_games:
        for user in game.users:
            db.session.delete(user)
            db.session.commit()
        db.session.delete(game)
        db.session.commit()
    client = app.test_client()
    url = '/api/game'
    mock_request_data = {
        'name': 'jimbo10',
    }
    response = client.post(url, data=json.dumps(mock_request_data), content_type='application/json',)
    data = json.loads(response.get_data(as_text=True))
    '''
    {
      "Link": "tele-schocken.de/a8a5fbc2-706e-11ea-825e-fa00a8584800",
      "UUID": "a8a5fbc2-706e-11ea-825e-fa00a8584800",
      "Admin_Id": 11
    }
    '''
    assert data['Link']
    assert data['UUID']
    global gameid
    gameid = data['UUID']
    assert data['Admin_Id']
    global admin_id
    admin_id = data['Admin_Id']
    assert response.status_code == 201
    response = client.post(url, data=json.dumps(mock_request_data), content_type='application/json',)
    data = json.loads(response.get_data(as_text=True))
    # Error Case
    assert response.status_code == 400
    assert data['Message']
    assert data['Message'] == 'username in use!'


def test_endpoint_game2():
    global gameid
    url = '/api/game/'+gameid
    client = app.test_client()
    response = client.get(url)
    assert response.status_code == 200
    data = json.loads(response.get_data(as_text=True))
    assert data['Stack']
    assert data['State']
    assert data['Game_Half_Count'] == 0
    assert data['Move'] is None
    assert data['Message'] is None
    assert data['First'] is None
    global admin_id
    assert data['Admin'] == admin_id
    assert data['User']
    # Error Case
    url = '/api/game/fake'
    response = client.get(url)
    assert response.status_code == 404
    data = json.loads(response.get_data(as_text=True))
    assert data['Message']
    assert data['Message'] == 'Game id not in Database'
