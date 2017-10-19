from __future__ import (absolute_import, division, print_function)
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase

from tornado.gen import coroutine, Return


__metaclass__ = type

DEFAULT_CONNECTION = 'ssh'
DEFAULT_TRANSPORT = 'paramiko'


class ResultCallback(CallbackBase):

    RUN_OK = 0
    RUN_ERROR = 1
    RUN_FAILED_HOSTS = 2
    RUN_UNREACHABLE_HOSTS = 4
    RUN_FAILED_BREAK_PLAY = 8
    RUN_UNKNOWN_ERROR = 255

    def __init__(self):
        self.result = dict()
        CallbackBase.__init__(self)

    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        if 'stdout_lines' in result._result:
            self.result[host.name] = self._dump_results({'msg': result._result['stdout_lines'], 'status': self.RUN_OK}, indent=4)
        else:
            self.result[host.name] = self._dump_results({'msg': result._result, 'status': self.RUN_OK}, indent=4)

    def v2_runner_on_failed(self, result, ignore_errors=True):
        host = result._host
        if 'stdout_lines' in result._result:
            self.result[host.name] = self._dump_results({'msg': result._result['stderr'], 'status': self.RUN_FAILED_HOSTS}, indent=4)
        else:
            self.result[host.name] = self._dump_results({'msg': result._result, 'status': self.RUN_FAILED_HOSTS}, indent=4)

    def v2_runner_on_unreachable(self, result):
        host = result._host
        self.result[host.name] = self._dump_results({'msg': result._result['msg'], 'status': self.RUN_UNREACHABLE_HOSTS}, indent=4)

    def get_ansible_result(self):
        return self.result


class AnsibleUtil(TaskQueueManager):

    remote_user = ''
    password_dict = dict()

    Options = tuple()
    option = None
    variable_manager = None
    loader = None
    host = None
    results_callback = None
    inventory = None

    play_tasks_list = None

    def __init__(self, host, user_info,play_tasks_list, forks_number=5):
        self.Options = namedtuple('Options', ['remote_user', 'connection', 'module_path', 'forks', 'become',
                                              'become_method', 'become_user', 'check', 'transport','host_key_checking',
                                              'private_key_file', 'record_host_keys'])
        self.variable_manager = VariableManager()
        self.loader = DataLoader()
        self.host = list()
        if isinstance(host, str):
            self.host.append(host)
        elif isinstance(host, list):
            self.host = host
        self.remote_user = user_info['remote_user'] if 'remote_user' in user_info else 'root'
        self.password_dict['password'] = user_info['password'] if 'password' in user_info else None

        self.options = self.Options(remote_user=self.remote_user,
                                    connection=DEFAULT_CONNECTION,
                                    module_path=None,
                                    forks=forks_number,
                                    become=None,
                                    become_method=None,
                                    become_user=None,
                                    check=False,
                                    transport=DEFAULT_TRANSPORT,
                                    host_key_checking=False,
                                    record_host_keys=False,
                                    private_key_file='keys/id_rsa')

        self.results_callback = ResultCallback()
        self.inventory = InventoryManager(loader=self.loader)
        self.variable_manager.set_inventory(self.inventory)

        self.play_tasks_list = play_tasks_list

        TaskQueueManager.__init__(self, self.inventory, self.variable_manager,
                                  self.loader, self.options, self.password_dict, self.results_callback)

    def get_result(self):
        return self.results_callback.get_ansible_result()

    @coroutine
    def run_ansible(self):
        tqm = None
        play_source = dict(
            name="Ansible Play",
            hosts=self.host,
            gather_facts='no',
            tasks=self.play_tasks_list
        )

        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        try:
            result = self.run(play)
            raise Return(result)
        finally:
            if tqm is not None:
                tqm.cleanup()