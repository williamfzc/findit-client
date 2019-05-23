import pytest
import subprocess
import time

from findit_client import FindItClient

find_it_client = FindItClient()


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
    result = find_it_client.analyse_with_path('pics/screen.png', 'wechat_logo.png')
    assert 'data' in result
