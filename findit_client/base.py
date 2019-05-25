# -*- coding:utf-8 -*-
import requests
import json
from findit_client import logger as logger_mod
from logzero import logger


class FindItBaseClient(object):
    def __init__(self, host=None, port=None):
        host = host or '127.0.0.1'
        port = port or 9410
        self.url = 'http://{}:{}'.format(host, port)
        logger.info('client init finished, server url: {}'.format(self.url))

    @staticmethod
    def switch_log(status):
        logger_mod.switch_log(status)

    def heartbeat(self):
        target_url = '{}/'.format(self.url)
        try:
            resp = requests.get(target_url)
            return resp.ok
        except requests.exceptions.ConnectionError:
            return False

    def _request(self, arg_dict, pic_data):
        resp = requests.post(
            '{}/analyse'.format(self.url),
            data=arg_dict,
            files={'file': pic_data}
        )
        resp_dict = resp.json()
        resp_dict['request']['extras'] = json.loads(resp_dict['request']['extras'])
        logger.info('response: {}'.format(json.dumps(resp_dict)))
        return resp_dict

    def analyse_with_path(self, target_pic_path, template_pic_name, **extra_args):
        with open(target_pic_path, 'rb') as f:
            pic_data = f.read()

        return self._request(
            arg_dict={
                'target_pic_path': target_pic_path,
                'template_name': template_pic_name,
                'extras': json.dumps(extra_args),
            },
            pic_data=pic_data,
        )

    def check_exist_with_path(self, target_pic_path, template_pic_name, threshold, **extra_args):
        result = self.analyse_with_path(target_pic_path, template_pic_name, pro_mode=True, **extra_args)
        return self.check_exist_with_resp(result['response'], threshold)

    @staticmethod
    def _fix_response(response):
        if ('data' not in response) and ('response' in response):
            return response['response']
        return response

    def check_exist_with_resp(self, response, threshold):
        response = self._fix_response(response)
        match_result = list(response['data'].values())[0]['TemplateEngine']['raw']['max_val']
        logger.info('matching result is: {}, and threshold is: {}'.format(match_result, threshold))
        return match_result > threshold

    def get_target_point_with_resp(self, response):
        response = self._fix_response(response)
        return list(response['data'].values())[0]['TemplateEngine']['raw']['max_loc']
