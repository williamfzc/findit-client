import cv2
import os
import pytest

from findit_client import FindItStandardClient

TARGET_PATH = r'tests/pics/screen.png'
TEMPLATE_NAME = r'wechat_logo.png'
PORT = 9410

pic_root = os.path.join(os.path.dirname(__file__), 'pics')
cli = None


@pytest.fixture(scope="session", autouse=True)
def run_at_beginning(request):
    global cli
    cli = FindItStandardClient(local_mode=True, pic_root=pic_root, python_path='python')
    yield
    cli.local_server.stop()


def test_heartbeat():
    assert cli.heartbeat()


def test_analyse_with_path():
    result = cli.analyse_with_path(TARGET_PATH, TEMPLATE_NAME)

    arg_list = ['msg', 'status', 'request', 'response', 'data', 'template_data']
    for each in arg_list:
        assert hasattr(result, each)


def test_analyse_with_object():
    pic_object = cv2.imread(TARGET_PATH)
    result = cli.analyse_with_object(pic_object, TEMPLATE_NAME)
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


def test_check_exist_with_object():
    pic_object = cv2.imread(TARGET_PATH)
    result = cli.analyse_with_object(pic_object, TEMPLATE_NAME)
    assert result.get_template_engine_target_sim(TEMPLATE_NAME) > 0.95


def test_get_target_point_with_object():
    pic_object = cv2.imread(TARGET_PATH)
    result = cli.get_target_point_with_object(pic_object, TEMPLATE_NAME)

    # is a target list, only one target we sent
    assert len(result) == 1
    # is a point list, only one point detected on screen ( in this sample )
    assert len(result[0]) == 1
    # is a point
    assert len(result[0][0]) == 2
