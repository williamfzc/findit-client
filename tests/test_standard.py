import pytest
import subprocess
import time
import cv2

from findit_client import FindItStandardClient

find_it_client = FindItStandardClient()


@pytest.fixture(scope="session", autouse=True)
def life_time():
    server_process = subprocess.Popen('python -m findit.server --dir tests/pics', shell=True)
    time.sleep(3)
    yield
    server_process.terminate()
    server_process.kill()


def test_heartbeat():
    assert find_it_client.heartbeat()


def test_analyse_with_path():
    result = find_it_client.analyse_with_path('tests/pics/screen.png', 'wechat_logo.png')
    assert 'data' in result


def test_analyse_with_object():
    pic_object = cv2.imread('tests/pics/screen.png')
    result = find_it_client.analyse_with_object(pic_object, 'wechat_logo.png')
    assert 'data' in result
