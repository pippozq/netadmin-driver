from utils.ansible_controller import AnsibleController
from models import ansible_model as m

import sys

sys.path.append('.')


class JuniperCommandsController(AnsibleController):
    async def get(self):
        eg = dict()
        eg['WARNNING'] = 'Do Not Support ping, traceroute, use interface: /ansible/juniper/shell'
        eg['hosts'] = dict(necessary=True, type='string or string,string,string')
        eg['port'] = dict(necessary=False, type='int', default=22, )
        eg['user'] = dict(necessary=True, type='dict', name=dict(default='root'), password=dict(default=None))
        eg['command'] = dict(necessary=True, type='string', eg='ls')
        eg['display'] = dict(necessary=False, type='string', eg='json|xml|set', default='text',
                             warning='when command is not [show ***], this must be necessary and format must be json')

        self.write(self.return_json(0, eg))

    async def post(self):
        if self.vars:
            try:
                hosts = self.vars['hosts']
                port = self.vars['port'] if 'port' in self.vars else 22
                command = self.vars['command']
                display = self.vars['display'] if 'display' in self.vars else 'text'
                s = m.Juniper()
                s.commands(command, display)
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
