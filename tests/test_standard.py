import cv2

from findit_client import FindItStandardClient

find_it_client = FindItStandardClient()

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


def test_analyse_with_object():
    pic_object = cv2.imread(TARGET_PATH)
    result = find_it_client.analyse_with_object(pic_object, TEMPLATE_NAME)
    assert 'request' in result
    assert 'response' in result
    assert 'msg' in result
    assert 'status' in result

    assert 'extras' in result['request']
    assert 'template_name' in result['request']
    assert 'data' in result['response']


def test_analyse_with_extras():
    result = find_it_client.analyse_with_path(
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
    result = find_it_client.check_exist_with_object(pic_object, TEMPLATE_NAME, 0.95)
    assert result
