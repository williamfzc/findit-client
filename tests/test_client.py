import os

from findit_client import FindItClient

TARGET_PATH = r'tests/pics/screen.png'
TEMPLATE_NAME = r'wechat_logo.png'
PORT = 9410

pic_root = os.path.join(os.path.dirname(__file__), 'pics')
cli = FindItClient(local_mode=True, pic_root=pic_root, python_path='python3')


def test_heartbeat():
    assert cli.heartbeat()


def test_analyse_with_path():
    result = cli.analyse_with_path(TARGET_PATH, TEMPLATE_NAME)
    assert 'request' in result
    assert 'response' in result
    assert 'msg' in result
    assert 'status' in result

    assert 'extras' in result['request']
    assert 'template_name' in result['request']
    assert 'data' in result['response']


def test_check_exist_with_path():
    result = cli.check_exist_with_path(TARGET_PATH, TEMPLATE_NAME, 0.95)
    assert result


def test_get_target_point_with_path():
    result = cli.get_target_point_with_path(TARGET_PATH, TEMPLATE_NAME)
    assert len(result) == 2


def test_get_target_point_list_with_path():
    result = cli.get_target_point_list_with_path(TARGET_PATH, TEMPLATE_NAME)
    assert len(result) >= 1
