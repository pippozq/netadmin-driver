from __future__ import print_function

from concurrent.futures import ThreadPoolExecutor

import sys
sys.path.append('.')

from .base_controller import BaseController


class AnsibleController(BaseController):
    executor = ThreadPoolExecutor(30)

    def return_json(self, code, msg):
        return_dict = dict()
        return_dict['status'] = code
        return_dict['msg'] = msg
        return return_dict