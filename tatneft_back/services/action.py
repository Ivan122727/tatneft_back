from typing import Optional

from tatneft_back.core.enumerations import UserRoles
from tatneft_back.db.collections.action import ActionFields
from tatneft_back.db.collections.base import Id
from tatneft_back.db.collections.event import EventFields
from tatneft_back.models.action import Action
from tatneft_back.models.user import User
from tatneft_back.core.consts import  db
from tatneft_back.models.event import Event

async def create_action(
        *,
        detected_human_id: Optional[int] = None,
        price: Optional[int] = None,
        title: Optional[str] = None,
        timeline: Optional[str] = None,
        event_id: Optional[int] = None,
):
    doc_to_insert = {
        ActionFields.price: price,
        ActionFields.detected_human_id: detected_human_id,
        ActionFields.title: title,
        ActionFields.timeline: timeline,
        ActionFields.event_id: event_id,
    }
    inserted_doc = await db.action_collection.insert_document(document=doc_to_insert)
    created_action = Action.parse_document(inserted_doc)
    return created_action

async def get_actions(event_id: int) -> list[Action]:
    actions = [Action.parse_document(doc) async for doc in db.action_collection.create_cursor() if doc[ActionFields.event_id] == event_id]
    return actions


async def get_action(
        *,
        id_: Optional[Id] = None,
        int_id: Optional[int] = None,
) -> Optional[Event]:
    filter_ = {}
    if id_ is not None:
        filter_.update(db.action_collection.create_id_filter(id_=id_))
    if int_id is not None:
        filter_[ActionFields.int_id] = int_id

    if not filter_:
        raise ValueError("not filter_")

    doc = await db.action_collection.find_document(filter_=filter_)
    if doc is None:
        return None
    return Action.parse_document(doc)