from pydantic import Field
from typing import Optional
from tatneft_back.db.collections.event import EventFields
from tatneft_back.models.base import BaseDBM

class Event(BaseDBM):
    # db fields
    filename: Optional[str] = Field(alias=EventFields.filename)
    user_id: Optional[int] = Field(alias=EventFields.user_id)
    privacy: Optional[str] = Field(alias=EventFields.privacy)