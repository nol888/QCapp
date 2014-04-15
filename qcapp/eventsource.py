"""
QCapp Server-Sent Events implementation.
"""
import json
import logging
import uuid

from tornado.web import RequestHandler, asynchronous

logger = logging.getLogger(__name__)

SSE_HEADERS = (
    ('Content-Type', 'text/event-stream; charset=utf-8'),
    ('Cache-Control', 'no-cache'),
    ('Connection', 'keep-alive'),
    ('Access-Control-Allow-Origin', '*'),
)

class SSEHandler(RequestHandler):
    """
    Handles subscriptions to the application's event stream.

    A more sophisticated and modular SSE implementation would include
    multiple channels, etc. For our purposes, there will only ever be
    one stream, so this is fine.

    This is loosely based off of tornado-sse (https://github.com/truetug/tornado-sse/).
    """

    __subscribers = []

    def __init__(self, application, request, **kwargs):
        super(SSEHandler, self).__init__(application, request, **kwargs)
        self.stream = request.connection.stream
        self._closed = False

    def initialize(self):
        for name, value in SSE_HEADERS:
            self.set_header(name, value)

    @asynchronous
    def get(self):
        headers = self._generate_headers()
        self.write(headers)
        self.flush()

        logger.info("200 STREAM ({})".format(self.request.connection.address[0]))

        SSEHandler.__subscribers.append(self)

    def on_connection_close(self):
        """Remove this client from the list of subscribers."""
        SSEHandler.__subscribers.remove(self)
        self.stream.close()

    @classmethod
    def push(cls, msg, event=None):
        try:
            msg = json.dumps(msg)
        except Exception:
            pass

        # Construct the SSE message.
        data = "event: {}\n".format(event) if event is not None else ""
        data += "data: {}\n\n".format(msg)
        data = data.encode("utf-8")

        logger.info("PUSH event={} ({} clients)".format("message" if event is None else event, len(cls.__subscribers)))

        for x in cls.__subscribers:
            x.write(data)
            x.flush()
