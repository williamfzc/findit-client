# -*- coding:utf-8 -*-
import requests
import json
import copy
from findit_client import logger as logger_mod
from logzero import logger
import atexit
import time
import subprocess


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

        # raise a error, if server did not work
        if self.server_process.poll() is not None:
            raise RuntimeError('findit server starts failed')

    def stop(self):
        self.server_process.terminate()
        self.server_process.kill()


class FindItResponse(object):
    """ standard response object, for further operations. """

    def __init__(self, raw_dict):
        # check
        self.msg = raw_dict['msg']
        self.status = raw_dict['status']
        assert self.status == 'OK', 'findit server status: {}, msg: {}'.format(self.status, self.msg)

        # parse
        self.request = raw_dict['request']
        self.response = raw_dict['response']

        self.data = self.response['data']
        self.template_data = self._get_template_engine_result()

    # all the functions based on template matching now.
    def _get_template_engine_result(self):
        resp_dict = dict()
        for each_key, each_value in self.data.items():
            resp_dict[each_key] = each_value['TemplateEngine']
        return resp_dict

    def is_target_in_resp(self, target_name):
        return target_name in self._get_template_engine_result()

    def get_template_engine_target_point(self, target_name):
        assert self.is_target_in_resp(target_name), 'target [{}] not in response'.format(target_name)
        target_point_list = self.template_data[target_name]['raw']['all']

        # sometimes target will display multi times in different places
        return target_point_list

    def get_template_engine_target_sim(self, target_name):
        assert self.is_target_in_resp(target_name), 'target [{}] not in response'.format(target_name)
        return self.template_data[target_name]['target_sim']

    def is_target_existed(self, target_name, threshold):
        if not self.is_target_in_resp(target_name):
            return False

        return self.get_template_engine_target_sim(target_name) > threshold


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
        logger.info('response: {}'.format(resp_dict))
        return FindItResponse(resp_dict)

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

    def get_target_point_with_path(self, target_pic_path, template_pic_name_list, threshold=None, **extra_args):
        """ return target position if existed """
        if isinstance(template_pic_name_list, str):
            template_pic_name_list = [template_pic_name_list]

        result = self.analyse_with_path(target_pic_path, template_pic_name_list, **extra_args)

        target_point_list = list()
        for each_template_pic_name in template_pic_name_list:
            if threshold and (result.get_template_engine_target_sim(each_template_pic_name) < threshold):
                continue
            target_point_list.append(result.get_template_engine_target_point(each_template_pic_name))
        return target_point_list
