from utils.ansible_controller import AnsibleController
from models import ansible_model as m

import sys

sys.path.append('.')


class CiscoCommandsController(AnsibleController):
    async def get(self):
        eg = dict()
        eg['hosts'] = dict(necessary=True, type='string or string,string,string')
        eg['port'] = dict(necessary=False, type='int', default=22, )
        eg['user'] = dict(necessary=True, type='dict', name=dict(default='root'), password=dict(default=None))
        eg['command'] = dict(necessary=True, type='string', eg='ls')

        self.write(self.return_json(0, eg))

    async def post(self):
        if self.vars:
            try:
                hosts = self.vars['hosts']
                port = self.vars['port'] if 'port' in self.vars else 22
                command = self.vars['command']
                s = m.Cisco()
                s.commands(command)
                tasks = list()
                tasks.append(s.ansible_task())
                result = await self.run_playbook(hosts, self.user, tasks, port=port, connection='local')
            except KeyError as ke:
                self.write(self.return_json(-1, 'KeyError:{}'.format(ke.args)))
            except Exception as ex:
                self.write(self.return_json(-1, ex.args))
            else:
                self.write(result)
        else:
            self.write(self.return_json(-1, 'invalid json'))
