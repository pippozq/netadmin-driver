from __future__ import print_function

from controllers import health, ansible

import sys
sys.path.append('.')


# Return Router
def init():
    routers = [
        (r'/ansible/status$', health.HealthController),
        (r'/ansible/ping', ansible.AnsiblePingController),
        (r'/ansible/shell', ansible.AnsibleShellController),
    ]

    return routers
