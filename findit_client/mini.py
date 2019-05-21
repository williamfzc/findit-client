# -*- coding:utf-8 -*-
from findit_client.base import FindItBaseClient


class FindItClient(FindItBaseClient):
    """
    this client only offers min functions (no opencv needed)
    """
    pass


if __name__ == '__main__':
    cli = FindItClient(host='127.0.0.1', port=9410)
    assert cli.heartbeat()
    result = cli.analyse_with_path(u'../tests/pics/screen.png', u'wechat_logo.png')
    print(result)
