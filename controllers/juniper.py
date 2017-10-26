from __future__ import print_function

from tornado.concurrent import run_on_executor
from tornado.web import asynchronous
from utils.ansible_controller import AnsibleController
from models import ansible_model as m

import sys
sys.path.append('.')


class JuniperCommandsController(AnsibleController):

    async def get(self):
        eg = dict()
        eg['host'] = dict(necessary=True, type='string or list[string,]')
        eg['port'] = dict(necessary=False, type='int', default=22, )
        eg['user'] = dict(necessary=True, type='dict', name=dict(default='root'), password=dict(default=None))
        eg['command'] = dict(necessary=True, type='string', eg='ls')
        eg['display'] = dict(necessary=False, type='string', eg='json|xml|set', default='text',
                             warning='when command is not [show ***], this must be necessary and format must be json')

        self.write(self.return_json(0, eg))

    @run_on_executor
    @asynchronous
    async def post(self):
        try:
            host = self.vars['host']
            port = self.vars['port'] if 'port' in self.vars else 22
            command = self.vars['command']
            display = self.vars['display'] if 'display' in self.vars else 'text'
            s = m.Juniper()
            s.commands(command, display)
            tasks = list()
            tasks.append(s.ansible_task())
            result = await self.run_playbook(host, self.user, tasks, port=port, connection='local')
        except Exception as ex:
            self.write(self.return_json(-1, ex.args))
        else:
            self.write(result)
