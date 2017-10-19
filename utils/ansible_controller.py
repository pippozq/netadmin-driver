from __future__ import print_function

from tornado.web import RequestHandler
from tornado.gen import coroutine
from tornado.escape import json_decode
from concurrent.futures import ThreadPoolExecutor


class BaseController(RequestHandler):
    executor = ThreadPoolExecutor(30)

    @coroutine
    def prepare(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            try:
                self.request.body = json_decode(self.request.body)
            except ValueError:
                self.write(self.return_json(-1, 'valid json'))

    def return_json(self, code, msg):
        return_dict = dict()
        return_dict['status'] = str(code)
        return_dict['msg'] = msg
        return return_dict