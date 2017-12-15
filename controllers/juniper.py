from utils.base_controller import BaseController
from tornado.platform.asyncio import to_tornado_future
from tornado.options import define, options
from utils.junos_util import Junos
import multiprocessing
import sys

sys.path.append('.')

define("multiprocess", help='multiprocess number', type=int)


def multiple_execute(func, hosts, user, port, command):
    result_dict = dict()
    result_list = list()
    pool = multiprocessing.Pool(processes=options.multiprocess)
    for host in hosts:
        res = pool.apply_async(func, args=(host, user, port, command))
        result_list.append(res)
    pool.close()
    pool.join()

    for r in result_list:
        res = r.get()
        result_dict[res[1]] = res[2]

    return result_dict


class JuniperCommandsController(BaseController):
    async def get(self):
        eg = dict()
        eg['hosts'] = dict(necessary=True, type='string list')
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
                result = await to_tornado_future(
                    self.executor.submit(multiple_execute, self.execute_command, hosts, self.user, port, command))
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

    @staticmethod
    def execute_command(host, user, port, command):
        dev = Junos(host=host, user=user, port=port)
        success, res = dev.execute_shell(command)
        return success, host, res


class JuniperConfigController(BaseController):
    async def get(self):
        eg = dict()
        eg['hosts'] = dict(necessary=True, type='string list')
        eg['port'] = dict(necessary=False, type='int', default=22, )
        eg['user'] = dict(necessary=True, type='dict', name=dict(default='root'), password=dict(default=None))
        eg['command'] = dict(necessary=True, type='string', eg='ls')
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
                    msg = list()
                    result = await to_tornado_future(
                        self.executor.submit(multiple_execute, self.get_device_result, hosts, user, port,
                                             command_lines.split('\n')))
                except Exception as err:
                    self.write(self.return_json(-1, err.args))
                else:
                    for host in result.keys():
                        msg.append('-----------------------------\n{}\n'.format(host))

                        for r in result[host]:
                            msg.append('{}\n'.format(r))

                    self.write(self.return_json(0, msg))
        else:
            self.write(self.return_json(-1, 'Invalid Json'))

    @staticmethod
    def get_device_result(host, user, port, command_lines):

        d = Junos(host, user, port)
        success = True
        result = list()
        try:
            d.open_connection()
            for line in command_lines:
                if line != "":
                    ok, err_msg = d.run_config(line)
                    if ok:
                        result.append('{} Done'.format(line))
                    else:
                        result.append('{} {}'.format(line, err_msg))
                        success = False
                        break
        except Exception as e:
            success = False
            result.append(e.args)
        finally:
            d.close()
            return success, host, result
