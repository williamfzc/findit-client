# -*- coding:utf-8 -*-
import requests
import json
import copy
from findit_client import logger as logger_mod
from logzero import logger


class FindItBaseClient(object):
    def __init__(self, host=None, port=None, **default_args):
        host = host or '127.0.0.1'
        port = port or 9410
        self.url = 'http://{}:{}'.format(host, port)

        # default args
        self.default_extra_args = {
            'engine_template_cv_method_name': 'cv2.TM_CCOEFF_NORMED',
            'pro_mode': True,
        }
        self.default_extra_args.update(default_args)

        assert self.heartbeat(), 'heartbeat check failed. make sure your findit-server is started.'
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
        resp_content = resp.text
        assert 'OK' in resp_content, 'error happened'.format(resp_content)
        resp_dict = resp.json()
        resp_dict['request']['extras'] = json.loads(resp_dict['request']['extras'])

        logger.info('response: {}'.format(resp_content))
        return resp_dict

    def analyse_with_path(self, target_pic_path, template_pic_name, **extra_args):
        """ return full response """
        with open(target_pic_path, 'rb') as f:
            pic_data = f.read()

        final_extra_args = copy.deepcopy(self.default_extra_args)
        final_extra_args.update(extra_args)

        return self._request(
            arg_dict={
                'target_pic_path': target_pic_path,
                'template_name': template_pic_name,
                'extras': json.dumps(final_extra_args),
            },
            pic_data=pic_data,
        )

    @staticmethod
    def _fix_response(response):
        if ('data' not in response) and ('response' in response):
            return response['response']
        return response

    def check_exist_with_path(self, target_pic_path, template_pic_name, threshold, **extra_args):
        """ return true or false """
        result = self.analyse_with_path(target_pic_path, template_pic_name, **extra_args)
        return self.check_exist_with_resp(result, threshold)

    def check_exist_with_resp(self, response, threshold):
        """ return true or false """
        response = self._fix_response(response)
        match_result = self.get_template_engine_result_with_resp(response)['raw']['max_val']
        logger.info('matching result is: {}, and threshold is: {}'.format(match_result, threshold))
        return match_result > threshold

    @staticmethod
    def get_template_engine_result_with_resp(response):
        return list(response['data'].values())[0]['TemplateEngine']

    def get_target_point_with_path(self, target_pic_path, template_pic_name, threshold=None, **extra_args):
        """ return target position if existed, else raise Error """
        result = self.analyse_with_path(target_pic_path, template_pic_name, **extra_args)
        if threshold:
            assert self.check_exist_with_resp(result, threshold)
        return self.get_target_point_with_resp(result)

    def get_target_point_list_with_path(self, target_pic_path, template_pic_name, threshold=None, **extra_args):
        result = self.analyse_with_path(target_pic_path, template_pic_name, **extra_args)
        if threshold:
            assert self.check_exist_with_resp(result, threshold)
        return self.get_target_point_list_with_resp(result)

    def get_target_point_with_resp(self, response, threshold=None):
        """ return target position if existed, else raise Error """
        response = self._fix_response(response)
        if threshold:
            assert self.check_exist_with_resp(response, threshold)
        return self.get_template_engine_result_with_resp(response)['raw']['max_loc']

    def get_target_point_list_with_resp(self, response, threshold=None):
        response = self._fix_response(response)
        if threshold:
            assert self.check_exist_with_resp(response, threshold)
        return self.get_template_engine_result_with_resp(response)['raw']['all']
