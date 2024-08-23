from typing import Optional
from xml.dom.minidom import Document
import pymongo

from tatneft_back.db.collections.base import BaseCollection, BaseFields


class ActionFields(BaseFields):
    detected_human_id = "detected_human_id"
    price = "price"
    title = "title"
    timeline = "timeline"
    event_id = "event_id"


class ActionCollection(BaseCollection):
    COLLECTION_NAME = "action"
    
    async def ensure_indexes(self):
        await super().ensure_indexes()
        self.pymongo_collection.create_index(
            [(ActionFields.int_id, pymongo.ASCENDING), (ActionFields.event_id, pymongo.ASCENDING), (ActionFields.detected_human_id, pymongo.ASCENDING)],
            unique=True, sparse=True
        )