from __future__ import print_function

import sys
from datetime import datetime

sys.path.append('.')

from tornado.options import options
from tornado.gen import coroutine

from utils.ansible_controller import AnsibleController


class HealthController(AnsibleController):

    @coroutine
    def get(self):
        now_time = datetime.now()
        now_time = now_time.strftime(options.date_fmt)
        check_msg = {
            'service': 'cmdb-ansible',
            'status': 200,
            'time': now_time
        }
        self.write(check_msg)