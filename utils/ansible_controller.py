from __future__ import print_function

from tornado.web import RequestHandler
from tornado.gen import coroutine
from tornado.options import define, options
from tornado.escape import json_decode
from concurrent.futures import ThreadPoolExecutor

from utils.ansible_task import AnsibleTask

import sys

sys.path.append('.')

define("thread_count", help='thread count', type=int)


class AnsibleController(RequestHandler):
    executor = ThreadPoolExecutor(options.thread_count)
    vars = dict()
    user = dict()

    async def prepare(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            try:
                self.vars = json_decode(self.request.body)
            except ValueError:
                self.vars = None
            else:
                self.user = self.vars['user'] if 'user' in self.vars.keys() else None

    def return_json(self, code, msg):
        return_dict = dict()
        return_dict['status'] = str(code)
        return_dict['msg'] = msg
        return return_dict

    @coroutine
    def run_playbook(self, host, user, tasks, port=22, connection=None):
        play = AnsibleTask(host, user, tasks, port, connection)
        try:
            code = yield self.executor.submit(play.run_ansible_playbook)
        except Exception as ex:
            raise ex
        else:
            result_detail_dict = play.get_result()
            for key in result_detail_dict.keys():
                result_detail_dict[key] = result_detail_dict[key].replace('\\n', '').replace('\\r', '').replace('\\t',
                                                                                                                '')
                result_detail_dict[key] = json_decode(result_detail_dict[key])
            return self.return_json(code, result_detail_dict)
