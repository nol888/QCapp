import json
import re

from tornado.web import RequestHandler

from .models import *

_items = []

class AddItemHandler(RequestHandler):
    """
    Handles requests to add a new QC issue.

    Returns a JSON object detailing success or failure.
    """
    TIME_PATTERN = re.compile("^[0-9]{2}:[0-9]{2}$")

    def post(self):
        try:
            payload = json.loads(self.request.body.decode('utf-8'))
            if not AddItemHandler.TIME_PATTERN.match(payload['time']):
                raise ValueError('time is invalid')

            _items.append(QCItem(status=ITEM_NEW, **payload))

            self.write({
                'id': len(_items) - 1 # lol this is terrible.
            })

        except Exception as e:
            self.set_status(500)
            self.write({
                'error': '{}: {}'.format(e.__class__.__qualname__, e)
            })

class ListItemsHandler(RequestHandler):
    """
    Handles requests to list all QC issues.

    Returns a JSON list; the index in the list is the ID of the issue.
    """

    def get(self):
        self.write({'items': [x.__dict__ for x in _items]})

class SetItemStatusHandler(RequestHandler):
    """
    Updates an item's status, based on the verb in the path.
    """

    def get(self, verb, id):
        VERB_TO_STATUS = {
            'reject': ITEM_REJECTED,
            'done': ITEM_DONE,
            'reopen': ITEM_NEW
        }

        try:
            id = int(id)
            _items[id].status = VERB_TO_STATUS[verb]

            self.write({
                'id': id,
                'status': _items[id].status
            })
        except Exception as e:
            self.set_status(500)
            self.write({
                'error': '{}: {}'.format(e.__class__.__qualname__, e)
            })

    def post(self, verb, id):
        return self.get(verb, id)