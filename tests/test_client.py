from findit_client import FindItClient

find_it_client = FindItClient()


def test_heartbeat():
    assert find_it_client.heartbeat()


def test_analyse_with_path():
    result = find_it_client.analyse_with_path('tests/pics/screen.png', 'wechat_logo.png')
    assert 'request' in result
    assert 'response' in result
    assert 'msg' in result
    assert 'status' in result

    assert 'extras' in result['request']
    assert 'template_name' in result['request']
    assert 'data' in result['response']
