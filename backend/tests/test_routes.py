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


def test_csp_nonce(client, create_game):
    import re
    gid, _ = create_game()
    for url in ['/', '/game_waiting/{}'.format(gid), '/game/{}'.format(gid)]:
        response = client.get(url)
        html = response.get_data(as_text=True)
        nonce = re.search(r"script-src 'nonce-([^']+)'", response.headers['Content-Security-Policy']).group(1)
        scripts = re.findall(r'<script[^>]*>', html)
        assert scripts
        assert all('nonce="{}"'.format(nonce) in tag and 'src=' in tag for tag in scripts), url
        assert not re.search(r'\son[a-z]+=', html), url
