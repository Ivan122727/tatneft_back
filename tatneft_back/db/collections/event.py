from typing import Optional
from xml.dom.minidom import Document
import pymongo

from tatneft_back.db.collections.base import BaseCollection, BaseFields


class EventFields(BaseFields):
    filename = "filename"
    user_id = "user_id"
    privacy = "privacy"

class EventCollection(BaseCollection):
    COLLECTION_NAME = "event"
    
    async def ensure_indexes(self):
        await super().ensure_indexes()
        self.pymongo_collection.create_index(
            [(EventFields.int_id, pymongo.ASCENDING), (EventFields.filename, pymongo.ASCENDING), (EventFields.user_id, pymongo.ASCENDING)],
            unique=True, sparse=True
        )