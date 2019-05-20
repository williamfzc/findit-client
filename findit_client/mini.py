# -*- coding:utf-8 -*-
import requests
import requests.exceptions

from findit_client.base import FindItBaseClient


class FindItClient(FindItBaseClient):
    def analyse_with_path(self, target_pic_path, template_pic_name):
        with open(target_pic_path, 'rb+') as f:
            pic_data = f.read()
        resp = requests.post(
            '{}/analyse'.format(self.url),
            data={'template_name': template_pic_name},
            files={'file': pic_data}
        )
        return resp.json()


if __name__ == '__main__':
    cli = FindItClient(port=29412)
    assert cli.heartbeat()
    result = cli.analyse_with_path(u'tests/pics/screen.png', u'wechat_logo.png')
    print(result)
