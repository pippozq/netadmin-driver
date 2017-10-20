from __future__ import print_function

from utils.ansible_model import AnsbileModel

import sys
sys.path.append('.')


class Ping(AnsbileModel):

    def __init__(self):
        super(Ping, self).__init__('ping', None)


class Shell(AnsbileModel):

    def __init__(self, args):
        super(Shell, self).__init__('shell', args)