"""
Quality Control data model.

I don't know why this is a separate module.
"""

from json import dumps

ITEM_NEW = 1
ITEM_DONE = 2
ITEM_REJECTED = 3

class QCItem:
    def __init__(self, time, text, author, status=ITEM_NEW):
        self.time = time
        self.text = text
        self.status = status
        self.author = author

    def __lt__(self, other):
        return self.time < other.time

    def json(self):
        return dumps(self.__dict__)