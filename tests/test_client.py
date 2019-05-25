import subprocess
import time
import pytest

from findit_client import FindItClient

TARGET_PATH = r'tests/pics/screen.png'
TEMPLATE_NAME = r'wechat_logo.png'
PORT = 9410
find_it_client = None


@pytest.fixture(scope="session", autouse=True)
def life_time():
    server_process = subprocess.Popen('python -m findit.server --dir tests/pics --port {}'.format(PORT), shell=True)
    time.sleep(3)
    global find_it_client
    find_it_client = FindItClient(port=PORT)
    yield
    server_process.terminate()
    server_process.kill()


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


def test_get_target_point_with_path():
    result = find_it_client.get_target_point_with_path(TARGET_PATH, TEMPLATE_NAME)
    assert len(result) == 2
