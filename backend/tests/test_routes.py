def test_index(client):
    response = client.get('/')
    assert response.status_code == 200


def test_game_waiting_page(client, create_game):
    gid, _ = create_game()
    response = client.get('/game_waiting/{}'.format(gid))
    assert response.status_code == 200


def test_game_page(client, create_game):
    gid, _ = create_game()
    response = client.get('/game/{}'.format(gid))
    assert response.status_code == 200
