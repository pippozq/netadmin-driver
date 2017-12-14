from jnpr.junos import Device
from jnpr.junos.utils.config import Config
from jnpr.junos import exception as junos_exception
from jnpr.junos.utils.start_shell import StartShell
from tornado.log import gen_log

Device.auto_probe = 10


class Junos(object):
    device = None

    def __init__(self, host, user=dict, port=22):
        self.device = Device(host=host, user=user['name'], password=user['password'], port=port)

    def open_connection(self):
        try:
            self.device.open()
        except junos_exception.ConnectTimeoutError as err:
            gen_log.error('junos connect timeout:{}'.format(err.args))
            err_msg = 'junos connect timeout:{}'.format(err.args)
            raise Exception(err_msg)
        except junos_exception.ConnectError as err:
            gen_log.error('junos connect error:{}'.format(err.args))
            err_msg = 'junos connect error:{}'.format(err.args)
            raise Exception(err_msg)

    def run_config(self, config):
        commit_result = False
        err_msg = ''
        try:
            with Config(self.device, mode='exclusive') as cu:
                try:
                    cu.load(config, format='set')
                except junos_exception.ConfigLoadError as err:
                    gen_log.error(err)
                    err_msg = 'junos config load {}'.format(err.message)
                else:
                    try:
                        check = cu.commit_check()
                        if check:
                            commit_result = cu.commit()
                    except junos_exception.CommitError as err:
                        err_msg = 'junos config commit error:{}'.format(err.message)
        except junos_exception.LockError as lock_err:
            err_msg = 'junos config lock {}'.format(lock_err.message)

        return commit_result, err_msg

    def execute_shell(self, command):
        shell = StartShell(self.device)
        try:
            shell.open()
            result = shell.run("cli -c " + "\"" + command + "\"")
            shell.close()
        except Exception as err:
            return False, err.args.__str__()
        else:
            return result[0], result[1]

    def close(self):
        try:
            self.device.close()
        except Exception as err:
            gen_log.error(err)
