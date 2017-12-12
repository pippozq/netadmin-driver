from tornado.options import define, options
from tornado.platform.asyncio import to_tornado_future
from utils.base_controller import BaseController
from models import ansible_model as m

import sys
import os

sys.path.append('.')

define("cisco_temp_path", help='cisco configuration file temporary path', type=str)


class CiscoCommandsController(BaseController):
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
                msg = list()
                for host in hosts:
                    msg.append('-------------------------------------\n{}\n'.format(host))
                    if result['msg'][host]['status'] == "0":
                        for item in result['msg'][host]['msg'][0]:
                            msg.append('{}\n'.format(item))
                    else:
                        msg.append('Command Error, Status: {}, Error: {}\n'.format(
                            result['msg'][host]['status'], result['msg'][host]['msg']))
                self.write(self.return_json(0, msg))
        else:
            self.write(self.return_json(-1, 'invalid json'))


class CiscoConfigController(BaseController):
    async def get(self):
        eg = dict()
        eg['hosts'] = dict(necessary=True, type='string or string,string,string')
        eg['port'] = dict(necessary=False, type='int', default=22, )
        eg['user'] = dict(necessary=True, type='dict', name=dict(default='root'), password=dict(default=None))
        eg['file_content'] = dict(necessary=True, type='string', eg='cisco configuration content')
        eg['blob_id'] = dict(necessary=True, type='string', eg='gitlab file id')

        self.write(self.return_json(0, eg))

    async def post(self):
        if self.vars:
            try:
                hosts = self.vars['hosts']
                port = self.vars['port'] if 'port' in self.vars else 22
                file_content = self.vars['file_content']
                blob_id = self.vars['blob_id']
                await to_tornado_future(self.executor.submit(self.write_to_file, blob_id, file_content))
                s = m.Cisco()
                s.config('{}/{}'.format(options.cisco_temp_path, blob_id))
                tasks = list()
                tasks.append(s.ansible_task())

                result = await self.run_playbook(hosts, self.user, tasks, port=port, connection='local')
            except KeyError as ke:
                self.write(self.return_json(-1, 'KeyError:{}'.format(ke.args)))
            except Exception as ex:
                self.write(self.return_json(-1, ex.args))
            else:
                await to_tornado_future(self.executor.submit(self.delete_temp_file, blob_id))
                msg = list()
                for host in hosts:
                    msg.append('-----------------------------\n{}\n'.format(host))

                    if result['msg'][host]['status'] == '0':
                        if not result['msg'][host]['msg']['failed']:
                            if result['msg']['msg']['changed']:
                                if 'updates' in result['msg'][host]['msg']:
                                    for line in result['msg'][host]['msg']['updates']:
                                        msg.append('Command: {} Status: Execute Success\n'.format(line))
                                else:
                                    msg.append('Nothing Updated\n')
                            else:
                                msg.append(
                                    'Nothing Updated\n')
                        else:
                            msg.append(
                                'Error:{}\n'.format(result['msg'][host]['msg']['msg']))
                    else:
                        msg.append(
                            'Error:{}\n'.format(result['msg'][host]['msg']['msg']))

                self.write(self.return_json(0, msg))
        else:
            self.write(self.return_json(-1, 'invalid json'))

    @staticmethod
    def delete_temp_file(blob_id):
        cisco_conf = '{}/{}'.format(options.cisco_temp_path, blob_id)

        if os.path.exists(cisco_conf):
            os.remove(cisco_conf)

    @staticmethod
    def write_to_file(blob_id, file_content):
        cisco_conf = '{}/{}'.format(options.cisco_temp_path, blob_id)

        if os.path.exists(cisco_conf):
            os.remove(cisco_conf)

        file_writer = open(cisco_conf, 'w')
        try:
            file_writer.write(file_content)
        except Exception:
            raise
        finally:
            file_writer.close()
