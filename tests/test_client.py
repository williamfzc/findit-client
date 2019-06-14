import os
import pytest

from findit_client import FindItClient

TARGET_PATH = r'tests/pics/screen.png'
TEMPLATE_NAME = r'wechat_logo.png'
PORT = 9410

pic_root = os.path.join(os.path.dirname(__file__), 'pics')
cli = None


@pytest.fixture(scope="session", autouse=True)
def run_at_beginning(request):
    global cli
    cli = FindItClient(local_mode=True, pic_root=pic_root, python_path='python')
    yield
    cli.local_server.stop()


def test_heartbeat():
    assert cli.heartbeat()


def test_analyse_with_path():
    result = cli.analyse_with_path(TARGET_PATH, TEMPLATE_NAME)

    arg_list = ['msg', 'status', 'request', 'response', 'data', 'template_data']
    for each in arg_list:
        assert hasattr(result, each)


def test_analyse_with_extras():
    result = cli.analyse_with_path(
        TARGET_PATH, TEMPLATE_NAME,
        a='123', b='456', pro_mode=True, engine_template_scale=(1, 4, 10))

    request_dict = result.request

    assert 'extras' in request_dict
    assert 'a' in request_dict['extras']
    assert 'b' in request_dict['extras']
    assert 'engine_template_scale' in request_dict['extras']
