from typing import Optional

from tatneft_back.core.enumerations import UserRoles
from tatneft_back.db.collections.base import Id
from tatneft_back.db.collections.event import EventFields
from tatneft_back.models.user import User
from tatneft_back.core.consts import  db
from tatneft_back.models.event import Event

async def upload_event(
        *,
        filename: Optional[str] = None,
        user_id: Optional[int] = None,
        privacy: Optional[str] = None,
):
    doc_to_insert = {
        EventFields.user_id: user_id,
        EventFields.filename: filename,
        EventFields.privacy: privacy,
    }
    inserted_doc = await db.event_collection.insert_document(document=doc_to_insert)
    created_research = Event.parse_document(inserted_doc)
    return created_research

async def get_events() -> list[Event]:
    users = [Event.parse_document(doc) async for doc in db.event_collection.create_cursor()]
    return users


async def get_event(
        *,
        id_: Optional[Id] = None,
        int_id: Optional[int] = None,
) -> Optional[Event]:
    filter_ = {}
    if id_ is not None:
        filter_.update(db.user_collection.create_id_filter(id_=id_))
    if int_id is not None:
        filter_[EventFields.int_id] = int_id

    if not filter_:
        raise ValueError("not filter_")

    doc = await db.event_collection.find_document(filter_=filter_)
    if doc is None:
        return None
    return Event.parse_document(doc)