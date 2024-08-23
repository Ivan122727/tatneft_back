from typing import Optional
from xml.dom.minidom import Document
import pymongo

from tatneft_back.db.collections.base import BaseCollection, BaseFields


class DetectedHumanFields(BaseFields):
    event_id = "event_id"
    avatar_filename = "avatar_filename"
    usefulness = "usefulness"

class DetectedHumanCollection(BaseCollection):
    COLLECTION_NAME = "detected_human"
    
    async def ensure_indexes(self):
        await super().ensure_indexes()
        self.pymongo_collection.create_index(
            [(DetectedHumanFields.int_id, pymongo.ASCENDING), (DetectedHumanFields.event_id, pymongo.ASCENDING)],
            unique=True, sparse=True
        )