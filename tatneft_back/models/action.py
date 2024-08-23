from pydantic import Field
from typing import Optional
from tatneft_back.db.collections.action import ActionFields
from tatneft_back.models.base import BaseDBM

class Action(BaseDBM):
    # db fields
    detected_human_id: Optional[int] = Field(alias=ActionFields.detected_human_id)
    price: Optional[int] = Field(alias=ActionFields.price)
    title: Optional[str] = Field(alias=ActionFields.title)
    timeline: Optional[str] = Field(alias=ActionFields.timeline)
    event_id: Optional[int] = Field(alias=ActionFields.event_id)