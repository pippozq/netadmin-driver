from controllers import health, ansible, juniper, cisco

import sys

sys.path.append('.')


# Return Router
def init():
    routers = [
        (r'/ansible/status$', health.HealthController),
        (r'/ansible/ping', ansible.AnsiblePingController),
        (r'/ansible/shell', ansible.AnsibleShellController),

        # juniper
        (r'/ansible/juniper/command$', juniper.JuniperCommandsController),

        # cisco
        (r'/ansible/cisco/command$', cisco.CiscoCommandsController)

    ]

    return routers
