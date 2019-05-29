import cv2
import os

from findit_client import FindItStandardClient

TARGET_PATH = r'tests/pics/screen.png'
TEMPLATE_NAME = r'wechat_logo.png'
PORT = 9410


pic_root = os.path.join(os.path.dirname(__file__), 'pics')
cli = FindItStandardClient(local_mode=True, pic_root=pic_root, python_path='python3')


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


def test_analyse_with_object():
    pic_object = cv2.imread(TARGET_PATH)
    result = cli.analyse_with_object(pic_object, TEMPLATE_NAME)
    assert 'request' in result
    assert 'response' in result
    assert 'msg' in result
    assert 'status' in result

    assert 'extras' in result['request']
    assert 'template_name' in result['request']
    assert 'data' in result['response']


def test_analyse_with_extras():
    result = cli.analyse_with_path(
        TARGET_PATH, TEMPLATE_NAME,
        a='123', b='456', pro_mode=True, engine_template_scale=(1, 4, 10))

    assert 'request' in result
    assert 'response' in result
    assert 'msg' in result
    assert 'status' in result

    assert 'extras' in result['request']
    assert 'a' in result['request']['extras']
    assert 'b' in result['request']['extras']
    assert 'engine_template_scale' in result['request']['extras']


def test_check_exist_with_object():
    pic_object = cv2.imread(TARGET_PATH)
    result = cli.check_exist_with_object(pic_object, TEMPLATE_NAME, 0.95)
    assert result


def test_get_target_point_with_object():
    pic_object = cv2.imread(TARGET_PATH)
    result = cli.get_target_point_with_object(pic_object, TEMPLATE_NAME)
    assert len(result) == 2


def test_get_target_point_list_with_path():
    pic_object = cv2.imread(TARGET_PATH)
    result = cli.get_target_point_list_with_object(pic_object, TEMPLATE_NAME)
    assert len(result) >= 1
