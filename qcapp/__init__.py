from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line
from tornado.web import Application, RequestHandler
from os import path

class ShitHandler(RequestHandler):
    def get(self):
        self.write("<h1>It works!</h1>")

def main():
    define("port", default=8888, help="run webserver on the given port", type=int)
    parse_command_line()

    app = Application(
        [
            (r"/", ShitHandler)
        ],
        template_path=path.join(path.dirname(__file__), "templates"),
        static_path=path.join(path.dirname(__file__), "static")
        )
    app.listen(options.port)
    IOLoop.instance().start()
    print("hello world!")
