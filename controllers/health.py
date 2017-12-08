from datetime import datetime
from tornado.options import options
from utils.base_controller import BaseController

import sys

sys.path.append('.')


class HealthController(BaseController):
    async def get(self):
        now_time = datetime.now()
        now_time = now_time.strftime(options.date_fmt)
        check_msg = {
            'service': 'ansible',
            'status': 200,
            'time': now_time
        }
        self.write(check_msg)
