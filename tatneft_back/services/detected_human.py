from typing import Optional
from tatneft_back.db.collections.base import Id
from tatneft_back.db.collections.detected_human import DetectedHumanFields
from tatneft_back.models.detected_human import DetectedHuman
from tatneft_back.core.consts import  db

async def create_detected_human(
        *,
        avatar_filename: Optional[str] = None,
        event_id: Optional[int] = None,
        usefulness: Optional[str] = None,
):
    doc_to_insert = {
        DetectedHumanFields.event_id: event_id,
        DetectedHumanFields.avatar_filename: avatar_filename,
        DetectedHumanFields.usefulness: usefulness,
    }
    inserted_doc = await db.detected_human_collection.insert_document(document=doc_to_insert)
    created_detected_human = DetectedHuman.parse_document(inserted_doc)
    return created_detected_human

async def get_detected_humans(event_id: int) -> list[DetectedHuman]:
    detected_humans = [DetectedHuman.parse_document(doc) async for doc in db.detected_human_collection.create_cursor() if doc[DetectedHumanFields.event_id] == event_id]
    return detected_humans

async def get_detected_human(
        *,
        id_: Optional[Id] = None,
        int_id: Optional[int] = None,
) -> Optional[DetectedHuman]:
    filter_ = {}
    if id_ is not None:
        filter_.update(db.user_collection.create_id_filter(id_=id_))
    if int_id is not None:
        filter_[DetectedHumanFields.int_id] = int_id

    if not filter_:
        raise ValueError("not filter_")

    doc = await db.event_collection.find_document(filter_=filter_)
    if doc is None:
        return None
    return DetectedHuman.parse_document(doc)