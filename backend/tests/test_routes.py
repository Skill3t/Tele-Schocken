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


def test_security_headers(client):
    for url in ['/', '/scripts/base.js']:
        response = client.get(url)
        assert response.headers['X-Content-Type-Options'] == 'nosniff', url
        assert response.headers['Referrer-Policy'] == 'strict-origin-when-cross-origin', url
        assert 'camera=()' in response.headers['Permissions-Policy'], url
        assert 'Strict-Transport-Security' not in response.headers, url

    # tele-schocken must stay embeddable in iframes
    response = client.get('/')
    assert 'frame-ancestors' not in response.headers['Content-Security-Policy']
    assert 'X-Frame-Options' not in response.headers


def test_hsts_header_behind_https_proxy(client):
    response = client.get('/', headers={'X-Forwarded-Proto': 'https'})
    assert response.headers['Strict-Transport-Security'] == 'max-age=31536000; includeSubDomains'
