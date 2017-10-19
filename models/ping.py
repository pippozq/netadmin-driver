from __future__ import print_function

from utils.ansible_model import AnsbileModel

import sys
sys.path.append('.')


class Shell(AnsbileModel):

    def __init__(self, args_dict):
        self.ansible_module_name = 'shell'
        self.args = args_dict['args']
        self.chdir = None
        self.creates = None
        self.executable = None
        self.free_form = None
        self.removes = False
        self.warn = True
        super(Shell, self).__init__()
