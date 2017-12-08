from utils.base_controller import BaseController
from tornado.platform.asyncio import to_tornado_future
from models import ansible_model as m
from utils.junos_util import Junos
import sys

sys.path.append('.')


# class JuniperCommandsController(BaseController):
#     async def get(self):
#         eg = dict()
#         eg['WARNNING'] = 'Do Not Support ping, traceroute, use interface: /netdriver/juniper/shell'
#         eg['hosts'] = dict(necessary=True, type='string or string,string,string')
#         eg['port'] = dict(necessary=False, type='int', default=22, )
#         eg['user'] = dict(necessary=True, type='dict', name=dict(default='root'), password=dict(default=None))
#         eg['command'] = dict(necessary=True, type='string', eg='ls')
#         eg['display'] = dict(necessary=False, type='string', eg='json|xml|set', default='text',
#                              warning='when command is not [show ***], this must be necessary and format must be json')
# 
#         self.write(self.return_json(0, eg))
# 
#     async def post(self):
#         if self.vars:
#             try:
#                 hosts = self.vars['hosts']
#                 port = self.vars['port'] if 'port' in self.vars else 22
#                 command = self.vars['command']
#                 display = self.vars['display'] if 'display' in self.vars else 'text'
#                 s = m.Juniper()
#                 s.commands(command, display)
#                 tasks = list()
#                 tasks.append(s.ansible_task())
#                 result = await self.run_playbook(hosts, self.user, tasks, port=port, connection='local')
#             except KeyError as ke:
#                 self.write(self.return_json(-1, 'KeyError:{}'.format(ke.args)))
#             except Exception as ex:
#                 self.write(self.return_json(-1, ex.args))
#             else:
#                 self.write(result)
#         else:
#             self.write(self.return_json(-1, 'invalid json'))


class JuniperCommandsController(BaseController):
    async def get(self):
        eg = dict()
        eg['hosts'] = dict(necessary=True, type='string or string,string,string')
        eg['port'] = dict(necessary=False, type='int', default=22, )
        eg['user'] = dict(necessary=True, type='dict', name=dict(default='root'), password=dict(default=None))
        eg['command'] = dict(necessary=True, type='string', eg='ls')

        self.write(self.return_json(0, eg))

    async def post(self):
        msg = list()
        if self.vars:
            try:
                hosts = self.vars['hosts']
                port = self.vars['port'] if 'port' in self.vars else 22
                command = self.vars['command']
                result = dict()
                for host in hosts:
                    dev = Junos(host=host, user=self.user, port=port)
                    success, res = await to_tornado_future(self.executor.submit(dev.execute_shell, command))
                    result[host] = res

            except Exception as ex:
                self.write(self.return_json(-1, ex.args))
            else:
                for host in result.keys():
                    msg.append('-----------------------------\n{}\n'.format(host))

                    for r in result[host].split('\n'):
                        if 'cli ' not in r:
                            msg.append('{}\n'.format(r))

                self.write(self.return_json(0, msg))
        else:
            msg.append(
                'invalid json')
            self.write(self.return_json(-1, msg))


class JuniperConfigController(BaseController):
    async def get(self):
        eg = dict()
        eg['hosts'] = dict(necessary=True, type='string or string,string,string')
        eg['port'] = dict(necessary=False, type='int', default=22, )
        eg['user'] = dict(necessary=True, type='dict', name=dict(default='root'), password=dict(default=None))
        eg['file_content'] = dict(necessary=True, type='string', eg='ls')
        self.write(self.return_json(0, eg))

    async def post(self):
        if self.vars:
            try:
                hosts = self.vars['hosts']
                user = self.vars['user']
                port = self.vars['port'] if 'port' in self.vars.keys() else 22
                command_lines = self.vars['file_content']
            except KeyError as err:
                self.write(self.return_json(-1, 'Json No arg: {}'.format(err)))
            else:
                try:
                    cmd_result = list()
                    for host in hosts:
                        d = Junos(host, user, port)
                        h, j, e = await to_tornado_future(
                            self.executor.submit(self.get_device_result, d, command_lines.split("\n")))
                        r = dict()
                        r[host] = dict(command=j, success=e)
                        cmd_result.append(r)
                except Exception as err:
                    self.write(self.return_json(-1, err.args))
                else:
                    self.write(self.return_json(0, cmd_result))
        else:
            self.write(self.return_json(-1, 'Invalid Json'))

    @staticmethod
    def get_device_result(d, command_lines=list()):
        success = True
        cmd_result = list()
        result_json = dict()
        try:
            d.open_connection()
            for line in command_lines:
                if line != "":
                    ok, err_msg = d.run_config(line)
                    if ok:
                        result_json[line] = 'ok'
                    else:
                        result_json[line] = 'error:{}'.format(err_msg)
                        success = False
                        break
        except Exception as e:
            success = False
            result_json['error'] = e.args
        finally:
            d.close()
            return cmd_result, result_json, success
