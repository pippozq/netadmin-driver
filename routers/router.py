from controllers import health, juniper, cisco

import sys

sys.path.append('.')


# Return Router
def init():
    routers = [
        (r'/netdriver/status$', health.HealthController),

        # juniper
        (r'/netdriver/juniper/command$', juniper.JuniperCommandsController),
        (r'/netdriver/juniper/config$', juniper.JuniperConfigController),

        # cisco
        (r'/netdriver/cisco/command$', cisco.CiscoCommandsController),
        (r'/netdriver/cisco/config$', cisco.CiscoConfigController)

    ]

    return routers
