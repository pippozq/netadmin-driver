from __future__ import print_function

from tornado.concurrent import run_on_executor
from tornado.web import asynchronous
from utils.ansible_controller import AnsibleController
from models import ansible_model as m

import sys
sys.path.append('.')


class AnsiblePingController(AnsibleController):

    async def get(self):
        eg = dict()
        eg['host'] = dict(necessary=True, type='string or list[string,]')
        eg['user'] = dict(necessary=False, type='string', default='root')

        self.write(self.return_json(0, eg))

    @run_on_executor
    @asynchronous
    async def post(self):
        try:
            host = self.vars['host']
            p = m.Ping()
            tasks = list()
            tasks.append(p.ansible_task())
            result = await self.run_playbook(host, self.user, tasks)
        except Exception as ex:
            self.write(self.return_json(-1, ex.args))
        else:
            self.write(result)


class AnsibleShellController(AnsibleController):

    async def get(self):
        eg = dict()
        eg['host'] = dict(necessary=True, type='string or list[string,]')
        eg['user'] = dict(necessary=False, type='dict', name=dict(default='root'), password=dict(default=None))
        eg['command'] = dict(necessary=False, type='string', eg='ls')

        self.write(self.return_json(0, eg))

    @run_on_executor
    @asynchronous
    async def post(self):
        try:
            host = self.vars['host']
            command = self.vars['command']
            s = m.Shell(command)
            tasks = list()
            tasks.append(s.ansible_task())
            result = await self.run_playbook(host, self.user, tasks)
        except Exception as ex:
            self.write(self.return_json(-1, ex.args))
        else:
            self.write(result)