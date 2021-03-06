from tornado.ioloop import IOLoop
from tornado.web import Application
from tornado.httpserver import HTTPServer
from tornado.options import define, options

from routers import router

# config
define("conf", help="Config File", type=str)
define("port", help='Ansible Web Port', type=int)
define("date_fmt", help='data time', type=str)
define("ssh_key_file", help='data time', type=str)
define("debug", help='debug on', type=bool)


class App(Application):
    def __init__(self, debug=False):
        settings = {
            'debug': debug,
        }
        handles = router.init()
        super(App, self).__init__(handles, **settings)


if __name__ == "__main__":
    options.parse_command_line()
    options.parse_config_file('conf/%s.conf' % options.conf)
    app = App(debug=options.debug)
    http_server = HTTPServer(app)
    http_server.listen(options.port)
    IOLoop.instance().start()
