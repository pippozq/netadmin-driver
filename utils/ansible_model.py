from __future__ import print_function


class AnsbileModel(object):

    def __init__(self, module_name, args):
        self.ansible_module_name = module_name
        self.args = args
        self.action_dict = dict()
        self.task_dict = dict()

    def ansible_task(self):
        self.action_dict['module'] = self.ansible_module_name
        if self.args:
            self.action_dict['args'] = self.args
        self.task_dict['action'] = self.action_dict

        return self.task_dict
