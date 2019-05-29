# -*- coding:utf-8 -*-
import requests
import json
import copy
from findit_client import logger as logger_mod
from logzero import logger
import atexit
import time
import subprocess
import pprint


class FindItLocalServer(object):
    DEFAULT_PYTHON = 'python'
    DEFAULT_PORT = 9410

    def __init__(self, port=None, pic_root=None, python_path=None, *_, **__):
        assert pic_root, 'local mode requires pic_root'

        self.pic_root = pic_root
        self.port = port or self.DEFAULT_PORT
        self.python_path = python_path or self.DEFAULT_PYTHON

        self.server_process = None

    def start(self):
        start_cmd = '{} -m findit.server --dir {} --port {}'.format(
            self.python_path,
            self.pic_root,
            self.port,
        )
        logger.info('local mode enabled. start cmd: [{}]'.format(start_cmd))

        self.server_process = subprocess.Popen(start_cmd, shell=True)
        time.sleep(5)

    def stop(self):
        self.server_process.terminate()
        self.server_process.kill()


class FindItBaseClient(object):
    def __init__(self, host=None, port=None, local_mode=None, pic_root=None, python_path=None, **default_args):
        host = host or '127.0.0.1'
        port = port or 9410
        self.url = 'http://{}:{}'.format(host, port)

        # local mode will start a local server
        if local_mode:
            try:
                import findit
            except ImportError:
                raise ImportError('local mode requires findit. install it first.')

            self.switch_log(True)
            server = FindItLocalServer(port, pic_root, python_path)
            server.start()
            atexit.register(server.stop)

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
        resp_dict = resp.json()
        resp_dict['request']['extras'] = json.loads(resp_dict['request']['extras'])
        assert resp_dict['status'] == 'OK', 'error happened: {}'.format(pprint.saferepr(resp_dict))
        logger.info('response: {}'.format(resp_dict))
        return resp_dict

    def analyse_with_path(self, target_pic_path, template_pic_name, **extra_args):
        """ return full response """
        with open(target_pic_path, 'rb') as f:
            pic_data = f.read()

        # support multi pictures in single request
        if isinstance(template_pic_name, (tuple, list)):
            template_pic_name = ','.join(template_pic_name)

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
