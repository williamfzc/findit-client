from findit_client import FindItClient

find_it_client = FindItClient()

TARGET_PATH = r'tests/pics/screen.png'
TEMPLATE_NAME = r'wechat_logo.png'


def test_heartbeat():
    assert find_it_client.heartbeat()


def test_analyse_with_path():
    result = find_it_client.analyse_with_path(TARGET_PATH, TEMPLATE_NAME)
    assert 'request' in result
    assert 'response' in result
    assert 'msg' in result
    assert 'status' in result

    assert 'extras' in result['request']
    assert 'template_name' in result['request']
    assert 'data' in result['response']


def test_check_exist_with_path():
    result = find_it_client.check_exist_with_path(TARGET_PATH, TEMPLATE_NAME, 0.95)
    assert result
