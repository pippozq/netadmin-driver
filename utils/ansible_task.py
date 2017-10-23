from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.data import InventoryData
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase

from tornado.gen import coroutine
from tornado.options import options

__metaclass__ = type

DEFAULT_CONNECTION = 'ssh'
LOCAL_CONNECTION = 'local'
DEFAULT_TRANSPORT = 'paramiko'


class InnerInventoryManager(InventoryManager):
    def __init__(self, loader, hosts):

        # base objects
        self._loader = loader
        self._hosts = hosts
        self._inventory = InventoryData()

        # a list of host(names) to contain current inquiries to
        self._restriction = None
        self._subset = None

        # caches
        self._hosts_patterns_cache = {}  # resolved full patterns
        self._pattern_cache = {}  # resolved individual patterns
        self._inventory_plugins = []  # for generating inventory
        super(InnerInventoryManager, self).__init__(loader, None)
        self._set_hosts()

    def _set_hosts(self):
        if isinstance(self._hosts, str):
            _host = list()
            _host.append(self._hosts)
            self._hosts = _host
        for h in self._hosts:
            self._inventory.add_host(host=h)


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


class AnsibleTask(TaskQueueManager):

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

    def __init__(self, host, user, tasks, connection=None, forks_number=5):
        self.Options = namedtuple('Options', ['remote_user','connection','module_path', 'forks', 'become',
                                              'become_method', 'become_user', 'check', 'transport','host_key_checking',
                                              'private_key_file','record_host_keys', 'diff'])

        self.variable_manager = VariableManager()
        self.loader = DataLoader()
        self.host = list()
        if isinstance(host, str):
            self.host.append(host)
        elif isinstance(host, list):
            self.host = host

        if user is None:
            self.remote_user = 'root'
            self.password_dict['password'] = None
        else:
            self.remote_user = user['name'] if 'name' in user else 'root'
            self.password_dict['conn_pass'] = user['password'] if 'password' in user else None

        # ssh key
        self.ssh_key_file = None if options.ssh_key_file is None else options.ssh_key_file
        self.options = self.Options(remote_user=self.remote_user,
                                    connection=DEFAULT_CONNECTION if connection is None else LOCAL_CONNECTION,
                                    module_path=None,
                                    forks=forks_number,
                                    become=None,
                                    become_method=None,
                                    become_user=None,
                                    check=False,
                                    transport=DEFAULT_TRANSPORT,
                                    host_key_checking=False,
                                    record_host_keys=False,
                                    private_key_file=self.ssh_key_file,
                                    diff=False)

        self.results_callback = ResultCallback()
        self.inventory = InnerInventoryManager(loader=self.loader, hosts=self.host)
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)

        self.play_tasks_list = tasks

        TaskQueueManager.__init__(self, self.inventory, self.variable_manager,
                                  self.loader, self.options, self.password_dict, self.results_callback)

    def get_result(self):
        return self.results_callback.get_ansible_result()

    @coroutine
    def run_ansible_playbook(self):
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
            return result
        finally:
            if tqm is not None:
                tqm.cleanup()
