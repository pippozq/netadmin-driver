from utils.ansible_controller import AnsibleController
from models import ansible_model as m

import sys

sys.path.append('.')


class AnsiblePingController(AnsibleController):
    async def get(self):
        eg = dict()
        eg['hosts'] = dict(necessary=True, type='string or string,string,string')
        eg['user'] = dict(necessary=False, type='string', default='root')

        self.write(self.return_json(0, eg))

    async def post(self):
        if self.vars:
            try:
                hosts = self.vars['hosts']
                p = m.Ping()
                tasks = list()
                tasks.append(p.ansible_task())
                result = await self.run_playbook(hosts, self.user, tasks)
            except KeyError as ke:
                self.write(self.return_json(-1, 'KeyError:{}'.format(ke.args)))
            except Exception as ex:
                self.write(self.return_json(-1, ex.args))
            else:
                self.write(result)
        else:
            self.write(self.return_json(-1, 'invalid json'))


class AnsibleShellController(AnsibleController):
    async def get(self):
        eg = dict()
        eg['hosts'] = dict(necessary=True, type='string or string,string,string')
        eg['user'] = dict(necessary=False, type='dict', name=dict(default='root'), password=dict(default=None))
        eg['command'] = dict(necessary=False, type='string', eg='ls')

        self.write(self.return_json(0, eg))

    async def post(self):
        if self.vars:
            try:
                hosts = self.vars['hosts']
                command = self.vars['command']
                s = m.Shell(command)
                tasks = list()
                tasks.append(s.ansible_task())
                result = await self.run_playbook(hosts, self.user, tasks)
            except KeyError as ke:
                self.write(self.return_json(-1, 'KeyError:{}'.format(ke.args)))
            except Exception as ex:
                self.write(self.return_json(-1, ex.args))
            else:
                self.write(result)
        else:
            self.write(self.return_json(-1, 'invalid json'))
