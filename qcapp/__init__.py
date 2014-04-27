import logging

from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import Application, RequestHandler
from os import path

from .service import AddItemHandler, ListItemsHandler, SetItemStatusHandler, TimeSearchHandler
from .eventsource import SSEHandler

logger = logging.getLogger(__name__)

class MainHandler(RequestHandler):
    def get(self):
        self.render("index.html")

def main():
    define("port", default=8888, help="run webserver on the given port", type=int)
    parse_command_line()

    logger.info("QCapp start up...")

    app = Application(
        [
            (r"/$", MainHandler),
            (r"/api/add$", AddItemHandler),
            (r"/api/list$", ListItemsHandler),
            (r"/api/(reopen|done|reject)/([0-9]+)$", SetItemStatusHandler),
            (r"/api/stream$", SSEHandler),
            (r"/api/search/time/([0-9]{2}:[0-9]{2})$", TimeSearchHandler)
        ],
        template_path=path.join(path.dirname(__file__), "templates"),
        static_path=path.join(path.dirname(__file__), "static")
        )
    app.listen(options.port)
    IOLoop.instance().start()
