import logging

from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import Application, RequestHandler
from os import path

from .service import *

logger = logging.getLogger(__name__)

class ShitHandler(RequestHandler):
    def get(self):
        self.write("<h1>It works!</h1>")

def main():
    define("port", default=8888, help="run webserver on the given port", type=int)
    parse_command_line()

    logger.info("QCapp start up...")

    app = Application(
        [
            (r"/$", ShitHandler),
            (r"/api/add$", AddItemHandler),
            (r"/api/list$", ListItemsHandler),
            (r"/api/(reopen|done|reject)/([0-9]+)$", SetItemStatusHandler)
        ],
        template_path=path.join(path.dirname(__file__), "templates"),
        static_path=path.join(path.dirname(__file__), "static")
        )
    app.listen(options.port)
    IOLoop.instance().start()
