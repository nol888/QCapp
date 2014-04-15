"""
QCapp RESTful API handlers.
"""

import json
import re

from tornado.web import RequestHandler

from .models import QCItem, ITEM_NEW, ITEM_DONE, ITEM_REJECTED
from .eventsource import SSEHandler

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

            item = QCItem(status=ITEM_NEW, **payload)
            _items.append(item)

            self.write({
                'id': len(_items) - 1 # lol this is terrible.
            })
            self.finish()

            # Now I wish this ID thing was a lot better.
            item = item.__dict__
            item['id'] = len(_items) - 1
            SSEHandler.push(item, "add")
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

            response = {
                'id': id,
                'status': _items[id].status
            }

            self.write(response)
            self.finish()

            SSEHandler.push(response, "change")
        except Exception as e:
            self.set_status(500)
            self.write({
                'error': '{}: {}'.format(e.__class__.__qualname__, e)
            })

    def post(self, verb, id):
        return self.get(verb, id)